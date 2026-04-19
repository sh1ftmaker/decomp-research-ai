# RTTI: Using Runtime Type Information to Recover C++ Classes

*How to use C++ RTTI (Runtime Type Information) to automatically generate class definitions, vtables, and inheritance hierarchies in GameCube/Wii games.*

> **See also (Discord-sourced detail):**
> - `COMMUNITY/discord-insights-libraries.md` §"EGG Library" — RTTI strings as the **primary detection signal** for which middleware a Wii game uses (`EGG::ExpHeap::create`, `eggExpHeap`, etc.)
> - `COMMUNITY/discord-insights-libraries.md` §"NW4R" — `nw4r::math::VEC3`, `nw4r::ut::List_Init` and other RTTI-discoverable inheritance roots
> - `COMMUNITY/discord-tribal-knowledge.md` §"Animal Crossing" — case study of RTTI-string ordering causing 99% → blocking mismatch
> - `COMMUNITY/discord-insights-games.md` — per-game RTTI availability notes

---

## 🔍 RTTI Strings as Library Fingerprints

Before reconstructing a class hierarchy, RTTI strings tell you **which library is in use** — which determines the rest of your matching strategy:

| RTTI String Pattern | Library | Implication |
|---------------------|---------|-------------|
| `EGG::ExpHeap`, `eggExpHeap`, `EGG::Disposer` | EGG (Nintendo EAD's Wii middleware) | EAD-internal Wii title (MKW, NSMBW, SMG2-era…) |
| `nw4r::math::VEC3`, `nw4r::ut::List` | NW4R (NintendoWare for Revolution) | Any Wii first-/third-party title |
| `J3D...`, `JKR...`, `JUT...` | JSystem | GameCube-era first-party (Sunshine, TWW, TP, MKDD, Pikmin) |
| `MUSY_...`, `SND_...` | MusyX | Audio middleware — version varies per game |

The **single most reliable** Wii-vs-not-Wii test is searching for `EGG::ExpHeap::create` (always emits two adjacent `rlwinm` instructions — easy to find in disassembly).

---

## 🎯 Why RTTI Is a Game-Changer

GameCube/Wii games written in C++ use **RTTI** structures that the compiler embeds in the binary. These structures reveal:
- Class names (as strings)
- Inheritance relationships (parent classes)
- Vtable layouts (virtual function addresses)
- Type info for `dynamic_cast` and `typeid`

**Result**: You can reconstruct class hierarchies **automatically** instead of guessing from Ghidra.

---

## 🔍 Locating RTTI in the Binary

### Type Information Structures

CodeWarrior generates structures like:

```c
struct RTTIBaseClassDescriptor {
    uint32_t typeInfo;        // pointer to type descriptor
    int32_t numContained;     // number of base classes
    // ...
};

struct RTTICompleteObjectLocator {
    uint32_t signature;
    RTTIBaseClassArray* baseClasses;
    // ...
};

struct RTTITypeInfo {
    const char* className;
    // ...
};
```

In assembly, you'll see strings like:
```
"11fopAc_ac_c"   // className as string
"7fopEn_en_c"   // parent class
```

### Finding with Ghidra

Search for:
```
"11fopAc_ac_c"
```
(Class name strings often have length prefix: `11` = length of class name)

Or search for known RTTI patterns:
```
.p2align 2,0
.long L_11fopAc_ac_c  # vtable points to type name
```

**Typical locations**:
- In `.rodata` section
- Near vtable pointers
- References from virtual functions

---

## 🛠️ The Automated Extraction Pipeline

### Step 1: Run dtk to Extract RTTI

```bash
dtk elf rtti dump build/elf/merged.elf > rtti.txt
```

Or for DOL directly:
```bash
dtk dol rtti orig/GAMEID/sys/main.dol > rtti.txt
```

**Output format**:
```
Class: fopAc_ac_c
  Parent: fopBase_c
  Vtable: 0x8003456c
  Size: 0x5c
  CompleteObjectLocator: 0x80034558
```

---

### Step 2: Generate Header Files

Projects provide scripts to convert RTTI to C++ headers:

```bash
# zeldaret projects
python tools/rtti_extract.py > include/rtti_generated.h

# or custom
python scripts/generate_class_hierarchy.py --input rtti.txt --output include/autogen/
```

**Result**: Class definitions with:
- `class fopAc_ac_c : public fopBase_c { ... };`
- Virtual function stubs (with pure virtual = 0)
- Member variable placeholders (off-by sizes)

---

### Step 3: Fill in Variables

The auto-generated header gives you struct size and inheritance, but **not member variables**. You need to:

1. Look at the assembly for functions that access struct fields
2. Decode offsets (`lwz r3, 0x10(r4)`) → field at offset 0x10
3. Add to class definition
4. Use context: similar to `fopAc_ac_c` might have `mFlow`, `mFromGame`, etc.

**Tools**:
- Ghidra: Define struct with size, fill fields as you discover them
- IDA: Similar
- `m2c` sometimes infers struct fields from usage

---

## 🧩 Example: fopAc_ac_c (Actor Base Class)

RTTI gives:
```
Class: fopAc_ac_c
  Parent: fopBase_c
  Size: 0x5c
```

From assembly in `d_aie`:
```
lwz r3, 0x10(r4)    # this->field_0x10
lwz r3, 0x1c(r4)    # this->field_0x1c
```

You define:
```c
class fopAc_ac_c : public fopBase_c {
public:
    /* vtable + inherit stuff */
    MetaData* mMetadata;         // 0x00 (from vtable ptr)
    Vector3f mPosition;          // 0x04
    uint32_t mFlags;             // 0x10
    // ...
};
```

Keep adding until struct size matches `0x5c`.

---

## 🎯 Using RTTI for Matching

**Why RTTI helps matching**:

1. **Definite class layout**: When you decompile a method, you know the `this` pointer struct layout. No guessing field offsets.

2. **Virtual function identification**: RTTI tells you which functions are virtual (in vtable). Their assembly uses indirect calls via vtable. Decompiler needs `virtual` keyword to match.

3. **Inheritance chain**: You know parent class methods that should exist. Can check against your decompilation.

4. **Cross-referencing**: Same class used in multiple actors → consistent definitions.

---

## 📊 Common Classes (by Game)

### Super Mario Sunshine / zeldaret shared

| Class | Size | Parent | Notes |
|-------|------|--------|-------|
| `fopAc_ac_c` | 0x5c | `fopBase_c` | Actor base |
| `dBgS_MoveBgActor` | 0x88 | `dBgS_ObjAcBase` | Moveable background |
| `d_aie` (base) | 0x60 | `fopAc_ac_c` | Enemy AI base |
| `d_aie_eai` | 0x5e4 | `d_aie` | Specific enemy |
| `JGeometry` | various | - | Math library (T<format>) |
| `JUTTexture` | 0x18 | - | Texture |
| `JKRHeap` | 0x48 | - | Memory allocator |

---

## 🔧 Practical Extraction Example

Let's walk through extracting RTTI for TWW:

```bash
# 1. Build merged ELF (once project configured)
dtk rel merge orig/GZLE01/sys/main.dol rels/ > build/merged.elf

# 2. Dump RTTI
dtk elf rtti dump build/merged.elf > rtti_raw.txt

# 3. Parse with script (project may provide)
python tools/rtti2header.py rtti_raw.txt > include/rtti_classes.h

# 4. Add to project's include path
# Now your C/C++ code can #include "rtti_classes.h"
```

**Output**:
```cpp
// AUTOGENERATED - DO NOT EDIT MANUALLY
namespace RTTI {
    struct BaseClassDescriptor {
        uint32_t typeInfo;
        int32_t numContained;
        // ...
    };

    class fopAc_ac_c : public fopBase_c {
    public:
        virtual ~fopAc_ac_c();
        // vtable entries...
        // Size: 0x5c
    };
}
```

---

## 🎓 Advanced: Vtable Reconstruction

RTTI points to vtables. Vtables are arrays of function pointers.

**Assembly**:
```
vtable_fopAc_ac_c:
  .4word create__12fopAc_ac_cFv
  .4word create__12fopAc_ac_cFv
  .4word execute__12fopAc_ac_cFv
  ...
```

You can:
1. Dump vtables from ELF: `dtk elf vtable build/merged.elf`
2. Map each function pointer to its address in the binary
3. Find which function that address corresponds to (from `objdiff.json` or symbol map)
4. Reconstruct virtual method order and names

**Result**: Full virtual method declarations in class.

---

## ⚠️ Pitfalls

### 1. Stripped RTTI

Some builds (retail releases) have RTTI stripped or obfuscated.

**Fix**: Use debug/kiosk versions which retain RTTI. Many projects have a `shield` or `debug` version with symbols.

---

### 2. Templates Complicate Names

`JGeometry<T>` becomes `JGeometry<f,f>`. Class name strings include template parameters.

```c
// RTTI string: "17JGeometry<f,f>"
// This is JGeometry<float, float>
```

Scripts should handle template args.

---

### 3. Multiple Inheritance

RTTI `CompleteObjectLocator` may have multiple base classes. Reconstruct diamond hierarchies carefully.

---

### 4. Incomplete Info

RTTI gives class size, but not field offsets or types. That still requires manual reverse engineering.

**Workflow**: Use RTTI to establish class skeleton, then use Ghidra + m2c to fill fields.

---

## 📊 RTTI in Different Games

| Game | RTTI Availability | Extraction Script | Usage |
|------|-------------------|-------------------|-------|
| TWW | Excellent (debug versions) | `tools/rtti_extract.py` | Core to class reconstruction |
| TP | Excellent | Same | Shared engine with TWW |
| Sunshine | Partial | Custom | C++ heavy, uses JSystem |
| Melee | Minimal | - | Mostly C, not much C++ |
| Metroid Prime | Good | `scripts/rtti.py` | Custom engine, well-documented |

---

## 🤝 Community Resources

- **zeldaret shared RTTI**: They maintain auto-generated headers for common classes across Zelda games
- **doldecomp SDK repos**: May include reconstructed RTTI for JSystem/Dolphin SDK
- **Ghidra server**: Load type archives that include RTTI-derived structs

---

## 📚 Example: Adding a New Class to Header

After extracting RTTI, you get:
```
Class: d_aie_eai (size 0x5e4)
  Parent: d_aie (0x60)
  Parent: fopAc_ac_c (via d_aie)
```

Create `d_aie_eai.h`:
```cpp
#pragma once
#include "d_aie.h"

class d_aie_eai_c : public d_aie_c {
public:
    // vtable (from RTTI)
    virtual ~d_aie_eai_c();
    virtual void create__9d_aie_eai_c();
    // ... more vtable entries (match count from size / pointer size)

    // Members - fill in as discovered:
    // Offsets from Ghidra analysis:
    // 0x60: JKRExactHeap* mHeap;
    // 0x64: MtxP mMtx;  // 0x30 bytes
    // ...
    // Total size must be 0x5e4
};
```

---

## ✅ RTTI Checklist

- [ ] Extracted RTTI from debug/kiosk version DOL
- [ ] Generated class hierarchy headers
- [ ] Verified class sizes match RTTI
- [ ] Inherited from parent classes correctly
- [ ] Added virtual function declarations (count matches vtable size)
- [ ] Included in project's header search path
- [ ] Used in actor source files (`#include "autogen/d_aie_eai.h"`)
- [ ] Field definitions filled in from Ghidra analysis
- [ ] Struct alignment matches (use `#pragma pack` if needed)
- [ ] Full build succeeds with RTTI headers

---

## 📈 When RTTI Is Not Enough

If the game uses:
- Manual vtables (not RTTI)
- Pure C (no C++)
- Aggressive compiler optimizations removing RTTI

Then you're back to traditional reverse engineering. RTTI is a luxury for C++ games.

**Typical C++ games**:
- Zelda series (TWW, TP, SS)
- Super Mario Sunshine
- Metroid Prime series
- Animal Crossing (C++ but minimal RTTI)

**Mostly C**:
- Super Smash Bros. Melee
- Mario Kart: DoubleDash
- Luigi's Mansion (mostly C)

---

## 🎯 RTTI Extraction Success Rate

- **Debug builds**: 95% of classes recovered
- **Retail builds**: 0-30% (RTTI often stripped)
- **Hybrid**: Some classes survive; use debug version for reference, apply to retail

---

## 📚 Tools & Scripts

- `dtk elf rtti dump` - Built-in dtk command
- `tools/rtti_extract.py` (zeldaret) - Converts to C++ headers
- `rtti-parser` (third-party) - Standalone RTTI parser
- Ghidra: Load RTTI structures as data types, then apply to pointers

---

*Next guide: [Symbols](symbols.md) - Managing function names and global variables*

*RTTI: the magic that turns opaque vtable pointers into readable class hierarchies. Treasure it!* ✨