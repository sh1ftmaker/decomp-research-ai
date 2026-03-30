# The Legend of Zelda: The Wind Waker Decompilation

*The crowning jewel of Zelda decompilation - a masterpiece in progress.*

---

## 📊 Project Overview

| Attribute | Value |
|-----------|-------|
| **Full Title** | The Legend of Zelda: The Wind Waker |
| **Game ID** | `GZLJ01` (Japan), `GZLE01` (USA), `GZLP01` (Europe) |
| **Platform** | GameCube |
| **Primary Repository** | https://github.com/zeldaret/tww |
| **Discord Server** | https://discord.gg/zeldaret |
| **Active Since** | 2021 (public) |
| **Current Completion** | ~15% (March 2025) |
| **Primary Language** | C++ (very heavy) |
| **SDK Used** | Dolphin SDK + JSystem (identical to Sunshine) |
| **Architecture** | PowerPC 750CL, 32-bit |

---

## 🎯 Quick Status

- **Decompilation progress**: ~60% (7,800+ of 12,900+ functions)
- **Build status**: ✅ Builds successfully (substantial matching)
- **Matching**: ~5,200 functions matching (40.41% fully linked)
- **Last major milestone**: Actor framework and many `fopAc` functions complete
- **Recommended for newcomers**: ⚠️ Advanced (large, C++ heavy, but excellent docs)

**Why TWW?**: The Zelda team maintains **exceptional documentation**. Their wiki is the gold standard for GameCube decomp guides. Learn from the best.

---

## 🏗️ Architecture Highlights

### Engine Systems

| System | Implementation | Notes |
|--------|----------------|-------|
| **Physics** | `dol_path` + `fopAc` collision | Complex actor-physics interaction |
| **Audio** | JAudio2 + mDoAud | Extensive sound system |
| **Graphics** | GX + J3D graphics | Vertex color animation, tev stages |
| **File I/O** | DVD + RARC + YAZ0 | `.arc` files, `./Pack/` directory structure |
| **Memory** | JKRHeap variants | Scene graph memory management |
| **Threading** | OSThread | Separate load thread (dvd thread) |
| **Math** | JGeometry library | Template-heavy (float/double) |

### Notable Frameworks

**`fopAc`** (Actor Framework):
- Base classes: `fopAc_ac_c` (actor), `fopAc_prm_base` (parameters)
- Actor creation: `fopAc_create`, `fopAc_createInEmptyLayer`
- Actor management: `fopAc_ac_c::create`, `fopAc_ac_c::destroy`
- Each in-game object (enemy, item, NPC) inherits from `fopAc_ac_c`

**`dMessage`** (Event system):
- Scripted events (conversations, cutscenes)
- Flow control with `dMsg` objects
- Uses `.mbl` files (message binary)

**`mDo`** (Main game logic):
- `mDoMtx` - Matrix operations
- `mDoAud` - Audio management
- `mDoMain` - Main loop, scene transitions

---

## 📁 Repository Structure

```
tww/
├── src/
│   ├── dolphin/          # SDK
│   ├── JSystem/         # JSystem (shared with Sunshine)
│   ├── nw4r/            # Not used much
│   ├── pe/              # Game code
│   │   ├── d/
│   │   │   ├── d_a/     # Actors (enemies, items, NPCs)
│   │   │   ├── d_bg/    # Background objects
│   │   │   ├── d_com/   # Common/utility
│   │   │   ├── d_ky/    # Menu?
│   │   │   ├── d_msg/   # Message/event system
│   │   │   ├── d_mtx2/  # Matrix math?
│   │   │   └── ...
│   │   └── ms/          # Main stage (ms_...) - scene management
│   └── ...
├── include/
│   ├── dolphin/
│   ├── JSystem/
│   └── zelda/           # Zelda-specific headers
├── tools/
│   ├── decomp.py
│   ├── rtti_extract.py  # Auto-generates RTTI headers
│   ├── gen_structs.py   # Struct recovery from Ghidra
│   └── ...
├── config/
│   ├── splits.txt
│   └── symbols.txt
├── data/                # Extracted game files (not committed)
│   ├── message/
│   ├── stage/
│   └── Pack/
├── orig/
│   └── GZLE01/
├── build/
├── configure.py
├── objdiff.json
├── PROGRESS.md
├── CLASSES.md           # Auto-generated class hierarchy
├── ACTORS.md            # Actor list with status
├── README.md
└── docs/
    ├── decompiling.md   ★★★ THE BEST GUIDE ★★★
    ├── architecture.md  # Engine overview
    ├── regalloc.md      # Register allocation tips
    ├── inlines.md       # Inline function handling
    ├── switches.md      # Switch statement patterns
    └── rtti.md          # Using RTTI
```

---

## 🔧 Toolchain Requirements

| Tool | Version | TWW Notes |
|------|---------|-----------|
| **decomp-toolkit** | Latest | Standard |
| **objdiff** | Latest | Supports TWW's config |
| **m2c** | Latest | `ppc-mwcc-c` target |
| **Python** | 3.11+ | For tools and configure |
| **Ghidra** | 10.x+ | Strongly recommended |
| **Dolphin** | Latest | Asset extraction |

**Special**: TWW uses `rtti_extract.py` to auto-generate class headers from debug ELF. Get the debug version if possible (has RTTI).

---

## 🚀 Getting Started (TWW-Specific)

1. **Clone**:
   ```bash
   git clone https://github.com/zeldaret/tww.git
   cd tww
   git submodule update --init --recursive
   ```

2. **ISO**: Place `The Legend of Zelda: The Wind Waker (USA).iso` in `orig/GZLE01/`. Use version **1.0** or **1.1** (1.2 is fine). The game is ~3.5GB.

3. **Configure**:
   ```bash
   python configure.py --extract-data  # Also extracts Pack/ if needed
   ```
   This may take 10-20 minutes. It analyzes the DOL, extracts RTTI if debug ELF found, generates class headers.

4. **Build**:
   ```bash
   ninja -j$(nproc)
   ```

5. **Open objdiff**: Set project dir to `tww/`. Sort by "Status" to see matching %.

6. **Explore docs**:
   ```bash
   cat docs/decompiling.md  # Start here!
   cat docs/architecture.md
   ```

---

## 🎯 Known Challenges (TWW-Specific)

### 1. Massive C++ Codebase

TWW is **heavily C++**:
- Templates everywhere (JGeometry, JUT)
- Multiple inheritance (fopAc hierarchy)
- Virtual functions (heavy vtable use)

**Impact**: m2c output needs significant manual cleanup. Expect to spend time fixing class definitions before functions match.

**Solution**:
- Use RTTI to generate accurate class hierarchies
- Study existing decompiled classes (`include/zelda/`) for patterns
- Copy variable naming conventions (`mName`, `field_0xX`)

---

### 2. Actor Parameter System

Actors have parameter structures (`fopAc_prm_base` and subclasses). These are stored in archives and loaded at creation.

**Challenge**: The parameter structs are not directly visible in function code; they're accessed via base class pointers with casts.

**Solution**: Reconstruct parameter class hierarchies by analyzing how actor's `create` function accesses parameters.

Example:
```c
// In d_a_objXXX.c
void create(fopAc_ac_c* actor, fopAc_prm_base* params) {
    s16 type = params->get<int>(0);  // offset 0
    // ...
}
```

Use Ghidra to trace `params` pointer offsets.

---

### 3. Message System (`d_msg`)

Event scripts are in binary `.mbl` files. The C code interprets them.

**Status**: Message system partially decompiled. Script format reverse-engineered but not fully documented.

---

## 🎮 Common Contribution Areas

### Good First Tasks (Beginner)

- `d_com` utility functions: `dComIfG_resLoad`, `dComIfG_setAlwaysNumber__FUlUl`
- `d_a` simple actors: `d_a_tag`, `d_a_obj_arrow` (arrow), `d_a_obj_bomb`
- `fopAc` framework functions: `fopAc_ac_c::create`, `fopAc_ac_c::setMyNumber`
- SDK wrappers: `OSReport_alt`, `JKRHeap::getCurrentHeap`

---

### Intermediate Tasks

- Complete an entire actor: all methods for one `d_a_*` class (300-800 LOC)
- `d_kfg` (key configuration) system
- `d_massage` (massage? Actually stage) - Stage loading
- `d_msg` message flow functions

---

### Advanced Tasks

- `fopAc` actor lifecycle management
- `d_dmsub` (display subsystem) - Rendering
- `d_draw` - Draw manager
- `d_kw` water (if present - actually Sunshine)
- Template-heavy JSystem classes (`JGeometry`, `JUTTextureArray`)

---

## 📈 Progress Milestones

| Milestone | Completed? | Date |
|-----------|------------|------|
| RTTI extraction automated | ✅ | 2022 |
| Core SDK (dolphin, JSystem) | ~60% | Ongoing |
| `fopAc` actor framework | ~50% | Ongoing |
| First complete actor (`d_a_tag`) | ✅ | 2022 |
| 10 complete actors | ✅ | 2023 |
| 50 complete actors | ~30% | 2025 |
| All actors complete | 0% | Far future |

---

## 🔗 Related Projects

- **Super Mario Sunshine** - Shares JSystem codebase (~40% identical)
- **zeldaret common** - Shared headers used across Zelda projects
- **decomp-toolkit** - Used for splitting
- **Ghidra server** at ghidra.decomp.dev (read-only) with TWW types pre-loaded

---

## 📚 Resources

### Documentation (Excellent)

- **[docs/decompiling.md](docs/decompiling.md)** - **THE guide** - Read this first!
- **[docs/architecture.md](docs/architecture.md)** - Engine systems overview
- **[docs/regalloc.md](docs/regalloc.md)** - Register allocation specific to TWW patterns
- **[docs/inlines.md](docs/inlines.md)** - Inline handling with TWW examples
- **[docs/rtti.md](docs/rtti.md)** - RTTI extraction walkthrough

These are **community best practices** that apply to all projects.

---

### External

- **[Class list](CLASSES.md)** - Auto-generated from RTTI
- **[Actor list](ACTORS.md)** - Actor decompilation status
- **[Wiki](https://github.com/zeldaret/tww/wiki)** - Additional notes

---

## 🆘 Getting Help

**Discord**: `#tww` channel in zeldaret server

**Before asking**:
- Read `docs/decompiling.md` cover to cover
- Search Discord history (use Ctrl+F in Discord)
- Check existing issues on GitHub

**When asking**:
- Include function name, objdiff screenshot
- What you've tried (variable renames, splitting, etc.)
- Link to relevant docs section

---

## 🎯 Tips from TWW Maintainers

1. **Start with `d_com`**: Utility functions are small and teach the conventions.
2. **Use RTTI-generated headers**: They give you class layouts; don't reinvent.
3. **Follow naming patterns**: `mName`, `mAttr`, `mScale`, etc.
4. **Don't match inlines at first**: Many are `Equivalent`; focus on core logic.
5. **Ask in Discord**: The community is friendly and knowledgeable.

---

## 📈 Comparison with Other Zelda Games

| Game | Rel | Completion | Notes |
|------|-----|------------|-------|
| Ocarina of Time (N64) | - | Not started (different arch) | |
| Majora's Mask (N64) | - | Not started | |
| Twilight Princess | GCN/Wii | ~40% | Shares engine with TWW, but different game logic |
| Skyward Sword (Wii) | - | Early research | Uses different SDK? |

TWW and TP share much of the same engine. Decoding TWW helps TP progress.

---

## 📝 Special Notes

- **Debug symbols**: TWW debug versions exist with full RTTI. Use them!
- **Stage data**: Stages are in `./Pack/` as `.arc` archives. Extract with `tools/arc.py`.
- **Strings**: Many Japanese strings appear; use UTF-8.
- **Class templates**: JGeometry classes are templates; you may need to manually instantiate for `float` and `float[3]` types.

---

*Last updated: March 2025*

*Check PROGRESS.md for latest numbers.*