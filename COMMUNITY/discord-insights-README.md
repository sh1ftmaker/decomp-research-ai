# Discord Insights — Index

This folder contains synthesized knowledge extracted from the GC/Wii Decompilation Discord server (~1.8M lines, 20+ channels, analyzed April 2026).

**All usernames have been anonymized. No raw message content is included. Insights are paraphrased and synthesized.**

## Files

### GC/Wii Decompilation Discord

| File | Source Channel | Lines | Status |
|------|---------------|-------|--------|
| discord-tribal-knowledge.md | **Master synthesis** (all channels) | ~580 | ✅ Complete |
| discord-insights-match-help.md | #match-help | 440 | ✅ Complete |
| discord-insights-tools.md | #compilers, #objdiff, #decomp-toolkit, #m2c, #ai, #ghidra, #mwcc-debugger, etc. | 460 | ✅ Complete |
| discord-insights-games.md | #smash-bros-melee, #animal-crossing, #mario-kart-double-dash, #mario-party | 270 | ✅ Complete |
| discord-insights-libraries.md | #jsystem, #egg, #musyx, #sdk | 392 | ✅ Complete |
| discord-insights-general.md | #general, #announcements, #resources | 273 | ✅ Complete |

### Zelda Decompilation Discord

| File | Source Channel | Focus | Status |
|------|---------------|-------|--------|
| zelda-insights-tww.md | #tww-decomp, #tww-decomp-help | Wind Waker matching techniques | ✅ Complete |
| zelda-insights-m2c.md | #m2c | mips_to_c / m2c decompiler (N64 MIPS→C) | ✅ Complete |
| zelda-insights-permuter.md | #permuter | decomp-permuter tool internals & workflow | ✅ Complete |
| zelda-insights-decomp-me.md | #decomp-me | decomp.me platform design & architecture | ✅ Complete |
| zelda-insights-ido-decomp.md | #ido-decomp | IDO (IRIX) compiler reverse engineering | ✅ Complete |
| zelda-insights-framework.md | #decomp-framework | N64 decomp framework founding debates | ✅ Complete |
| zelda-insights-tools-other.md | #tools-other | diff.py, Ghidra, IDA, n64split, ROM format | ✅ Complete |

**Total synthesized:** ~2,415 lines of actionable knowledge extracted from ~1.8M lines of Discord conversation.

## Key Findings Summary

### Most Impactful Discoveries
1. **Peephole optimizer bug** — `asm {}` blocks disable peephole for rest of file; fix with `#pragma peephole on`
2. **Full MWCC build stamp registry** — All GC/Wii compiler versions with exact build numbers
3. **`const` changes register assignment** — Adding/removing `const` on pointers shifts register coloring
4. **`#pragma gecko_float_typecons on`** — Undocumented pragma discovered by searching compiler binary
5. **`-ipa file` changes inline ordering** — Explains decomp.me vs. local build discrepancies
6. **mwcc-debugger** — Tool for inspecting MWCC's internal virtual register assignment (enables surgical regalloc fixes)
7. **MusyX version registry** — Full version-to-game mapping with identification method
8. **devkitPPC r40 breaking change** — Documented with fix and archived r39 download location

### Gaps Now Filled (was in GAPS.md as critical)
- ✅ SDK Version Matrix — now documented in discord-insights-libraries.md
- ✅ Build Error Troubleshooting — 10 specific errors with solutions
- ✅ Advanced m2c Context Patterns — preprocessing workflow, M2CTX, jump table labels
- ✅ Platform Quirks — WSL, macOS, wibo vs. Wine, devkitPPC versioning
- ✅ Code Review Standards — PR requirements, NONMATCHING guard, naming conventions
- ✅ AI-Assisted Decompilation — Workflows, model comparison, known limitations
- ⚠️ CI/CD YAML configs — Pattern documented; exact files still not in public repos
- ❌ PPC permuter — Still does not exist publicly

## Privacy Notes

- All Discord usernames replaced with role descriptors (contributor, maintainer, tool author, etc.)
- No raw message content reproduced
- Insights are paraphrased and synthesized, not quoted
- The source JSON files are NOT committed to this repository
- The `decomp discord/` folder is gitignored
