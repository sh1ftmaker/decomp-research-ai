# Animal Crossing (GameCube) Decompilation

*Your village is almost fully documented!*

---

## 📊 Project Overview

| Attribute | Value |
|-----------|-------|
| **Full Title** | Animal Crossing (Dōbutsu no Mori in Japan) |
| **Game ID** | `AQEE01` (USA), `AQAJ01` (Japan) |
| **Platform** | GameCube |
| **Primary Repository** | https://github.com/doldecomp/animalcrossing |
| **Discord Server** | https://discord.gg/doldecomp (#animalcrossing channel) |
| **Active Since** | 2021 (public) |
| **Current Completion** | **99.52%** (March 2025) |
| **Primary Language** | C++ (moderate) |
| **SDK Used** | JSystem (similar to Sunshine) |
| **Architecture** | PowerPC 750CL, 32-bit |

---

## 🎯 Quick Status

- **Decompilation progress**: **99.52%** - **Virtually complete!**
- **Build status**: ✅ Builds successfully (near-matching)
- **Fully linked**: **98.44%**
- **Matching**: Thousands of functions matching
- **Last major milestone**: Nearly full completion (2025)
- **Recommended for newcomers**: ⚠️ Moderate (core done, but many details remain)

**Historic**: Animal Crossing will be among the **first** fully complete GameCube decompilations, joining Mario Party 4 and Twilight Princess!

---

## 🏗️ Architecture Highlights

### Engine Systems

| System | Implementation | Notes |
|--------|----------------|-------|
| **Physics** | Custom (d家具, dPlayer) | Object placement, collision |
| **Audio** | JAudio2 + AX | `.aw`, `.bseq`, `.bnk` |
| **Graphics** | J3D (GX wrapper) | Character models, house interiors |
| **File I/O** | DVD + RARC + YAZ0 | `.arc` archives for items, villagers |
| **Memory** | JKRHeap variants | Standard JSystem allocators |
| **Threading** | OSThread | Main + clock thread |
| **Clock** | Custom `mDo` time module | Real-time simulation (24/7) |
| **Save** | Flash memory (FZ) format | Encrypted, checksummed |

### Notable Modules

- **`d_a`** - Actors (villagers, furniture, items, animals, insects, fish)
- **`d_bg`** - Background (outdoors, house interiors)
- **`d_house`** - House management, upgrades
- **`d_npc`** - Villager AI, dialogue, schedules
- **`d_item`** - Inventory, item placement
- **`d_savedata`** - Save file I/O, encryption
- **`d_main`** - Main loop, clock management, day transitions
- **`d_nes`** - NES emulator (plays classic NES games!)
- **`d_kanko`** - Visitor system (multiplayer visits)
- **`d_mail`** - Mail system (letters, bills)
- **`d_fruit`** - Fruit growth, orchard mechanics
- **`d_event`** - Special events (holidays, birthdays)

---

## 📁 Repository Structure

```
animalcrossing/
├── src/
│   ├── dolphin/
│   ├── JSystem/          # Almost identical to Sunshine
│   ├── pe/
│   │   ├── d/
│   │   │   ├── d_a/     # Actors (villagers, items, animals, bugs, fish)
│   │   │   ├── d_bg/    # Ground, trees, rivers, buildings
│   │   │   ├── d_event/ # Events, holidays
│   │   │   ├── d_fruit/ # Fruit growth
│   │   │   ├── d_house/ # House customization
│   │   │   ├── d_item/  # Inventory, item dropping
│   │   │   ├── d_kanko/ # Visitors/multiplayer
│   │   │   ├── d_mail/  # Mail system
│   │   │   ├── d_main/  # Clock, main loop
│   │   │   ├── d_nes/   # NES emulator! ⚠️ legal considerations
│   │   │   ├── d_npc/   # Villager AI, dialogue
│   │   │   ├── d_savedata/
│   │   │   └── ...
│   │   └── nw4r/
│   └── ...
├── include/
├── tools/
│   ├── decomp.py
│   ├── arc_extract.py    # Extract .arc archives
│   ├── nes_extract.py    # Extract NES ROMs (⚠️)
│   └── save_tool.py      # Decrypt/encrypt save files
├── config/
│   ├── splits.txt        # Almost complete
│   └── symbols.txt       # Nearly all symbols identified
├── data/                 # Game data (item tables, villager data, etc.)
│   ├── item/
│   ├── villager/
│   ├── house/
│   └── nes_roms/         # ⚠️ NOT INCLUDED (copyright)
├── orig/
│   └── AQEE01/
├── build/
├── configure.py
├── objdiff.json
├── PROGRESS.md           # Shows ~99.5%
├── ACTORS.md             # List of all actors and status
├── VILLAGERS.md          # Villager data
└── README.md
```

---

## 🔧 Toolchain Requirements

Same as other GameCube projects.

**Memory**: ~12GB recommended (large data tables for items/villagers)

---

## 🚀 Getting Started

1. **Clone**:
   ```bash
   git clone https://github.com/doldecomp/animalcrossing.git
   cd animalcrossing
   git submodule update --init --recursive
   ```

2. **ISO**: `Animal Crossing (USA).iso` (v1.0 or 1.1) → `orig/AQEE01/`. ~1.3GB.

3. **Configure**:
   ```bash
   python configure.py --extract-data  # Extracts item/villager tables
   ```
   Takes 5-10 minutes.

4. **Build**:
   ```bash
   ninja -j$(nproc)
   ```

5. **Open objdiff**: See remaining ~0.5% - mostly data or tricky functions.

---

## 🎯 Known Challenges (Remaining)

### 1. Real-Time Clock Uncertainty

The game's clock must match original behavior exactly:
- Day transitions at 6:00 AM (in-game time?)
- Save file timestamps
- RNG seeded by clock

**Status**: Mostly solved, but edge cases may remain.

---

### 2. Save File Encryption

The `.sav` format uses custom encryption with keys derived from:
- Console ID? (probably not on GameCube)
- Clock value at time of save
- Possibly player name

**Status**: Decryption/encryption functions likely matched, but need verification.

---

### 3. NES Emulator

**Legal**: The NES ROMs embedded in the game are copyrighted. They cannot be redistributed.

**Approach**:
- Decompile the emulator code itself (likely a modified `nester` or custom)
- Document how to provide your own homebrew NES ROMs
- Or create a port that expects external ROM files

**Status**: NES emulator code may be partially decompiled; verify.

---

### 4. Data Tables

**Massive tables** to document:
- **400+ furniture items** (prices, colors, placements)
- **250+ villagers** (names, personalities, dialogue)
- **80+ insects** (species, spawn times, locations)
- **80+ fish** (species, spawn conditions)
- **Holiday events** (date-specific logic)

**Status**: Tables may be in `.c` files but need review/cleanup.

---

## 🎮 Common Contribution Areas (Final 0.5%)

Since the project is nearly complete, remaining work is likely **tricky corner cases**:

- Save file edge cases (corrupted save recovery)
- Clock edge cases (DST, leap years, year changes)
- NES emulator quirks (PPU timing, APU cycles)
- Multiplayer visitor synchronization
- Rare villager dialogue triggers
- Bug compatibility (original had bugs that must be preserved!)

**Not recommended for beginners** at this stage.

---

## 📈 Progress Milestones

| Milestone | Completed? | Est. Date |
|-----------|------------|-----------|
| Core SDK (JSystem, Dolphin) | ✅ 100% | 2023 |
| Actors (所有 `d_a`) | ✅ ~99% | 2025 |
| Villager AI (`d_npc`) | ✅ 99% | 2025 |
| Save system (`d_savedata`) | ✅ ~99% | 2025 |
| NES emulator (`d_nes`) | ⚠️ ~95% | 2025 |
| Clock system (`d_main`) | ✅ 100% | 2025 |
| Full game | ✅ 99.52% | 2025 |

---

## 🔗 Related Projects

- **Super Mario Sunshine** - Almost identical JSystem version
- **The Wind Waker** - Slightly newer JSystem
- **Mario Party 4** - First complete (similar minigame structure)
- **Pikmin** - Also nearly complete (99.17%)

---

## 📚 Resources

- **[PROGRESS.md](PROGRESS.md)** - Detailed breakdown by module
- **[ACTORS.md](ACTORS.md)** - List of all decompiled actors
- **[VILLAGERS.md](VILLAGERS.md)** - Villager database
- Discord `#animalcrossing` for questions

---

## 🆘 Getting Help

**Discord**: `#animalcrossing` in doldecomp server

Given the near-completion, most questions will be about **specific remaining issues** (0.48% remaining). Search Discord history first.

---

## 🎯 Porting Prospects

Animal Crossing is **perfect for a PC port**:
- 24/7 clock would run natively on PC
- Save files can be in AppData
- NES emulator can use PC input
- Graphics: GX → OpenGL straightforward (same engine as Sunshine port)

**Status**: A port is naturally the next step after 100% decomp. Likely will happen soon after completion.

---

## 📊 Comparison with Other Near-Complete Games

| Game | Decomp % | Linked % | Est. Completion |
|------|----------|----------|-----------------|
| Mario Party 4 | 100.00% | 100.00% | ✅ Done |
| Twilight Princess | 100.00% | 87.13% | ✅ Done |
| Animal Crossing | 99.52% | 98.44% | Almost done |
| Pikmin | 99.17% | 89.90% | Almost done |
| Super Smash Bros. Melee | 61.28% | 33.74% | 2-3 years |
| Zelda: Wind Waker | 60.43% | 40.41% | 2-3 years |

---

## 🏆 Historic Significance

Animal Crossing is:
- First life-sim game fully decompiled
- First game with functional real-time clock (preserved)
- First with NES emulator (legal complexities)
- One of the first **100% complete** GameCube titles

This paves the way for:
- Ports to modern systems (Switch, PC, mobile)
- Mods (custom villagers, items)
- Translations (other languages)
- Quality-of-life improvements (faster text, etc.)

---

## 📝 Legal Note on NES ROMs

**DO NOT** include copyrighted NES ROMs in any distribution.

The decompilation can include:
- ✅ Emulator code (clean-room)
- ✅ How to configure the emulator
- ⚠️ Instructions to provide your own legally-owned ROMs
- ❌ Actual Mario, Zelda, etc. ROM binaries

This is similar to how Dolphin emulator handles BIOS files.

---

*Last updated: March 2025 (based on decomp.dev data)*

*Nearly there! Just a few more functions to go!* 🏠🐟🐞