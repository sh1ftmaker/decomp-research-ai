# Toolchain Overview: The Modern GameCube/Wii Decompilation Stack

*What tools you need, how they fit together, and what each one does.*

---

## 🎯 The Big Picture

```
Your Game ISO
      ↓
[Dolphin Emulator] ──→ Extract → filesystem/ (orig/)
      │
      └──→ Debugging → Game analysis
             ↓
    [decomp-toolkit] (configure.py) → Generate configs, split DOL
             ↓
         .o files + .s files
             ↓
      [Ghidra] ──→ Disassemble → Understand functions
             │           ↓
             │       [m2c] ──→ Generate C code
             ↓
      [objdiff] ←──────── Compare ← Recompile (Ninja)
             ↓
      Iterate until match!
```

---

## 📦 Core Toolchain Components

### 1. **decomp-toolkit (dtk)** ⭐ Primary Workhorse

**Purpose**: All-in-one toolkit for analyzing, splitting, and managing GameCube/Wii binaries

**Language**: Rust (99.7%)
**License**: Apache-2.0 / MIT dual
**Maintainer**: encounter
**Installation**: Single binary download from GitHub releases

**Key Commands**:

| Command | Purpose | Example |
|---------|---------|---------|
| `dtk dol config <main.dol>` | Generate project configuration | `dtk dol config orig/GMSJ01/sys/main.dol` |
| `dtk dol split <config.yml>` | Split DOL into .o files | `dtk dol split config.yml` |
| `dtk vfs ls <container>` | List nested archives | `dtk vfs ls disc.rvz:files/RELS.arc` |
| `dtk demangle <symbol>` | Demangle CodeWarrior C++ | `dtk demangle 'BuildLight__9CGuiLightCFv'` |
| `dtk rel merge` | Merge DOL+RELs→ELF | For Ghidra analysis |
| `dtk elf disasm` | Disassemble ELF files | Inspect generated code |
| `dtk yaz0 compress/decompress` | Handle Nintendo compression | Common format for in-game files |

**Why it's essential**:
- Eliminates dependency on devkitPPC (old, hard-to-setup toolchain)
- Handles complex DOL/REL splitting automatically
- Built-in knowledge of Metrowerks/CodeWarrior conventions
- Virtual file system for nested archives (ISO→ARC→REL)
- Generizes `configure.py` template for new projects

**Project Template**: `dtk-template` repo (recommended starting point)

---

### 2. **objdiff** ⭐ Verification Engine

**Purpose**: Compare compiled object files to target binary, show differences

**Language**: Rust (99.9%)
**License**: Apache-2.0 / MIT dual
**Maintainer**: encounter
**Integration**: Works automatically with project `objdiff.json`

**Key Features**:
- GUI + CLI modes
- Automatic rebuild on file changes (filesystem watching)
- Symbol demangling (CodeWarrior, GCC, MSVC)
- Interactive diff viewer with hex/assembly/IR views
- Function-level matching percent
- WebAssembly API for web interfaces

**Workflow**:
1. Run your build → produces `build/src/foo.o`
2. objdiff compares against `build/asm/foo.o` (target)
3. Shows differences in instruction encoding, sections, data
4. Click through to see exactly which bytes differ

**Critical Settings**:
- **"Relax relocation diffs"**: Allows same instruction with different relocation target (common when linking order changes)
- **Watch patterns**: `*.c`, `*.cpp`, `*.h`, `configure.py`, `splits.txt`, `symbols.txt`
- **Custom make**: Usually `ninja` or `make`

**Installation**: Download prebuilt binary OR `cargo install objdiff-gui`

---

### 3. **m2c** ⭐ Decompiler

**Purpose**: Convert PowerPC assembly → C code designed for matching decompilation

**Language**: Python
**License**: GPL-3.0
**Author**: matt-kempster
**Supported Platforms**: MIPS, PowerPC (GameCube/Wii), ARM (GBA/DS)

**Targets**:
- `ppc-mwcc-c` (Metrowerks CodeWarrior for GameCube/Wii)
- `mips-ido-c` (SGI IDO for N64/PS1)
- `arm-gba` (GBA)
- `arm-eabi` (DS)

**Key Options**:

```bash
# Basic usage
m2c.py -t ppc-mwcc-c -f function_name assembly.s

# With context for types/structs
m2c.py -t ppc-mwcc-c -f foo -context types.h assembly.s

# Primitive modes if output is weird
m2c.py --gotos-only -t ppc-mwcc-c assembly.s
m2c.py --no-andor -t ppc-mwcc-c assembly.s
m2c.py --no-switches -t ppc-mwcc-c assembly.s
```

**Special Features**:

- **Struct inference**: Auto-fills `struct { int unk_0; }` based on usage
- **Context caching**: `.m2c` files speed up repeated runs
- **Visualization**: `--visualize` generates SVG control flow graphs
- **Stack frame templates**: `--stack-structs` outputs frame layouts
- **DWARF support**: Can read debug info when available

**Limitations**:
- Partial C++ support (needs manual cleanup of classes/inheritance)
- No automatic loop detection in some edge cases
- Best results with clean, well-annotated assembly

**Online Version**: simonsoftware.se/other/m2c.html (for quick tests)

---

### 4. **Ghidra** (Optional but Highly Recommended)

**Purpose**: Disassembler + decompiler + analysis suite

**Official**: NSA's open-source reverse engineering platform
**Why useful for game decomp**:
- Powerful interactive analysis
- Shared Ghidra servers (decomp projects run them)
- Type recovery and struct building
- Scripting in Python/Java
- Export functions to m2c format

**GameCube/Wii Specific**:
- PPC (PowerPC) Big Endian architecture
- Load Dolphin SDK types (many projects provide `.json` type archives)
- Shared servers: `ghidra.decomp.dev` (zeldaret Wind Waker server, etc.)

**Typical Workflow**:
1. Import `main.dol` (or merged ELF from `dtk rel merge`)
2. Analyze (auto-detect PPC, Big Endian)
3. Load type archives for known SDK structs
4. Rename functions, define structs
5. Export decompilation, clean up in m2c

**Note**: Ghidra's own decompiler is not used for matching - use m2c instead. But Ghidra is invaluable for understanding code structure.

---

### 5. **Dolphin Emulator** (Essential)

**Purpose**: GameCube/Wii emulator with crucial decompilation features

**Why you need it**:
- **Asset extraction**: Extract `sys/main.dol` and `*.rel` files from ISOs
- **Debugging**: Set breakpoints, inspect memory, trace execution
- **Symbol maps**: Some games include debug symbols (RTTI, map files)
- **Testing**: Verify your rebuilt DOL runs identically

**Feature**: Right-click game in Dolphin → **Properties** → **Filesystem** → **Export** to extract `sys/` directory

**Build Debug Version**:
Some projects need Dolphin built with debugging features (memory breakpoints). Follow project-specific instructions.

---

### 6. **Build System: Python + Ninja**

Every modern decomp project uses this standard setup:

**`configure.py`**:
- Generates `objdiff.json` with all object unit definitions
- Creates `build/` directory structure
- Sets up compiler flags (CodeWarrior-compatible via `wibo`)
- Handles version-specific configurations

**`Ninja`**:
- Fast, minimal build system
- Called as `ninja` from command line
- Incremental builds (only rebuilds changed files)
- Uses `build.ninja` generated by `configure.py`

**`wibo`** (Win32 binary wrapper):
- Minimal wrapper to run 32-bit Windows tools on Linux/macOS
- Automatically downloaded/used by `configure.py` on non-Windows
- Provides CodeWarrior-compatible environment on non-Windows

**Standard Commands**:
```bash
# First time setup
git clone https://github.com/project/repo.git
cd repo
python configure.py                    # Generates build files
ninja                                 # Builds everything

# For changes
python configure.py                    # Update config if needed
ninja                                 # Rebuild affected files
```

---

## 🛠️ Environment Setup by OS

### Windows (Recommended)

All projects **strongly recommend** native Windows (not WSL):

```powershell
# 1. Install Python 3.11+ from python.org
# Add to PATH, verify: python --version

# 2. Install Ninja
pip install ninja

# 3. Download objdiff
#   - From https://github.com/encounter/objdiff/releases
#   - Extract to C:\objdiff\ or add to PATH

# 4. Download decomp-toolkit (optional, configure.py can auto-download)
#   - From https://github.com/encounter/decomp-toolkit/releases
#   - Add to PATH as 'dtk'

# 5. Install Ghidra (optional but recommended)
#   - Download from https://ghidra-sre.org/
#   - Extract, run ghidraRun.bat

# 6. Install Dolphin Emulator
#   - From https://dolphin-emu.org/download/
#   - Use for asset extraction and testing
```

**Why not WSL?**:
- objdiff's filesystem watcher doesn't work reliably across WSL/Windows boundary
- Build performance is worse
- Some Windows-only tools (CodeWarrior compatibility layers) need native Windows

---

### macOS

```bash
# 1. Install prerequisites with Homebrew
brew install ninja python

# 2. Install Wine Crossover (needed for 32-bit toolchain)
brew install --cask --no-quarantine gcenx/wine/wine-crossover

# If macOS blocks Wine after upgrade:
sudo xattr -rd com.apple.quarantine '/Applications/Wine Crossover.app'

# 3. Install objdiff (download .dmg or build from source)
# 4. Install Dolphin (native macOS build)
# 5. Install Ghidra (works on macOS)
```

---

### Linux

```bash
# Ubuntu/Debian:
sudo apt-get install python3 python3-pip ninja-build

# For x86_64: wibo is auto-downloaded
# For non-x86 (ARM): install Wine
sudo apt-get install wine

# Then same objdiff, Dolphin, Ghidra installation
```

**Note**: Most projects are tested thoroughly on Windows, less so on macOS/Linux. Windows is the primary development platform.

---

## 🔄 Full Workflow Example: First Contribution

Let's trace through decompiling one function in Super Mario Sunshine:

```
1. CLONE & SETUP
   git clone https://github.com/doldecomp/sms.git
   cd sms
   Copy your Sunshine ISO to orig/GMSJ01/

2. INITIAL CONFIGURE
   python configure.py
   → Creates objdiff.json, build directories
   → Splits DOL into hundreds of .o files

3. OPEN OBJDIFF
   Launch objdiff, set project directory to sms/
   Left panel: List of all object units
   Find something small: src/pe/d/aie/d_aie_eai.c (an AI enemy)

4. IDENTIFY TARGET FUNCTION
   In objdiff: Click unit → See assembly target (build/asm/...)
   Note: It's currently "Non-Matching" (red)

5. ANALYZE IN GHIDRA (optional but helpful)
   dtk rel merge                    # Create merged ELF
   Open in Ghidra → Analyze → Find function
   Understand structure, calling conventions

6. DECOMPILE WITH M2C
   python tools/decomp.py d_aie_eai_init  # Decompile specific function
   → Creates/updates src/pe/d/aie/d_aie_eai.c

7. ITERATE
   Save file → objdiff auto-rebuilds
   objdiff shows diff: "57 instructions differ"
   → Tweak C code to match assembly better
   → Try different m2c options
   → Manual adjustments (switch statements, ternary ops)

8. ACHIEVE MATCH
   objdiff shows: "0 differences" ✅
   Run ninja → Full build still passes
   Update splits.txt status: "Matching"

9. COMMIT & PR
   git commit -m "d_aie_eai: Decompile and match init function"
   git push
   Open PR on GitHub following CONTRIBUTING.md
```

**Time estimate**: First function (learning curve): 2-4 hours. Subsequent functions: 30min-2hr each depending on complexity.

---

## 📚 Toolchain Evolution

### Legacy (Pre-2020)
- Manual assembly splitting (painful)
- Custom Makefiles, devkitPPC dependency
- No automated diffing (manual hex comparison)
- Fragmented tools

### Modern (2020-2023)
- `decomp-toolkit` introduced (standardized splitting)
- `objdiff` created (automated verification)
- `m2c` matured (good CodeWarrior support)
- `wibo` eliminated Linux/macOS pain points
- Standardized project templates

### Current (2024-2025)
- All major projects migrated to dtk + objdiff
- VS Code integration (objdiff extension)
- `decomp-permuter` for register allocation issues
- `decomp.me` web-based collaborative platform
- Shared Ghidra servers for community analysis
- CI/CD integration (GitHub Actions for verification)

---

## 🤔 Choosing the Right Tool for Each Task

| Task | Primary Tool | Supporting Tools |
|------|--------------|------------------|
| Extract game files from ISO | Dolphin Emulator | dtk vfs |
| Understand binary layout | dtk dol info | Ghidra |
| Split DOL into .o files | dtk dol split | configure.py |
| Generate initial config | dtk dol config / configure.py | dtk |
| Disassemble for analysis | Ghidra | dtk rel merge |
| Generate C from asm | m2c.py | custom scripts |
| Verify matching | objdiff (GUI/CLI) | ninja builds |
| Automate builds | Ninja + configure.py | Python |
| Register allocation issues | decomp-permuter | m2c options |
| Collaborative scratch work | decomp.me | objdiff-web |
| Compression formats | dtk yaz0/yay0/nlzss | — |

---

## 🔧 Advanced Tools (Less Common)

- **decomp-permuter**: Tries permutations of register allocation to match
- **asm-differ**: Older diff tool (mostly superseded by objdiff)
- **splat**: Splatting tool for N64 (different ecosystem)
- **ret-dec**: Generic decompiler (not for matching)
- **IDA Pro**: Commercial alternative to Ghidra (rarely used in this community)

---

## 🎓 Learning Resources by Tool

- **decomp-toolkit**: [GitHub README](https://github.com/encounter/decomp-toolkit) + [dtk-template](https://github.com/encounter/dtk-template)
- **objdiff**: [GitHub README](https://github.com/encounter/objdiff) + [video tutorials](https://www.youtube.com/watch?v=...)
- **m2c**: [GitHub README](https://github.com/matt-kempster/m2c) + [online demo](https://simonsoftware.se/other/m2c.html)
- **Ghidra**: [Official tutorials](https://ghidra-sre.org/) + [zeldaret TWW guide](https://github.com/zeldaret/tww/blob/main/docs/decompiling.md)
- **Dolphin**: [Official docs](https://dolphin-emu.org/docs/) + [debugging guide](https://mintlify.com/dolphin-emu/dolphin/contributing/debugging)

---

## 🐛 Common Issues & Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| objdiff doesn't auto-rebuild | Filesystem watcher failed | Restart objdiff, check `objdiff.json` watch_patterns |
| `wibo` download fails | Network issue, missing ca-certificates | Download manually from GitHub releases |
| Build fails: " unrecognized opcode" | Wrong compiler flags | Check `configure.py` uses correct CodeWarrior flags |
| m2c generates garbage | Wrong target or missing context | Use `-t ppc-mwcc-c` and provide `.h` files |
| Cannot link: undefined reference | Missing SDK function | Check if function is in doldecomp/sdk_* repos |
| Ghidra can't find symbols | Load wrong file | Use `dtk rel merge` output, not raw DOL |
| Different object sizes | Splitting mismatch | Rerun `dtk dol split` with updated config |

See [CHALLENGES/](CHALLENGES/) for detailed problem-solving guides.

---

## 📈 The Toolchain in Numbers

- **decomp-toolkit**: ~15,000 lines of Rust
- **objdiff**: ~12,000 lines of Rust (GUI + CLI)
- **m2c**: ~8,000 lines of Python
- **Total downloads**: 100,000+ across all tools
- **Active users**: 500+ contributors across all projects
- **Build times**: Small object (1-10s), full project (1-5min on modern CPU)

---

*This document synthesizes information from tool READMEs, project documentation, and community wiki pages.*
*For tool-specific questions, consult the official repositories.*