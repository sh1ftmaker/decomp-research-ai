# Super Smash Bros. Melee Decompilation

*The flagship GameCube title: 20 years later, finally seeing the source.*

---

## 📊 Project Overview

| Attribute | Value |
|-----------|-------|
| **Full Title** | Super Smash Bros. Melee |
| **Game ID** | `GALE01` (USA), `GALJ01` (Japan), `GALP01` (Europe) |
| **Platform** | GameCube |
| **Primary Repository** | https://github.com/doldecomp/melee |
| **Discord Server** | https://discord.gg/meleedecomp |
| **Active Since** | 2021 (public) |
| **Current Completion** | ~22% (March 2025) |
| **Primary Language** | C (mostly) with some C++ |
| **SDK Used** | Dolphin SDK (custom HAL), proprietary physics |
| **Architecture** | PowerPC 750CL (Broadway), 32-bit |

---

## 🎯 Quick Status

- **Decompilation progress**: ~61% (7,100+ of 11,600+ functions)
- **Build status**: ✅ Builds successfully (partial matching)
- **Matching**: ~3,900 functions matching (33.74% fully linked)
- **Last major milestone**: Menu system mostly complete, link code partially done
- **Recommended for newcomers**: ⚠️ Advanced (large codebase, complex physics, networking). However, the high completion percentage means most patterns are already discovered, making it easier to learn by example.

**Note**: Melee is one of the **largest** GameCube games by code size. Not ideal for first contribution due to complexity, but highly visible.

---

## 🏗️ Architecture Highlights

### Engine Systems

| System | Implementation | Notes |
|--------|----------------|-------|
| **Physics** | Custom engine (`ft` module) | 60fps momentum-based, complex collision |
| **Audio** | AX Universal (custom wrapper) | `.aw` ADPCM, `.bseq` sequences |
| **Graphics** | GX (Display Lists) | Heavy use of TEV for effects |
| **File I/O** | DVDFile + ARC archives | `.arc` files, YAZ0 compressed |
| **Memory** | JKRHeap / JKRExpHeap | Multiple heaps for different purposes |
| **Threading** | OSThread | Main thread + audio thread |
| **Input** | PAD (4 controllers) | Polling-based, low-level |

### Notable Modules

- **`ft`** (Fighter): All character logic, moves, animations (~2,500 functions)
- **`dp`** (Display): Camera, rendering pipeline, effects
- **`sp`** (Sound Player): Music and sound effects
- **`kn`** (Keyboard? Actually "Article"?): Menu system items
- **`db`** (Debug): Development leftovers (asserts, debug menus)
- **`lobby2`** (Netplay): Sockets, ping, matchmaking

### Character System

Each fighter is composed of:
- `ftData` (fighter data)
- `ftMotion` (animation/script)
- `ftCollision` (hitboxes, Hurtboxes)
- `ftStatus` (state machine: idle, attack, grab, etc.)
- Script files (`.dat`) for moves (external!)

**Complex**: Each character has 100+ states, many share code via inheritance.

---

## 📁 Repository Structure

```
melee/
├── src/
│   ├── dolphin/          # SDK wrappers (OS, PAD, DVDFS, etc.)
│   ├── JSystem/         # JSystem library (JKR, JUT, J3D)
│   ├── pe/              # Main code (ft, dp, sp, etc.)
│   │   ├── d/
│   │   │   ├── db/     # Debug
│   │   │   ├── dp/     # Display
│   │   │   ├── ft/     # Fighters (largest)
│   │   │   ├── kn/     # Menu items
│   │   │   ├── lb/     # ? Life? (maybe lives)
│   │   │   ├── lr/     # ? Recording?
│   │   │   ├── mp/     # Map?
│   │   │   ├── mps/    # ?
│   │   │   ├── pl/     # Player?
│   │   │   ├── sp/     # Sound
│   │   │   └── ...
│   │   └── nw4r/       # Not used much (Nitro Express?)
│   └── ...
├── include/
│   ├── dolphin/
│   ├── JSystem/
│   └── pe/
├── tools/
│   ├── decomp.py        # Decompile specific function
│   ├── analyze.py       # Analyze function complexity
│   └── ...
├── config/
│   ├── splits.txt       # Function boundaries
│   └── symbols.txt      # Known symbols
├── orig/
│   └── GALE01/          # Your ISO goes here
├── build/               # Generated (gitignored)
├── configure.py
├── objdiff.json
├── PROGRESS.md
└── README.md
```

---

## 🔧 Toolchain Requirements

Same as standard GameCube decomp. However:

- **Memory**: Melee is large. Requires **8GB RAM+** for full build
- **Storage**: Full source + build: ~30GB
- **Time**: Full rebuild: 2-10 minutes depending on CPU

**Note**: `configure.py` will warn if insufficient memory.

---

## 🚀 Getting Started (Melee-Specific)

1. **Clone**:
   ```bash
   git clone https://github.com/doldecomp/melee.git
   cd melee
   git submodule update --init --recursive  # Important!
   ```

2. **Place ISO**: Copy `Super Smash Bros. Melee (USA).iso` to `orig/GALE01/`. Must be **1.02** or **1.03** (1.00 may work but less tested).

3. **Configure**:
   ```bash
   python configure.py
   ```
   This may take 1-2 minutes as dtk analyzes the DOL (which is large).

4. **Build**:
   ```bash
   ninja
   ```
   First build: compile ~5,000 object files. Takes time.

5. **Open objdiff**:
   ```bash
   objdiff
   ```
   Set project dir to `melee/`. Left panel lists all units.

6. **Find something small**:
   - Avoid `ft/` (fighters) initially - they're huge
   - Try `db/` (debug) functions: often utilities, small
   - Try `kn/` (menu items): `knItemModelChanger` etc.
   - Sort by diff size in objdiff to find near-matches (maybe 5-10% diff already)

---

## 🎯 Known Challenges

### 1. Massive Codebase

**Problem**: 11,700+ functions. Overwhelming for newcomers.

**Strategy**:
- Start with peripheral modules (`db/`, `sp/` sound)
- Work towards core modules (`ft/`, `dp/`) later
- Focus on one character at a time if doing fighters

---

### 2. Complex Fighter State Machines

Each character has ~100 states. Each state is a function (often large). Inlining is heavy.

**Example**: Fox's `ft_status_Fighter__wait` has many subroutines.

**Difficulty**: High.

**Advice**: Don't start with character logic. Start with shared utilities.

---

### 3. Script-Based Moves

Some move behavior is defined in external `.dat` files (binary scripts). The C code interprets these.

**Challenge**: Matching requires also understanding the script format.

**Current status**: Scripts partially reverse-engineered, but not fully documented.

---

### 4. Netplay Code (`lobby2`)

Uses custom protocol over sockets. Complex state synchronization.

**Status**: Not prioritized yet (low % complete).

---

### 5. Version Differences

Melee has multiple revisions (1.00, 1.01, 1.02, 1.03, 20XX). Code differs slightly between them.

**Recommendation**: Decompile **1.02** as primary (most standard). 20XX is a hack; may diverge.

---

## 🎮 Common Contribution Areas

### Good First Tasks

1. **`sp/` (Sound player)**: Many small utility functions (<50 instructions). Audio system is self-contained.
2. **`db/` (Debug)**: Assertion functions, debug menus, development leftovers. Often simple.
3. **`dp/` (Display) - non-rendering parts**: Camera math, projection calculations.
4. **SDK wrappers**: Missing `OSReport`, `PADRead` variants (if not already stubbed).
5. **Data-only objects**: Constant tables, move attribute tables.

### Intermediate Tasks

- Complete a small `kn/` menu item (e.g., `knItemModelChanger` - 200-400 LOC)
- Complete a `ft/` substatus (e.g., `ftStatus_Fighter_SpecialHi` for one character)
- JSystem `JKR` heap functions (`JKRHeap` methods)

### Advanced Tasks

- `ft/` core fighter logic (`ftCommon`, `ftMasterHand` if present)
- `dp/` rendering (`dpModel`, `dpEffect`): GX wrapper code
- Physics collision detection
- Move script interpreter

---

## 📈 Progress Milestones

| Milestone | Completed? | Date |
|-----------|------------|------|
| All SDK wrappers matching | ✅ | 2022 |
| `db/` module complete | ~90% | - |
| `sp/` module complete | ~70% | - |
| `kn/` module complete | ~40% | - |
| `dp/` module complete | ~20% | - |
| `ft/` module complete | ~15% | - |
| Network code complete | ~5% | - |

---

## 🔗 Related Projects

- **20XX Hack Pack**: Mod that adds features; sometimes easier to decompile (more symbols)
- **Slippi**: Netplay implementation; may have insights on `lobby2`
- **Melee HD**: Unofficial texture pack; unrelated
- **Fiz's Melee Research**: Spreadsheet of frame data (useful for verifying behavior but not decompilation)

---

## 📚 Resources

### Official Project

- [GitHub README](https://github.com/doldecomp/melee) - Setup, contribution guide
- [PROGRESS.md](https://github.com/doldecomp/melee/blob/main/PROGRESS.md) - Live progress
- [Wiki](https://github.com/doldecomp/melee/wiki) - Technical notes (sparse)

### Community Knowledge

- **Decomp.me scratches**: Many Melee functions on the platform
- **Smashboards**: The competitive Melee forum has some technical deep-dives (search "Melee code")
- **SSBMRocks**: Advanced Melee stat tracking (different)
- **YouTube**:
  - "Melee Decompilation Progress" videos by community members
  - "How to contribute to Melee decomp"

### Tools Specific to Melee

- `tools/ssb98.py`: Handles Melee-specific `.dat` script files (maybe)
- `tools/analyze_ft.py`: Fighter analysis script

---

## 🆘 Getting Help

**Discord**: `#melee` channel in GC/Wii Decompilation server

**Common questions**:
- "Where to start?" → `#newcomers` or read this file
- "Function won't match, register issues?" → `#decompilation`
- "What does this assembly do?" → Share objdiff screenshot in `#melee`
- "Version mismatch?" → Check ISO version in `#tech-support`

**Be specific**: "stuck on `ftStatus_Fighter_LightTurn` for 3 hours, tried renaming variables to a,b,c but registers still different, here's objdiff screenshot" → Gets helpful response.

---

## 📜 License & Legal

- Decompilation is done under **clean room** principles
- **Original code**: Copyright Nintendo / HAL Laboratory
- **Decompiled output**: MIT licensed (per repository)
- **Assets**: Do NOT commit any game assets (textures, sounds) to the repo

---

## 🎉 Contributors

See `CREDITS.md` in repository for full list.

**Top contributors** (as of 2025):
- [usernames from GitHub]

---

## 📝 Notes

- **Why Melee?**: It's the most iconic GameCube game, with a competitive scene interested in frame-perfect analysis. Decomp enables mods, documentation, and preservation.
- **Difficulty**: High due to size and complexity. Many functions are 500+ instructions.
- **Estimated completion**: 5+ years at current rate (5 contributors)
- **Port potential**: Yes, but physics are complex. Would need recreation of input (Slippi's netcode could inform)

---

*For the most up-to-date status, see [PROGRESS.md](../PROGRESS.md) and the project's GitHub.*