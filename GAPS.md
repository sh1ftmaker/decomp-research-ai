# Knowledge Gaps: Discord vs Public Sources

**Analysis Date:** 2026-03-30  
**Updated:** 2026-04-17 — Discord mining complete; gaps reassessed  
**Public Coverage:** ~70-75% (original estimate)  
**Post-Discord Coverage:** ~92-95%  
**Remaining Gaps:** ~5-8%

> **Status Update (2026-04-17):** Discord archives for the GC/Wii Decompilation server have been analyzed (~1.8M lines across 20+ channels). Most critical gaps are now addressed. See `COMMUNITY/discord-tribal-knowledge.md` for the master synthesis and the `COMMUNITY/discord-insights-*.md` files for per-channel detail. Gaps marked ✅ below have been substantially filled.

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

## 🎯 RESIDUAL EXTRACTION PRIORITIES (post-April-2026)

The bulk extraction has happened. The items below are what would still benefit from focused work:

### **Highest leverage (would meaningfully change agent answers)**
1. **PPC permuter** — A real implementation, not just discussion. Currently does not exist publicly; would need original engineering, not extraction.
2. **CI YAML files** — Convince at least one major project (Melee, TP, AC, MP4) to commit a non-secret subset of their workflow files publicly.
3. **Per-project PR checklists** — Even one written-up checklist from a maintainer would close most of the "what's expected in a PR" question.

### **Medium leverage (refines existing answers)**
4. **WSL ARM64 / Snapdragon** — As Copilot+ PCs proliferate, this will start mattering.
5. **Linux distro-specific issues** — Especially around 32-bit library availability (Arch, Fedora, NixOS).
6. **Per-project preset drift on decomp.me** — Which projects publish which preset, and why some are intentionally held back.
7. **JSystem template context strategies** — The remaining edge of m2c context engineering.

### **Lower leverage (nice-to-have, low impact)**
8. Formal testing/fuzzing practices (currently: SHA1 + objdiff + human review).
9. Cross-distro performance benchmarks for Ninja/wibo.
10. Legal/clean-room formalization (currently: community consensus, no written policy).

---

## 🔍 SEARCH KEYWORDS FOR LIVE DISCORD (residual gaps)

If you have live Discord access and want to fill the residual ~5–8%, search for:

- "ci" + "secret" / "workflow_dispatch" — for the unpublished YAML files
- "permuter" + "ppc" / "powerpc" — for any progress on PPC permuter
- "snapdragon" / "wsl arm" / "arm64" — for the platform-quirk gap
- "checklist" / "before merging" / "review" — for per-project PR standards
- "preset" + "decomp.me" / "scratch" — for preset publication policies

For everything else, **check `COMMUNITY/discord-insights-*.md` first** — it's likely already extracted.

---

## 📝 HOW TO DOCUMENT NEW DISCORD INSIGHTS

When you extract additional Discord content, add it to the existing `COMMUNITY/` files rather than creating new top-level structure:

```
COMMUNITY/
├── discord-insights-README.md           # Update index if you add a new file
├── discord-tribal-knowledge.md          # Master synthesis — add to relevant section
├── discord-insights-match-help.md       # Regalloc/inline/switch additions
├── discord-insights-tools.md            # Tool-specific additions
├── discord-insights-games.md            # Per-game additions
├── discord-insights-libraries.md        # JSystem/EGG/MusyX/SDK additions
├── discord-insights-general.md          # Onboarding/PR/platform additions
└── zelda-insights-*.md                  # Zelda-server-specific additions
```

Cite as:
```
Source: GC/Wii Decompilation Discord, #channel-name, paraphrased (April 2026 synthesis)
Confidence: High/Medium/Low
```

**Do not** include raw message text or usernames. The COMMUNITY/ folder is paraphrased synthesis only — see `COMMUNITY/discord-insights-README.md` for the privacy policy.

---

## 🚢 WHY DISCORD KNOWLEDGE IS STILL HARD TO ACCESS LIVE

Discord content is ephemeral:
- **No search engine indexing** (Discord blocks crawlers)
- **No public archives** (the April 2026 synthesis is itself a snapshot)
- **Rapidly outdated** (tool updates, bug fixes — the snapshot ages)
- **Conversational** (hard to extract clean documentation)

The April 2026 synthesis is the first systematic extraction; expect periodic re-syntheses to be necessary.

---

## ✅ COMPLETION METRICS (current)

**Combined coverage:** ✅ ~92–95%
- All major games documented (12 deep-dives + 76+ tracked)
- Toolchain reference complete (TOOLS/overview.md + COMMUNITY/discord-insights-tools.md)
- Core workflow explained (WORKFLOW/* + COMMUNITY/discord-insights-general.md)
- Challenges deep-dived (CHALLENGES/* + COMMUNITY/discord-insights-match-help.md)
- Community resources cataloged (COMMUNITY/websites.md)
- MWCC build registry, per-game flags, library version registries (COMMUNITY/discord-tribal-knowledge.md, COMMUNITY/discord-insights-libraries.md)
- AI-assisted decomp workflows captured (COMMUNITY/discord-insights-tools.md)

**Residual gap:** ❌ ~5–8%
- PPC permuter (non-existent publicly)
- Exact CI/CD YAML files (pattern documented; specific files private)
- Per-project PR checklists (vary by maintainer)
- Live in-progress conversation (by definition not in any archive)
- A few platform corners (WSL ARM64, some Linux distros)

---

*Last updated: 2026-04-19*
*Analysis depth: 50+ public sources + ~1.8M lines of Discord conversation synthesized into 14 COMMUNITY files (~2,415 lines)*
