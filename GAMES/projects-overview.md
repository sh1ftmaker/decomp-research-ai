# GameCube & Wii Decompilation Projects Overview

*Comprehensive snapshot of active decompilation efforts as of March 2025*

---

## 📊 Summary Statistics

| Platform | Active Projects | 90%+ Complete | 50-89% | 10-49% | <10% |
|----------|----------------|---------------|--------|--------|------|
| **GameCube** | 29 | 6 | 4 | 10 | 9 |
| **Wii** | 22 | 2 | 3 | 11 | 6 |
| **N64** | 11 | 5 | 2 | 3 | 1 |
| **DS/3DS** | 9 | 1 | 3 | 4 | 1 |
| **Switch** | 5 | 0 | 1 | 3 | 1 |
| **Other** | 10 | 2 | 3 | 4 | 1 |

**Total Tracked**: 76+ active projects across 8 console generations

---

## 🏆 Completed or Substantially Complete Projects (≥90%)

These projects are essentially finished or have reached 100% function decompilation.

| Game | Platform | Decomp % | Linked % | Organization | Notes |
|------|----------|----------|----------|--------------|-------|
| **Mario Party 4** | GameCube | 100.00% | 100.00% | mariopartyrd | **First complete GameCube decomp** |
| **The Legend of Zelda: Twilight Princess** | GameCube/Wii | 100.00% | 87.13% | zeldaret | First major AAA 100% (linking ongoing) |
| **Animal Crossing** | GameCube | 99.52% | 98.44% | doldecomp | Nearly complete; port likely imminent |
| **Pikmin** | GameCube | 99.17% | 89.90% | projectPiki | Almost complete, small codebase |
| **Paper Mario (N64)** | N64 | 100% | ? | pmret | Complete (separate from TTYD) |
| **N64 Emulator (GC)** | GameCube | 100% | 100% | zeldaret | Built-in emulator, used for OOT/Majora |

---

## 🎯 Major Active Projects (50-89%)

### Super Mario Series

| Game | Platform | Decomp % | Linked % | Organization | Status |
|------|----------|----------|----------|--------------|--------|
| **Super Smash Bros. Melee** | GameCube | 61.28% | 33.74% | doldecomp | 840 stars! Most popular GC project |
| **Super Mario Sunshine** | GameCube | 29.09% | 13.61% | doldecomp | Active, good for beginners |
| **Super Mario Galaxy 1** | Wii | 46.62% | 18.83% | SMGCommunity/Petari | **Very active**, updated 3h ago |
| **Super Mario Galaxy 2** | Wii | ~15% | ~5%? | SMGCommunity/Garigari | Early stage |
| **Super Mario 64** | N64 | 100% | Complete | n64decomp | First 100% ever (2019) |
| **Super Mario Odyssey** | Switch | ~14% | - | ? | Early, huge undertaking |

### Mario Kart Series

| Game | Platform | Decomp % | Linked % | Organization | Status |
|------|----------|----------|----------|--------------|--------|
| **Mario Kart: Double Dash!!** | GameCube | 43.05% | 37.76% | doldecomp | Moderate progress, needs help |
| **Mario Kart Wii** | Wii | Early | - | snailspeed3 | Started (separate repo) |
| **Mario Kart 64** | N64 | 100% | 100% | 2.8decomp | Complete |

### Legend of Zelda Series

| Game | Platform | Decomp % | Linked % | Organization | Status |
|------|----------|----------|----------|--------------|--------|
| **The Legend of Zelda: Ocarina of Time** | N64 | ~95% | 80%+ | zeldaret | Nearing completion |
| **The Legend of Zelda: Majora's Mask** | N64 | ~88% | 70%+ | zeldaret | Strong progress |
| **The Legend of Zelda: The Wind Waker** | GameCube | 60.43% | 40.41% | zeldaret | Active, Ghidra server used |
| **The Legend of Zelda: Skyward Sword** | Wii | ~30% | 15%? | zeldaret | Just starting |
| **The Legend of Zelda: Breath of the Wild** | Switch | ~15%? | - | zeldaret | Huge C++17 engine, long-term |
| **The Legend of Zelda: A Link to the Past** | SNES | ~90%? | - | ? | Possibly in progress? |

### Metroid Series

| Game | Platform | Decomp % | Linked % | Organization | Status |
|------|----------|----------|----------|--------------|--------|
| **Metroid Prime** | GameCube | 35.63% | 18.67% | PrimeDecomp | Very active, 1500+ commits |
| **Metroid Prime 2: Echoes** | GameCube | ~30% | - | PrimeDecomp | Following Prime's progress |
| **Metroid Prime 3: Corruption** | Wii | Early | - | ? | Not started yet |
| **Metroid Fusion** | GBA | Early | - | metroidret | Active |
| **Metroid: Zero Mission** | GBA | Early | - | metroidret | Active |
| **Metroid Prime Remastered (Switch)** | Switch | Tools done | - | PrimeDecomp | Structs and formats released |

### Other Notable Projects

| Game | Platform | Decomp % | Linked % | Notes |
|------|----------|----------|----------|-------|
| **Paper Mario: TTYD** | GameCube | 97%? | 90%+? | Almost complete (est.) |
| **Luigi's Mansion** | GameCube | 7.02% | 6.53% | Recently revived (Moddimation/Yasiki) |
| **F-Zero GX** | GameCube | ~25% | - | Arcade-style racer, tough but doable |
| **Wii Sports** | Wii | 5.78% | - | System software level, complex |
| **N64 Emulator (Wii)** | Wii | 64.98% | - | Virtual Console version |
| **Sonic Adventure DX** | GameCube | ~65% | - | Third-party, good progress |
| **Sonic Riders** | GameCube | Early | - | Started |
| **Legacy of Kain: Soul Reaver** | PS1/PC | 81.50% | - | Multi-platform project |
| **Vagrant Story** | PS1 | 50.66% | 29.30% | Square classic, active |
| **Castlevania: Symphony of the Night** | PS1 | 34.64% | - | Beloved classic, needs more help |
| **Final Fantasy VII** | PS1 | ~7%? | - | xeeynamo's project |
| **Phantom Hourglass** | DS | Early | - | zeldaret project |
| **Spirit Tracks** | DS | Early | - | zeldaret project |
| **Mario Party 5-8** | GameCube/Wii | Not started | - | Natural successors to MP4 |

---

## 🔧 Supporting Infrastructure Projects

These are decompilations of SDKs, libraries, and system software that power the games.

| Project | Description | Status | Usage |
|----------|-------------|--------|-------|
| **Dolphin SDK 2001** | GameCube SDK libraries (May 23, 2001) | Fully decompiled | Base for many GC projects |
| **Dolphin SDK 2009-12-11** | Wii SDK (specific version) | Fully decompiled | Base for Wii projects |
| **JSystem** | Nintendo's OO game framework | Fully decompiled | Used widely (Zelda, Mario) |
| **MusyX** | Audio library (formerly AX) | Decompiled | Audio in many titles |
| **Wii System Menu** | System software | 41.38% decompiled | 33.84% linked |
| **Wii Menu IOS** | System libraries | 1.32% | Early |
| **Wii Sport Club** | Wii U? | 37.44% | 21.67% linked |
| **Wii Fit** | Wii | 0.20% | Just started |

---

## 🌍 Organization & Community Structure

### Primary GitHub Organizations

| Organization | Focus | Active Repos | Key Contributors |
|--------------|-------|--------------|------------------|
| **doldecomp** | GameCube/Wii first-party | ~20 | encounter, Mrkol, NWPlayer123 |
| **zeldaret** | Zelda franchise | 10+ | zsrtp, contributors worldwide |
| **PrimeDecomp** | Metroid Prime series | 3 | PrimeDecomp team |
| **SMGCommunity** | Super Mario Galaxy | 2 | Community-run, very active |
| **pret** | Pokémon series | 15+ | Well-established team |
| **n64decomp** | N64 Mario/Zelda | 3 | Original pioneers |
| **projectPiki** | Pikmin series | 1-2 | Dedicated team |

### Community Platforms

- **decomp.dev**: Automated progress tracking (pulls from GitHub)
- **decomp.me**: Collaborative scratch work platform for solving functions
- **Discord**: Separate servers per organization (invites in READMEs)
- **GitHub Issues**: Primary task tracking (labels: `help wanted`, `easy object`)
- ** Wikis**: zeldaret wiki, SMGCommunity wiki, GitHub wikis

---

## 📈 Progress Patterns & Insights

### Completion Timeframes (Estimates)

| Game | Start Date | Completion Est. | Total Duration |
|------|------------|-----------------|----------------|
| Super Mario 64 | 2019 | 2022 | ~3 years |
| Mario Party 4 | 2021 | 2022 | ~4 months (unusually fast - smaller) |
| Twilight Princess | 2020 | 2024-2025 | 4-5 years |
| Animal Crossing | 2021 | 2025 | ~4 years |
| Paper Mario 64 | ? | 2025 | ? |
| Pikmin 1 | ? | 2025 | ~3 years |
| Super Smash Bros. Melee | 2018 | - | 7+ years, still active |
| Super Mario Sunshine | ~2020 | - | 5+ years, ongoing |
| Super Mario Galaxy 1 | ~2022 | - | 3-4 years est. |

### The "Last 10%" Problem

Common pattern: The final 10% takes as long as the first 90%. Reasons:

1. **Tough functions**: The hardest puzzle pieces are left for last
2. **Linking complexity**: Linker ordering, data section alignment
3. **Version differences**: Supporting multiple regions/revisions identically
4. **Perfect matching**: Tiny differences in constants, ordering, register allocation
5. **No low-hanging fruit**: Only challenging corner cases remain

**Example**: Twilight Princess hit 99% in 2023 but took over a year to reach 100%. Animal Crossing at 99.52% may take many more months. Melee at 61% may take another 5+ years to finish.

---

## 🏗️ Technical Characteristics by Game

| Game | DOL Size | Main Language | Major Libraries | Notable Challenges |
|------|----------|---------------|-----------------|---------------------|
| **Melee** | ~3.6 MB | C (95.6%) | Baslib | Massive 11,700+ functions, complex physics, 6-frame-perfect netcode |
| **Sunshine** | ~3.5 MB | C++ (77%) | JSystem v2 | Large C++ codebase, FLUDD physics |
| **Wind Waker** | ~3.3 MB | C++ (89.6%) | JSystem v3 | Shared engine with TP |
| **Twilight Princess** | ~3.8 MB | C++ (54%), C (45%) | JSystem v3 | GC/Wii dual, many versions (5+) |
| **Metroid Prime** | ~4.2 MB | C++ (74.8%), C (21%) | Custom engine | Complex 3D systems, AI |
| **Mario Party 4**| ~2.5 MB | C | Custom engine | Modular minigames, easier |
| **Pikmin** | ~1.8 MB | C | Custom engine | Swarm AI, day/night cycle |
| **Galaxy 1** | ~3.8 MB | C++ | JSystem v4 | Streaming worlds, transformations |

---

## 📚 Key Documentation Sources

This research archive compiles information from:

- **Official GitHub READMEs**: All major projects (setup, progress, CONTRIBUTING)
- **decomp.dev**: Automated progress tracking site
- **decomp.wiki**: Community-maintained game-specific pages
- **GitHub Wikis**: zeldaret/tww, SMGCommunity/Petari, doldecomp/melee
- **Guides**: zeldaret's detailed `decompilation.md`, SMGCommunity guides
- **Tool Docs**: `decomp-toolkit`, `objdiff`, `m2c` READMEs
- **Discord**: Publicly shared announcements, pinned messages
- **Forums**: GBAtemp, Reddit r/Gamecube, r/ReverseEngineering, ResetEra
- **Blogs**: Developer blogs (encounter, ripper_, etc.)
- **YouTube**: Decompilation progress videos, presentations

---

## 🎮 What Makes a Good "First Game"?

When choosing a decompilation project to contribute to, consider:

| Factor | Good Choice | Avoid |
|--------|-------------|-------|
| **Size** | Small to medium (<2MB code) | Very large (>4MB) |
| **Language** | Mostly C (easier matching) | Heavy C++ templates |
| **Progress** | 10-40% (room to contribute) | >80% (few easy tasks) |
| **Documentation** | Active wiki, CONTRIBUTING.md | Poor docs, inactive maintainers |
| **Community** | Active Discord, responsive veterans | Dead or toxic community |
| **Tools** | Modern dtk setup, CI/CD | Legacy build system |
| **Interest** | You genuinely love the game | Just looking for any project |
| **Port potential** | Clear path to PC (GX→OpenGL) | Too coupled to hardware |

### Recommended Starter Games (Current offerings):

1. **Luigi's Mansion** (revived, lots of foundational work at 7%)
2. **Paper Mario TTYD** (early stage, ~97% but could help verify)
3. **Mario Party 4** (complete, but good for studying patterns)
4. **Pikmin** (small, clean code at 99% - final push help)
5. **N64 titles** (smaller, simpler, good practice)
6. **Animal Crossing** (almost done, but final 0.48% tricky)

### Games to Avoid as Beginner:

- Super Smash Bros. Melee (too large, too many edge cases)
- Twilight Princess (massive C++ codebase)
- Super Mario Galaxy (streaming complexity)
- Metroid Prime (custom engine, complex 3D)

---

## 🔮 The Future

### Upcoming Projects (Rumored/Early)

- Super Mario Galaxy 2 (following Galaxy 1 completion)
- Sonic Heroes (GameCube)
- Spyro trilogy (PS1/N64)
- More third-party titles (PS2, Xbox 360)
- NES/SNES/GBA compilation decomps
- Nintendo Switch titles (slowly starting)

### Technical Frontiers

- AI-assisted decompilation (controversial but happening)
- Automated matching with LLMs for function skeletons
- Improved decompilers (next-gen `m2c`, `retdec` integrations)
- Better C++ reconstruction (vtable recovery, inheritance)
- Cross-platform port toolchains becoming more common
- Formal verification of matching correctness

---

## 📈 Project Completion Roadmap (Near-Term)

**2025 Milestones Expected**:

| Project | Expected Completion |
|---------|---------------------|
| Animal Crossing | 100% (Q2-Q3 2025) |
| Pikmin 1 | 100% (Q2 2025) |
| Paper Mario TTYD | 100% (Q3-Q4 2025?) |
| Twilight Princess | 100% linked (Q2 2025) |
| Super Mario Galaxy 1 | 60-70% (steady) |
| Melee | 65-70% (gradual) |
| Wind Waker | 65-70% |

**Longer-term**:

| Project | 5-Year Target |
|---------|---------------|
| Melee | 100% (2030?) |
| Galaxy 1 | 100% (2028-2030) |
| Wind Waker | 100% (2030?) |
| Metroid Prime | 100% (2030?) |
| BotW | Too big? maybe 50% (2030) |

---

## 🏆 Historic Achievements (So Far)

- **2019**: Super Mario 64 - First 100% completed game ever (N64)
- **2021**: Paper Mario 64 - Second 100% (N64)
- **2022**: Mario Party 4 - First 100% GameCube title
- **2024**: Twilight Princess - First major AAA 100% (GC/Wii)
- **2025**: Animal Crossing, Pikmin 1 - pushing toward 100%
- **2025**: Twilight Princess 100% Linked? (pending)

These milestones prove that **fully matching decompilation is possible** for large, complex console titles. The community has developed sophisticated toolchains and workflows that are now standardized.

---

## 📊 By Language Stack

### C-only Projects (Easier)

- Mario Party 4
- Pikmin
- Paper Mario 64
- Luigi's Mansion
- Mario Kart 64
- F-Zero X
- Dr. Mario 64
- Most N64 titles

**Why easier**: No C++ complications (templates, inheritance, vtables, RTTI)

### C++ Heavy Projects (Harder)

- Twilight Princess (54% C++, 45% C)
- Super Mario Sunshine (77% C++)
- Metroid Prime (75% C++)
- The Wind Waker (89% C++)
- Super Mario Galaxy (70%+ C++)
- Super Smash Bros. Melee (mostly C, but some C++)

**Challenges**: Recovering class hierarchies, virtual tables, template instantiations, exception handling (if any), RTTI.

---

## 🤝 How to Help Right Now

If you want to contribute but don't know which project:

1. **Join the Discord** servers (doldecomp, zeldaret, SMGCommunity)
2. **Check `help wanted` issues** on GitHub
3. **Try decomp.me** to claim a function (scratch work)
4. **Pick a project** from the "starter" list above
5. **Read the CONTRIBUTING.md** and PROGRESS.md files
6. **Build the game** and verify it matches
7. **Start with a small function** (statics, getters, simple math)

**Remember**: Not every contribution needs to be code! Documentation, testing, tool improvements, and community support are all valuable.

---

*Last updated: March 2025*

*Data sources: decomp.dev (live), GitHub APIs, project READMEs, community discussions*

*Questions? Check the README of the specific project you're interested in!* (◕‿◕✿)
