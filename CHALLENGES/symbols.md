# Symbol Resolution: Mapping Addresses to Names

*How to identify functions and global variables when they're not labeled, using various techniques from symbol maps to pattern recognition.*

> **See also (Discord-sourced detail):**
> - `COMMUNITY/discord-insights-tools.md` §"cwparse" — Rust library for parsing Metrowerks `.map` files (Melee, Pikmin, Monkey Ball, Metroid Prime tested)
> - `COMMUNITY/discord-insights-tools.md` §"objdiff" — right-click → "Copy mangled name" workflow for grepping symbols across the project
> - `COMMUNITY/zelda-insights-tools-other.md` — Ghidra symbol-map import (must remove the `Offset` column before pasting)
> - `COMMUNITY/discord-insights-libraries.md` §"JSystem"/"EGG"/"NW4R" — namespace prefixes & RTTI string conventions

---

## ⚡ Two Tools Worth Knowing About First

**`cwparse`** is a Rust library that parses Metrowerks linker `.map` files into structured symbol data. It's the foundation of `objdiff.csv` generation, progress calculation, and symbol-order mismatch detection. If you've imported a leaked debug map, `cwparse` is what reads it.

**objdiff's "Copy mangled name"** — right-click any symbol in objdiff to copy the mangled CodeWarrior name to the clipboard. Then `grep -r "<mangled>"` across the project to find every reference. Faster than re-demangling and re-grepping by hand.

---

## 🎯 The Symbol Problem

When you decompile a GameCube/Wii binary, you often encounter:
```
0x80001234:  some_function
0x80005678:  another_function
```

These are just **addresses**. You need to figure out:
- What does this function do?
- What's a good name for it?
- What global variables does it reference?

Naming things is half the battle. Good names make the code readable, help matching, and enable collaborative work.

---

## 🔍 Types of Symbol Information Available

| Source | What It Gives | Typical Format | Reliability |
|--------|---------------|----------------|-------------|
| **Debug Map Files** (`*.map`) | Function names, file paths, line numbers | Text (Metrowerks format) | ★★★★★ (Perfect) |
| **Symbol Stubs** (`symbols.txt`) | Names + VRAM addresses | `0x80012345 function_name` | ★★★★★ (if accurate) |
| **RTTI** | Class names, virtual methods | Embedded in binary | ★★★★☆ (only C++) |
| **String References** | Function names as strings | `"OSReport"` etc. | ★★★★☆ (SDK functions) |
| **Demangle** | C++ mangled names → readable | `?func@@YAXXZ` → `func(void)` | ★★★★★ |
| **Ghidra Analysis** | Heuristic names based on patterns | `FUN_80012345`, `LAB_80012345` | ★★☆☆☆ (auto) |
| **Pattern Recognition** | Known SDK function signatures | Manual identification | ★★★★☆ (expert) |

---

## 📂 Map Files: The Holy Grail

### What Are They?

Linker map files list **every** symbol in the binary with:
- VRAM address
- Function size
- Source file (if debug info present)
- Parent namespace/module

### Obtaining Maps

**Available for**:
- Nintendo kiosk/demo builds (often leak)
- Debug versions of games (internal)
- Developer discs
- Some retail builds with partial symbols

**Example** (from zeldaret TP debug map):
```
  section  .text  base=0x80004A20, length=0x003A44
  0x80004A20  _m2cma_init
  0x80004A50  m2cma_Alloc
  0x80004A90  m2cma_Free
```

### Using Maps

Projects store maps in:
```
maps/
  GZ2E01/
    main.map
    RELS.map
```

Then `dtk` or `configure.py` uses them for:
- Automatic symbol naming
- Splitting validation
- Demangling

**If you have a map file**:
1. Add to project's `maps/` directory
2. Rerun configure
3. objdiff will show real names instead of addresses

---

## 🔧 Symbol Files and Stubs

### `symbols.txt` Format

Common format for manually specifying symbols:

```txt
# VRAM address   Symbol name
0x80001234      d_aie_eai_init
0x80001260      d_aie_eai_init_attention
0x80003528      mDoAud_seStartLevel
```

**Sources**:
- Manually discovered
- Imported from map files
- Shared across projects

**Location**: Usually at project root or in `config/`.

**Usage**:
```bash
dtk dol split config.yml --sym symbols.txt
```

Or automatically picked up by `configure.py`.

---

### `splits.txt` (or `chunks.yaml`)

These define function boundaries **and** symbols:

```yaml
# Example from decomp-toolkit format
symbols:
  - address: 0x80001234
    name: d_aie_eai_init
    object: d_aie_eai
    section: .text
```

Or simpler:
```
80001234,d_aie_eai_init,d_aie_eai,0,0
```

**Projects differ**: Check project's README for exact format.

---

## 🕵️ Manual Symbol Discovery Techniques

### 1. String References

Search for ASCII strings in `.rodata`:

```bash
dtk disasm -s .rodata build/asm/main.s | grep -i "OSReport"
```

Or in Ghidra: `Search → For Encoded Strings`

Common SDK strings:
- `"OSReport"`
- `"Assertion Failed!"`
- `"DSP"` (audio)
- `"JUT"` (JSystem)
- `"JKernel"` (memory)
- `"mDo"` (metroid/mario common prefix)

When you see a string reference:
```asm
lis r3, h"OSReport"@ha
addi r3, r3, h"OSReport"@l
```
That's a clear indicator the function at that address calls `OSReport`. Name it accordingly.

---

### 2. Pattern Matching SDK Functions

**The Dolphin SDK has recognizable patterns**.

For example, `cMtx_multVec` (matrix multiply):
```asm
mftb r0
stw r0, 0x10(r1)
# ... matrix multiplication opcodes (fmuls, fadds, etc)
blr
```

You can create **signature database**:

```python
sdk_patterns = {
    "cMtx_multVec": b'\x7c\x08\x02\xa6\x4e\x60\x80\x20...',  # first 8 bytes
    "JUTTexture_store": b'\x94\x21\xff\xd0\x7c\x08\x02\xa6...',
}
```

Scan binary for these byte sequences.

**Tools**:
- `dtk` has built-in signature matching: `dtk dol signatures main.dol`
- Custom scripts with `yara` or `ssdeep`

---

### 3. Cross-reference with Other Games

Same SDK function appears in multiple games. If Zelda Wind Waker has it named `mDoAud_seStartLevel`, and you see similar code in Animal Crossing, rename similarly.

**Shared libraries**:
- `dolphin/source/export` - Common across all games
- `JSystem` - Used by many first-party titles
- `JAudio` - Audio library

Clone `doldecomp/sdk_*` repos and compare.

---

### 4. Demangling C++ Symbol Names

Metrowerks mangles C++ names as:
```
?funcName@@YAXXZ  # __cdecl funcName(void)
?ClassName::Method@@QAEXXZ  # public method
```

Use `dtk demangle`:
```bash
dtk demangle '?Create__12fopAc_ac_cFv'
# Output: fopAc_ac_c::Create(void)
```

**In objdiff**: Enable demangling in settings; it auto-demangles CodeWarrior symbols.

---

### 5. Call Graph Analysis

If function A calls B, and B calls C, and you know C's name, infer A and B.

Example:
```
A → B → printf_stub
```
If B is clearly `printf` wrapper, A might be `debug_menu_draw` or something that prints.

Use Ghidra's **Function Graph** or **References** view to trace.

---

## 🏷️ Naming Conventions

### What's Standard?

Nintendo (and decomp community) uses:

| Prefix | Meaning | Example |
|--------|---------|---------|
| `d_a` | Actor (d? for dol? d_aie) | `d_aie_eai` (enemy AI) |
| `d_b` | Background object | `d_bg` |
| `d_k` | Something? | `d_k_wall` |
| `fop` | Framework (fopAc, fopEn) | `fopAc_ac_c` |
| `mDo` | Metroid / Mario lib | `mDoAud`, `mDoMtx` |
| `J` | JSystem library | `JKRHeap`, `JUTTexture` |
| `cM` | Math/utility | `cMtx`, `cLib` |
| `OS` | Operating system | `OSReport`, `OSThread` |
| `DB` | Debug | `DBError` |

**Pattern**: `[library]_[module]_[function]`

Follow the project's existing naming. Copy the style.

---

### Class Naming (C++)

- UpperCamelCase: `fopAc_ac_c`, `d_aie_eai_c`
- Suffix `_c` for classes (common in these codebases)
- Base class first in inheritance: `class Child : public Base { }`

---

### Variable Naming

- `this` pointer always `this` (or `this` in C++;
- Member variables: `mVariable` (m prefix)
- Parameters: no prefix or `param`
- Locals: `local1`, `temp`, or meaningful names

**Match existing code**. If project uses `field_0x10`, keep that until you discover real meaning.

---

## 🎯 The Symbol Discovery Workflow

### For a New Function

1. **Check if already named**: Look in `objdiff.json`, `symbols.txt`, or map files
2. **If not**, open assembly in Ghidra or disassembly
3. **Look at cross-references**:
   - Who calls this function?
   - What strings does it reference?
   - What global variables does it access?
4. **Pattern match**: Does it look like an SDK function? Use signature DB
5. **Ask the community**: Someone might have seen it before
6. **Make educated guess**: Name it descriptively: `sub_80012345` → `actor_delete` if evidence points there
7. **Add to symbols.txt** and commit (if you're confident)
8. **Better**: Wait until you have decompiled it enough to be sure

---

## 🧩 Real Example: Finding a Function Name

**Scenario**: You have an address `0x80034560` in `d_aie_eai.c`. What to name it?

1. **Look at call sites**: Is it called from `init`? Maybe `create` or `setProperties`.
2. **Disassemble**:
   ```asm
   80034560:  stwu r1, -0x20(r1)
              mflr r0
              stw r0, 0x24(r1)
              # ... loads constant 0x5a0
              bl 0x80001234  (some other function)
              blr
   ```
3. **Search constant**: What's `0x5a0`? Could be `ACTOR_ID_EAI` or object type.
4. **Check `.rodata`**: Nearby string `"EAI"`?
5. **Cross-reference**: Look up `0x80001234` - if that's `fopAc_ac_c::create`, then this is likely the actor's `create` method.
6. **Name**: `create__9d_aie_eai_cFv` (mangled) or `d_aie_eai_c::create(void)`.

**Ghidra can help**: Set function name, see how decompilation looks. Does `this` pointer have right fields? That confirms.

---

## 📊 Common Global Variable Patterns

SDK globals often have prefix:

| Pattern | Type | Example |
|---------|------|---------|
| `mDoMain_` | Main engine struct | `mDoMain_g` |
| `mGameInfo_` | Game state | `mGameInfo_mp_c` |
| `cameraMgr` | Camera manager | `cameraMgr_c` |
| `g_` | Global (general) | `g_GlobalTimer` |
| `lbl_` | Local to file (static) | `lbl_80012345` |

In decompiled C, globals are usually:
```c
namespace nw4r { math:: ... }
extern "C" {
    JKernel.dll... // Not actual; more like: JKRHeap* heap;
}
```

---

## 🎓 Advanced: Type Recovery

Once you know a symbol is:
- Global struct → analyze fields from how it's accessed
- Function pointer → determine signature from call sites

**Example**: `mDoAud_seStartLevel`:
- Called as: `mDoAud_seStartLevel(0x1234, 0x56, &pos, &velocity);`
- With pattern of audio functions, infer parameters: `(uint sound_id, uint volume, Vec* pos, Vec* vel)`

Add comment or define proper function prototype in header. Changes matching because function call instruction differs based on parameter count/types (PowerPC ABI).

---

## 🤝 Shared Symbol Databases

Community maintains:

- **doldecomp/sdk_* repos**: Header files with function prototypes for Dolphin SDK
- **zeldaret/common**: Shared types and symbols across Zelda games
- **decomp.dev**: Auto-extracted symbols from all projects (JSON API)
- **decomp.me**: When you solve a "scratch", the symbol name is recorded

Use these as authoritative references. Don't rename things that are already well-known.

---

## 🐛 Pitfalls

### Renaming After Matching

Changing a symbol name in one file can affect others if it's declared extern. Keep consistency across translation units. Use headers properly.

**Bad**: Rename `sub_80012345` to `foo` in `d_aie.c` but other files still call `foo`? They need prototype in header.

---

### Duplicate Names

Two different functions might have similar logic but are separate. Don't merge them:
- `actor_move` vs `enemy_move` might both be subroutines with similar prologue. Check call sites.

---

### Over-Naming

Don't name every `sub_800XXXXXX`. Some static functions are only used once and their purpose isn't obvious. It's okay to keep them as `static void func_80012345(void)` until more context emerges. Better than a misleading name.

---

## ✅ Symbol Resolution Checklist

For each function/global variable you encounter:

1. [ ] Is it already named in symbols.txt/map file?
2. [ ] Can I demangle it? (C++ only)
3. [ ] Does it reference known SDK strings (OSReport, JUT, etc.)?
4. [ ] Can I match it to a signature pattern?
5. [ ] Who calls it? What's the context?
6. [ ] Can I inspect RTTI (for class methods)?
7. [ ] Ask community if unsure
8. [ ] When confident, add to symbols.txt or commit name change
9. [ ] Update headers with external declarations if needed

---

## 📚 Resources

- `doldecomp/sdk-dolphin` - Dolphin SDK headers
- `doldecomp/sdk-JSystem` - JSystem library
- `zeldaret/common` - Common Zelda definitions
- Metrowerks C++ name mangling reference (PDF archive.org)

---

## 🎯 Priority Order

When approaching a new object file:

1. **Match the build first** (empty stubs okay)
2. **Add RTTI-derived class definitions** (if C++)
3. **Import known symbols** (from SDK repos)
4. **Name obvious functions** (main, create, execute, draw)
5. **Fill in based on decompilation** (as you understand what each function does)
6. **Commit symbol names** when certain (>80% confidence)

---

*Next guide: [Porting Strategies](../PORTING/strategies.md) - From decompilation to native PC*

*Symbols are the Rosetta Stone that turns addresses into readable code. Treasure them, share them, use them wisely!* 🔮