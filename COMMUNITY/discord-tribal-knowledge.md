# Discord Tribal Knowledge: Master Synthesis

**Source:** doldecomp Discord server — 5 channel categories, ~1.8M lines analyzed  
**Extracted:** 2026-04-17  
**Coverage:** #match-help, #compilers, #objdiff, #decomp-toolkit, #m2c, #ai, #tools-general, #decomp-dev, #ghidra, #mwcc-debugger, #jsystem, #egg, #musyx, #sdk, #general, #smash-bros-melee, #animal-crossing, #mario-kart-double-dash, #mario-party, #announcements, #resources  
**Privacy:** All usernames anonymized. No verbatim quotes reproduced.

> This document synthesizes the highest-value insights. For full detail on any topic, see the per-channel files in this folder.

---

## Table of Contents

1. [Critical Discoveries (Read First)](#1-critical-discoveries-read-first)
2. [Compiler Version Registry](#2-compiler-version-registry)
3. [Confirmed Game Compiler Flags](#3-confirmed-game-compiler-flags)
4. [Pragma Reference (Documented + Undocumented)](#4-pragma-reference-documented--undocumented)
5. [Matching Techniques Cheat Sheet](#5-matching-techniques-cheat-sheet)
6. [Tool Reference: Operational Knowledge](#6-tool-reference-operational-knowledge)
7. [Library Knowledge: JSystem, EGG, MusyX, SDK](#7-library-knowledge-jsystem-egg-musyx-sdk)
8. [Game-Specific Insights](#8-game-specific-insights)
9. [Community Standards and Practices](#9-community-standards-and-practices)
10. [Platform Setup and Toolchain](#10-platform-setup-and-toolchain)
11. [Infrastructure and Resources](#11-infrastructure-and-resources)
12. [Gaps That Remain](#12-gaps-that-remain)

---

## 1. Critical Discoveries (Read First)

These are the "aha moments" from the archive — insights that unlocked many previously-stuck functions and are now considered standard knowledge.

### The Peephole Optimizer Bug

**Any `asm {}` block in a source file silently disables the peephole optimizer for all subsequent C functions in that file.** This is a confirmed bug in MWCC 1.2.5 and related versions.

Symptoms: functions after an `asm` block produce `beq label` + `blr` instead of the single `beqlr` instruction; missing `mr.` combinations; slightly wrong branch-to-return folding.

Fix:
```cpp
asm void myAsmFunc() { /* ... */ }

#pragma push
#pragma peephole on
void myNormalFunc() { /* will now use peephole */ }
#pragma pop
```

This affects header-included inline asm functions too — the bug activates at the include point.

---

### `const` Changes Register Assignment

Adding or removing `const` on a pointer type changes which physical register MWCC assigns to it. The compiler must prove the value cannot alias before it can keep it in a register across other operations. This is the first technique to try when you have a single register swap:

```cpp
// Try: void* instead of const void*, or vice versa
// Try: (void*) cast on a pointer variable
// These are semantically equivalent but produce different register coloring
```

---

### `-ipa file` Changes Inline Ordering

Functions that match on decomp.me but not locally are often caused by decomp.me including `-ipa file` by default. Adding this flag to the local build fixes the ordering of inlined code blocks. Note: `-ipa file` only works in MWCC 3.0+.

---

### Macro vs. Inline: The `__LINE__` Test

If an assertion or error-reporting call shows the **same line number** across all call sites → it is an **inline function** (line number fixed at definition). If each call site shows a **different line number** → it is a **macro** (each expansion captures its own line).

---

### `#pragma gecko_float_typecons on`

An undocumented pragma discovered by text-searching the compiler binary. It affects float type conversion code generation in a way not in any official manual. Confirmed to change generated code for specific float patterns.

---

### Volatile Forces Stack Roundtrip

`volatile float intermediateVar = expr;` forces the compiler to store to the stack and reload, reproducing unusual `stfs` + `lfs` pairs that appear in optimized float operations. Used successfully to match fast-distance functions.

---

## 2. Compiler Version Registry

The canonical MWCC build stamp registry, as documented by the community. Reference by build stamp — more precise than the CodeWarrior package version label.

### GameCube Compilers

| Build Stamp | CW Package | Runtime Date | Key Games |
|-------------|-----------|--------------|-----------|
| `Version 2.3.3 build 144` | GC CW 1.0 | Apr 13 2000 | Very early GC devkits |
| `Version 2.3.3 build 159` | GC CW 1.1 | Feb 7 2001 | Melee (Build 156/158 variant) |
| `Version 2.3.3 build 163` | GC CW 1.2.5 | Apr 23 2001 | Super Mario Sunshine, early titles |
| `Version 2.4.2 build 81` | GC CW 1.3.2 | May 7 2002 | Animal Crossing RELs, some JSystem |
| `Version 2.4.7 build 92` | GC CW 2.0 | Sep 16 2002 | |
| `Version 2.4.7 build 105` | GC CW 2.5 | Feb 20 2003 | |
| `Version 2.4.7 build 107` | GC CW 2.6 | Jul 14 2003 | Mario Kart DD, Mario Party 4 |
| `Version 2.4.7 build 108` | GC CW 2.7 | Jul 22 2004 | Late GC games |
| `Version 4.1 build 60831` | GC CW 3.0 | Aug 31 2006 | |

### Wii Compilers

| Build Stamp | CW Package | Runtime Date |
|-------------|-----------|--------------|
| `Version 4.2 build 142` | Wii CW 1.0 | Aug 26 2008 |
| `Version 4.3 build 151` | Wii CW 1.1 | Apr 2 2009 |
| `Version 4.3 build 172` | Wii CW 1.3 | Apr 23 2010 |
| `Version 4.3 build 213` | Wii CW 1.7 | Sep 5 2011 |
| `Version 4201_127` | (EGG/MKW) | — |

**Important:** Build 163 (GC CW 1.2.5) has a branch-related codegen bug absent from build 159. This distinction matters for byte-exact matching in Melee-era games.

### Compiler Identification Methods (in reliability order)

1. Check the MetroTRK version string embedded in the binary
2. Check SDK build date strings: `<< Dolphin SDK - OS release build: Sep 5 2002 >>` — pins the build date range
3. Try simple functions on CExplorer/decomp.me with different compilers
4. Use game release date as upper bound

Online sandbox: `cexplorer.red031000.com` (sometimes down; decomp.me preferred)

---

## 3. Confirmed Game Compiler Flags

These flag sets are confirmed from community analysis of matching builds — not guesses.

### Super Smash Bros. Melee

```
-O4,p -fp hard -proc 750
```
(NOT `-proc gekko` — Melee appears to have been compiled without the `__PPCGEKKO__` define)
- sysdolphin layer likely used `-proc 750 -O4,p`
- `-fp_contract on` must be passed as `#pragma fp_contract on`, not as compiler flag
- `-inline deferred` causes cross-function interference; handle carefully
- Compiler is approximately **MWCC Build 156/158** (early 2001 vintage)

### Animal Crossing (DOL)

```
-fp hard -proc gekko -enum int -O4,p -Cpp_exceptions off
```
- JSystem within AC requires separate flags: `-fp hard -proc gekko -enum int -O4,p -Cpp_exceptions off -inline auto` plus `-sym on`
- JSystem `.sdata` threshold is **8** (not default 4)
- REL modules use **MWCC 1.3.2**
- Linker: `-fp hard -w off -maxerrors 1 -mapunused`
- Common mistake: `-fp hard` must be on the **compiler** command, not just the linker

### Mario Kart: Double Dash (Release)

```
-O4,p (Kaneshige), -O4,s -peephole off (JMath release), -O0 (some OsakoM input files)
```
- Main game: **MWCC 2.6**
- MSM audio library: **MWCC 1.2.5**
- JSystem in MKDD was built with `peephole off` for release

### Mario Party 4

```
-O4,p (main DOL, MWCC 2.6)
-O4,p (MSM audio, MWCC 1.2.5)
-pool on (string pooling enabled)
```

### Paper Mario TTYD

```
-Cpp_exceptions off -proc gekko -fp hard -O4,p -nodefaults -msgstyle gcc
-sdata 48 -sdata2 8 -inline all,deferred -use_lmw_stmw on -enum int -maf on
```
(with project-wide `#pragma defer_codegen on`, `#pragma auto_inline on`)

### Super Mario Galaxy (approximate)

```
-c -nodefaults -proc gekko -DHOLLYWOOD_REV -DEPPC -enum int -fp hard
-Cpp_exceptions off -rtti off -ipa file -O4,s -inline auto
```
NW4R library code within SMG uses `-O4,p` (performance, not size).

### Pikmin 2

```
-Cpp_exceptions off -proc gekko -RTTI off -fp hard -fp_contract on -rostr
-O4,p -use_lmw_stmw on -sdata 8 -sdata2 8 -nodefaults -msgstyle gcc
```

### EGG Library (Mario Kart Wii)

```
-lang=c99 -use_lmw_stmw=on -ipa function -rostr
```
`eggHeap.cpp` additionally uses `-ipa file`. Compiler: `4201_127`.

### Wii game general template

```
-nodefaults -proc gekko -DRELEASE -Cpp_exceptions off -gccinc -O4,s
-fp hardware -enum int -sdata 4 -sdata2 4 -lang=c99 -align powerpc
-inline auto -W noimplicitconv -DEPPC -DHOLLYWOOD_REV -DTRK_INTEGRATION
-DGEKKO -DMTX_USE_PS -MMD -rtti off -ipa file
```

---

## 4. Pragma Reference (Documented + Undocumented)

### Optimization Control

| Pragma | Effect |
|--------|--------|
| `#pragma optimization_level N` | Set optimizer level 0–4 for subsequent functions |
| `#pragma optimize("O4,p", on)` | Set level + speed/space tradeoff simultaneously |
| `#pragma optimizewithasm off` | Disable optimization for functions with inline asm |
| `#pragma opt_propagation off` | Prevent constant propagation (undocumented) |

### Scheduling Control

| Pragma | Effect |
|--------|--------|
| `#pragma scheduling off` | Disable instruction scheduling |
| `#pragma scheduling 750` | Force PPC 750 pipeline model |
| `#pragma scheduling on` | Re-enable scheduling |

### Inlining Control

| Pragma | Effect |
|--------|--------|
| `#pragma always_inline on` | Force all inline-declared functions to always inline |
| `#pragma auto_inline on/off` | Enable/disable automatic inlining |
| `#pragma inline_depth(N)` | Set maximum inline chain depth |
| `#pragma inline_bottom_up off` | Change top-down vs. bottom-up inline order |
| `#pragma defer_codegen on` | Defer code emission to end of TU (affects inline ordering) |
| `#pragma warn_notinlined off` | Suppress "could not inline" warnings |

### Peephole, Jump Tables, Sections

| Pragma | Effect |
|--------|--------|
| `#pragma peephole on/off` | Enable/disable peephole optimizer (critical — see Section 1) |
| `#pragma switch_tables off` | Force branch chains instead of jump tables |
| `#pragma section code_type ".init"` | Place functions in `.init` section |
| `#pragma force_active on` | Prevent dead-code stripping |
| `#pragma use_lmw_stmw on/off` | Enable/disable `stmw`/`lmw` multi-register save/restore |

### Data and Pooling

| Pragma | Effect |
|--------|--------|
| `#pragma pool_data on/off/reset` | Control data pooling behavior |
| `#pragma cats off` | Suppress CATS profiling data; reduces ELF size ~30% (undocumented) |
| `#pragma c9x on` | Partial C99 mode (compound literals work, VLAs do not) |

### Undocumented Pragmas (Discovered from Compiler Binary)

| Pragma | Effect |
|--------|--------|
| `#pragma gecko_float_typecons on` | Changes float type conversion code generation |
| `#pragma fp_contract on` | Enable fused multiply-add (sometimes must be pragma not flag) |
| `#pragma scheduling 401–860` | Select specific processor pipeline models |

### The Push/Pop Pattern

Always use push/pop for per-function pragma control:
```cpp
#pragma push
#pragma optimization_level 2
void specificFunction() { /* ... */ }
#pragma pop
```

---

## 5. Matching Techniques Cheat Sheet

### Register Allocation (Most Common Issue)

- MWCC allocates non-volatile registers top-down: first variable declared → `r31`, next → `r30`, etc.
- **Reorder variable declarations** to shift register assignments.
- **Add/remove `const`** on pointer variables — changes which register the compiler assigns.
- **`(void*)` cast** forces the compiler to treat a variable as a new slot.
- **`register` keyword** forces specific register positions (brittle — use sparingly).
- **Explicit intermediate variables** for return values affect liveness and shift assignments.
- **`stmw` starts at wrong register?** Adjust number of nonvolatile registers used.
- For deep analysis: use `mwcc-debugger` to see virtual register numbering.

### Register Allocation: mwcc-debugger Insights

- Variables receive "virtual register numbers" at creation time. Lower virtual number → lower priority → higher-numbered physical register.
- Pressure threshold for spilling is 29 neighbors (30 allocatable GPRs).
- The "coalescing bug": MWCC merges a temporary into a physical register but doesn't remove it from the interference graph — this inflates neighbor counts, exploitable to shift other variables.
- Fix strategies: declare variables earlier (lower VRN), add `(void)param;` to introduce coalescing temporaries, replace struct field accesses with temporaries.

### Inline Functions

- **Recognizing inline:** same `__LINE__` at all call sites = inline function; different = macro.
- **Getting inlining:** `-inline auto`, `#pragma always_inline on`, or define body in header file.
- **Preventing inlining:** `-inline off` or `#pragma auto_inline off` (removing `inline` keyword alone does NOT prevent auto-inlining).
- **Depth limit exceeded:** if a function only inlines at some call sites, the call chain may exceed MWCC's depth limit. Use `#pragma always_inline on`.
- **Double `beq beq` at function start** = inlined destructor from parent class.

### Switch Statements

- Dense cases → jump table in `.rodata`; sparse or small → branch chain.
- `#pragma switch_tables off` forces branch chains for all switches.
- Default case placement in source affects branch ordering.
- `switch(localVar)` vs. `switch(field->member)` changes branch ordering.

### Float Patterns

- `fcmpo` = ordered comparison (NaN can raise exception); `fcmpu` = unordered.
- `cror 2, 1, 2` (cror EQ, GT, EQ) = NaN-aware `>=` comparison — standard C `>=` generates this, no special syntax needed.
- `fctiwz` + `stfd` + `lwz offset+4` = float-to-int via stack (MWCC's standard pattern).
- `fmadds` requires both `-fp fmadd` (or `-fp_contract on`) AND single-precision operands.
- `frsp` appears when double-precision intermediate is rounded to single. Use `fmuls` (not `fmul`) to avoid it.
- `volatile float x = expr;` forces store+reload through stack — reproduces unusual `stfs`/`lfs` patterns.
- `abs(x)` on integers → `srawi rA, rX, 31` / `xor rB, rA, rX` / `subf rB, rA, rB` (branchless).
- `x == 0` returning int → `cntlzw` + `srwi` pattern.

### Struct and Alignment

- `-sdata N -sdata2 N`: variables ≤ N bytes go to small data sections (`.sdata`/`.sdata2`). Access via `r13`/`r2` instead of `lis+addi`.
- All TUs must use the same `-sdata` threshold or the linker errors on small-data relocations.
- `-use_lmw_stmw on`: enables `stmw`/`lmw`. Without it: individual `stw`/`lwz` or `_savegpr` stubs.
- `_savegpr_N` stubs appear with `-O4,s` (size optimization).

---

## 6. Tool Reference: Operational Knowledge

### objdiff

- Config file: `objdiff.yml` or `objdiff.json`. Projects should ship this file.
- Startup failure on Windows: delete `%APPDATA%\objdiff` to reset stale config.
- Symbol sizes are inferred from the next label — use `.fn`/`.endfn` macros for accurate sizes.
- Data sections count as "matched" only when the **entire** section matches 100%.
- `-sym on` (MWCC debug symbols) can cause incorrect objdiff diffs — be aware.
- `report generate` CLI command → `VERSION_report` artifact → consumed by decomp.dev.
- Filesystem watching in v0.5.1+ covers externally-changed files.
- objdiff v3 introduced breaking changes to report format; check when upgrading.

### decomp-toolkit (dtk)

- Entry points: `dtk dol split` (DOL → per-object `.s`), `dtk rel info` (REL inspection).
- `dtk elf fixup` patches GNU-assembled objects for CodeWarrior linker compatibility.
- Re-running `dtk dol split` without clearing output → `File exists (os error 17)` → delete `asm/` directory first.
- `Conflicting size for <symbol>` warning = safe to proceed, manually verify boundary.
- `Unpaired epilogue` = unusual control flow (overlapping functions, tail-call edge cases) — fixed in later dtk by adding boundary hints.
- Wii linker quirk: MWLD 2.7+ requires a `.comment` section and `__init_cpp_exceptions.cpp` file symbol — dtk can generate these automatically.
- DWARF 1.1 debug info can be parsed for function boundaries (`RUST_LOG=debug` for verbose output).
- Symbol hashing for SDK library matching uses relocation-aware approach.
- dtk is updated frequently; most "bugs" are fixed in HEAD before being reported.

### m2c

- Input: `doldisasm`/`reldisasm` format. Raw `objdump` output does not work cleanly.
- Context files dramatically improve output. Preprocess with `-E` (preprocessor only) and feed output.
- `--reg-vars` flag: use named variables for saved registers instead of `temp_rN` — strongly recommended.
- `M2C_STRUCT_COPY`: m2c detected unrolled struct copy. Replace with `*dst = *src` or `memcpy` as appropriate.
- Jump tables require label starting with `jtbl`, `jpt_`, `lbl_`, or `jumptable_` before `bctr`.
- `psq_l` (paired-single load) not supported — exclude or suppress.
- Context file `#ifdef`/`#ifndef` guards not supported — flatten with preprocessor first.
- `M2CTX` macro pattern: Melee uses `#ifdef M2CTX` in headers for better m2c type inference vs. correct codegen.

### Ghidra

- Use the community fork at `github.com/encounter/ghidra-ci/releases` — includes improved PPC decompiler and paired-single decoding.
- Ghidra server: `ghidra.decomp.dev` (migrated from earlier domain).
- SDA21 relocations are not supported by mainline Ghidra — community fork partially mitigates.
- Import symbol map: remove the `Offset` column (newer format breaks the importer).
- Use Ghidra for exploratory analysis and struct discovery; use m2c for matching-ready C.
- Ghidra C struct parser: add one struct at a time, not bulk imports.

### wibo vs. Wine

| | wibo | Wine |
|---|---|---|
| Speed | ~2x faster than Wine | Baseline |
| Compatibility | Most Metrowerks tools | Full Win32 support |
| Gaps | Cannot read Windows string resources | Full support |
| Install | Auto-downloaded by dtk-template | Manual install |

Build time comparison: one project benchmarked wibo at ~12s vs. Wine at ~25s for a full build.

### AI-Assisted Decompilation

**Current effective workflows (as of April 2026):**
- One-shot: provide target assembly + current C stub + objdiff output → ask model for matching C. Works well under ~100 instructions.
- Iterative agent loop: orchestrator spawns subagents for Ghidra exploration, C scaffolding, and iterative matching attempts.
- Two-model pipeline: cheaper model (fast draft) → more capable model (hard residuals). More cost-effective than using the best model for everything.
- Skills/slash commands define tool boundaries for agents: how to build, how to diff, which Ghidra instance to query.

**Model notes:**
- Claude Opus 4.6: strongest context retention, best for multi-step reasoning across large code contexts.
- Claude Sonnet 4.6: strong balance of quality and cost for most matching tasks.
- GPT-5.3-Codex: fewer thinking tokens for equivalent quality — economical for the compile-diff-fix loop.

**Known AI limitations:**
- MWCC register allocation: models cannot reliably derive C variable orderings that produce a specific register assignment from assembly alone.
- "Nonsense functions": AI can produce C that byte-matches but is semantically meaningless. Human verification is non-negotiable.
- Context exhaustion is a real risk on large functions or when Ghidra DWARF dumps are included.

### decomp.dev

**API endpoints:**
```
https://decomp.dev/<owner>/<repo>.json?mode=measures   # Current metrics (fast)
https://decomp.dev/<owner>/<repo>.json?mode=report     # Full function-level report
https://decomp.dev/<owner>/<repo>.json?mode=history    # Historical measurements
https://decomp.dev/<owner>/<repo>.svg?mode=shield      # Progress badge
```
- Report artifact must be named `VERSION_report` (e.g., `GALE01_report`).
- Minimum **0.5% matched** to appear publicly.
- Data matched % only counts when an entire section matches 100%.
- Progress metrics: `matched_code_percent`, `fuzzy_match_percent`, `complete_code_percent` (linked).

---

## 7. Library Knowledge: JSystem, EGG, MusyX, SDK

### JSystem

Every game has a slightly different JSystem version. A monolithic JSystem repo is impractical — add sub-libraries only once fully matched in a specific game.

**Evolution chain:** JSystem (GC) → NW4R + EGG (Wii) → NW4C (3DS) → NW4F (Wii U) → libnn (Switch)

**Library packaging:**
- SMS era and before: single `JSystem.a` archive
- TWW era and after: discrete archives (`JKernel.a`, `JUtility.a`, etc.)

**Compiler flags vary per sub-library.** Pikmin 1's JAudio requires `-proc 750` (unique — the only known case where the processor flag differs from the rest of the game). MKDD release JMath uses `-O4,s -peephole off`.

**Vtable ordering** is the dominant matching problem for J2D and any multi-file class hierarchy. Declare virtual functions in the same order as the vtable.

**Static class variables** cause BSS ordering issues. Workaround: declare them later in the TU.

**Key sub-library per-game status:**

| Sub-library | Notes |
|------------|-------|
| JKernel | Most widely used; AC uses older version |
| JSupport | First JSystem sub-lib fully matched (Pikmin 2) |
| JAudio | At least 4 distinct versions; Pikmin 1 requires `-proc 750` |
| JGadget | Pattern: `Vector_void`/`List_void` backing + template wrappers |
| JMessage | Mostly uncharted outside TP and Pikmin 2 |

### EGG Library

**Detection:** Presence of `EGG::ExpHeap::create` (always emits two adjacent `rlwinm`). Search for `eggExpHeap` strings.

**Inheritance:** `EGG::Vector2f`/`3f` inherits `nw4r::math::VEC2`/`VEC3`. `EGG::Quatf` inherits `EGG::Vector3f` (design mistake — x/y/z accessed via Vector3f members).

**Heap types:** `ExpHeap` (most common), `FrmHeap` (frame/stack), `UnitHeap` (fixed-block), `AssertHeap` (256 bytes for assert console).

`sizeof(EGG::Heap)` = `0x3C`. `EGG::Heap::alloc` uses `_savegpr_27` (useful fingerprint).

**Compiler flags (MKW):** `-lang=c99 -use_lmw_stmw=on -ipa function -rostr` with compiler `4201_127`. `eggHeap.cpp` additionally uses `-ipa file`.

### MusyX

**Version identification method:**
1. Find build date string in binary.
2. Check for `SetHWMix` (added in ≥ 1.5.4).
3. Check for `lastPSFromBuffer` assignment in `streamHandle` (absent in certain versions).

**Game-to-version mapping:**
| Game | MusyX Version |
|------|--------------|
| Metroid Prime | 1.5 patch 3 (with `-proc 750`/GC 1.2.5n) |
| Mario Party 4 | Between 1.5.3 and 1.5.4 |

**Hardest function:** `salBuildCommandList` — 0x294C bytes, ~50 local variables, manages DSP voice processing. This was matched for at least one version; adding subsequent version variants is described as straightforward.

**Assert macro form must match exactly:** `((cond) || (MUSY_PANIC(...), 0))`. A different form causes the entire function to not match.

**Version guard pattern:**
```c
#if MUSY_VERSION < MUSY_VERSION_CHECK(1, 5, 4)
    /* old code path */
#else
    /* new code path */
#endif
```

MusyX 2.0 SDK disc: `https://archive.org/details/musyx-2003-01-09`

### Dolphin SDK / RVL SDK

**Build string format:**
```
<< Dolphin SDK - <MODULE> release build: <DATE> (0x<COMPILER_VER>) >>
```
Compiler version encoding: `0x2301` = GC MW 2.3.0 Build 1; `0x4201_127` = Wii MW 4.2.0 Build 127.

**Important:** SDK modules within the same game have different build dates. GX, OS, DVD, and AX are frequently updated independently.

**Key game SDK dates:**
| Game | OS Version | Date |
|------|-----------|------|
| Luigi's Mansion | OS Rev 37 | 2001 |
| Super Monkey Ball / Melee | OS Rev ~37 | May 2001 |
| Twilight Princess | OS Rev 58 | Sep 5 2002 |

**Community SDK repos:**
- [doldecomp/dolsdk2001](https://github.com/doldecomp/dolsdk2001)
- [doldecomp/dolsdk2004](https://github.com/doldecomp/dolsdk2004)
- [doldecomp/sdk_2009-12-11](https://github.com/doldecomp/sdk_2009-12-11)

**OSGetTime encoding:** `mftbu`/`mftb`/`mftbu` — raw encoding `7C6D42E6 7C8C42E6 7CAD42E6`. Standard Linux assemblers may not recognize `mftb` in gekko mode; encode as `.4byte` literals.

---

## 8. Game-Specific Insights

### Super Smash Bros. Melee

- DOL split: game code (first half of text section) vs. CW PPC/Dolphin SDK library code (second half).
- sysdolphin (`HSD_*`) has confirmed file-to-address mappings for 18 source files.
- `hsd_gobj` is split across ≥3 translation units.
- File names can be cross-referenced from Bloody Roar: Primal Fury debug symbols.
- Fighter files use Japanese character names: `ftMario`, `ftFalco`, `ftseak` (Sheik), etc.
- `ftData` struct offset within fighter struct: `0x10C`.
- `SET_ATTRIBUTES` macro must be reproduced as a macro with forced pointer struct-copy.
- **GNW (Game and Watch)** identified as easiest fighter to match due to simple move set.
- Build SHA1 (NTSC 1.02): `08e0bf20134dfcb260699671004527b2d6bb1a45`.
- **Cross-reference resources:** Killer7 (leaked sysdolphin source), Bloody Roar: Primal Fury (debug symbols), FRAY project (struct definitions).

### Animal Crossing (GC)

- Architecture: N64 port (`Doubutsu no Mori+`) with N64 graphics emulator (`emu64`), N64 audio ROM format with GC DSP translation, and an in-game NES emulator (`Famicom.a`).
- `jaudio` is considered the hardest module — completely customized N64 audio library with GC DSP conversion.
- JSystem in AC uses older version than Pikmin 2; different vtable layout for `JKRHeap`.
- RTTI string ordering caused persistent mismatches near 99% completion. Resolved via separate JSystem compilation flags.
- N64 symbol map (`DnM+`) has two versions: a detailed map (with unused functions) and a trimmed one. The detailed map shows code stripped from the US GC release.

### Mario Kart: Double Dash

- Code organized by programmer surname: `KaneshigeM.a`, `OsakoM.a`, `YamamotoM.a`, `SatoM.a`, etc.
- **Kaneshige boolean style (required for matching):**
  ```c
  // Required:
  bool ret = false;
  if (condition) ret = true;
  return ret;
  // NOT: return condition;
  ```
- Multiple compiler flag presets within one DOL — needs 4-5 decomp.me preset configurations.
- Common BSS inflation bug caused by `JASFakeMatch.h` header — creates spurious `sinit` and float array in every including TU.
- Debug and release builds of the same function sometimes require different C source to match — use `#ifdef DEBUG`.

### Mario Party 4

- First GameCube game to reach 100% matched and 100% linked.
- Hudson engine: all content in REL v2 "DLL" files. Each minigame and board is a separate REL.
- REL build path embedded in binary: `e:\project\mpgce\prog\DLLS\bootDll\bootDll.elf`.
- REL format: `.ctors`/`.dtors` must be zeroed in section table; `.rodata` and `.data` aligned to 8 bytes.
- MSM audio library: MWCC 1.2.5. Main DOL: MWCC 2.6. Switching compiler versions caused ~10% immediate progress jump.
- **Hardest files:** `hsfdraw.c`, `player.c`, `mapspace.c`.
- **MusyX** was integrated as a submodule from another project — provided a significant free percentage boost.
- The 0.5 and 3.0 double constants (64-bit IEEE 754) appear as first items in `.rodata` for nearly every REL TU — useful verification check.

---

## 9. Community Standards and Practices

### PR Standards (de facto, no formal CONTRIBUTING.md)

- The **build as a whole** must match (byte-for-byte identical DOL). Individual functions in a PR don't each need to be 100% matching.
- Nonmatching functions **must** use `#ifdef NONMATCHING` (or project-equivalent). `#if 0` and comment-outs are rejected.
- Symbol naming follows map-derived or Nintendo naming conventions: CamelCase for methods, lowercase for C functions.
- Alignment directives (`.balign 8`) required at section starts — omitting causes relocation mismatches on newer toolchains.

### Progress Calculations

- Progress % = bytes still in `.s` files / total code bytes.
- **"Shiftable"** = all pointers use relocations, no hardcoded addresses. A project can match its DOL hash without being shiftable.
- Projects track "linked percentage" separately from "matched percentage."
- The `calcprogress` script has known bugs around static init symbols and templates — use updated versions.

### Community Milestones

| Milestone | Significance |
|-----------|-------------|
| DOL rebuildability | Baseline: project assembles back to a DOL |
| DOL shiftability | All pointers are relocatable; enables modding |
| 10% matched | Threshold before public announcement recommended |
| Completion (~99%+) | Four GC projects achieved this; considered breakthrough |

### Onboarding Pattern

1. Sort `.s` files by line count → start with the shortest
2. Study merged PRs more than tutorials (toolchain evolves too fast)
3. Post questions directly in `#match-help` without preamble — "ask to ask" culture doesn't exist here
4. Load map/symbol file into Ghidra first if the game has one

---

## 10. Platform Setup and Toolchain

### WSL (Windows)

- Store project in **WSL filesystem** (`/home/...`), NOT `/mnt/c/`. NTFS access is slow.
- WSL1 **cannot** run 32-bit applications (MWCC, MWLD). WSL2 required.
- Some setups require Wine specifically for the linker (`mwldeppc.exe`) even when wibo handles the compiler.

### DevkitPPC Version Critical Note

- **devkitPPC r40 introduced a breaking linker behavior change** that broke DOL matching on multiple projects.
- Root cause: repos not strictly enforcing alignment directives, which newer binutils exposed.
- Fix: update the repo (add proper `.balign` directives), OR downgrade to r39-2.
- r39 archive: `https://wii.leseratte10.de/devkitPro/devkitPPC/r39%20(2021-05-25)/`

### macOS Apple Silicon

- wibo has no macOS support as of this archive. Workarounds: SSH into Linux VPS, or use Docker + Wine.
- macOS ARM cannot natively run 32-bit x86 Windows executables.

### Build System

- **Ninja** strongly preferred over Make on Windows: benchmarked at ~5s vs ~30s for equivalent builds.
- Old Makefile-based projects hit `Argument list too long` errors at ~9,000+ `.s` files — dtk-template + Ninja handles this.
- dtk-template-based projects auto-download wibo and compilers from `files.decomp.dev`.

### Common Linker Errors (mwldeppc)

| Error | Cause | Fix |
|-------|-------|-----|
| `Can not mix BSS section '.sbss2'` | Wrong elf2dol mode | Use `wii` mode even for GC games with `.sbss2` |
| `Missing __init_cpp_exceptions.cpp` | Wrong linker version or missing TU | Let dtk generate synthetic TU; use MWLD 2.7 |
| `Relocation out of range` for floats | Float in wrong section (out of SDA range) | Ensure float is in correct section |
| `Argument list too long` when linking | Too many `.o` files | Use response file or intermediate ELFs |
| `Small data relocation requires symbol in small data section` | Mismatched `-sdata` thresholds across TUs | Ensure all TUs use same thresholds |

---

## 11. Infrastructure and Resources

### files.decomp.dev (Always-Current Links)

- `compilers_latest.zip` — all GC/Wii Metrowerks compiler versions
- IBM PPC Compiler Writer's Guide (CWG) — most-referenced document for unusual assembly
- Gekko User Manual (GameCube)
- Broadway User Manual (Wii)
- Standard PowerPC ISA reference

### Key Online Tools

| Tool | URL | Notes |
|------|-----|-------|
| decomp.me | https://decomp.me | Collaborative matching scratchpad; GC/Wii support added late 2021 |
| CExplorer | https://cexplorer.red031000.com | PPC compiler explorer; sometimes down |
| ghidra.decomp.dev | https://ghidra.decomp.dev | Shared Ghidra server; contact moderator for access |
| decomp.dev | https://decomp.dev | Progress tracking hub; 0.5% minimum to appear |
| YAGCD | https://www.gc-forever.com/yagcd/ | GC hardware documentation |

### Key Local Tools

| Tool | Notes |
|------|-------|
| decomp-toolkit (dtk) | Project management, disassembly, splitting — modern standard |
| objdiff | Local binary diff; integrates with dtk-template projects |
| wibo | Lightweight Wine alternative; ~2x faster |
| gc-wii-binutils | Cross-platform `powerpc-eabi` binutils builds |
| cwparse | Rust library for CW map file parsing |
| decomp-permuter | PPC support absent at time of archive — a known pain point |

### Adding a decomp.me Preset

- Contact a decomp.me maintainer with the exact `mwcceppc` version string and full flag set.
- Presets cannot be added via PR — must go through site administrators.

---

## 12. Gaps That Remain

Despite this Discord mining effort, the following remain undocumented:

| Topic | Status |
|-------|--------|
| PPC permuter | Does not exist publicly; repeatedly requested |
| Exact CI/CD YAML configs | Shared informally; not in public repos |
| Per-project PR checklists | Varies by project lead; learned through submitted PRs |
| WSL ARM64 compatibility | Unresolved in archive |
| JAudio internal structure (all 4+ versions) | Complex; partially charted |
| JMessage outside TP and Pikmin 2 | Largely uncharted |

---

## See Also

For full detail by topic, see the per-channel analysis files:

| File | Coverage |
|------|----------|
| `discord-insights-match-help.md` | Register allocation, inlines, switch, float patterns, pragmas (440 lines) |
| `discord-insights-tools.md` | MWCC compiler registry, objdiff, dtk, m2c, Ghidra, AI, decomp.dev (460 lines) |
| `discord-insights-games.md` | Melee, Animal Crossing, MKDD, Mario Party 4 (270 lines) |
| `discord-insights-libraries.md` | JSystem, EGG, MusyX, Dolphin/RVL SDK (392 lines) |
| `discord-insights-general.md` | Community onboarding, PR standards, platform setup, progress culture (273 lines) |

---

*Synthesized from doldecomp Discord archives (2021–2026). All contributor identities anonymized. No verbatim message content reproduced. For current project status, always check live repositories and decomp.dev — this document reflects knowledge as of April 2026.*
