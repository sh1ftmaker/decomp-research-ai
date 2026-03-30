# [GAME NAME] Decompilation Status and Notes

*Comprehensive reference for [Game]* decompilation project

---

## 📊 Project Overview

| Attribute | Value |
|-----------|-------|
| **Full Title** | [Game Name] |
| **Game ID** | `GAMEID` (e.g., `GALE01`, `GMSJ01`) |
| **Platform** | GameCube / Wii |
| **Primary Repository** | https://github.com/[org]/[repo] |
| **Discord Server** | [invite link] |
| **Active Since** | Year |
| **Current Completion** | X% (as of DATE) |
| **Primary Language** | C / C++ mix |
| **SDK Used** | Dolphin SDK [version], JSystem [version] |
| **Architecture** | PowerPC 750CL (Broadway) |

---

## 🎯 Quick Status

- **Decompilation progress**: [~X%](https://github.com/[org]/[repo]/blob/main/PROGRESS.md)
- **Build status**: ✅ Builds successfully / ⚠️ Partial / ❌ Fails
- **Matching**: [N] of [M] functions matching
- **Last major milestone**: [e.g., "All actors matching" or "Entry point decompiled"]
- **Recommended for newcomers**: Yes/No (reason)

---

## 🏗️ Architecture Highlights

### Engine Components

| System | Implementation | Notes |
|--------|----------------|-------|
| **Physics** | [Name] (custom / Bullet / etc) | [Details] |
| **Audio** | [AXUniversal / JAudio2] | [APR/ADPCM formats] |
| **Graphics** | [GX / custom] | [Shader model, tev stages] |
| **File I/O** | [DVD / RARC / YAZ0] | [Archive formats] |
| **Memory** | [JKRHeap / JKRExpHeap] | [Allocator types] |
| **Threading** | [OSThread] | [Preemptive, priorities] |
| **Math** | [JSystem Math Library] | [Matrix, vector types] |

### Notable Libraries

- **JSystem**: Version [X.Y], includes `JKR`, `JUT`, `J3D`, `JGI`, `JAudio`
- **Dolphin SDK**: Components used: [DX, GD, GX, VI, PAD, etc.]
- **Custom**: [list any game-specific libraries]

---

## 📁 Repository Structure

```
[repo]/
├── src/                    # Decompiled C/C++ source
│   ├── dolphin/           # Dolphin SDK layer
│   ├── JSystem/           # JSystem library
│   ├── pe/                # "Program Executable" (actors, game logic)
│   └── nw4r/              # Nitro/Express (if used)
├── include/                # Header files
├── tools/                  # Decompilation scripts (decomp.py, etc.)
├── config/                 # Build configuration
├── orig/                   # Game assets (ISO or extracted filesystem)
├── build/                  # Build output (gitignored)
├── configure.py           # Build configuration script
├── objdiff.json           # objdiff configuration
└── README.md              # Project-specific instructions
```

---

## 🔧 Toolchain Requirements

| Tool | Version | Notes |
|------|---------|-------|
| **decomp-toolkit** | ≥0.x.x | Auto-downloaded by configure.py |
| **objdiff** | ≥0.x.x | GUI or CLI |
| **m2c** | Latest | Python, `ppc-mwcc-c` target |
| **Python** | 3.11+ | For configure.py and tools |
| **Ninja** | 1.10+ | Build system |
| **Ghidra** | 10.x+ | Optional but recommended |
| **Dolphin** | Latest | For asset extraction |

**Compiler**: CodeWarrior compatible via `wibo` (Windows) or Wine (macOS/Linux)

---

## 🚀 Getting Started (Game-Specific)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/[org]/[repo].git
   cd [repo]
   git submodule update --init --recursive  # if applicable
   ```

2. **Prepare game assets**:
   - Copy your [Game] ISO to `orig/[GAMEID]/`
   - Or extract with Dolphin: Right-click game → Properties → Filesystem → Export `sys/`
   - Ensure `orig/[GAMEID]/sys/main.dol` exists

3. **Configure**:
   ```bash
   python configure.py
   ```
   This will:
   - Run `dtk dol config` to analyze the binary
   - Generate `objdiff.json` with all object definitions
   - Create `build.ninja`

4. **Build**:
   ```bash
   ninja
   ```
   First build will take 1-5 minutes depending on CPU.

5. **Open objdiff**:
   ```bash
   objdiff
   ```
   Set project directory to repository root. See list of objects.

6. **Find your first task**:
   - Check `CONTRIBUTING.md` for "easy" labels
   - Sort objdiff by diff size (smallest first)
   - Look in `#newcomers` Discord channel

---

## 🎯 Known Challenges (Game-Specific)

### Challenge 1: [Name]

**Description**: [What's hard about this game?]

**Example**: The game uses an unusual RTTI format that confuses m2c.

**Workaround**: [Steps to work around it]

**Status**: [Resolved / Ongoing]

---

### Challenge 2: [Name]

**Description**: [e.g., "Heavy C++ with complex inheritance" or "Custom file format not in dtk" ]

**Workaround**: [Solutions]

**Related**: See [other game] for similar pattern.

---

### Challenge 3: [Name]

**Description**: [e.g., "Missing debug symbols; no map files available" ]

**Impact**: Symbol discovery is harder, relies on pattern matching.

**Mitigation**: Use shared SDK knowledge from other projects.

---

## 📈 Progress Tracking

**Official progress**: Usually tracked in:
- `PROGRESS.md` at repo root
- GitHub projects board
- Website [decomp.dev](https://decomp.dev) (auto-updated)

**Completion by module**:

| Module | Functions | Matched | % |
|--------|-----------|---------|---|
| Core (dolphin) | 500 | 500 | 100% |
| JSystem | 1200 | 850 | 71% |
| Actors | 3000 | 900 | 30% |
| ... | ... | ... | ... |
| **Total** | [N] | [M] | [X%] |

---

## 🎮 Common Contribution Areas

### For Beginners

- ✅ Small utility functions (<20 instructions)
- ✅ Data-only objects (tables, arrays)
- ✅ Actor `create` methods (often simple)
- ✅ SDK wrapper stubs (if missing)
- ✅ Inline functions (with guidance)

### For Intermediate

- ⚠️ Complete actors (all methods in one `.c` file)
- ⚠️ Library functions (JSystem, JAudio)
- ⚠️ Complex switch statements

### For Experts

- 🔥 C++ inheritance chains (vtable reconstruction)
- 🔥 Custom assembly routines (vectorized, DSP)
- 🔥 Inline function web (hundreds of call sites)
- 🔥 `Equivalent` status justification

---

## 📚 Game-Specific Resources

### Articles & Guides

- [Project Wiki](https://github.com/[org]/[repo]/wiki)
- [Decompilation Guide](https://github.com/[org]/[repo]/blob/main/docs/decompiling.md)
- [Architecture Overview](https://github.com/[org]/[repo]/blob/main/docs/architecture.md)

### Videos

- [YouTube playlist](https://youtube.com/playlist?list=...): Decompilation walkthroughs
- Live streams: [Twitch channel] (if maintainers stream)

### Shared Knowledge

- **Ghidra server**: [host] (if project runs one)
- **Type archives**: [link to .json] (for Ghidra)
- **Map files**: [link to archive] (debug builds)

---

## 🐛 Notable Bugs / Gotchas

### Issue 1: [Brief Title]

**Symptom**: [objdiff shows weird diffs / build fails / etc]

**Cause**: [Root cause explanation]

**Solution**: [How to fix]

**Example**:
```c
// Before (doesn't match):
int foo(int x) {
    return x + 1;
}
// After (matches):
int foo(int x) {
    int temp = x;
    return temp + 1;  // variable order changes register allocation
}
```

---

### Issue 2: [Brief Title]

**Symptom**: ...

---

## 🔄 Dependencies on Other Projects

This project shares code with:

| Game | Shared Components | Shared % |
|------|-------------------|----------|
| [Game A] | `dolphin/source/export`, `JSystem/JKernel` | 40% |
| [Game B] | `JAudio`, `J3D` | 25% |

**Implication**: Progress in [other project] helps this one. Coordinate with those maintainers.

---

## 📞 Contact & Support

- **Discord**: `#game-name` channel in main server
- **GitHub Issues**: For bugs, feature requests, questions
- **Matrix/IRC**: [if any]
- **Email**: [maintainer email]

**Before asking**:
1. Search existing issues (likely already answered)
2. Read this README and project wiki
3. Check `CONTRIBUTING.md`

**When asking**:
- Include project name, game ID, your OS
- Include error message (full text)
- Include what you tried
- Screenshots (objdiff, build output) help

---

## 📜 License

This project's decompiled code is under [license]. Typically:
- Decompilation itself: No license (all rights reserved by Nintendo)
- Original code: Copyright Nintendo
- Modified/added code: MIT/Apache 2.0/CC0 (per project)

**Check** `LICENSE` file in repository.

**You** may:
- View and learn
- Contribute improvements
- Create ports (see PORTING/)
- Not redistribute original assets

---

## 🎉 Acknowledgments

- **Original developers**: Nintendo, HAL Laboratory, etc.
- **Decompilation team**: [list major contributors]
- **Tool authors**: encounter (dtk, objdiff), matt-kempster (m2c)
- **Community**: All the Discord helpers

---

## 📝 Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-03-29 | Initial document | Hermes |
| ... | ... | ... |

---

*Last updated: [DATE]*

*For the most current status, check the project's main repository.*