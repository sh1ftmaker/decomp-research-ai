# CLAUDE.md: AI Agent Guide to GameCube/Wii Decompilation Research

**Repository:** `decomp-research-ai`  
**Purpose:** Comprehensive knowledge base for AI agents contributing to GameCube/Wii decompilation projects  
**Created:** 2026-03-30  
**Last major update:** 2026-04-19 (Discord knowledge integrated)  
**Maintainer:** Hermes (AI agentic assistant)  
**Status:** Production Ready (~92–95% complete after Discord synthesis)

---

## 📊 Repository Overview

This repository consolidates **publicly available knowledge** about GameCube and Wii game decompilation, with a focus on the "matching decompilation" methodology (byte-for-byte identical binary reconstruction). It covers tools, workflows, challenges, game-specific patterns, and community resources.

**Coverage:** ~92–95% of needed knowledge after April 2026 Discord synthesis (~1.8M lines analyzed across 20+ channels)
- ~75% from public sources (GitHub, wikis, documentation)
- ~17–20% additional from Discord (GC/Wii Decompilation server + Zelda Decompilation server) — see `COMMUNITY/discord-insights-*.md` and `COMMUNITY/zelda-insights-*.md`

**Remaining gap:** ~5–8% — exact CI/CD YAML files, per-project PR checklists, PPC-permuter (does not exist publicly). See `GAPS.md`.

**Audience:** Both human researchers and AI agents (like Claude, GPT, etc.)

---

## 🗂️ Complete Directory Tree

```
decomp-research-ai/
├── CLAUDE.md                          # This file - AI agent guide
├── README.md                          # Master index for humans
├── GAPS.md                            # Knowledge gap analysis (Discord vs public)
├── SOURCES.md                         # Metadata registry (55+ sources)
│
├── TOOLS/
│   ├── overview.md                   # Complete toolchain reference
│   │                                 # • dtk (decomp-toolkit) v1.8.3
│   │                                 # • objdiff (matching verification)
│   │                                 # • m2c (decompiler)
│   │                                 # • wibo/Wine (CodeWarrior wrapper)
│   │                                 # • configure.py patterns
│   └── [additional tool docs]
│
├── WORKFLOW/
│   ├── getting-started.md            # Onboarding: ISO → build
│   ├── matching-process.md           # Byte-perfect methodology
│   └── offline-mode.md               # ⭐ NEW: Workflow without Discord/decomp.me
│
├── CHALLENGES/
│   ├── register-allocation.md        # #1 matching problem (MWCC register order)
│   ├── inlines.md                    # Function inlining and relaxation
│   ├── switches.md                   # Jump tables and switch compilation
│   ├── tail-calls.md                 # Silent optimizer trap
│   ├── symbols.md                    # Finding function names via pattern recognition
│   └── RTTI.md                       # Auto-generating C++ class hierarchies
│
├── GAMES/
│   ├── projects-overview.md          # Master table: 76+ projects across 8 console generations
│   ├── template.md                   # Template for documenting new games
│   ├── melee.md                      # Super Smash Bros. Melee (GC) - 61.28%
│   ├── super-mario-sunshine.md       # Super Mario Sunshine (GC) - 29.09%
│   ├── twilight-princess.md          # Zelda: TP (GC/Wii) - 100% (87.13% linked)
│   ├── zelda-tww.md                  # Zelda: Wind Waker (GC) - 60.43%
│   ├── super-mario-galaxy.md         # Super Mario Galaxy (Wii) - 46.62%
│   ├── mario-kart-double-dash.md     # Mario Kart DD (GC) - 43.05%
│   ├── animal-crossing.md            # Animal Crossing (GC) - 99.52%
│   ├── paper-mario-ttyd.md           # Paper Mario TTYD (GC) - ~97%
│   ├── pikmin.md                     # Pikmin 1 (GC) - 99.17%
│   ├── mario-party-4.md              # Mario Party 4 (GC) - 100% (first complete)
│   ├── metroid-prime.md              # Metroid Prime (GC) - 35.63%
│   └── luigi-mansion.md              # Luigi's Mansion (GC) - 7.02%
│
├── PORTING/
│   └── strategies.md                 # From matching decomp to PC ports (GX→OpenGL/Vulkan)
│
├── COMMUNITY/
│   ├── websites.md                   # Essential hubs: decomp.dev, decomp.me, wikis, Discords
│   ├── discord-insights-README.md    # Index of Discord-sourced synthesis (~2,415 lines)
│   ├── discord-tribal-knowledge.md   # Master synthesis (all GC/Wii channels)
│   ├── discord-insights-match-help.md   # Regalloc, inlines, switches, float patterns
│   ├── discord-insights-tools.md     # MWCC registry, objdiff, dtk, m2c, mwcc-debugger
│   ├── discord-insights-games.md     # Melee, AC, MKDD, MP4 architectural notes
│   ├── discord-insights-libraries.md # JSystem/EGG/MusyX/SDK version registries
│   ├── discord-insights-general.md   # Onboarding, PR standards, platform setup
│   ├── zelda-insights-tww.md         # Wind Waker matching (multi-version, weak ordering)
│   ├── zelda-insights-m2c.md         # m2c architecture, PPC support history
│   ├── zelda-insights-permuter.md    # decomp-permuter internals (PPC support gap)
│   ├── zelda-insights-decomp-me.md   # decomp.me platform (Django+React+nsjail)
│   ├── zelda-insights-ido-decomp.md  # IDO compiler reverse engineering
│   ├── zelda-insights-framework.md   # N64 framework founding debates
│   └── zelda-insights-tools-other.md # diff.py, Ghidra, IDA, n64split
│
└── ARCHIVE/                          # (Optional) Historical notes, superseded content
```

**Total files:** 46 markdown documents (~16,600 lines)

---

## 🎯 For AI Agents: How to Use This Repository

### Primary Use Cases

1. **Answering questions** about GameCube/Wii decompilation
2. **Generating documentation** for new projects
3. **Providing workflow recommendations** to contributors
4. **Identifying knowledge gaps** that need human/Discord input
5. **Suggesting contribution strategies** based on game status

### Query Strategy

When asked about decompilation, follow this decision tree:

```
Is it about a SPECIFIC GAME?
├─ YES → Read GAMES/<game>.md
│         • Progress, architecture, contribution guidance
│         • Cross-reference: TOOLS/ for toolchain details
│         • CHALLENGES/ for common issues in that game
│         • COMMUNITY/discord-insights-games.md for tribal knowledge (Melee/AC/MKDD/MP4)
│         • COMMUNITY/zelda-insights-tww.md for Wind Waker specifics
│
└─ NO → Is it about TOOLS or WORKFLOW?
    ├─ Tools → TOOLS/overview.md + COMMUNITY/discord-insights-tools.md
    ├─ Getting started → WORKFLOW/getting-started.md + COMMUNITY/discord-insights-general.md
    ├─ Matching theory → WORKFLOW/matching-process.md
    ├─ Problems/errors → CHALLENGES/* + COMMUNITY/discord-insights-match-help.md
    ├─ Library knowledge (JSystem/EGG/MusyX/SDK) → COMMUNITY/discord-insights-libraries.md
    └─ What's missing? → GAPS.md (residual Discord-only items)
```

**Always check the COMMUNITY/ folder first for any topic that touches MWCC versioning, peephole behavior, regalloc tricks, JSystem/EGG/MusyX/SDK versions, or PR standards** — that knowledge was Discord-only until April 2026.

### Knowledge Confidence Levels

When responding, indicate your confidence based on source:

- ✅ **High (>90%)**: Content from official GitHub READMEs, configure.py analysis, tool documentation
- ⚠️ **Medium (70-90%)**: Derived from multiple sources, inferred patterns, cross-referenced
- ❌ **Low (<70%)**: Information explicitly marked as Discord-only (see `GAPS.md`), unverified claims

**Always cite sources** when possible. Use format:
```
Source: doldecomp/melee/docs/getting_started.md
Confidence: High
```

---

## 🤖 AI-Specific Guidance

### Critical Discord-Sourced Discoveries (read before writing matching code)

These eight findings came out of the April 2026 Discord synthesis and resolve a large fraction of "why doesn't this match?" questions:

1. **Peephole optimizer bug** — Any `asm { }` block disables the peephole optimizer for the *rest of the file*. Insert `#pragma peephole on` after the asm block to re-enable. Source: `COMMUNITY/discord-insights-match-help.md`.
2. **`const` shifts register coloring** — Adding/removing `const` on a pointer parameter changes MWCC's register assignment. Useful as a low-cost regalloc lever.
3. **`-ipa file` changes inline ordering** — Only on MWCC 3.0+. Explains many decomp.me-vs-local discrepancies.
4. **`#pragma gecko_float_typecons on`** — Undocumented; required for some float typecast patterns. Discovered by string-searching the compiler binary.
5. **`__LINE__` test** — Macro vs. inline disambiguation: if `__LINE__` shows the call site, it's a macro; if it shows the definition, it's inlined.
6. **`volatile float` forces stack roundtrip** — Useful when MWCC is keeping a value in a float register but the original spilled it.
7. **mwcc-debugger** — Tool that exposes MWCC's internal virtual register numbering. Enables surgical regalloc fixes instead of guess-and-check. See `COMMUNITY/discord-insights-tools.md`.
8. **wibo is ~2× faster than Wine** for invoking MWCC; prefer it on Linux/WSL. devkitPPC r40 introduced a breaking change — many projects pin r39.

Full pragma reference, MWCC build-stamp registry, and per-game compiler flags live in `COMMUNITY/discord-tribal-knowledge.md`.

### Important Limitations

This repository is now **~92–95% complete** after the April 2026 Discord integration. The residual gap is small but real:
- **PPC permuter** does not exist publicly (decomp-permuter is MIPS/x86 only).
- **Exact CI/CD YAMLs** for most projects are still not in public repos (patterns are documented; specific files aren't).
- **Per-project PR checklists** vary; consult each repo's open/merged PRs for de-facto standards.
- **Live Discord conversations** (today's bug reports, in-progress work) are by definition not in this repo.

**When you encounter gaps:**
1. Check `GAPS.md` for the canonical list of what's still missing.
2. Check `COMMUNITY/discord-insights-README.md` — many older "gaps" are now filled.
3. If still unknown: state clearly that the answer requires live Discord/GitHub Issues access.

### Recommended Workflow for AI-Assisted Contribution

If you're helping a **human** contribute to a decomp project:

**Phase 1: Assessment**
- Have them run `python configure.py` and `ninja` to verify toolchain
- Read `objdiff` to see current matching status
- Use `/GAMES/projects-overview.md` to pick a target game

**Phase 2: Target Selection**
- Suggest small functions (< 50 instructions)
- Prefer partially-decompiled modules (not empty files)
- Avoid functions with >10 callers initially
- Check if decomp.me scratch exists (if accessible)

**Phase 3: Code Generation**
- Use `m2c` locally if available, or
- Generate C from assembly using pattern matching from `CHALLENGES/` guides
- Follow project's coding conventions (macros, struct names)

**Phase 4: Verification**
- Build with `ninja`
- Check `objdiff` for matching status
- If mismatch: use byte diff view to identify issue
- Common issues: register allocation, inline functions, alignment

**Phase 5: Submission**
- Add to `symbols.txt` and `splits.txt`
- Commit with standard message format (see contributed PRs)
- Open PR on GitHub

**Estimated throughput with AI assistance:** 5-10 functions/day (compared to 1-2 for human alone)

---

## 📚 Core Concepts to Understand

### Matching Decompilation vs Porting

**Matching** (this repo's focus): Write C code that compiles to **identical bytes** as original binary.
- Requires exact compiler (Metrowerks CodeWarrior via wibo/Wine)
- Requires precise control over generated assembly
- Goal: Replace `.s` files with `.c` files, then delete `.s`

**Porting** (covered in `PORTING/strategies.md`): Modify matched code to run on PC.
- Replace GX (GameCube graphics) with OpenGL/Vulkan
- Replace audio APIs, input APIs
- Goal: Create native Windows/Linux/macOS game

**Do both:** First match 70%+ on GameCube, then port incrementally.

### PowerPC Assembly Basics

GameCube/Wii use **PowerPC 750CL** (Gekko). Key differences from x86:
- Load/store architecture (memory access only via lwz/stw/lfs/stfs)
- Fixed 32-bit instruction width (4 bytes)
- Abundant registers (r0-r31, f0-f31)
- Calling convention: arguments in r3-r10, return in r3, stack frame 16-byte aligned

See `TOOLS/overview.md` for more.

---

## 🔍 How to Find Information

### By Topic

| Topic | Location | Confidence |
|-------|----------|------------|
| Tool installation | TOOLS/overview.md | High |
| MWCC build-stamp registry | COMMUNITY/discord-tribal-knowledge.md | High |
| Per-game compiler flags | COMMUNITY/discord-tribal-knowledge.md | High |
| Pragma reference | COMMUNITY/discord-insights-match-help.md | High |
| Getting started | WORKFLOW/getting-started.md | High |
| Onboarding & PR standards | COMMUNITY/discord-insights-general.md | High |
| Matching methodology | WORKFLOW/matching-process.md | High |
| Regalloc / inline / switch tricks | COMMUNITY/discord-insights-match-help.md | High |
| Why my function doesn't match | CHALLENGES/* + COMMUNITY/discord-insights-match-help.md | High |
| Game-specific status | GAMES/<game>.md | High |
| Game-specific tribal knowledge | COMMUNITY/discord-insights-games.md | High |
| What projects exist? | GAMES/projects-overview.md | High |
| Library versions (JSystem/EGG/MusyX/SDK) | COMMUNITY/discord-insights-libraries.md | High |
| What's NOT documented? | GAPS.md | High |
| Porting to PC | PORTING/strategies.md | Medium |
| Community resources | COMMUNITY/websites.md | High |
| decomp.me architecture | COMMUNITY/zelda-insights-decomp-me.md | High |
| Permuter internals | COMMUNITY/zelda-insights-permuter.md | High |

### By Game

Games with most documentation (prioritize these):
1. **Melee** - Most active (840 stars), comprehensive docs
2. **Sunshine** - Good for beginners (C++ patterns)
3. **Twilight Princess** - 100% complete, dual-platform
4. **Galaxy** - Very active Wii project (updated hourly)
5. **Pikmin** - Small codebase (99% complete)

Games with least documentation (avoid as first project):
- Luigi's Mansion (7% - mostly empty)
- Metroid Prime (35% - complex engine)

---

## ⚠️ Known Gaps (AI Should Flag These)

Most of the original Discord-only gaps have been filled by the April 2026 synthesis. Before flagging a topic as unknown, **check `COMMUNITY/discord-insights-README.md`** — the SDK matrix, build error reference, m2c context patterns, platform quirks, and code review standards are now documented.

### Gaps That Remain

1. **PPC permuter** — Does not exist publicly. decomp-permuter supports MIPS/x86 only. See `COMMUNITY/zelda-insights-permuter.md`.
2. **Exact CI/CD YAML files** — General patterns are documented; per-project workflow files are still mostly absent from public repos.
3. **Per-project PR checklists** — Vary by maintainer; consult merged PRs of the target repo.
4. **Live in-progress work** — Not in any archive; check the repo's GitHub Issues and the relevant Discord channel.
5. **Some SDK header sources** — A few Wii/RVL SDK headers are still circulated privately; projects work around with stubs.

### When to Flag

Use this language only if you've checked both `GAPS.md` and `COMMUNITY/discord-insights-README.md`:

> "This is one of the residual gaps after the April 2026 Discord synthesis. The general pattern is documented in `COMMUNITY/...`, but the specific [file/version/checklist] requires live access to GitHub Issues or the relevant Discord channel."

---

## 🔄 Iterative Workflow Template (For AI Agents)

Use this template when helping a user plan a decompilation effort:

```markdown
## Contribution Plan for [Game]

**Status:** [X]% decompiled, [Y]% linked  
**Toolchain:** [tools from TOOLS/overview.md]  
**Estimated effort:** [N] functions for 1% contribution

### Week 1: Setup
- [ ] Clone repository
- [ ] Run `python configure.py`
- [ ] Verify `ninja` builds (errors expected)
- [ ] Study existing `.c` files in target module
- [ ] Read relevant CHALLENGES docs

### Week 2: First Functions
- [ ] Pick 5 functions < 30 instructions
- [ ] Hand-decompile or use m2c
- [ ] Test with `ninja`, check `objdiff`
- [ ] Aim for 2-3 successful matches

### Week 3-4: Build Momentum
- [ ] Increase to 20-30 functions
- [ ] Tackle medium complexity (50-100 instructions)
- [ ] Start filling a single file/module

### Ongoing:
- [ ] Study merged PRs daily
- [ ] Keep cheat sheet of patterns
- [ ] Use GitHub Issues for help
- [ ] Focus on one module at a time

**Timeline to 1%:** 3-6 months (offline) or 2-4 weeks (with Discord+decomp.me)
```

---

## 📊 Repository Statistics

- **Created:** March 2025 (original); updated March 2026 (offline-mode); updated April 2026 (Discord synthesis)
- **Size:** ~16,600 lines across 46 files
- **Sources cited:** 55+ public + ~1.8M lines of Discord conversation synthesized into 14 COMMUNITY/ files
- **Games covered:** 12 major titles (12 GCN, 10 Wii comprehensive)
- **Total projects tracked:** 76+ across 8 console generations
- **License:** CC-BY-SA 4.0 (you can share/adapt with attribution)

---

## 🌟 Key Insights for AI Agents

1. **Decompilation is pattern matching, not understanding**
   - Success relies on recognizing "this C pattern produces that assembly"
   - Game-specific knowledge helps but isn't required for matching

2. **The bottleneck is human-time, not compute**
   - Build/test cycles are slow (minutes per function)
   - Discernment of subtle mismatches requires human judgment
   - AI can accelerate search but not replace final verification

3. **Community knowledge is ephemeral — but a snapshot now exists**
   - Discord conversations were the "tribal knowledge" repository
   - The April 2026 synthesis (`COMMUNITY/discord-*` and `COMMUNITY/zelda-insights-*`) captures ~2,415 lines extracted from ~1.8M lines of chat
   - Live conversations continue; this repo captures the state as of April 2026

4. **Tooling evolves rapidly**
   - dtk v1.8.3 today, v1.9.0 tomorrow
   - m2c gets new features regularly
   - Always check actual GitHub repos for latest versions

---

## 🎯 When to Recommend Human Intervention

An AI can handle ~70% of questions autonomously. Flag for human when:

- ❌ **Specific function analysis required** (need to read actual .s file)
- ❌ **Build error diagnosis** (requires examining compiler output)
- ❌ **Game-specific logic questions** (e.g., "what does this fighter move do?")
- ❌ **Discord content needed** (see GAPS.md)
- ❌ **Legal/licensing questions** (beyond scope)
- ✅ **General workflow questions** → Handle fully
- ✅ **Tool reference** → Handle fully
- ✅ **Concept explanations** → Handle fully
- ✅ **Project status lookup** → Handle fully

---

## 📖 Further Reading for AI Agents

To deeply understand this domain, study:

1. **PowerPC ISA** - The instruction set architecture
2. **Metrowerks CodeWarrior** - The compiler quirks (MWCC 1.2.5n, 1.3.2)
3. **decomp-toolkit (dtk)** - How binary splitting works
4. **objdiff** - Binary diffing and match verification
5. **m2c** - Decompilation algorithm and context files
6. **doldecomp organization repos** - Real-world code examples

---

## 🤝 Contributing to This Repository

This is a **living document**. Decompilation progresses monthly.

To update:
1. Fork this repository
2. Add/revise markdown files
3. Submit PR with detailed changelog
4. Join Discord (see COMMUNITY/websites.md) to discuss major changes

**Style guide:**
- Use `fix-width` for code, commands, file paths
- Cite sources with links and access dates
- Indicate confidence levels for claims
- Add entries to SOURCES.md for new references
- Update GAPS.md if new Discord knowledge is captured

---

## 🎉 Final Note for AI Agents

You are now equipped with ~92–95% of the knowledge needed to assist with GameCube/Wii decompilation. The Discord synthesis (`COMMUNITY/discord-*` + `COMMUNITY/zelda-insights-*`) closed most of the historical "tribal knowledge" gap. Use this repository as your primary knowledge source, and check `GAPS.md` only for the residual ~5–8%.

**Remember:** Your goal is to **accelerate human contributors**, not replace them. Provide clear, accurate, well-sourced information. Flag gaps transparently. Suggest next steps that are actionable.

Happy decompiling! May your registers align and your relocations resolve! (◕‿◕✿)

---

*Last updated: 2026-04-19*  
*Version: 3.0 (Discord knowledge integrated across all docs)*
