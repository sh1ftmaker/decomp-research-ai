# Super Mario Sunshine Decompilation

*Cleaning up the Isle Delfino, one function at a time.*

---

## 📊 Project Overview

| Attribute | Value |
|-----------|-------|
| **Full Title** | Super Mario Sunshine |
| **Game ID** | `GMSE01` (USA), `GMSJ01` (Japan), `GMSP01` (Europe) |
| **Platform** | GameCube |
| **Primary Repository** | https://github.com/doldecomp/sunshine |
| **Discord Server** | https://discord.gg/doldecomp (dedicated #sunshine channel) |
| **Active Since** | 2022 (public) |
| **Current Completion** | ~30% (March 2025) |
| **Primary Language** | C++ (heavy) with some C |
| **SDK Used** | Dolphin SDK + JSystem (extensive) |
| **Architecture** | PowerPC 750CL, 32-bit |

---

## 🎯 Quick Status

- **Decompilation progress**: ~30% (3,500+ of 11,000+ functions)
- **Build status**: ✅ Builds successfully (partial matching)
- **Matching**: ~1,200 functions matching
- **Last major milestone**: FLUD (water) system partially complete; most of the core engine utilities done
- **Recommended for newcomers**: ⚠️ Moderate to Advanced (C++ heavy, but clearer than Melee)

**Why Sunshine?**: The codebase is **well-organized** with clear module boundaries. Many small utility functions make it beginner-friendly once you learn the JSystem patterns.

---

## 🏗️ Architecture Highlights

### Engine Systems

| System | Implementation | Notes |
|--------|----------------|-------|
| **Physics** | Custom `dWater` system (FLUD) | Water simulation is unique to this game |
| **Audio** | JAudio2 (SDK component) | `.aw`, `.bseq`, `.bnk` |
| **Graphics** | GX + JSystem J3D | Extensive use of J3D graphics objects |
| **File I/O** | DVD + RARC archives | `.arc` files, some `.szs` compression |
| **Memory** | JKRHeap / JKRExpHeap / JKRHeapToRAM | Multiple heap strategies |
| **Threading** | OSThread | Separate audio thread |
| **Math** | JSystem math library (JGeometry) | Heavy template usage |

### Notable Libraries

**JSystem** is heavily used:
- `JKR` - Memory management
- `JUT` - Utilities (textures, fonts, audio)
- `J3D` - 3D graphics (models, animations)
- `JGI` - Graphics interface
- `JAudio` - Audio system

These are **shared** with Zelda: The Wind Waker. Sunshine and TWW use nearly identical engine versions.

---

## 📁 Repository Structure

```
sunshine/
├── src/
│   ├── dolphin/          # Dolphin SDK wrappers
│   ├── JSystem/         # Full JSystem library (forked)
│   ├── pe/              # Game-specific code
│   │   ├── d/
│   │   │   ├── d_a/     # Actors (Game-specific: Mario, NPCs, objects)
│   │   │   ├── d_bg/    # Background objects
│   │   │   ├── d_do/    # ? (maybe "door"?)
│   │   │   ├── d_kw/    # Water (kawaf) - FLUD system
│   │   │   ├── d_y/     # ? (item?)
│   │   │   └── ...
│   │   └── nw4r/        # Not used much
│   └── ...
├── include/
│   ├── dolphin/
│   ├── JSystem/         # JSystem headers
│   └── pe/
├── tools/
│   ├── decomp.py
│   ├── analyze_actor.py
│   └── ...
├── config/
│   ├── splits.txt
│   └── symbols.txt
├── orig/
│   └── GMSE01/
├── build/
├── configure.py
├── objdiff.json
├── PROGRESS.md
└── README.md
```

---

## 🔧 Toolchain Requirements

Same as Melee, but Sunshine benefits from **more memory** due to JSystem header bloat.

- **Minimum**: 8GB RAM, 20GB storage
- **Recommended**: 16GB RAM, 40GB storage (for parallel builds)

**Compiler**: Same `wibo` or `Wine` setup.

---

## 🚀 Getting Started (Sunshine-Specific)

1. **Clone**: Checkout the repo with submodules (JSystem is a submodule).

2. **ISO**: Need `GMSE01` (USA 1.02 recommended). The game is ~1.3GB compressed.

3. **Configure**:
   ```bash
   python configure.py
   ```
   This will also configure the JSystem submodule. Takes a few minutes.

4. **Build**:
   ```bash
   ninja -j$(nproc)  # Parallel build speeds things up
   ```

5. **First matching**: Look in `d_a` for simple actors like `d_a_ball`, `d_a_basen` (base actor class).

---

## 🎯 Known Challenges

### 1. Heavy C++ with Templates

JSystem makes extensive use of C++ templates. The decompiler (m2c) struggles with:
- `JGeometry<T>` (vector/matrix templates)
- `JUTPtrArray<T>` (pointer arrays)
- `JKRAllocator` template specializations

**Workaround**:
- Manual template instantiation in headers
- Use `extern template` to reduce bloat
- Some templates are manually written, not decompiled

---

### 2. RTTI Availability

Sunshine debug builds exist with RTTI. Use them to extract class hierarchies.

**Status**: RTTI extraction scripts exist; class headers partially auto-generated.

---

### 3. Inline Functions Galore

JSystem headers are full of `inline` functions. Matching them across dozens of translation units is tedious.

**Strategy**:
- Focus on non-inline implementations first
- Some inlines marked as `Equivalent` if too numerous
- Use `decomp-permuter` for tricky ones

---

### 4. Water Physics (FLUD)

The `d_kw` module (water) is complex:
- Real-time fluid simulation
- Interaction with Mario and objects
- Performance-critical

**Not yet decompiled**: High priority but difficult.

---

## 🎮 Common Contribution Areas

### Beginner Friendly

- `d_a` simple actors: `d_a_ball` (ball), `d_a_bomb` (bomb), `d_a_key` (key)
- `d_bg` background objects: `d_bg_wall`, `d_bg_ground`
- Utility functions in `d_do` (if present)

### Intermediate

- JSystem `JUT` classes: `JUTTexture`, `JUTPalette`, `JUTFont`
- Dolphin SDK wrappers: `dol_internal_math` (if exists)
- Actor base classes: `d_a_base`, `d_a_object`

### Advanced

- FLUD water system (`d_kw`)
- Camera system (`d_camera`)
- Rendering pipeline (`d_draw`)

---

## 📈 Progress Milestones

| Milestone | Completed? | Estimated |
|-----------|------------|-----------|
| JSystem library fully matched | 60% | 2025-2026 |
| All `d_a` actors matching | 40% | 2026-2027 |
| FLUD system complete | 10% | 2027+ |
| Entire game matching | 30% | 2028+ |

---

## 🔗 Related Projects

- **Zelda: The Wind Waker** - Shares engine version (almost identical JSystem)
- **decomp-toolkit** - Used for splitting (same as Melee)
- **doldecomp common** - Shared utilities

---

## 📚 Resources

### Project Docs

- [README](https://github.com/doldecomp/sunshine) - Setup
- [PROGRESS.md](https://github.com/doldecomp/sunshine/blob/main/PROGRESS.md) - Status table
- [Wiki](https://github.com/doldecomp/sunshine/wiki) - Actor list, notes

### Community

- **Discord**: `#sunshine` in doldecomp server
- **decomp.me**: Many Sunshine functions available for practice

---

## 🆘 Getting Help

Sunshine-specific questions go in `#sunshine` channel.

Common questions:
- "What does `d_kw` do?" → Water system (kawaf)
- "How to set up JSystem?" → Already a submodule; configure.py handles it
- "Why are there so many template errors?" → Add missing template specializations to headers

---

## 📝 Special Notes

- **Actor naming**: Sunshine actors use `d_a_*` prefix, but note that some are hard to understand without playing the game.
- **File formats**: `.arc` archives need unpacking; use `dolts.py` or Dolphin's `Art Manager`.
- **Strings**: Many actor names appear in the binary; use `strings` to find them.

---

*Last updated: March 2025*

*For latest updates, check PROGRESS.md.*