# Luigi's Mansion Decompilation

*Boo! Did you match that function?*

---

## 📊 Project Overview

| Attribute | Value |
|-----------|-------|
| **Full Title** | Luigi's Mansion |
| **Game ID** | `GALM01` (USA), `GALJ01` (Japan) |
| **Platform** | GameCube |
| **Primary Repository** | https://github.com/doldecomp/luigismansion |
| **Discord Server** | https://discord.gg/doldecomp (channel #luigismansion) |
| **Active Since** | 2023 (public) |
| **Current Completion** | ~15% (March 2025) |
| **Primary Language** | C (mostly) |
| **SDK Used** | Dolphin SDK (similar to Melee) |
| **Architecture** | PowerPC 750CL, 32-bit |

---

## 🎯 Quick Status

- **Decompilation progress**: ~7% (450+ of 6,400+ functions)
- **Build status**: ✅ Builds successfully (early stage)
- **Matching**: ~420 functions matching (6.53% fully linked)
- **Last major milestone**: Basic room loading and ghost AI partially complete
- **Recommended for newcomers**: ✅ **Yes!** (Smaller codebase, clear structure)

**Why Luigi's Mansion?**: It's a **smaller** GameCube game (~6,500 functions vs Melee's 11,700+). Easier to wrap your head around. Good first project before tackling Zelda or Melee.

---

## 🏗️ Architecture Highlights

### Engine Systems

| System | Implementation | Notes |
|--------|----------------|-------|
| **Physics** | Custom (`dol_path`?) | 3D room navigation, ghost collision |
| **Audio** | AX Universal | `.aw`, `.bseq` |
| **Graphics** | GX | Fog, lighting, transparency effects |
| **File I/O** | DVD + RARC | `.arc` archives |
| **Memory** | JKRHeap | Similar to Melee |
| **Threading** | OSThread | Main + audio |
| **Input** | PAD | Poltergeist 3000 controls |

### Notable Modules

- **`d_a`** - Actors (ghosts, items, doors, furniture)
- **`d_bg`** - Background objects (walls, floors)
- **`d_mario`** - Mario/Luigi (player)
- **`d_room`** - Room loading/unloading
- **`d_vib`** - Vibrations (gamepad rumble)
- **`d_light`** - Lighting system (darkness, flashlight)

### Ghost AI

Each ghost type (`d_a_*)` has:
- Behavior script (`d_a_ghost_base`)
- Movement patterns
- Health and damage logic
- Special attacks

~50+ ghost types across mansion rooms.

---

## 📁 Repository Structure

```
luigismansion/
├── src/
│   ├── dolphin/
│   ├── JSystem/          # Smaller subset than Zelda
│   ├── pe/
│   │   ├── d/
│   │   │   ├── d_a/     # Actors (ghosts, items)
│   │   │   ├── d_bg/    # Backgrounds
│   │   │   ├── d_light/
│   │   │   ├── d_mario/
│   │   │   ├── d_room/
│   │   │   └── ...
│   └── ...
├── include/
├── tools/
├── config/
├── orig/
│   └── GALM01/
├── build/
├── configure.py
├── objdiff.json
├── PROGRESS.md
└── README.md
```

---

## 🔧 Toolchain Requirements

Same as other GameCube projects.

**Memory**: ~8GB sufficient (smaller than Melee).

---

## 🚀 Getting Started

1. **Clone**:
   ```bash
   git clone https://github.com/doldecomp/luigismansion.git
   cd luigismansion
   git submodule update --init --recursive
   ```

2. **ISO**: `Luigi's Mansion (USA).iso` → `orig/GALM01/`. ~1GB.

3. **Configure**:
   ```bash
   python configure.py
   ```

4. **Build**:
   ```bash
   ninja
   ```

5. **First task**: Look at `d_a_boo` (Boo actor) or `d_mario` movement.

---

## 🎯 Known Challenges

### 1. Smaller But Less Documentation

Fewer functions is good, but fewer community members mean slower progress. Less Discord chatter.

**Workaround**: Use Melee/Sunshine knowledge as reference (identical JSystem parts).

---

### 2. Room System

Rooms are loaded/unloaded dynamically. The `d_room` module manages:
- Room data (geometry, collision, objects)
- Adjacency (which rooms connect)
- Lighting and fog per room

**Challenge**: Matching requires understanding of room data format (`.arc` internals).

---

### 3. Ghost Scripts

Ghost behaviors might be scripted (like Melee's move scripts). Not confirmed yet.

---

## 🎮 Common Contribution Areas

### Beginner

- `d_mario` simple movement: `dMario_move`, `dMario_angle`
- `d_light` flashlight handling
- `d_vib` vibration functions
- Simple `d_a` actors: `d_a_boo` (basic ghost), `d_a_coin`

---

### Intermediate

- Complete ghost AI: `d_a_ghost_base` and one specific ghost type
- Room loading/unloading (`d_room`) - file I/O
- Poltergeist 3000 vacuum physics

---

### Advanced

- `d_a_boss` - Boss fights (King Boo, etc.)
- `d_demo` - Cutscene system
- `d_savedata` - Save game logic

---

## 📈 Progress Milestones

| Milestone | Est. |
|-----------|------|
| Core SDK + JSystem matching | 2025 |
| All `d_a` complete (50+ actors) | 2026 |
| Player and room system complete | 2026-2027 |
| Full game | 2028+ |

---

## 🔗 Related Projects

- **Melee** - Shared SDK (JKR, AX)
- **Sunshine** - Shared JSystem (graphics, fonts)
- **Animal Crossing** - Similar time period, different style

---

## 📚 Resources

- [PROGRESS.md](PROGRESS.md) - Current status
- [Discord](https://discord.gg/doldecomp) - #luigismansion channel

---

## 🆘 Getting Help

Ask in `#luigismansion` on doldecomp Discord.

Small community, but members are helpful. Be patient.

---

## 🎯 Why This Game Is Approachable

1. **Single-player only** - No network code to worry about
2. **Linear progression** - Fewer systems than open-world games
3. **Clear actor types** - Ghosts, items, doors each have distinct roles
4. **Not C++ heavy** - Mostly C, simpler inheritance
5. **Fun theme** - Spooky fun! 👻

---

*Last updated: March 2025*

*Good luck, and don't get scared by the Boos!* 😄