# The Legend of Zelda: Twilight Princess Decompilation

*The Twilight Realm awaits... and so does 100%! 💜*

---

## 📊 Project Overview

| Attribute | Value |
|-----------|-------|
| **Full Title** | The Legend of Zelda: Twilight Princess |
| **Game ID** | `TPE01` (USA GameCube), `TPJ01` (Japan GC), `TPP01` (Europe GC), `R3E01` (Wii) |
| **Platform** | GameCube & Wii (both supported) |
| **Primary Repository** | https://github.com/zeldaret/tp |
| **Discord Server** | https://discord.gg/zeldaret |
| **Active Since** | 2021 |
| **Current Completion** | **100%** (March 2024-2025) ✅ |
| **Primary Language** | C++ (heavy) |
| **SDK Used** | JSystem (v3.x) + custom ZELDA engine |
| **Architecture** | PowerPC 750CL (GC) / Broadway (Wii) |

---

## 🎯 Quick Status

- **Decompilation progress**: **100%** (functions) ✅
- **Build status**: ✅ **Fully linked?** (87.13% linked)
- **Matching**: **100%** of functions decompiled
- **Fully linked**: **87.13%** (some data may not link perfectly yet)
- **Last major milestone**: **COMPLETION** (2024/2025)
- **Recommended for newcomers**: ⚠️ Advanced (massive C++)

**Historic milestone**: The **first 100%** for a major Zelda title! Sets the standard for large-scale decomps.

---

## 🏗️ Architecture Highlights

### Engine Systems

| System | Implementation | Notes |
|--------|----------------|-------|
| **Physics** | Custom `d_kcol` + `d_kfly` | Link movement, Epona, Midna |
| **Audio** | JAudio2 + AX | `.aw`, `.bseq`, `.bnk` |
| **Graphics** | J3D (GX wrapper) | Heavy use: 3D world, effects |
| **File I/O** | DVD + RARC + YAZ0 | `.arc` archives for stage data |
| **Memory** | JKRHeap variants | Multiple heaps (game, graphics) |
| **Threading** | OSThread | Main + audio + possibly DVD |
| **Camera** | Custom `camera` system | 3D Zelda camera (lock-on) |
| **Save** | `gameinfo` system | ZLUS format? |
| **Actor System** | `d_a_` framework | Standard Zelda actor pattern |
| **dProc** | Process system | Similar to Melee? but different |

### Notable Modules

- **`d_a`** - Actors (Link, Midna, enemies, items, NPCs)
- **`d_bg`** - Background (Hyrule Field, dungeons, villages)
- **`d_kcol`** - Collision (KCL format, line-of-sight)
- **`d_kfly`** - Character movement (Link, Epona)
- **`d_s_play`** - Stage management, game flow
- **`d_sun**` - Sun? (maybe not, Twilight theme)
- **`d_timer`** - In-game timer (Goddess Statues)
- **`d_item`** - Inventory, rupees, heart containers
- **`d_meter`** - HUD (Rupees, hearts, stamina, etc.)
- **`d_msg`** - Dialogue system
- **`d_maps`** - Minimap, dungeon maps
- **`d_event`** - Event system (cutscenes, triggers)
- **`f_op`** - Scene/actor management (standard ZELDA)
- **`l_bd`** - Stage-specific logic? (bd = battle?)
- **`l_dan`** - Dungeon system

The codebase is **enormous** - probably 15,000+ functions (largest Zelda after BotW).

---

## 📁 Repository Structure

```
tp/
├── src/
│   ├── dolphin/
│   ├── JSystem/          # Decompiled (shared across zeldaret projects)
│   │   ├── J3D/
│   │   ├── J2D/
│   │   ├── JAudio/
│   │   ├── JKR/
│   │   └── ...
│   ├── pe/
│   │   ├── d/
│   │   │   ├── d_a/     # Actors (Link, Zant, Ganondorf, Midna, etc.)
│   │   │   ├── d_bg/    # Overworld, dungeons, villages
│   │   │   ├── d_kcol/  # Collision
│   │   │   ├── d_kfly/  # Movement (Link, Epona)
│   │   │   ├── d_msg/   # Dialogue
│   │   │   ├── d_maps/  # Minimap
│   │   │   ├── d_item/  # Inventory
│   │   │   ├── d_meter/ # HUD
│   │   │   ├── d_timer/ # Timer, time-based events
│   │   │   ├── d_event/ # Events
│   │   │   ├── d_s_play/# Stage management
│   │   │   ├── d_dmap/  # Dungeon maps?
│   │   │   ├── d_dm/front/
│   │   │   ├── d_dm/rear/
│   │   │   ├── d_dm/s demo?/
│   │   │   └── ...
│   │   ├── f_op/
│   │   │   ├── f_scene/
│   │   │   ├── f_actor/
│   │   │   └── ...
│   │   ├── l_bd/
│   │   ├── l_dan/
│   │   ├── l_material/
│   │   ├── l_show/
│   │   └── nw4r/
│   └── ...
├── include/
├── tools/
│   ├── decomp.py
│   ├── arc_extract.py
│   ├── kcl_extract.py
│   ├── map_extract.py
│   └── msg_extract.py
├── data/
│   ├── actors/
│   ├── items/
│   ├── dungeons/
│   ├── maps/
│   └── messages/
├── orig/
│   ├── TPE01/
│   ├── TPJ01/
│   ├── TPP01/
│   └── R3E01/            # Wii version
├── build/
├── configure.py
├── objdiff.json
├── PROGRESS.md           # Shows 100%
├── ACTORS.md             # Actor list
├── DUNGEONS.md           # Dungeon breakdown
├── ITEMS.md              # Item database
└── README.md
```

---

## 🔧 Toolchain Requirements

Same as other GC/Wii projects.

**Note**: Supports **both** GameCube and Wii versions. The code diverges slightly (different entry points, RTC). Most work focuses on GameCube first.

---

## 🚀 Getting Started

1. **Clone**:
   ```bash
   git clone https://github.com/zeldaret/tp.git
   cd tp
   git submodule update --init --recursive
   ```

2. **ISO**: `Zelda Twilight Princess (USA) (GC).iso` → `orig/TPE01/`. Or Wii version `R3E01/`.

3. **Configure**:
   ```bash
   python configure.py --extract-data
   ```
   Takes 10-15 minutes (more than Sunshine).

4. **Build**:
   ```bash
   ninja -j$(nproc)
   ```

5. **Check objdiff**: Should show **100%** functions decompiled! Remaining may be data mismatches or non-matching functions that have been marked `/* NON_MATCHING */` after verification.

---

## 🎯 Known Challenges (Remaining ~13% linking gap)

Even with 100% of functions decompiled, **linking perfectly** is tough:

### 1. Data Section Mismatches

- `.rodata` may have different ordering
- `.sdata`/`.sbss` alignment quirks
- `.ctors`/`.dtors` order changes
- `.bss` zero-initialization differences

**Status**: Likely being addressed by linker script tweaks or manual annotations.

---

### 2. Compiler Differences

Metrowerks CodeWarrior had subtle version differences:
- Nintendo SDK patch versions (1.2.5a vs 1.2.5n)
- `-O` optimization levels (maybe different per file)
- `-inline` hints, `-char` signedness

**Status**: Need to identify the exact compiler version and flags used.

---

### 3. Non-Matching Functions

Some functions may be correctly decompiled but still don't match due to:
- Register allocation differences
- Instruction ordering (NOP placement, scheduling)
- Different constant propagation
- Different inlining decisions

These get `/* NON_MATCHING */` comments and are accepted after manual review. But to get **100% linked**, they must be fixed.

---

### 4. Assembly Blocks

Zelda TP has **inline assembly** for:
- Matrix operations (4x4 transforms)
- Vector math (quaternion, cross products)
- GX setup code
- Hardware-specific stuff (VI, PE, etc.)

These need exact reproduction.

---

## 📈 Progress Milestones

- **2021**: Project begins, 5%
- **2022**: Major systems done, battle system, 40%
- **2023**: Dungeons mostly complete, 75%
- **2024**: Main story decompiled, 95%
- **2025 (Mar)**: **100%** functions → final push for linking!

---

## 🏆 Historic Significance

Twilight Princess is:
- **First major AAA title** to reach 100% (Melee is larger but not 100% yet)
- **First Zelda** (besides OoT/MM) to be fully documented
- **Heavy C++** - demonstrates ability to match complex class hierarchies
- **Dual version** (GC/Wii) - shows portability
- **Sets the bar** for future large decomps (BotW, etc.)

---

## 🔗 Related Zelda Projects

- **Ocarina of Time** (N64) - ~90%+? (already long done, but ongoing?)
- **Majora's Mask** (N64) - similar status
- **The Wind Waker** (GC) - 60% (shares JSystem)
- **Skyward Sword** (Wii) - maybe 50%?
- **Breath of the Wild** (Switch) - early, C++ heavy

Twilight Princess serves as the **bridge** between classic 3D Zelda (OoT) and modern (BotW).

---

## 🎮 Porting Prospects

**Excellent!** TP is a prime candidate for a PC port:
- Mature engine (JSystem)
- Clear graphical style (GX)
- Less reliant on hardware specifics than BotW
- Fan demand high (remaster rumors)

**Likely port features**:
- Higher resolution textures
- 60fps (original is 30)
- Improved camera
- Mod support (custom dungeons)

**Estimated effort**: Post-100% decomp → port could take 1-2 years.

---

## 📊 Actor System Deep Dive

Zelda uses `d_a_*` pattern:

```
d_a/
├── d_a_npc_              # NPCs (Ruslan, Ilia, etc.)
├── d_a_e_npc_            # Enemy NPCs (bulblins, bokoblins)
├── d_a_e_ym_             # Big enemies (Ganondorf, Zant)
├── d_a_kytag_            # Tags (triggers)
├── d_a_obj_              # Objects (crates, pots)
├── d_a_it_               # Items (rupees, hearts, weapons)
├── d_a_bg_               # Background objects (walls, bridges)
├── d_a_door_             # Doors (stage transitions)
├── d_a_al55_             # Midna? (special actor)
├── d_a_mirror_           # Mirror surfaces?
├── d_a_leon_             # Link's horse (Epona)
├── d_a_telesa_           # Environmental effects (water, fire)
└── ...
```

Each actor class:
- Inherits from `fpa::fpc_rect` or `fpa::fpc_rect`
- Has `create()`, `execute()`, `draw()`
- Uses `mScope` for C++ member ordering
- Dialogue via `m_msg`

---

## 🎯 Learning from TP

**Recommended study order**:

1. **Simple actor** (d_a_it_heart, d_a_obj_box)
2. **NPC actor** (d_a_npc_ruslan)
3. **Enemy actor** (d_a_e_ym_bigpo)
4. **Stage background** (d_bg_something)
5. **Collision** (d_kcol)
6. **Game flow** (d_s_play, stage change)

---

## 📈 Comparison with Other 100% Games

| Game | Decomp % | Linked % | Functions | Notes |
|------|----------|----------|-----------|-------|
| Mario Party 4 | 100% | 100% | ~6,000 | First GC complete |
| Twilight Princess | 100% | 87% | ~15,000? | Largest Zelda |
| Animal Crossing | 99.5% | 98.4% | ~9,000? | Almost complete |
| Pikmin | 99.2% | 90% | ? | Almost complete |

TP is the **largest** (by function count) completed decompilation so far. A massive technical achievement!

---

## 📝 Stats

- **Total functions (est)**: ~15,000+
- **Matched**: 100%
- **Fully linked**: 87.13% (as of March 2025)
- **Platforms**: GC (v1.0, 1.1) + Wii (v1.0, 1.1)
- **C++ classes**: Hundreds (full type info recovered)
- **Size**: ~10MB code segment?

---

## 🏗️ Dungeon List

1. **Forest Temple**
2. **Goron Mines**
3. **Lakebed Temple**
4. **Forest Temple again?** No, after which?
Actually TP order:
- Inside Forest Temple
- Goron Mines
- Lakebed Temple
- **Forest Temple** - wait, it's not repeated
Let me check:

**Dungeons**:
1. Forest Temple (Faron Woods)
2. Goron Mines (Death Mountain)
3. Lakebed Temple (Zora's Domain)
4. **Arbiter's Grounds** (Disused Temple)
5. **Snowpeak Ruins**
6. **Temple of Time** (optional, not main)
7. **City in the Sky**
8. **Palace of Twilight**
9. **Hyrule Castle** (final)

**Total**: 9 main dungeons + numerous mini-dungeons (caves).

---

## 🎯 Notes

- **Wii version**: Uses different controls (motion), but core engine same
- **GameCube version**: Traditional controls, easier to port
- **ZRET**: Zeldaret team maintains all Zelda projects; high standards
- **BotW**: Decompilation announced; will be toughest (C++17, modern engine)

---

*Last updated: March 2025*

*The Twilight has been conquered!* 🌟