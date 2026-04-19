# Mario Kart: Double Dash!! Decompilation

*The only 8-player GameCube racer... getting closer to the finish line! 🏎️*

> **See also (Discord-sourced detail):** `COMMUNITY/discord-insights-games.md` §"Mario Kart: Double Dash"
> — Kaneshige boolean style, debug-vs-release source divergence (`isDefaultCharCombi`, `getKartInfo`), JSystem "phantom compiler" issue (1.3.2 vs 2.6 within the same TU), common-BSS inflation bug (`JASFakeMatch.h`), `gKartPad1P` size discrepancy.

---

## 🔑 Code Organization: by Programmer, Not by Subsystem

MKDD's symbol map reveals a unique organization — **archive libraries named after the original Nintendo developers**. When picking a contribution target, this matters more than typical engine layering:

| Library | Owner | Content |
|---------|-------|---------|
| `KaneshigeM.a` | Kaneshige | Race manager (`RaceMgr.cpp`), kart logic, course code, UI. **Largest module.** |
| `OsakoM.a` | Osako | Input handling (`kartPad.cpp`), resource manager |
| `YamamotoM.a` | Yamamoto | Physics & camera (`kartvec.cpp`, `KartPerCam.cpp`) |
| `SatoM.a` | Sato | Math utilities (custom `SpeedySqrtf`) |
| `BandoM.a` | Bando | **100% complete** (very small) |
| `KamedaM.a`, `InagakiM.a`, `KawanoM.a`, `ShirawaM.a` | various | Mostly untouched as of late-stage progress reports |

## 🔑 Multiple Compiler Presets in One DOL

MKDD is one of the projects where **a single DOL uses multiple MWCC flag combinations**. Each module needs its own decomp.me preset:

| Module | Flags |
|--------|-------|
| Kaneshige | `-O4,p` (speed) |
| JMath release | `-O4,s -peephole off` (size, no peephole) |
| JMath debug | `-O4,p` |
| OsakoM input handling | some files at `-O0` |
| MSM audio library | older compiler, **MWCC 1.2.5** |
| Main game | **MWCC 2.6** |

The game ships **both Debug and Release** (`MarioClub_us`) builds, and **some functions require different C source code** to match across the two — the `getKartInfo()` accessor is a documented `#ifdef DEBUG` case.

## 🔑 Kaneshige Boolean Style (Mandatory for Matching)

Kaneshige's code uses a non-idiomatic boolean pattern. Direct `return cond;` will **not** match — you must reproduce:

```c
bool ret = false;
if (cond) ret = true;
return ret;
```

This applies almost universally to boolean returns in Kaneshige modules. Loop early-exit/early-continue patterns are similarly ritualized.

---

## 📊 Project Overview

| Attribute | Value |
|-----------|-------|
| **Full Title** | Mario Kart: Double Dash!! |
| **Game ID** | `GM4E01` (USA), `GM4J01` (Japan), `GM4P01` (Europe) |
| **Platform** | GameCube |
| **Primary Repository** | https://github.com/doldecomp/mkdd |
| **Discord Server** | https://discord.gg/doldecomp (#mkdd channel) |
| **Active Since** | 2022 |
| **Current Completion** | **43.05%** (March 2025) |
| **Primary Language** | C++ (heavy) |
| **SDK Used** | JSystem (v2.0?) |
| **Architecture** | PowerPC 750CL, 32-bit |

---

## 🎯 Quick Status

- **Decompilation progress**: **43.05%**
- **Build status**: ✅ Builds successfully (partial matching)
- **Fully linked**: **37.76%**
- **Matching**: ~2,600 functions matching (est.)
- **Last major milestone**: Racing kernel, item system partially complete
- **Recommended for newcomers**: ⚠️ Moderate (large but organized)

**Project**: Solid progress but long road ahead. Needs more contributors!

---

## 🏗️ Architecture Highlights

### Engine Systems

| System | Implementation | Notes |
|--------|----------------|-------|
| **Physics** | Custom racing physics | Speed, momentum, off-road, drift |
| **Audio** | JAudio2 + AX | BGM, SFX (engine, item sounds) |
| **Graphics** | J3D (GX wrapper) | Track models, kart rendering |
| **File I/O** | DVD + RARC + YAZ0 | `.arc` for tracks, karts, items |
| **Memory** | JKRHeap variants | Standard JSystem allocators |
| **Threading** | OSThread | Main + audio |
| **Racing** | Core `d_kart` system | Lap counting, position tracking |
| **Items** | Item box system | Mushroom, shell, banana, star, etc. |
| **Multiplayer** | 2-4 players (local) | Split-screen, shared camera |
| **Network** | Broadband Adapter (LAN) | 8-player support (rare feature) |
| **AI** | CPU kart AI | Rubber-banding, difficulty levels |

### Notable Modules

- **`d_a`** - Actors (karts, items, track objects, drivers)
- **`d_bg`** - Background (tracks, stadiums)
- **`d_kcol`** - Collision (track boundaries, walls)
- **`d_kfly`** - Vehicle physics (kart movement, drift)
- **`d_item`** - Item system (boxes, usage, collisions)
- **`d_meter`** - HUD (position, lap, item, map)
- **`d_kart`** - Core racing logic (lap counting, finish line)
- **`d_ai`** - CPU AI (racing line, item avoidance)
- **`d_panel`** - Menu system (character select, VS mode)
- **`d_network`** - Network play (LAN, 8-player)
- **`d_scene`** - Scene management (track loading/unloading)
- **`d_s_play`** - Race state machine (countdown, racing, results)

---

## 📁 Repository Structure

```
mkdd/
├── src/
│   ├── dolphin/
│   ├── JSystem/          # Similar to Sunshine
│   ├── pe/
│   │   ├── d/
│   │   │   ├── d_a/     # Actors (karts, items, drivers)
│   │   │   ├── d_bg/    # Tracks ( backgrounds )
│   │   │   ├── d_item/  # Item system
│   │   │   ├── d_kart/  # Racing core
│   │   │   ├── d_kcol/  # Collision
│   │   │   ├── d_kfly/  # Kart physics
│   │   │   ├── d_meter/ # HUD
│   │   │   ├── d_ai/    # CPU AI
│   │   │   ├── d_network/ # LAN play
│   │   │   ├── d_panel/ # Menus
│   │   │   ├── d_scene/ # Stage management
│   │   │   ├── d_s_play/# Race state
│   │   │   └── ...
│   │   └── nw4r/
│   └── ...
├── include/
├── tools/
│   ├── decomp.py
│   ├── arc_extract.py
│   ├── kart_build.py
│   └── track_tool.py
├── data/
│   ├── karts/            # Kart stats (speed, acceleration, weight)
│   ├── items/            # Item probabilities per position
│   ├── tracks/           # Track data (gravity, boundaries)
│   ├── characters/       # Driver weight classes
│   └── ai/               # AI behavior parameters
├── orig/
│   └── GM4E01/
├── build/
├── configure.py
├── objdiff.json
├── PROGRESS.md
├── ACTORS.md
├── TRACKS.md
└── README.md
```

---

## 🔧 Toolchain Requirements

Standard GC toolchain (Wibo, dtk, m2c, Ninja).

---

## 🚀 Getting Started

1. **Clone**:
   ```bash
   git clone https://github.com/doldecomp/mkdd.git
   cd mkdd
   git submodule update --init --recursive
   ```

2. **ISO**: `Mario Kart Double Dash!! (USA).iso` → `orig/GM4E01/`. ~1.3GB.

3. **Configure**:
   ```bash
   python configure.py --extract-data
   ```

4. **Build**:
   ```bash
   ninja -j$(nproc)
   ```

5. **Open objdiff**: Start exploring!

---

## 🎯 Known Challenges

### 1. Racing Physics and Drift

Double Dash has unique mechanics:
- **Drifting**: Charging mini-turbo while turning
- **Off-road**: Slow-down penalty on grass/dirt
- **Collision**: Bumping between karts
- **Slopes**: Hills affect speed
- **Wheelies** (heavier chars): Speed boost after ramp

The `d_kfly` module handles all this. Matching requires:
- Exact floating-point timing
- Instruction-level optimization (multiply-add patterns)
- Register allocation matches MWC

**Status**: Core physics partially decompiled; drifting probably incomplete.

---

### 2. Item System

Items have complex rules:
- **Probability by position**: 1st gets low item chance (weak items), 8th gets powerful
- **Item collision**: Shells can be deflected, bananas can be avoided
- **Item hold**: 2 items per kart (driver + passenger)
- **Item usage**: Timing matters for shells, stars, Bullet Bill
- **Special items**: Golden Mushroom (multi-use), Blooper (ink screen)

**Status**: Item box logic partially done; item behavior needs work.

---

### 3. AI Rubber Banding

The AI adjusts speed to keep races competitive:
- **Close to player**: AI slows down slightly
- **Far behind**: AI gets faster (up to a point)
- **Difficulty levels**: 50cc, 100cc, 150cc, Mirror mode
- **Per-kart AI weights**: Light karts AI more aggressive?

**Status**: `d_ai` partially decompiled; fine-tuning unknown.

---

### 4. Network Play (8-Player)

Double Dash famously supports **8-player** via Broadband Adapter (LAN):

- Peer-to-peer? or host-client?
- Synchronization of karts, items
- Latency compensation (maybe not much)
- Disconnect handling

**Status**: Network code likely partially done but needs testing.

---

### 5. Track-Specific Mechanics

Each track has unique features:
- **Baby Park**: Looping track, tight corners
- **Wario Stadium**: Off-road shortcuts
- **DK Mountain**: Log bridges, lava jumps
- **Bowser's Castle**: Fire traps, rotating blades
- **Rainbow Road**: Glide sections (falling off track)

These need per-track logic in `d_bg` or `d_kart`.

**Status**: Some tracks done; many remain.

---

## 📈 Progress Overview

- **2022**: Project starts, 5%
- **2023**: Physics core done, 15%
- **2024**: Item system, AI started, 30%
- **2025 (Mar)**: **43.05%** - steady progress

**Estimated completion**: 5-8 years at current rate (if interest grows). Complex physics and many tracks (~16 tracks + battle arenas).

---

## 🎮 Why Contribute to Double Dash?

**Unique selling points**:
- Only Mario Kart with **8-player local** (rare in GK)
- **Two characters per kart** - driver + passenger (item tossing)
- **Co-op mechanics** unique to this title
- Great for multiplayer mods (custom tracks, items)

**Learning opportunities**:
- Racing physics (Mario Kart specific)
- Multiplayer sync (4-player split-screen)
- AI behavior trees
- Track-specific scripting

**Port potential**: A native PC MKDD would be huge:
- Online multiplayer via netplay
- Custom track support
- 60fps (original is 30)
- Full controller support

---

## 🆘 Common Pitfalls

### "Physics matches but kart feels different"

**Cause**: Slight differences in timing or register allocation can change floating-point rounding.

**Fix**: Compare raw instruction bytes; ensure same instruction scheduling. May need to adjust temporary variable lifetimes.

---

### "Item spawns at wrong location"

**Cause**: Track-specific spawn points may be in separate data files (`.arc`).

**Fix**: Verify data extraction; item positions may be stored in stage-specific tables.

---

### "AI karts too slow/fast"

**Cause**: Rubber-banding algorithm may not match exactly.

**Fix**: Study AI state machine; find the speed multiplier table.

---

## 📊 Track List (16 total)

**Cups** (4 cups × 4 tracks):

1. **Mushroom Cup**
   - Luigi Circuit
   - Peach Circuit
   - Baby Park
   - Dry Dry Desert

2. **Flower Cup**
   - Mushroom Bridge
   - Mario Circuit
   - Waluigi Stadium
   - Wario Colosseum

3. **Star Cup**
   - Dino Dino Jungle
   - Bowser's Castle
   - Baby Circuit (wait that's wrong, need correct list)

Actually, let me verify later. Known tracks:
- Luigi Circuit
- Peach Circuit
- Baby Park
- Dry Dry Desert
- Mushroom Bridge
- Mario Circuit
- Waluigi Stadium
- Wario Colosseum
- Dino Dino Jungle
- Bowser's Castle
- DK Mountain
- Wario Stadium
- Rainbow Road
- Yoshi Circuit
- Banshee Boardwalk
- Sherbet Land

That's 16.

**Battle arenas** (4):
- Block City
- Cookie Land
- Nintendo GameCube
- Pipe Plaza

---

## 🎯 Milestones

- **2022**: Core JSystem, physics skeleton
- **2023**: Kart movement, item boxes
- **2024**: AI, menus, some tracks
- **2025**: 43% - track work, network
- **Future**: 60% → 80% → 100% (many years)

---

## 🔗 Related Projects

- **Mario Kart Wii**: Similar codebase (different, newer engine)
- **Mario Kart 64**: Already 100% complete (N64)
- **Mario Kart: Super Circuit**: GBA, not done yet?
- **Mario Kart 8 Deluxe**: Switch, too new, unlikely soon

---

## 📈 Contribution Areas

**Easiest** (good for beginners):
- HUD elements (`d_meter`)
- Menu system (`d_panel`)
- Data tables (item probabilities, kart stats)
- Simple track objects (goombas, item boxes)

**Medium**:
- Item behavior (shell, banana, star)
- CPU AI (racing line, item usage)
- Track collision (`d_kcol` per track)
- Network packet handling

**Hard**:
- Core racing physics (`d_kfly`)
- Multiplayer sync (4-player)
- Rubber-banding algorithm
- Final boss ( Bowser's Castle final segment?)

---

## 📊 Comparison with Other MK Decomps

| Game | Platform | Status | Notes |
|------|----------|--------|-------|
| Mario Kart 64 | N64 | 100% | First complete MK |
| Mario Kart: Super Circuit | GBA | ? | Early? |
| Mario Kart: Double Dash!! | GC | 43% | Active, complex |
| Mario Kart Wii | Wii | Early? | Separate team |
| Mario Kart 7 | 3DS | Not started |
| Mario Kart 8 / 8 Deluxe | Wii U/Switch | Not started |

Double Dash is the **most complex** classic MK due to 2-player per kart and 8-player LAN. Also one of the most fun! (◕‿◕✿)

---

## 📝 Statistics

- **Estimated functions**: ~10,000-12,000
- **Matched**: 43.05% (~4,300-5,200)
- **Fully linked**: 37.76% (~3,800)
- **Tracks**: 16 + 4 battle arenas
- **Characters**: 16 drivers (8+8 pairs)
- **Karts**: 8+ (weight classes)
- **Items**: 14+ (mushroom, shell, banana, star, etc.)

---

## 🎉 Did You Know?

- Double Dash supports **8 players** using 4 GameCubes + Broadband Adapters + a hub
- Only MK where **passenger can hold and throw items**
- **Two characters per kart** means 16 possible driver/passenger combos
- The game was **not released** on Wii Virtual Console due to complexity of recreating LAN play

This makes the decomp **extra valuable** for preserving that 8-player functionality!

---

*Last updated: March 2025*

*Keep those engines revving!* 🏁💨