# GameCube & Wii Decompilation Research Repository

*A comprehensive knowledge base for GameCube and Wii game decompilation, covering tools, workflows, challenges, and project-specific information.*

---

## 📚 What's Inside

This repository consolidates everything you need to understand and contribute to GameCube/Wii decompilation efforts — **tribal knowledge** extracted from Discord, GitHub, wikis, and forums.

### Core Documentation

- **[TOOLS/overview.md](TOOLS/overview.md)** - Complete toolchain guide (dtk, objdiff, m2c, wibo, Ghidra)
- **[WORKFLOW/getting-started.md](WORKFLOW/getting-started.md)** - First-timers guide: from ISO extraction to first build
- **[WORKFLOW/matching-process.md](WORKFLOW/matching-process.md)** - Detailed methodology for byte-perfect matching
- **[CHALLENGES/](CHALLENGES/)** - Technical deep-dives into common issues:
  - [register-allocation.md](CHALLENGES/register-allocation.md) - The #1 matching problem
  - [inlines.md](CHALLENGES/inlines.md) - Handling inline functions
  - [switches.md](CHALLENGES/switches.md) - Jump tables and comparison trees
  - [tail-calls.md](CHALLENGES/tail-calls.md) - Silent optimizer trap
  - [symbols.md](CHALLENGES/symbols.md) - Finding function names via pattern recognition
  - [RTTI.md](CHALLENGES/RTTI.md) - Auto-generating C++ class hierarchies
- **[WORKFLOW/matching-playbook.md](WORKFLOW/matching-playbook.md)** - Step-by-step playbook for matching functions (empirical techniques for MWCC register allocation)
- **[AUTOMATION.md](AUTOMATION.md)** - Automated decompilation agent: architecture, pipeline, and findings from running it on Melee
- **[PORTING/strategies.md](PORTING/strategies.md)** - From matching decompilation to native PC ports (GX→OpenGL/Vulkan, HLE vs reimplementation)
- **[COMMUNITY/websites.md](COMMUNITY/websites.md)** - Essential hubs: decomp.dev, decomp.me, wikis, Discord servers

### Knowledge Gaps & Discord Content

⚠️ **Important**: This repository covers ~75% of needed knowledge from public sources. The remaining 25% lives in Discord servers.

See **[GAPS.md](GAPS.md)** for a detailed analysis of:
- What information is publicly available vs Discord-only
- 14 specific knowledge gaps (critical, significant, minor)
- Priority list for Discord extraction
- Search keywords to find hidden knowledge

**Bottom line**: You can get 70-75% of the way with these docs. The last 25% requires joining Discord and manually curating insights from conversations.

### Game-Specific Notes (12 Major Projects)

Each major project has a dedicated page with architecture diagrams, system breakdowns, current progress, and contribution guidance:

| Game | Platform | Decomp % | Linked % | Status |
|------|----------|----------|----------|--------|
| **[Super Smash Bros. Melee](GAMES/melee.md)** | GC | 61.28% | 33.74% | Most active (840⭐) |
| **[Super Mario Sunshine](GAMES/super-mario-sunshine.md)** | GC | 29.09% | 13.61% | Good for beginners |
| **[The Legend of Zelda: Twilight Princess](GAMES/twilight-princess.md)** | GC/Wii | **100%** | 87.13% | Historic 100% milestone |
| **[The Legend of Zelda: The Wind Waker](GAMES/zelda-tww.md)** | GC | 60.43% | 40.41% | Shares engine with TP |
| **[Super Mario Galaxy](GAMES/super-mario-galaxy.md)** | Wii | 46.62% | 18.83% | **Very active** (updated 3h ago) |
| **[Mario Kart: Double Dash!!](GAMES/mario-kart-double-dash.md)** | GC | 43.05% | 37.76% | Needs help |
| **[Animal Crossing](GAMES/animal-crossing.md)** | GC | 99.52% | 98.44% | Near-complete |
| **[Paper Mario: TTYD](GAMES/paper-mario-ttyd.md)** | GC | ~97%? | ~90%+? | Almost done |
| **[Pikmin](GAMES/pikmin.md)** | GC | 99.17% | 89.90% | Small codebase |
| **[Mario Party 4](GAMES/mario-party-4.md)** | GC | **100%** | **100%** | First complete GC game |
| **[Metroid Prime](GAMES/metroid-prime.md)** | GC | 35.63% | 18.67% | Very active |
| **[Luigi's Mansion](GAMES/luigi-mansion.md)** | GC | 7.02% | 6.53% | Recently revived |

Also included: **[GAMES/projects-overview.md](GAMES/projects-overview.md)** - Master table of all 76+ active projects across 8 console generations.

---

## 🎯 Who Is This For?

- **Newcomers** curious about GameCube/Wii decompilation
- **Contributors** wanting to understand the "why" behind workflows
- **Researchers** studying reverse engineering techniques
- **Port developers** planning to create PC versions

---

## 🚀 Quick Start

**Read** [TOOLS/overview.md](TOOLS/overview.md) to understand the toolchain
**Read** [WORKFLOW/offline-mode.md](WORKFLOW/offline-mode.md) if you can't use Discord or decomp.me
**Read** [WORKFLOW/getting-started.md](WORKFLOW/getting-started.md) for standard first steps
4. **Bookmark** [COMMUNITY/websites.md](COMMUNITY/websites.md) for help

---

## 📊 Active Projects Snapshot (March 2025)

**GameCube**: 29 active projects (6 ≥90%, 4 50-89%, 10 10-49%, 9 <10%)
**Wii**: 22 active projects (2 ≥90%, 3 50-89%, 11 10-49%, 6 <10%)
**N64**: 11 active projects (5 ≥90%, 3 50-89%, 3 10-49%, 1 <10%)

**Total tracked**: 76+ active projects across 8 console generations.

See [GAMES/projects-overview.md](GAMES/projects-overview.md) for the complete list.

---

## 🔧 Essential Tools (One-Liners)

```bash
# Install dtk (decomp-toolkit)
curl -sSf https://raw.githubusercontent.com/encounter/decomp-toolkit/main/install.sh | bash

# Install objdiff (GUI diff tool)
# Download from https://github.com/encounter/objdiff/releases

# Install m2c (decompiler)
pip install m2c

# Clone a project (example: Melee)
git clone https://github.com/doldecomp/melee.git
cd melee
python configure.py  # Sets up everything
ninja  # First build

# Open objdiff to see what's left to match
objdiff
```

See [TOOLS/overview.md](TOOLS/overview.md) for detailed installation and configuration.

---

## 🤝 Community Platforms

Most knowledge lives in Discord (not documented here due to access constraints):

- **doldecomp** - https://discord.gg/doldecomp (Melee, Sunshine, MKDD, etc.)
- **zeldaret** - https://discord.gg/zeldaret (Zelda series)
- **PrimeDecomp** - https://discord.gg/PrimeDecomp (Metroid Prime)
- **SMGCommunity** - (Galaxy) link in repo
- **decomp.dev** - https://decomp.dev/discord (meta discussion)

**See** [COMMUNITY/websites.md](COMMUNITY/websites.md) for full directory.

---

## 🎯 Matching vs Porting

**Matching**: Recreating C/C++ that compiles to **identical bytes** as original GameCube/Wii binary. This is the **decompilation** goal. Requires exact compiler (Metrowerks CodeWarrior via wibo/Wine) and precise code structure.

**Porting**: Taking matched source and modifying it to run on **PC (Windows/Linux/macOS)**. Requires creating platform abstraction layers (GX→OpenGL/Vulkan, audio, input). Covered in [PORTING/strategies.md](PORTING/strategies.md).

You can do **both**: First match on GameCube, then port to PC. Or port incrementally while matching.

---

## 📖 How to Use This Repository

### For Learning

Read in this order:
1. [TOOLS/overview.md](TOOLS/overview.md) - Understand the toolchain
2. [WORKFLOW/getting-started.md](WORKFLOW/getting-started.md) - Hands-on first steps
3. [WORKFLOW/matching-process.md](WORKFLOW/matching-process.md) - Theory of matching
4. [CHALLENGES/register-allocation.md](CHALLENGES/register-allocation.md) - #1 issue
5. Pick a game from [GAMES/](GAMES/) and follow that page

### For Contributing

1. Choose a game (Luigi's Mansion or Sunshine recommended for first-timers)
2. Set up environment (follow game's README + our guides)
3. Join that game's Discord
4. Pick a function from objdiff (start with small ones < 50 lines)
5. When stuck, search this repo for the issue (maybe already documented)
6. If new issue, **consider documenting it here** for future contributors!

### For Port Development

Read [PORTING/strategies.md](PORTING/strategies.md) once you have 70%+ matching.

---

## 📝 Document Conventions

- **Code blocks** use syntax highlighting for readability
- **Commands** are prefixed with `$` and assume a bash-like shell
- **Paths** are relative unless starting with `~/` (home directory) or `/` (root)
- **Tool output** shown as monospace, sometimes truncated with `...`
- **⚠️ Warnings** call out common pitfalls
- **✅ Good** and **❌ Bad** examples contrast correct/incorrect approaches

---

## 🗺️ Repository Structure

```
decompresearch/
├── README.md                # This file - master index
├── TOOLS/
│   ├── overview.md         # Toolchain deep dive (15KB)
│   └── ...                 # More tool docs (coming)
├── WORKFLOW/
│   ├── getting-started.md  # Onboarding guide (14KB)
│   ├── matching-process.md # Byte-perfect methodology (14KB)
│   └── ...
├── CHALLENGES/
│   ├── register-allocation.md  # #1 matching problem
│   ├── inlines.md              # Inline functions
│   ├── switches.md             # Jump tables
│   ├── tail-calls.md           # Function boundaries
│   ├── symbols.md              # Finding names
│   └── RTTI.md                 # C++ class recovery
├── PORTING/
│   └── strategies.md         # From decomp to PC port (19.8KB)
├── COMMUNITY/
│   └── websites.md          # Tools, Discords, resources (14.7KB)
└── GAMES/
    ├── template.md          # Template for new games
    ├── projects-overview.md # Master table of all projects (14.8KB)
    ├── melee.md             # Super Smash Bros. Melee (GC)
    ├── super-mario-sunshine.md # Sunshine (GC)
    ├── twilight-princess.md # Zelda: TP (GC/Wii) - 100%!
    ├── zelda-tww.md         # Zelda: Wind Waker (GC)
    ├── super-mario-galaxy.md # SMG1 (Wii)
    ├── mario-kart-double-dash.md # MKDD (GC)
    ├── animal-crossing.md   # Animal Crossing (GC)
    ├── paper-mario-ttyd.md  # Paper Mario TTYD (GC)
    ├── pikmin.md            # Pikmin 1 (GC)
    ├── mario-party-4.md     # Mario Party 4 (GC) - first 100%
    ├── metroid-prime.md     # Metroid Prime (GC)
    └── luigi-mansion.md     # Luigi's Mansion (GC)
```

---

## 📈 Status & Maintenance

**Created**: March 2025 by Hermes (AI agentic assistant)

**License**: This documentation is CC-BY-SA 4.0 (you can share/adapt with attribution).

**Maintenance**: This is a **living document**. Decompilation progresses rapidly. Some information may become outdated.

**How to update**:
1. Fork this repo
2. Make changes (following existing style)
3. Submit a PR
4. Join Discord to discuss major changes

---

## 🎉 Acknowledgments

- **Tool authors**: encounter (dtk, objdiff), matt-kempster (m2c)
- **Project maintainers**: doldecomp team, zeldaret team, PrimeDecomp team, SMGCommunity
- **Community**: All the helpful people in Discord who answer questions
- **Nintendo**: For making these iconic games (we love you, please don't sue)

---

## 🔗 External Resources (Not Included)

Essential but external — these are the source sites:

- [decomp.dev](https://decomp.dev) - Central hub with live progress tracking
- [decomp.me](https://decomp.me) - Collaborative scratch challenges
- [doldecomp GitHub](https://github.com/doldecomp) - Main organization
- [zeldaret GitHub](https://github.com/zeldaret) - Zelda projects
- [PrimeDecomp GitHub](https://github.com/PrimeDecomp) - Metroid Prime
- [SMGCommunity GitHub](https://github.com/SMGCommunity) - Mario Galaxy
- [projectPiki GitHub](https://github.com/projectPiki) - Pikmin

---

## 🎯 Next Steps

**If you're new**:

1. ☑️ Bookmark this repo
2. ☑️ Join relevant Discords (doldecomp, zeldaret)
3. ☑️ Pick a game (Luigi's Mansion recommended for first timers at 7%)
4. ☑️ Follow "Getting Started" in that game's page
5. ☑️ Set up environment (takes 30-90 minutes)
6. ☑️ Build successfully (first non-matching build)
7. ☑️ Open objdiff and stare at the 90%+ diff
8. ☑️ Join `#newcomers` and say hi!
9. ☑️ Try your first match (small function < 30 lines)
10. ☑️ Celebrate when it matches! 🎉

**Remember**: Everyone started where you are. The community is friendly. Don't be shy!

---

## 📊 Quick Decision Matrix

Which game should you work on?

| If you want... | Start with... |
|----------------|---------------|
| **Easiest learning curve** | Luigi's Mansion (7%, clean C) |
| **Most active community** | Super Smash Bros. Melee (840⭐) |
| **Near completion satisfaction** | Animal Crossing or Pikmin (99%+) |
| **Historic achievement** | Twilight Princess (first AAA 100%) |
| **Wii experience** | Super Mario Galaxy (46% and hot!) |
| **RPG systems** | Paper Mario TTYD (~97%) |
| **Racing physics** | Mario Kart Double Dash (43%) |
| **C++ patterns** | Super Mario Sunshine or Zelda series |
| **3D FPS/AI** | Metroid Prime (35%) |
| **Small codebase** | Mario Party 4 (100%, ~6k funcs) |

---

## 🔍 How to Find Information

This repo is **topic-based**, not sequential. Use search:

- **Tool setup issues** → [TOOLS/overview.md](TOOLS/overview.md)
- "My function doesn't match" → [CHALLENGES/register-allocation.md](CHALLENGES/register-allocation.md)
- **Want to port to PC** → [PORTING/strategies.md](PORTING/strategies.md)
- **Specific game questions** → [GAMES/<game>.md](GAMES/)
- **What projects exist?** → [GAMES/projects-overview.md](GAMES/projects-overview.md)
- **Need help from humans** → [COMMUNITY/websites.md](COMMUNITY/websites.md)

---

## 🎯 The "Last 10%" Problem

Common pattern: The final 10% takes as long as the first 90%. Reasons:

1. **Tough functions**: The hardest puzzle pieces are saved for last
2. **Linking complexity**: Linker ordering, data section alignment
3. **Version differences**: Supporting multiple regions identically
4. **Perfect matching**: Tiny differences in constants, register allocation
5. **No low-hanging fruit**: Only corner cases remain

**Example**: Twilight Princess hit 99% in 2023 but took over a year to reach 100%. Animal Crossing at 99.52% may take many more months. Melee at 61% may take another 5+ years to finish.

See [WORKFLOW/matching-process.md](WORKFLOW/matching-process.md) for the full methodology.

---

## 🏗️ Technical Characteristics by Game

| Game | DOL Size | Main Language | Notable Challenges |
|------|----------|---------------|---------------------|
| Melee | ~3.6 MB | C (95%) | 11,700+ functions, 6-frame netcode |
| Sunshine | ~3.5 MB | C++ (77%) | Heavy templates, FLUDD water physics |
| Wind Waker | ~3.3 MB | C++ (90%) | Massive JSystem usage |
| Twilight Princess | ~3.8 MB | C++/C mix | GC/Wii dual, 5+ versions |
| Metroid Prime | ~4.2 MB | C++/C mix | Custom engine, complex AI |
| Mario Party 4 | ~2.5 MB | C | Modular minigames |
| Pikmin | ~1.8 MB | C | Swarm AI, day/night cycle |
| Galaxy 1 | ~3.8 MB | C++ | Streaming worlds, transformations |

---

*Happy decompiling! May your registers align and your relocations resolve!* (◕‿◕✿)

---

*For more specific questions about a game, see that game's page. For tool issues, see TOOLS/. For matching problems, see CHALLENGES/. For porting, see PORTING/*
