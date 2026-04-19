# Super Mario Galaxy Decompilation

*Stardust and starships... a Wii wonder!*

> **See also (Discord-sourced detail):** `COMMUNITY/discord-insights-libraries.md` §"NW4R" / §"EGG" — Wii middleware reference; `COMMUNITY/discord-tribal-knowledge.md` §"Super Mario Galaxy".

---

## 🔑 Galaxy Is Not a JSystem Game (Important!)

By the Wii era, Nintendo's middleware split into two separate libraries — and **SMG uses neither EGG nor JSystem**:

- **EGG** (Nintendo EAD's internal Wii middleware) is used by **Mario Kart Wii, NSMBW, Skyward Sword, Punch-Out!! Wii** — but **NOT Galaxy**. SMG uses a **different internal framework**.
- **NW4R** (NintendoWare for Revolution) **is** used by SMG and is shared with virtually every other Wii title.

If you've worked on a TWW/TP/Sunshine actor and expect `JKRHeap`, `J3D...`, or `J2D...` to be present in SMG: they aren't. Math types you'll see instead live under `nw4r::math::` (`VEC3`, `MTX34`, etc.) and the heap layer is SMG-specific.

## 🔑 Compiler Flags (Approximate, from Discord)

```
-c -nodefaults -proc gekko -DHOLLYWOOD_REV -DEPPC -enum int -fp hard
-Cpp_exceptions off -rtti off -ipa file -O4,s -inline auto
```

- **`-ipa file`** is required (and **only works on MWCC 3.0+** — SMG uses a 3.0+ compiler). This is what causes some functions to match on decomp.me but not locally if your context omits the flag.
- **NW4R library code within SMG** uses `-O4,p` (performance, not size) — note this differs from the SMG game code's `-O4,s`. Per-file flag selection matters.
- **`-DHOLLYWOOD_REV -DEPPC`** are mandatory Wii defines.

---

## 📊 Project Overview

| Attribute | Value |
|-----------|-------|
| **Full Title** | Super Mario Galaxy (and Galaxy 2?) |
| **Game ID** | `RMGJ01` (Japan), `RMGE01` (USA), `RMGP01` (Europe) |
| **Platform** | Wii |
| **Primary Repository** | Original moved: https://github.com/SMGCommunity/Petari |
| **Backup/Archived**: https://github.com/doldecomp/smg (archived) |
| **Discord Server** | https://discord.gg/doldecomp (and SMGCommunity) |
| **Active Since** | 2022 (original doldecomp), 2024 (SMGCommunity) |
| **Current Completion** | **46.62%** (March 2025, updated 3h ago!) |
| **Primary Language** | C++ (heavy) |
| **SDK Used** | JSystem (v4.x?) + custom Galaxy engine |
| **Architecture** | PowerPC Broadway (Wii), 32-bit |

---

## 🎯 Quick Status

- **Decompilation progress**: **46.62%** (growing rapidly!)
- **Build status**: ✅ Builds successfully (partial matching)
- **Fully linked**: **18.83%**
- **Matching**: ~3,500 functions matching (est.)
- **Last major milestone**: Active development - updated **3 hours ago**!
- **Recommended for newcomers**: ✅ **YES!** (High activity, many patterns from Sunshine/TP)

**Status**: One of the **most active** Wii projects. Very hot right now!

---

## 🏗️ Architecture Highlights

### Engine Systems

| System | Implementation | Notes |
|--------|----------------|-------|
| **Physics** | Custom `d_kfly` extended | Spinning, star bits, gravity |
| **Audio** | JAudio2 + AX | BGM, SFX, voice |
| **Graphics** | J3D (GX wrapper) | Massive worlds, star effects |
| **File I/O** | DVD + RARC + YAZ0 | `.arc` archives (galaxy data) |
| **Memory** | JKRHeap variants | Multiple heaps |
| **Threading** | OSThread | Main + audio + streaming |
| **Camera** | Custom `d_camera` | Spherical camera, lock-on |
| **Player** | Mario (various forms) | Bee, Boo, Spring, etc. |
| **Star Bits** | `d_star` system | Collectible logic |
| **Co-op** | `d_2p` system | Second player as star pointer |
| **Loading** | Streaming system | Load galaxies on demand |

### Notable Modules

- **`d_a`** - Actors (Mario, Lumas, Enemies, Bosses)
- **`d_bg`** - Galaxies (space backgrounds, planets)
- **`d_kcol`** - Collision (spherical planets)
- **`d_kfly`** - Character movement (Mario spin, gravity)
- **`d_2p`** - Co-op player 2 (Luma pointer)
- **`d_stage`** - Stage loading, galaxy selection
- **`d_map`** - Star map, comet appearances
- **`d_msg`** - Dialogue (Princess Peach, NPCs)
- **`d_meter`** - HUD (star bits, lives, co-op)
- **`d_event`** - Events (cutscenes, star appearances)
- **`d_lib`** - Library functions (math, allocators)
- **`d_util`** - Utilities

---

## 📁 Repository Structure

```
Petari/  (formerly smg)
├── src/
│   ├── dolphin/
│   ├── JSystem/          # Decompiled (shared)
│   │   ├── J3D/
│   │   ├── J2D/
│   │   ├── JAudio/
│   │   ├── JKR/
│   │   └── ...
│   ├── pe/
│   │   ├── d/
│   │   │   ├── d_a/     # Actors (Mario, Luma, enemies)
│   │   │   ├── d_bg/    # Galaxies (space backgrounds)
│   │   │   ├── d_event/ # Events
│   │   │   ├── d_kcol/  # Collision
│   │   │   ├── d_kfly/  # Movement
│   │   │   ├── d_lib/   # Shared math
│   │   │   ├── d_map/   # Star map, comet logic
│   │   │   ├── d_meter/ # HUD
│   │   │   ├── d_msg/   # Dialogue
│   │   │   ├── d_scene/ # Scene
│   │   │   ├── d_stage/ # Stage loading
│   │   │   ├── d_timer/ # Timer
│   │   │   ├── d_2p/    # Co-op
│   │   │   └── ...
│   │   ├── f_op/
│   │   ├── m_Do/
│   │   └── nw4r/
│   └── ...
├── include/
├── tools/
│   ├── decomp.py
│   ├── arc_extract.py
│   ├── galaxy_defs.py
│   └── message_extract.py
├── data/
│   ├── galaxies/         # List of galaxies
│   ├── actors/
│   ├── stages/
│   └── msg/
├── orig/
│   └── RMGE01/
├── build/
├── configure.py
├── objdiff.json
├── PROGRESS.md
├── ACTORS.md
├── GALAXIES.md
└── README.md
```

---

## 🔧 Toolchain Requirements

Same as GC/Wii (Wibo, dtk, m2c, Ninja).

**Special note**: Galaxy's streaming system may require more memory during build (16GB+ recommended).

---

## 🚀 Getting Started

1. **Clone**:
   ```bash
   git clone https://github.com/SMGCommunity/Petari.git
   cd Petari
   git submodule update --init --recursive
   ```

2. **ISO**: `Super Mario Galaxy (USA).iso` → `orig/RMGE01/`. ~3.5GB!

   Hint: Extract from disc image using `wit` or `gcn-split-tool`.

3. **Configure**:
   ```bash
   python configure.py --extract-data
   ```
   Takes 15-30 minutes (huge data).

4. **Build**:
   ```bash
   ninja -j$(nproc)
   ```

5. **Open objdiff**: See progress, ~46% so lots of work remains!

---

## 🎯 Known Challenges

### 1. Star Pointer / Co-op System

Second player uses Wii Remote pointer to collect Star Bits and stun enemies:

- Pointer tracking (IR camera)
- Star Bit collection collision
- Luma spawning and AI
- Network? (no, local only)

**Status**: Partially decompiled; complex state machine.

---

### 2. Mario Transformations

Mario has **many power-ups** that change physics:

- **Bee Mario**: Flying, hover
- **Boo Mario**: Invisibility, floating
- **Spring Mario**: Bouncing
- **Rainbow Mario**: Invincibility, speed
- **Rock Mario**: Rolling, breaking crystals
- **Cloud Mario**: Cloud platform generation
- **Fire Mario**: (Galaxy 2?) fireballs

Each transformation modifies:
- Movement (`d_kfly`)
- Collision
- Animation
- Interaction with enemies

**Status**: Some transformations done; many still need work.

---

### 3. Gravity and Orbital Mechanics

Galaxies are **spherical worlds**:

- Gravity pulls toward planet center
- Mario can walk on any surface (spherical)
- Curved collision tracking
- Fall off edges (to space)
- Transition between planets (jumping, launch stars)

**Status**: Core gravity system partially done; edge cases many.

---

### 4. Streaming Loader

Galaxy loads/unloads galaxies on demand:

- Background streaming from DVD
- Memory management (free old galaxy, load new)
- Asset caching (textures, models)
- Loading screen transitions

**Status**: System understood; functions being matched.

---

### 5. Galaxy & Comet Logic

The star map and comet appearances:

- Which galaxies are available when
- Comet appearances (timer-based)
- Hidden stars (Prankster Comet)
- Final boss unlock conditions

**Status**: `d_map` partially decompiled; needs more.

---

## 📈 Progress & Activity

**SMGCommunity/Petari** is **extremely active**:

- Daily commits (as recent as 3 hours ago!)
- Multiple core contributors
- Discord server active
- Regular progress updates on decomp.dev

This is **the hottest Wii project** right now. Might reach 70% by end of 2025.

---

## 🎮 Why Contribute to Galaxy?

**High reward**:
- Wii's most iconic game
- Beautiful physics (space, gravity)
- Huge codebase (likely 12,000+ functions)
- Potential for amazing PC port (4K HDR, 60fps+)

**Learning value**:
- Streaming systems
- Complex transformations
- Co-op parallel logic
- Large-scale organization

**Fun**: Who doesn't love Mario in space? (≧◡≦)

---

## 🆘 Getting Help

**Discord**:
- GC/Wii Decompilation server: `#smg` channel (now `#petari`?)
- `SMGCommunity` server (likely separate)
- `#general` for general decomp questions

**Resources**:
- `ACTORS.md` - Actor list (Mario, Luma, enemies)
- `GALAXIES.md` - All 42 galaxies (or 42? Actually: 42 in SMG1 + 43 in SMG2? total 85 if combined)
- `PROGRESS.md` - Status breakdown

---

## 🔗 Related Projects

- **Super Mario Sunshine**: Predecessor on GC, same JSystem
- **Super Mario Galaxy 2**: Likely uses same codebase, different galaxies
- **Super Mario 3D All-Stars**: Contains Galaxy; could benefit from decomp
- **SMG2 Project**: Might be same repo (combined) or separate

**Note**: SMG2 is similar engine; may be merged into same decomp effort.

---

## 📊 Galaxy Count

Super Mario Galaxy 1:
- **42 galaxies** total (including hidden)
- Grand Finale Galaxy (final boss)
- Various types: normal, ghost, timed, red coins, etc.

Super Mario Galaxy 2:
- **43+ galaxies** (new levels, some from SMG1)
- New galaxy types (challenge, cosmic, etc.)

**Total across both**: ~85 galaxies if combined.

Porting SMG2 would require additional work if not included.

---

## 📈 Comparison with Other Major Projects

| Game | Platform | Decomp % | Linked % | Est. Functions | Notes |
|------|----------|----------|----------|----------------|-------|
| Melee | GC | 61.28% | 33.74% | 11,700+ | Oldest, largest |
| Twilight Princess | GC | 100% | 87% | ~15,000? | First AAA 100% |
| Wind Waker | GC | 60.43% | 40.41% | ~12,900+ | Similar to TP |
| Sunshine | GC | 29.09% | 13.61% | ~8,000? | Well-documented |
| Galaxy | Wii | 46.62% | 18.83% | ~12,000? | Active, streaming |
| Animal Crossing | GC | 99.52% | 98.44% | ~9,000? | Almost complete |
| Mario Party 4 | GC | 100% | 100% | ~6,000 | First complete |

Galaxy is **midway** in progress but **high activity** suggests rapid completion ahead.

---

## 🏗️ Mario Forms

List of transformations in Galaxy:

1. **Normal Mario** - baseline
2. **Bee Mario** - wings, hover
3. **Boo Mario** - invisibility, float
4. **Spring Mario** - spring jump
5. **Rainbow Mario** - invincible, rainbow trail
6. **Rock Mario** - roll, break crystals
7. **Cloud Mario** - cloud platforms
8. **Fire Mario** (Galaxy 2) - fireballs
9. **Ice Mario**? (Galaxy 2?) - ice balls

Each has dedicated `d_kfly` code and collision.

---

## 🎯 Getting Involved

**Best first contributions**:

- Simple actors (Goombas, Koopas, stars)
- HUD elements (`d_meter`)
- Galaxy background objects (`d_bg`)
- Data tables (actor lists, spawn positions)
- Message extraction (`d_msg`)

**Avoid early**:
- Core Mario physics (`d_kfly` main functions)
- Streaming loader (complex)
- Stage-specific complex (Bowser battles)
- Co-op logic (state machine)

---

## 📈 Project Timeline & Estimates

Based on 46% in March 2025:

- **If current rate (2-3%/mo)**: 50% by mid-2025, 70% by 2026, 100% by 2028-2030
- **If contributors increase** (likely): 70% by 2026, 100% by 2027-2028

**Galaxy 2** may require **additional** work beyond Galaxy 1 completion.

---

## ✅ Stats

- **Total functions (est)**: 12,000-14,000 (Galaxy 1), maybe 20,000 total (both)
- **Matched**: 46.62% (~5,600)
- **Fully linked**: 18.83% (~2,300)
- **ISO size**: ~3.5GB (SMG1), SMG2 similar
- **Platform**: Wii (Broadway, 729MHz)
- **Language**: C++ (moderate template usage)

---

## 🎯 Why This Project Matters

Galaxy is:
- One of the **greatest games ever made** (critical acclaim)
- **Innovative** (spherical gravity, coop)
- **Iconic** (music, levels, powers)
- **High demand** for a modern port (Switch? PC?)
- **Complex engineering** - impressive decomp target

Completing Galaxy would be a **massive win** for the community.

---

*Last updated: March 2025*

*Let's-a-go!* 🌟🚀