# Getting Started: Your First Decompilation Contribution

*A practical, hands-on guide for newcomers to GameCube/Wii decompilation*

---

## 🎯 Pre-Checklist: Are You Ready?

Before diving in, ensure you have:

✅ **Legal game copy**: You must own the game you want to decompile (dumped from your own disc/console)
✅ **Time commitment**: First contribution ~4-8 hours (setup + learning)
✅ **Patience**: Decompilation is meticulous, like "unbaking a cake"
✅ **Curiosity**: Willing to learn PowerPC, C, and reverse engineering
✅ **Community respect**: Will follow project guidelines and codes of conduct

---

## 📦 Step 1: Choose Your Game

**Criteria for First Game**:
- **Size**: Small to medium (under 3MB code)
- **Language**: Mostly C (not heavy C++)
- **Progress**: 10-40% decompiled (plenty of easy tasks left)
- **Documentation**: Active wiki, clear contribution guide
- **Community**: Active Discord, helpful maintainers
- **Personal interest**: You actually like the game!

### Recommended Starter Games

| Game | Platform | Why It's Good for Beginners | Current Progress | Discord |
|------|----------|---------------------------|------------------|---------|
| **Luigi's Mansion** | GameCube | Small, well-documented, many foundational tasks | ~7% | [discord.gg/hKx3FJJgrV](https://discord.com/invite/hKx3FJJgrV) |
| **Paper Mario: TTYD** | GameCube | Good documentation, clear actor structure | ~10% | Same as above |
| **Mario Party 4** | GameCube | Already 100% - great for learning without pressure | Complete | - |
| **F-Zero GX** | GameCube | Mid-size, interesting challenges, active | ~25% | zeldaret server |
| **Metroid Prime** | GameCube | Excellent documentation, but larger | ~35% | PrimeDecomp server |
| **Kirby Air Ride** | GameCube | Small, simple, good first project | ~40% | doldecomp server |

**Avoid for Now**: Melee (too big/complex), Sunshine (C++ heavy), Zelda games (many already partially done by experts)

---

## 💻 Step 2: Environment Setup

### A. Windows Setup (Recommended)

Most projects assume Windows. Here's the exact install order:

1. **Install Python 3.11+**
   - Download from python.org (not Microsoft Store!)
   - During install: ✓ Add Python to PATH
   - Verify: Open PowerShell → `python --version` → shows version

2. **Install Git**
   - Download from git-scm.com
   - Use defaults, but select "Git Bash Here" and "Git GUI Here"
   - Verify: `git --version`

3. **Install Ninja**
   ```powershell
   pip install ninja
   ```
   Or download from [ninja-build.org](https://ninja-build.org/) and add to PATH

4. **Install Visual Studio Build Tools** (optional but helpful)
   - Download [Build Tools for Visual Studio](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio)
   - Select "Desktop development with C++" (for C compiler)

5. **Download objdiff**
   - Go to [objdiff releases](https://github.com/encounter/objdiff/releases)
   - Download `objdiff-x86_64-pc-windows-msvc.zip`
   - Extract to `C:\objdiff\` (or somewhere on PATH)
   - Test: Open Command Prompt → `objdiff --version`

6. **Download Dolphin Emulator**
   - From [dolphin-emu.org](https://dolphin-emu.org/download/)
   - Install normally
   - Test: Launch Dolphin, configure controller

7. **Install Ghidra** (Optional but recommended)
   - Download from [ghidra-sre.org](https://ghidra-sre.org/)
   - Extract (portable), run `ghidraRun.bat`

8. **Prepare Your Game Disc Image**
   - Must have original GameCube/Wii disc
   - Rip with CleanRip (homebrew) or similar
   - Formats accepted: ISO, GCM, RVZ, WIA, WBFS, CISO
   - Keep it safe (you'll need it for builds)

---

### B. macOS Setup

```bash
# 1. Homebrew (if you don't have it)
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Prerequisites
brew install python3 ninja

# 3. Wine Crossover (for 32-bit Windows tools)
brew install --cask --no-quarantine gcenx/wine/wine-crossover

# 4. If macOS complains about Wine:
sudo xattr -rd com.apple.quarantine '/Applications/Wine Crossover.app'

# 5. objdiff, Dolphin, Ghidra as above
```

---

### C. Linux Setup (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip git ninja-build

# For x86_64: wibo auto-downloaded
# For ARM/other: install wine
sudo apt-get install wine

# Then objdiff, Dolphin, Ghidra
```

---

## 🎮 Step 3: Pick a Project & Clone

### Example: Luigi's Mansion

```bash
# Navigate to your workspace (usually Desktop)
cd ~/Desktop

# Clone the repository
git clone https://github.com/Moddimation/zmansion.git
cd zmansion

# Or one of the active ones:
git clone https://github.com/doldecomp/melee.git --depth=1
```

**Clone with `--depth=1`** if you don't need full history (saves space, faster).

---

## 💾 Step 4: Prepare Game Assets

1. **Locate your game ISO** (e.g., `Luigi's Mansion (USA).iso`)
2. **Copy to project's `orig/` directory**
   - The directory name must match the game ID (e.g., `GLME01`, `GMSJ01`)
   - Look in `configure.py` or README to find the correct ID

```
Example structure:
zmansion/
├── orig/
│   └── GLMJ01/              ← Game ID (Japanese)
│       └── sys/
│           └── main.dol      ← Will be auto-extracted
├── src/
├── include/
└── configure.py
```

3. **If your `orig/` doesn't have `sys/main.dol`**, use Dolphin to extract:
   - Open Dolphin → Games → Right-click Luigi's Mansion → **Properties**
   - Go to **Filesystem** tab → Right-click `sys/` → **Export**
   - Copy exported `sys/` folder to `orig/GLMJ01/`

---

## 🔧 Step 5: Initial Configuration

```bash
# Make sure you're in the project root
python configure.py
```

**What this does**:
- Scans your game ISO in `orig/[GAMEID]/`
- Runs `dtk dol config` to analyze the binary structure
- Creates `objdiff.json` with all object definitions
- Generates `build/` directory and `build.ninja`
- Extracts any REL files if present

**Troubleshooting**:
- `Error: dtk not found`: Download `dtk.exe` and put in PATH, or it auto-downloads
- `No such file or directory: orig/...`: Check your game folder structure
- `Unsupported version`: You have wrong region; check README for supported versions

---

## 🏃 Step 6: First Build

```bash
ninja
```

**Expected output**:
```
[1/500] Building C object src/...
[2/500] Building C object src/...
...
[500/500] Linking build/recompiled.dol
```

**Success criteria**:
- Build completes without errors
- `build/recompiled.dol` is created (byte-for-byte matching WILL NOT happen yet)
- Most objects will be "NonMatching" - that's expected!

**If build fails**:
- Check error message (missing SDK functions? Out of memory?)
- Some projects require submodules: `git submodule update --init --recursive`
- Ask in Discord (include full error log)

---

## 🔍 Step 7: Learn to Use objdiff

### Launch objdiff

```
# GUI mode (recommended for first time)
objdiff

# CLI mode
objdiff --headless --unit "actor/d_aie"
```

### First objdiff Session

1. **Set Project Directory**: File → Open → Select your project root folder
2. **Left Panel**: List of all object units (thousands)
3. **Click any unit**:
   - Top pane: Recompiled assembly (from your C code)
   - Bottom pane: Target assembly (from original game)
   - Differences highlighted in red
   - Matching bytes shown in green
4. **Search**: Filter by filename to find something small (e.g., `ai` for enemy AI)

**Your first goal**: Find a *tiny* function to start with.

---

## 🔎 Step 8: Find an "Easy" Target

### Look for these signs:

✅ **Small function** (10-50 assembly instructions)
✅ **Already partially decompiled** (some `.c` file exists)
✅ **Non-matching but close** (only few differences)
✅ **No complex C++** (just plain C)
✅ **No inline functions** (simpler)

### Where to find tasks:

1. **GitHub Issues**: Look for "help wanted" or "easy object" labels
   - Example: https://github.com/doldecomp/melee/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22
2. **objdiff**: Sort by `Diff` column (smallest differences first)
3. **Discord**: Channels like `#easy-stuff` or `# newcomers`
4. **Project wikis**: Lists of actors by difficulty

---

## 🧩 Step 9: Decompile Your First Function

### The Iterative Process

**Step 9.1: Locate the assembly**

1. In objdiff, click your target unit (e.g., `src/pe/d/aie/d_aie_eai.c`)
2. Copy the **target assembly** (bottom pane) for the function you want
3. Save it as `temp.s` somewhere

**Step 9.2: Generate C with m2c**

```bash
# Basic m2c invocation
m2c.py -t ppc-mwcc-c -f function_name temp.s > temp.c

# With context (if types.h exists)
m2c.py -t ppc-mwcc-c -f function_name -context include/types.h temp.s > temp.c
```

**Step 9.3: Inspect the output**

```c
// Example m2c output (may be messy)
void function_name(void) {
  // m2c tries to convert GOTO-style PPC to C
  // You'll see: while(1) { switch(...) { ... } }
}
```

**Step 9.4: Integrate into project**

1. Open the actual source file: `src/pe/d/aie/d_aie_eai.c`
2. Add the new function at the appropriate location
3. Clean up: Remove unnecessary casts, fix formatting, match project style
4. Add any needed `#include`s

**Step 9.5: Build and check**

```bash
ninja                    # Rebuild
# objdiff should auto-refresh
```

**Step 9.6: Iterate if not matching**

Common fixes:
- Switch statement order? Use `m2c --no-switches` or check [SWITCHES guide](../CHALLENGES/switches.md)
- Ternary vs if/else? Try the other form
- Constants different? Check literal values in objdiff
- Register allocation different? See [REGALLOC guide](../CHALLENGES/register-allocation.md)
- Order of statements? Swap blocks, invert condition

**Repeat 9.2-9.6 until objdiff shows 0 differences for that function.**

---

## ✅ Step 10: Mark as Matching

Once a unit fully matches (all functions in that `.c` file):

1. **Update `configure.py` or `splits.txt`**
   - Most projects: Status is in `splits.txt` or a database
   - Change `NonMatching` to `Matching` for that file
   ```python
   # Example from zeldaret projects
   Status.add("d_aie_eai", status="Matching")
   ```
2. **Re-run configure** (if you changed status tracking):
   ```bash
   python configure.py
   ```
3. **Full rebuild**: `ninja clean && ninja`
4. **Verify no regressions**: objdiff should still show all green

---

## 📤 Step 11: Submit Your Contribution

### Common PR Pattern:

```bash
git add src/pe/d/aie/d_aie_eai.c
git add configure.py  # if status updated
git commit -m "pe/d_aie: Decompile d_aie_eai_init and d_aie_eai_init_attention"

# Detailed PR body example:
"""
## Changes
- Decompile and match d_aie_eai_init (20 lines) → 0 diff
- Decompile and match d_aie_eai_init_attention (35 lines) → 0 diff

## Testing
- Built successfully with ninja
- objdiff confirms 100% match for these functions
- No regressions in related units

## Notes
This is my first contribution. Feedback welcome!

Closes #1234  # (if issue existed)
"""
```

```bash
git push origin my-branch-name
# Then open PR on GitHub
```

### PR Checklist (before submitting):

- [ ] Follows project's code style (run `clang-format` if configured)
- [ ] Objdiff shows 0 diffs for modified functions
- [ ] Full project still builds (`ninja` succeeds)
- [ ] No new warnings/errors
- [ ] Commit message follows project conventions
- [ ] Linked to any relevant issue
- [ ] Ran any project-specific lint/check scripts

---

## 🎓 Step 12: Keep Learning

After your first function:

1. **Graduate to bigger functions** (100-200 instructions)
2. **Work on complete objects** (all functions in one `.c` file)
3. **Tackle complex constructs**:
   - C++ classes & inheritance
   - Switch statements with jump tables
   - Inline functions
   - Complex data structures
4. **Contribute to lower-level work**:
   - SDK function stubs
   - Library decompilation (JSystem, MusyX)
   - Data-only objects (tables, arrays)

---

## 🆘 Getting Help

### Before asking:

1. **Search existing documentation**: README, wiki, CONTRIBUTING.md
2. **Check closed PRs/issues**: Someone probably had your problem
3. **Google the error message**
4. **Re-read your steps**: Did you miss something obvious?

### Where to ask:

| Question Type | Best Channel |
|---------------|--------------|
| Setup issues | `#setup-help` or `#tech-support` |
| How to use a tool | `#tool-support` (objdiff, m2c, etc.) |
| Where to start | `#newcomers` or `#getting-started` |
| General decompilation questions | `#decompilation` |
| Game-specific questions | Game-specific channel (e.g., `#melee`, `#tww`) |
| Code review (before PR) | `#code-review` or ping maintainers |

**What to include in your question**:
- Project and game you're working on
- What you tried
- Error messages (full text)
- Screenshots if helpful (objdiff diff, build error)
- Your OS and tool versions

---

## 📚 What's Next?

After your first contribution:

- Read the **advanced guides** in this archive:
  - [The Matching Process](../WORKFLOW/matching-process.md)
  - [Common Challenges](../CHALLENGES/register-allocation.md)
  - [Verification Techniques](../WORKFLOW/verification.md)

- Explore the game-specific documentation for your chosen project
- Join the Discord and introduce yourself
- Check for "help wanted" issues regularly
- Consider becoming a regular contributor!

---

## ⚠️ Important Reminders

1. **Legal**: You must own a legitimate copy of the game
2. **No assets**: Do NOT commit any copyrighted game data (ISO, textures, sounds)
3. **No AI** (for most projects): Several projects ban AI-generated code; check guidelines
4. **Follow style**: Match existing code formatting exactly
5. **Be patient**: Reviews can take days/weeks; maintainers are volunteers
6. **Ask questions**: The community is friendly and helpful to newcomers!

---

## ✨ You're Ready!

You have:
- ✅ Tools installed
- ✅ Game assets prepared
- ✅ Project cloned and building
- ✅ Understanding of objdiff and m2c
- ✅ Know how to find easy tasks
- ✅ Know the contribution workflow

**Start small. Ask questions. Be persistent. Have fun!**

The first matching function is a huge milestone - celebrate it! 🎉

---

*Next guide: [The Matching Process](../WORKFLOW/matching-process.md) - Deep dive into byte-perfect matching techniques*

*Need help? Check the [Community Resources](../../COMMUNITY/websites.md)*