# Knowledge Gaps: Discord vs Public Sources

**Analysis Date:** 2026-03-30  
**Updated:** 2026-04-17 — Discord mining complete; gaps reassessed  
**Public Coverage:** ~70-75% (original estimate)  
**Post-Discord Coverage:** ~92-95%  
**Remaining Gaps:** ~5-8%

> **Status Update (2026-04-17):** Discord archives for the doldecomp server have been analyzed (~1.8M lines across 20+ channels). Most critical gaps are now addressed. See `COMMUNITY/discord-tribal-knowledge.md` for the master synthesis and the `COMMUNITY/discord-insights-*.md` files for per-channel detail. Gaps marked ✅ below have been substantially filled.

This document identifies what information is publicly available versus what remains trapped in Discord servers (particularly `ZeldaRET` and `doldecomp`). Use this as a guide for targeted Discord extraction.

---

## 🔴 CRITICAL GAPS (High Impact, Nearly Impossible to Find Publicly)

### 1. CI/CD & Testing Workflows
**Status:** ⚠️ Partially addressed by Discord mining
- ✅ CI runs via GitHub Actions with wibo pre-installed, compilers downloaded from `files.decomp.dev`
- ✅ `objdiff report generate` → `VERSION_report` artifact → consumed by decomp.dev
- ✅ dtk-template `.github.example/workflows/build.yml` is the recommended starting point
- ✅ PR bot downloads objdiff reports from CI artifacts and posts progress comparison comments
- ❌ Actual YAML config files not in public repos; shared informally
- ❌ Exact build matrix configurations not documented

**See:** `COMMUNITY/discord-insights-tools.md` §decomp.dev, `COMMUNITY/discord-insights-general.md` §7

---

### 2. SDK Version Matrix (Per Game)
**Status:** ✅ Substantially addressed by Discord mining
- ✅ Full MWCC build stamp registry documented (GC CW 1.0 through Wii CW 1.7)
- ✅ Per-game compiler versions confirmed (Melee: Build 156/158; AC RELs: 1.3.2; MKDD/MP4: 2.6; MSM audio: 1.2.5)
- ✅ SDK build string format documented; per-module dates documented
- ✅ JSystem version per game documented; evolution chain mapped
- ✅ Community SDK repos catalogued (dolsdk2001, dolsdk2004, sdk_2009-12-11)
- ✅ How to identify SDK version from binary (build string extraction method)

**See:** `COMMUNITY/discord-insights-tools.md` §1, `COMMUNITY/discord-insights-libraries.md` §Dolphin SDK

---

### 3. Build Error Troubleshooting Reference
**Status:** ✅ Substantially addressed by Discord mining
- ✅ 6 specific dtk error messages documented with causes and fixes
- ✅ 4 mwldeppc linker errors documented with fixes
- ✅ devkitPPC r40 breaking change documented with workaround
- ✅ objdiff startup failure fix (`%APPDATA%\objdiff` deletion)
- ✅ wibo vs. Wine decision documented with benchmarks
- ❌ "Relax relocations" edge cases still undocumented
- ❌ No central troubleshooting guide exists; error diagnosis still done by posting in channel

**See:** `COMMUNITY/discord-insights-tools.md` §3, `COMMUNITY/discord-insights-general.md` §8, §10

---

### 4. Advanced Context File Patterns (m2c)
**Status:** ✅ Substantially addressed by Discord mining
- ✅ Context file preprocessing workflow documented (`-E` flag, flattening guards)
- ✅ Common failure modes: `#ifdef` guards, struct with function pointers, binary literals
- ✅ `--reg-vars` flag effect documented
- ✅ `M2C_STRUCT_COPY` semantics documented
- ✅ Jump table label naming requirements documented
- ✅ `M2CTX` macro pattern (Melee) for C++ context documented
- ❌ Complex JSystem template context strategies still partially undocumented

**See:** `COMMUNITY/discord-insights-tools.md` §4

---

## 🟡 SIGNIFICANT GAPS (Useful, Partially Available Publicly)

### 5. Platform-Specific Quirks
**Status:** ✅ Substantially addressed by Discord mining
- ✅ WSL1 vs WSL2 distinction (WSL1 cannot run 32-bit apps)
- ✅ WSL filesystem location requirement (`/home/...` not `/mnt/c/`)
- ✅ devkitPPC r40 breaking change documented
- ✅ wibo vs. Wine decision documented with benchmarks
- ✅ macOS Apple Silicon workarounds (VPS, Docker + Wine)
- ❌ WSL ARM64 compatibility (Snapdragon laptops) unresolved
- ❌ Linux distro-specific issues not documented

**See:** `COMMUNITY/discord-insights-general.md` §3

---

### 6. Symbol Resolution Best Practices
**Status:** ⚠️ Partially addressed
- ✅ Symbol map parsing: `cwparse` Rust library documented
- ✅ Ghidra symbol map import: remove `Offset` column requirement
- ✅ objdiff right-click → copy mangled name workflow documented
- ❌ Systematic function naming workflows still Discord-only
- ❌ Weak symbol duplicate handling not fully documented

**See:** `COMMUNITY/discord-insights-tools.md` §5

---

### 7. Code Review Standards & Contribution Guidelines
**Status:** ✅ Substantially addressed by Discord mining
- ✅ PR requires byte-matching DOL (not individual function matching)
- ✅ `#ifdef NONMATCHING` required; `#if 0` rejected
- ✅ Symbol naming conventions documented (CamelCase methods, lowercase C)
- ✅ Alignment directives (`.balign 8`) requirement documented
- ✅ Leaked SDK headers: community has unresolved debate; leaked compilers accepted
- ❌ Per-project PR checklists vary by lead; still learned through submitted PRs
- ❌ No public CONTRIBUTING.md exists in any major project

**See:** `COMMUNITY/discord-insights-general.md` §2

---

### 8. Multi-ROM/VERSION Support Strategies
**Status:** ⚠️ Partially addressed
- ✅ MusyX version guard pattern documented (`MUSY_VERSION_CHECK`)
- ✅ EGG version differences documented (`EGG_VERSION 200704L`)
- ✅ SDK per-module versioning strategy documented
- ✅ Mario Party 4 tracked both 1.00 and 1.01 build targets
- ❌ `configure.py --version` implementation patterns not documented
- ❌ PAL vs NTSC conditional compilation patterns not documented

**See:** `COMMUNITY/discord-insights-libraries.md`

---

### 9. Testing & Verification Strategies
**Status:** ⚠️ Partially addressed
- ✅ Verification method: `objdiff` green + SHA1 hash of built DOL
- ✅ `ninja baseline` / `ninja changes` targets for regression detection
- ✅ decomp.dev progress tracking serves as continuous integration feedback
- ❌ No formal unit testing; no fuzzing practices documented
- ❌ "Nonsense function" detection (correct bytes, wrong semantics) — only human review

**See:** `COMMUNITY/discord-insights-tools.md` §2, §7

---

## 🟢 MINOR GAPS (Nice-to-have, May Exist Elsewhere)

### 10. Performance Optimization
- Parallel build configuration
- Ninja job count tuning
- Cache management (dtk cache, wibo cache)
- Disk space optimization strategies

---

### 11. Debugging Techniques
- Dolphin debugger integration (breakpoints in decompiled code)
- Memory watch patterns
- Assembly inspection tools
- Logging strategies

---

### 12. Legal/Clean Room Procedures
- What materials are legally safe to use
- Documentation requirements for clean room
- Licensing considerations (CC0 vs MIT vs public domain)
- Disclaimers and policies

---

## 📊 DETAILED BREAKDOWN BY TOPIC

*Updated 2026-04-17 after Discord mining*

| Topic | Pre-Discord | Post-Discord | Notes |
|-------|------------|--------------|-------|
| Getting started | 90% | 95% | devkitPPC r40 pitfall now documented |
| Tool reference | 80% | 95% | Build stamps, error table, AI workflows added |
| Workflow | 85% | 95% | wibo benchmarks, CI pattern documented |
| Challenges (deep-dives) | 85% | 97% | Peephole bug, gecko_float_typecons, mwcc-debugger |
| CI/CD | 20% | 70% | Pattern documented; exact YAMLs still private |
| SDK matrix | 35% | 92% | ✅ Full build stamp registry + per-game mapping |
| Build errors | 40% | 88% | ✅ 10 specific errors with solutions |
| Context patterns | 55% | 80% | ✅ m2c workflow, M2CTX pattern documented |
| Platform quirks | 45% | 90% | ✅ WSL, macOS, devkitPPC versioning |
| Symbol workflows | 50% | 70% | cwparse, objdiff demangler documented |
| Code standards | 25% | 80% | ✅ PR standards, NONMATCHING guard, naming |
| Multi-version | 40% | 70% | Version guards, per-module SDK dates |
| Testing | 30% | 60% | SHA1 + objdiff; no formal test suite exists |
| Performance | 35% | 70% | Ninja vs Make benchmarks, wibo vs Wine |
| Debugging | 30% | 75% | mwcc-debugger fully documented |
| Legal | 20% | 50% | Community consensus documented; no formal policy |
| JSystem | 50% | 92% | ✅ Per-game versions, sub-library coverage |
| EGG | 20% | 90% | ✅ Compiler flags, hierarchy, file map |
| MusyX | 40% | 95% | ✅ Version registry, game mapping, hardest function |
| Game: Melee | 70% | 92% | ✅ Compiler, cross-refs, file boundaries |
| Game: Animal Crossing | 60% | 88% | ✅ N64 architecture, JSystem flags |
| Game: Mario Party 4 | 50% | 92% | ✅ REL format, Hudson engine, milestones |
| AI-assisted decomp | 0% | 85% | ✅ Entirely new section from #ai channel |

---

## 🎯 RECOMMENDED DISCORD EXTRACTION PRIORITY

If you have access to the target Discord channel, extract in this order:

### **Phase 1: Critical Infrastructure**
1. **CI/CD patterns** - Ask: "How do you set up CI for matching builds?" "How do you test CI?"
2. **SDK version mapping** - Find pinned versions, ask: "What SDK does X game use?" "How to tell which SDK from binary?"
3. **Error troubleshooting** - Collect recent error logs + solutions
4. **Context file patterns** - Get example context files for complex JSystem code

### **Phase 2: Workflow Efficiency**
5. **Platform quirks guide** - OS-specific gotchas
6. **Symbol resolution** - Systematic workflows, scripts
7. **Code review standards** - What's expected in PRs
8. **Multi-version support** - Real examples

### **Phase 3: Advanced Topics**
9. Testing strategies
10. Performance optimization
11. Debugging techniques
12. Project management

---

## 🔍 SEARCH KEYWORDS FOR DISCORD

Use Discord's search (Ctrl+F) with these terms:

**Critical:**
- "ci" OR "workflow" OR "github actions"
- "SDK" OR "dolphin-sdk" OR "JSystem"
- "error" OR "failed" OR "doesn't build"
- "context" OR "m2c" OR "ctx.h"
- "wibo" OR "wine" OR "crossover"

**Significant:**
- "symbol" OR "demangle" OR "map file"
- "pr" OR "pull request" OR "review"
- "version" OR "pal" OR "ntsc" OR "rev"
- "test" OR "verify" OR "check"
- "platform" OR "macos" OR "windows" OR "linux"

**Minor:**
- "performance" OR "slow" OR "fast"
- "debug" OR "breakpoint"
- "legal" OR "clean room" OR "license"

---

## 📝 HOW TO DOCUMENT DISCORD INSIGHTS

When you extract Discord content, create files in these locations:

```
decompresearch/
├── GAPS/addressed/
│   ├── ci-cd-workflows.md           # From Phase 1, #1
│   ├── sdk-version-matrix.md        # From Phase 1, #2
│   ├── build-errors-troubleshooting.md  # From Phase 1, #3
│   ├── context-patterns.md          # From Phase 1, #4
│   ├── platform-quirks.md           # From Phase 2, #5
│   └── symbolic-resolution.md       # From Phase 2, #6
├── GAPS/partial/
│   ├── code-review-standards.md     # From Phase 2, #7
│   ├── multi-version-support.md     # From Phase 2, #8
│   └── testing-strategies.md        # From Phase 3, #9
├── COMMUNITY/
│   └── code-of-conduct.md           # If found (Discord norms)
└── GAPS.md                          # This master analysis
```

Each file should cite Discord sources:
```
Source: Discord #decomp-melee, user "username", date
Discord Message Link: (paste Discord message URL)
Confidence: High/Medium/Low
```

---

## 🚢 WHY PUBLIC SOURCES ARE LIMITED

Discord content is ephemeral:
- **No search engine indexing** (Discord blocks crawlers)
- **No public archives** (some bots exist but incomplete)
- **Rapidly outdated** (tool updates, bug fixes)
- **Conversational** (hard to extract clean documentation)

This is why **manual curation** remains necessary despite the excellent public GitHub docs.

---

## ✅ COMPLETION METRICS

**Public Documentation Status:** ✅ 70-75% Complete
- All major games documented
- Toolchain reference complete
- Core workflow explained
- Challenges deep-dived
- Community resources cataloged

**Missing Critical Content:** ❌ 25-30%
- CI/CD workflows
- SDK version matrix
- Build error reference
- Advanced context patterns
- Code review standards

**Estimated Discord Mining Effort:**
- Phase 1 (Critical): 8-12 hours of targeted Discord searching
- Phase 2 (Significant): 6-8 hours
- Phase 3 (Minor): 4-6 hours
- **Total:** 18-26 hours of focused extraction

---

*Last updated: 2026-03-30*
*Analysis depth: 50+ public sources examined, 28 documentation files created*
