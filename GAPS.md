# Knowledge Gaps: Discord vs Public Sources

**Analysis Date:** 2026-03-30  
**Public Coverage:** ~70-75%  
**Discord-Only Knowledge:** ~25-30%  

This document identifies what information is publicly available versus what remains trapped in Discord servers (particularly `ZeldaRET` and `doldecomp`). Use this as a guide for targeted Discord extraction.

---

## 🔴 CRITICAL GAPS (High Impact, Nearly Impossible to Find Publicly)

### 1. CI/CD & Testing Workflows
**Status:** ❌ Not found in any public repo
- Actual `.github/workflows/*.yml` files (all 404'd)
- Automated matching verification (how do they test CI?)
- Build matrix configurations (OS, compiler version matrices)
- Integration testing for multiple games
- Regression testing strategies
- Coverage metrics and reporting

**Where to find in Discord:** Search for "CI", "workflows", "testing", "automated", "GitHub Actions"

---

### 2. SDK Version Matrix (Per Game)
**Status:** ⚠️ Fragmented, no centralized mapping
- Exact dolphin-sdk versions used per game (1.0 vs 1.2 vs JSystem variants)
- MWCC compiler versions per library (1.2.5 vs 1.2.5n vs 1.3.2)
- How to identify SDK version from binary signatures
- Known incompatibilities between SDK versions
- Which SDK features require which compiler flags

**Where to find in Discord:** Search "SDK version", "MWCC", "compiler version", "dolphin-sdk", "JSystem"

---

### 3. Build Error Troubleshooting Reference
**Status:** ⚠️ Only scattered in issues/chat
- Common dtk error messages and solutions
- objdiff configuration pitfalls (when to check/uncheck options)
- mwldeppc linker errors (deadstrip, extab, weak symbols)
- Wine/wibo compatibility matrix (OS version → Wine version)
- "Relax relocations" - when to use vs when it hides real mismatches
- "Function permutation failed" - causes and fixes
- "Relocation overflow" - how to split sections

**Where to find in Discord:** Search specific error messages, "dtk error", "objdiff not updating", "wibo crash"

---

### 4. Advanced Context File Patterns (m2c)
**Status:** ⚠️ Basic context generation documented, master patterns hidden
- Complex JSystem C++ context examples (templates, inheritance)
- How to handle heavily templated code
- Multi-game shared context strategies (melee + ttyd both use JSystem)
- Context file evolution (how to know when to regenerate vs hand-edit)
- Order-dependent includes and macro conflicts
- Demangling C++ symbols in context

**Where to find in Discord:** Search "context file", "m2c context", "JSystem", "templates", "demangle"

---

## 🟡 SIGNIFICANT GAPS (Useful, Partially Available Publicly)

### 5. Platform-Specific Quirks
**Status:** ⚠️ Some documented, many edge cases missing
- Windows vs macOS vs Linux differences in build times
- WSL2 limitations (objdiff filesystem notifications don't work)
- Homebrew vs pip installation differences
- Wine version requirements (crossover vs vanilla Wine)
- ARM64 Mac (M1/M2/M3) compatibility issues and Rosetta usage
- Linux distribution-specific issues (Ubuntu vs Fedora vs Arch)

**Public sources:** Basic setup guides mention WSL is discouraged, Wine needed on macOS
**Discord needed:** Specific error logs, workarounds, version pinning

---

### 6. Symbol Resolution Best Practices
**Status:** ⚠️ File formats documented, workflow not
- How to systematically find function names from assembly
- Using map files effectively (which ones are trustworthy)
- Demangling C++ symbols and reading them
- Handling weak symbol duplicates across libraries
- When to use `__destroy` vs `__dt__` naming
- Decomp.me hints - how reliable are they?

**Public sources:** `symbols.txt` format, basic demangling tool
**Discord needed:** Real workflows, common pitfalls, tool scripts

---

### 7. Code Review Standards & Contribution Guidelines
**Status:** ❌ Virtually no formal documentation
- What makes a PR mergeable (matching % thresholds, test requirements?)
- Commit message format conventions
- Code style guidelines beyond clang-format (naming, organization)
- Required testing before PR
- Review process (who reviews, turnaround time)
- Handling merge conflicts in active modules

**Public sources:** None (no CONTRIBUTING.md found in major repos)
**Discord needed:** Entirely Discord-based governance

---

### 8. Multi-ROM/VERSION Support Strategies
**Status:** ⚠️ Basic version flags documented, patterns not
- PAL vs NTSC differences handling (conditional compilation)
- Managing multiple revisions (Rev0, Rev1, Rev2)
- Shared code across versions and version-specific overrides
- `configure.py --version` implementation patterns
- How to add a new version support

**Public sources:** Basic `--version` flag usage
**Discord needed:** Real project examples, debugging version mismatches

---

### 9. Testing & Verification Strategies
**Status:** ⚠️ objdiff usage documented, testing minimal
- Manual testing procedures after matching
- Automated testing approaches (any unit tests?)
- Regression testing when upstream changes
- How to verify byte-perfect beyond objdiff green
- Testing rare code paths and edge cases
- Fuzzing or property-based testing

**Public sources:** objdiff UI usage, build verification
**Discord needed:** Actual QA practices, known untested areas

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

| Topic | Public | Discord | Notes |
|-------|--------|---------|-------|
| Getting started | 90% | 10% | Guides exist, but current pitfalls not |
| Tool reference | 80% | 20% | Basic usage clear, edge cases hidden |
| Workflow | 85% | 15% | Binary split documented, subtleties not |
| Challenges (6 deep-dives) | 85% | 15% | Theory documented, real cases not |
| CI/CD | 20% | 80% | ⚠️ Critical gap |
| SDK matrix | 35% | 65% | ⚠️ Critical gap |
| Build errors | 40% | 60% | ⚠️ Critical gap |
| Context patterns | 55% | 45% | ⚠️ Critical gap |
| Platform quirks | 45% | 55% | Scattered, needs curation |
| Symbol workflows | 50% | 50% | Format doc'd, process not |
| Code standards | 25% | 75% | ⚠️ Almost entirely Discord |
| Multi-version | 40% | 60% | More complex than docs suggest |
| Testing | 30% | 70% | Minimal formal testing docs |
| Performance | 35% | 65% | Optimizations shared orally |
| Debugging | 30% | 70% | Techniques tribal |
| Legal | 20% | 80% | Policies exist only in Discord |

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
