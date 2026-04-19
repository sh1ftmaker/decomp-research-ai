# Mario Party 4 Decompilation

*The first complete GameCube decompilation! 🎉*

> **See also (Discord-sourced detail):** `COMMUNITY/discord-insights-games.md` §"Mario Party 4"
> — full REL build pipeline, `elf2rel` customization, parallel-link map-file conflict, HSF (Hudson Scene Format), `HuMemDirectMalloc` heap-number convention, two-variant Yaz0-like compressor edge cases.

---

## 🔑 Why MP4 Was the First to Reach 100% (Architectural Clues)

- **Hudson Soft proprietary engine** (not Nintendo SDK middleware). Smaller surface area than JSystem-based titles.
- **Massive REL-based modularity:** every minigame is a separate `.rel` file, every board is a separate `.rel`. Master table at `_ovltbl` (`0x8012FDE0`). Naming scheme:
  - `m1xx` = MP2-era ports
  - `m2xx` = MP3-era ports
  - `m3xx` = mid-development stubs (mostly empty — confusing but harmless)
  - `m4xx` = new MP4 minigames
- **REL format version 2** (not v3). v2 retains all relocation data — heavier but matchable. (v3 trims self/DOL relocs to save memory but can't be unlinked.)
- **Embedded build paths** in REL files reveal original directory structure: `e:\project\mpgce\prog\DLLS\bootDll\bootDll.elf`.
- **Compiler:** MWCC **2.6** for the DOL; **MWCC 1.2.5** for Hudson's MSM audio library (newer compiler caused MSM prologue ordering issues — staying on 1.2.5 was required).
- **String pooling enabled** (`-pool on`) for the DOL.

## 🔑 REL Build Gotchas Worth Knowing

- **`.ctors`/`.dtors` data must be zeroed** in the section table; keeping them causes relocation failures.
- **`.rodata` and `.data` must be 8-byte aligned** in REL outputs.
- **ASCII strings in REL `.s` files** need their `.balign 4` directives **removed** and string encoding fixed (Hudson REL disassembler quirk).
- **Parallel REL builds with ninja conflict on the linker `.MAP` file** — concurrent writes corrupt it. Run REL link commands sequentially or per-target.
- **`.rodata` first item** is almost always the `0.5` or `3.0` double constants — handy section-generation sanity check.

---

## 📊 Project Overview

| Attribute | Value |
|-----------|-------|
| **Full Title** | Mario Party 4 |
| **Game ID** | `GMPJ01` (Japan), `GMPE01` (USA), `GMPP01` (Europe) |
| **Platform** | GameCube |
| **Primary Repository** | https://github.com/mariopartyrd/marioparty4 |
| **Discord Server** | ? (likely part of larger communities) |
| **Active Since** | 2021? (recent completion) |
| **Current Completion** | **100.00%** (March 2025) |
| **Primary Language** | C |
| **SDK Used** | Dolphin SDK, custom party engine |
| **Architecture** | PowerPC 750CL, 32-bit |

---

## 🎯 Quick Status

- **Decompilation progress**: **100%** - **FIRST complete GameCube decompilation!**
- **Build status**: ✅ **Fully matching** (both USA versions)
- **Matching**: **100%** of functions match byte-perfect
- **Fully linked**: **100%** (all object files link correctly)
- **Last major milestone**: **COMPLETION** (2024/2025)
- **Recommended for newcomers**: ⚠️ Advanced now (mostly done)

**Historic achievement**: Mario Party 4 is the **first fully decompiled GameCube title**, and the first with a PC port already in development!

---

## 🏗️ Architecture Highlights

### Engine Systems

| System | Implementation | Notes |
|--------|----------------|-------|
| **Physics** | Simple 2D board movement | Dice rolls, movement on boards |
| **Audio** | AX Universal | `.aw`, `.bseq`, `.bnk` |
| **Graphics** | GX | Character models, boards, minigames |
| **File I/O** | DVD + RARC + YAZ0 | `.arc` archives for boards, minigames |
| **Memory** | JKRHeap | Standard allocator |
| **Threading** | OSThread | Main + audio |
| **Minigames** | Self-contained scenes | 60+ minigames, each separate |

### Notable Modules

- **`mp`** - Main party system (board game logic)
- **`mg`** - Minigame engine (each minigame is a separate module)
- **`d_a`** - Actors (characters, items, effects)
- **`d_bg`** - Boards (background scenes)
- **`d_meter`** - Coin/star meter, UI
- **`d_timer`** - Timer for minigames

### Game Structure

Mario Party 4 consists of:
- **5 boards** (each with unique mechanics)
- **60+ minigames** (each with independent code)
- **Character selection** (Mario, Luigi, Peach, etc.)
- **Party system**: Dice roll → movement → event → minigame → repeat

The codebase is **modular** with clear boundaries between boards and minigames. Made decompilation more manageable.

---

## 📁 Repository Structure

```
marioparty4/
├── src/
│   ├── dolphin/
│   ├── JSystem/          # Minimal? maybe not heavily used
│   ├── pe/
│   │   ├── d/
│   │   │   ├── d_a/     # Actors (characters, items)
│   │   │   ├── d_bg/    # Boards
│   │   │   ├── d_meter/
│   │   │   ├── d_timer/
│   │   │   ├── mp/      # Main party logic
│   │   │   ├── mg/      # Minigames (60+ subdirectories!)
│   │   │   └── ...
│   │   └── nw4r/
│   └── ...
├── include/
├── tools/
├── config/
│   ├── splits.txt       # All functions defined
│   └── symbols.txt      # Complete symbol list
├── orig/
│   └── GMPE01/          # USA version (primary)
├── build/
├── configure.py
├── objdiff.json
├── PROGRESS.md          # Shows 100%
└── README.md
```

---

## 🔧 Toolchain Requirements

Same as other GameCube projects.

**Note**: Being complete means all code is available and matching. The repository is stable; no more active development (except maybe bug fixes and port work).

---

## 🚀 Getting Started (For Understanding)

Even though it's complete, you can still learn:

1. **Clone**:
   ```bash
   git clone https://github.com/mariopartyrd/marioparty4.git
   cd marioparty4
   ```

2. **Build**:
   ```bash
   python configure.py
   ninja
   ```

3. **Explore**:
   - Read the complete source to understand GameCube patterns
   - Study how they solved matching for 100% of functions
- See how minigames are structured as separate modules
   - Use as reference for other party games (Mario Party 5-8)

4. **Porting**: A PC port is already in development (likely using the Animal Crossing/Sunshine porting strategies).

---

## 🎯 Completion Notes

### What "100% Complete" Means

- ✅ Every function in the binary has been decompiled
- ✅ All functions match byte-perfect (objdiff shows 0% diff)
- ✅ All symbols identified and named
- ✅ Build system produces identical DOL
- ✅ Code is well-organized and documented

### What It Doesn't Mean

- ❌ Not all comments are present (some functions lack documentation)
- ❌ Not all variable names are perfect (some are still generic)
- ❌ Not all inline functions are matched (may be marked Equivalent)
- ❌ Asset extraction still needs work (but code handles all assets)

---

## 🎮 Porting Efforts

**Status**: A PC port is already in development by community members.

**Approach**: Likely follows the PAL strategy (see PORTING/strategies.md):
- Implement GX → OpenGL wrapper
- Implement AX → SDL/miniaudio
- Replace DVD → std::filesystem
- Keep game logic unchanged

**Result**: Native PC version of Mario Party 4, potentially with online multiplayer!

---

## 📚 Lessons Learned

### What Made This Successful?

According to community discussions:
1. **Modular design** - Minigames isolated, easy to complete one at a time
2. **Reasonable size** - ~6,000 functions (smaller than Melee's 11,700+)
3. **Clear ownership** - One team coordinated efforts, no conflicts
4. **Steady progress** - Consistent contributors over 3-4 years
5. **Dedication** - Several contributors spent significant time

### Challenges Overcome

- Minigame-specific optimizations (some were tough to match)
- Board loading/unloading (archive handling)
- Audio synchronization (minigame music timing)
- Memory constraints (original used multiple heaps)

---

## 🔗 Related Projects

- **Mario Party 5-8**: Not yet started but likely next
- **Mario Party 9** (Wii): Probably similar structure
- **Super Mario Party** (Switch): Different era, likely not soon
- **Mario Party remasters**: Could be based on this decomp

---

## 📈 Timeline

| Year | Milestone |
|------|-----------|
| 2021 | Project begins |
| 2022 | ~30% complete |
| 2023 | ~60% complete |
| 2024 | ~90% complete |
| 2025 | **100% complete** |

---

## 🆘 Getting Help (While Learning)

Even though project is done, you can still:
- Ask about techniques used (in Discord)
- Read commit history to see how functions were matched
- Study the codebase as a reference for other projects
- Contribute to the PC port (if separate repo exists)

---

## 🎯 Why This Matters

**Historic significance**:
- First complete GameCube decompilation
- Proves full matching is possible for GC titles
- Opens the door for ports, mods, and preservation
- Demonstrates community can tackle large projects

**For the community**:
- Can now create Mario Party 4 PC native port
- Can add online multiplayer, quality-of-life improvements
- Can translate to other languages easily
- Can create mods, cheat codes, custom minigames

---

## 📊 Comparison with Other Complete Decomps

| Game | Platform | Completion | Year |
|------|----------|------------|------|
| Mario Party 4 | GameCube | 100% | 2025 |
| Twilight Princess | GameCube/Wii | 100% | 2024? |
| Animal Crossing | GameCube | 99.52% | 2025 |
| Pikmin | GameCube | 99.17% | 2025 |
| N64 Emulator for GC | GameCube | 100% | ? |

Mario Party 4 is the **first** to reach 100% (or among the first). Twilight Princess may have also reached 100% according to decomp.dev.

---

## 🏆 Credits

See `CREDITS.md` (if exists) or GitHub contributors.

**Major contributors** likely include the `mariopartyrd` team and many individual helpers from the broader decomp community.

---

## 📝 Special Notes

- **Multiple versions**: The USA versions (both revisions) are fully matching. Other regions may differ slightly.
- **Licensing**: Check the repository's license - likely CC0 or MIT.
- **Assets**: Game assets (textures, sounds) are not included; you need your own ISO.
- **Porting**: The PC port may be a separate repository; search GitHub for `marioparty4-port` or similar.

---

*Last updated: March 2025 (based on web search)*

*Congratulations to the team on this monumental achievement!* 🎉🎉🎉