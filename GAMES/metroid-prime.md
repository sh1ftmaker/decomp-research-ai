# Metroid Prime Decompilation

*Exploring the Chozo ruins, one function at a time.*

---

## 📊 Project Overview

| Attribute | Value |
|-----------|-------|
| **Full Title** | Metroid Prime |
| **Game ID** | `GM8E01` (USA), `GM8J01` (Japan) |
| **Platform** | GameCube |
| **Primary Repository** | https://github.com/PrimeDecomp/prime |
| **Discord Server** | https://discord.gg/PrimeDecomp |
| **Active Since** | 2022 (public) |
| **Current Completion** | ~12% (March 2025) |
| **Primary Language** | C (mostly) with some C++ |
| **SDK Used** | Proprietary "Metal" engine (custom) + Dolphin SDK |
| **Architecture** | PowerPC 750CL, 32-bit |

---

## 🎯 Quick Status

- **Decompilation progress**: ~36% (4,100+ of 11,400+ functions)
- **Build status**: ✅ Builds successfully (partial matching)
- **Matching**: ~2,100 functions matching (18.67% fully linked)
- **Last major milestone**: Player movement and camera system partially complete
- **Recommended for newcomers**: ⚠️ Moderate (clear code style, but fewer shared resources)

---

## 🏗️ Architecture Highlights

### Engine Systems

| System | Implementation | Notes |
|--------|----------------|-------|
| **Physics** | Custom "Metal" engine | Capsule-based collision, player movement |
| **Audio** | AX Universal (like Melee) | `.aw` ADPCM |
| **Graphics** | GX + custom renderer | Heavy use of display lists |
| **File I/O** | DVDFile + `.pak` archives | Nintendo "PAK" format |
| **Memory** | Custom heap system (CMemory) | Multiple memory pools |
| **Threading** | OSThread | Main + audio threads |
| **Input** | PAD | Polling |

### Notable Modules

- **`player`** (pl*) - Samus movement, weapons, health
- **`cinematic`** (cs*) - Cutscenes, camera control
- **`world`** (wp*) - World geometry, collision
- **`boss`** (bs*) - Boss fight logic
- **`weapon`** (wp*) - Beam weapons, missiles
- **`interface`** (if*) - HUD, menus
- **`meta`** (mt*) - Metroid database, scans

### Engine Style

Metroid Prime uses a **custom engine** ("Metal") developed by Retro Studios. It's different from Nintendo's JSystem. Code is more "game-specific" and less generic than Zelda.

---

## 📁 Repository Structure

```
prime/
├── src/
│   ├── dolphin/          # SDK wrappers (partially)
│   ├── metal/            # Custom engine (CMemory, etc.)
│   ├── pe/               # Game code
│   │   ├── d/
│   │   │   ├── player/   # plPlayer, pl moves
│   │   │   ├── weapon/   # wpBeam, wpMissile
│   │   │   ├── world/    # wpWorld, collision
│   │   │   ├── boss/     # bs*
│   │   │   ├── cinematic/# cs*
│   │   │   ├── interface/# if* (HUD)
│   │   │   ├── meta/     # mt* (scan data)
│   │   │   ├── game/     # Main game logic
│   │   │   └── ...
│   │   └── nw4r/         # Not used
│   └── ...
├── include/
│   ├── dolphin/
│   ├── metal/
│   └── prime/
├── tools/
│   ├── decomp.py
│   ├── pak_extract.py    # Extract .pak files
│   └── ...
├── config/
│   ├── splits.txt
│   └── symbols.txt
├── data/
│   └── primes/           # Extracted .pak archives
├── orig/
│   └── GM8E01/
├── build/
├── configure.py
├── objdiff.json
├── PROGRESS.md
└── README.md
```

---

## 🔧 Toolchain Requirements

Same as other GameCube projects.

**Note**: Prime uses fewer headers, so build is faster than Melee/Sunshine. ~30 minutes first build on 8-core.

---

## 🚀 Getting Started (Prime-Specific)

1. **Clone**:
   ```bash
   git clone https://github.com/PrimeDecomp/prime.git
   cd prime
   ```

2. **ISO**: `Metroid Prime (USA).iso` (v1.02) to `orig/GM8E01/`. ~1.5GB.

3. **Configure**:
   ```bash
   python configure.py --extract-data  # Extracts .pak files to data/
   ```

4. **Build**:
   ```bash
   ninja -j$(nproc)
   ```

5. **First function**: Try `plPlayer::update` or `ifHud::draw`.

---

## 🎯 Known Challenges

### 1. Custom Engine (Metal)

No JSystem means **no shared knowledge** from Zelda/Sunshine.

Everything must be reverse-engineered from scratch:
- `CMemory` heap system
- `CActionState` (player states)
- `CCollision` (collision primitives)

**Silver lining**: Code is more self-contained; fewer dependencies.

---

### 2. Asset Format `.pak`

Prime uses `.pak` archives (different from `.arc`). Need to implement extraction.

**Tool**: `tools/pak_extract.py` exists but may be incomplete.

---

### 3. Scan System (`meta`)

The scan database (`mt*` functions) is complex:
- Parses object "scan data" from assets
- Builds the "Logbook" entries
- Cross-references with game objects

Not yet well understood.

---

## 🎮 Common Contribution Areas

### Good First Tasks

- `dolphin/` SDK wrappers (missing functions)
- `metal/` core utilities: `CMemory`, `CGraphics`
- `ifHud` drawing functions (simple)
- `wpBeam` weapon logic (some functions small)

---

### Intermediate

- `plPlayer` movement states (substates like `PLS0_Wait`, `PLS0_Move`)
- `wpWorld` collision response
- `bsSpacePirate` boss AI

---

### Advanced

- `cinematic` camera scripting
- `meta` scan database
- Scanned object data parsing

---

## 📈 Progress Milestones

| Milestone | Status |
|-----------|--------|
| SDK wrappers complete | ~70% |
| Player movement (`pl`) | ~20% |
| Weapons (`wp`) | ~15% |
| Bosses (`bs`) | ~10% |
| Collision (`wpWorld`) | ~10% |
| Full game | ~12% |

---

## 🔗 Related Projects

- **Metroid Prime 2: Echoes** - Similar engine, later project
- **Metroid Prime 3: Corruption** - Wii, different SDK (yet to start)
- **PrimeDecomp community** - Small but dedicated

---

## 📚 Resources

### Project

- [README](https://github.com/PrimeDecomp/prime)
- [PROGRESS.md](https://github.com/PrimeDecomp/prime/blob/main/PROGRESS.md)

### Community

- **Discord**: `#prime`, `#decompilation`
- **decomp.me**: Prime scratches available

### External

- **Metroid Prime wiki** (https://wiki.metroidprime.de) - Game mechanics, not decomp
- **Retro Studios** - Original developer (no SDK leaks known)

---

## 🆘 Getting Help

**Discord**: `#prime` in PrimeDecomp server

Prime has fewer contributors than Melee/Sunshine. Your contributions will have high impact!

---

## 🎯 Differences from Zelda/Mario

| Aspect | Zelda/Mario | Metroid Prime |
|--------|-------------|---------------|
| Engine | JSystem (shared) | Metal (custom) |
| C++ usage | Heavy | Moderate |
| File format | `.arc` + YAZ0 | `.pak` (unknown) |
| Actor system | `fopAc` | No standard; per-module actors |
| RTTI | Available (debug) | Minimal |
| Shared code | 40% between Z/T | 0% |

---

## 📝 Special Notes

- **No RTTI**: Don't expect auto-generated class headers.
- **Direct struct access**: Many `struct` definitions need manual reverse engineering.
- **Collision**: Uses capsule-based system, not bounding boxes.
- **Scan visor**: The "logbook" data is stored in `.sav` files and `.pak` resources.

---

*Last updated: March 2025*

*Check PROGRESS.md for latest.*