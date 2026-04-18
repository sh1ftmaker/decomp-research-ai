# Discord Insights: Tools Channels

**Source:** Discord archives from the `Tools/` category  
**Files analyzed:** compilers.json, objdiff.json, decomp-toolkit.json, m2c.json, ai.json, tools-general.json, decomp-dev.json, ghidra.json, training.json, mwcc-debugger.json  
**Extracted:** 2026-04-17  
**Note:** All contributor names have been anonymized. No verbatim quotes longer than code snippets are reproduced.

---

## Table of Contents

1. [MWCC Compilers](#1-mwcc-compilers)
2. [objdiff](#2-objdiff)
3. [decomp-toolkit (dtk)](#3-decomp-toolkit-dtk)
4. [m2c Decompiler](#4-m2c-decompiler)
5. [Ghidra](#5-ghidra)
6. [AI-Assisted Decompilation](#6-ai-assisted-decompilation)
7. [decomp.dev](#7-decompdev)
8. [Training Repository](#8-training-repository)
9. [General Tooling Patterns](#9-general-tooling-patterns)
10. [mwcc-debugger](#10-mwcc-debugger)

---

## 1. MWCC Compilers

### Compiler Version Registry

The community has catalogued every known MWCC build stamp. The canonical version list (frequently referenced and updated) is:

**GameCube:**
- `Version 2.3.3 build 144` (GC CW 1.0) — Runtime: Apr 13 2000
- `Version 2.3.3 build 159` (GC CW 1.1) — Runtime: Feb 7 2001
- `Version 2.3.3 build 163` (GC CW 1.2.5) — Runtime: Apr 23 2001
- `Version 2.4.2 build 81` (GC CW 1.3.2) — Runtime: May 7 2002
- `Version 2.4.7 build 92` (GC CW 2.0) — Runtime: Sep 16 2002
- `Version 2.4.7 build 105` (GC CW 2.5) — Runtime: Feb 20 2003
- `Version 2.4.7 build 107` (GC CW 2.6) — Runtime: Jul 14 2003
- `Version 2.4.7 build 108` (GC CW 2.7) — Runtime: Jul 22 2004
- `Version 4.1 build 60831` (GC CW 3.0) — Runtime: Aug 31 2006

**Wii:**
- `Version 4.2 build 142` (Wii CW 1.0) — Runtime: Aug 26 2008
- `Version 4.3 build 151` (Wii CW 1.1) — Runtime: Apr 2 2009
- `Version 4.3 build 172` (Wii CW 1.3) — Runtime: Apr 23 2010
- `Version 4.3 build 213` (Wii CW 1.7) — Runtime: Sep 5 2011

**Important note:** Contributors distinguish between the CodeWarrior *package version* (e.g., "GC CW 1.3.2") and the internal MWCC *build stamp* (`Version 2.4.2 build 81`). Referencing by build stamp is considered more precise because multiple CW package versions can share the same compiler binary.

### Compiler Flag Patterns (Frequently Discussed)

- **Standard GC flag set:** `-O4,p -proc gekko -fp hard -fp_contract on -Cpp_exceptions off -enum int -RTTI off`
- **Melee:** Uses `-O4,s` (optimize for size + speed combined). Some files are compiled with different optimization levels — one contributor discovered `ParserErrors.c` compiled at `-O1` while everything else used `-O4,p`.
- **TTYD:** Uses `-O4,p -maf on -fp hard -enum int -use_lmw_stmw on -rostr -sdata 48 -sdata2 6 -multibyte -opt nodeadcode`
- **BFBB:** Uses `-O4,p -inline off -str reuse,pool,readonly -char unsigned -use_lmw_stmw on -pragma "check_header_flags off"` among others.
- The `-O4` flag was a common source of surprise — contributors unfamiliar with the toolchain expected `-O3` to be the maximum, as with GCC/Clang.
- Combining `-O4,s` and `-O4,p` can be achieved by passing both flags; each applies their respective sub-mode on top of `-O4`.

### Pragmas (High-frequency topic)

- `#pragma inline_depth(1024)` — forces deep inlining; available via command-line as `-pragma "inline_depth(1024)"`.
- `#pragma cats off` — suppresses CATS profiling data, reducing ELF size by ~30%; also available as `-pragma "cats off"`. This pragma is largely undocumented in official manuals.
- `#pragma pool_data on|off|reset` — controls data pooling behavior. Contributors found that some files in Animal Crossing (AC) used `pool_data off`, which produces noticeably different codegen. The linker, not just the compiler, plays a role in whether pooling saves code.
- `#pragma scheduling off` — can fix certain register allocation issues in very small functions, but tends to break most other code.
- `#pragma c9x on` — has an unusual scope: enabling it does not actually unlock all C99 features (no designated initializers, no VLAs), but compound literals still work even with it off.
- `#pragma warn_notinlined off` — suppresses warnings about functions that could not be inlined.
- `#pragma force_active on` — keeps symbols that would otherwise be dead-stripped.
- The `-pragma` command-line flag can inject any pragma into a compilation unit without modifying source files, e.g., `-pragma "cats off"`.

### Compiler Identification

- When trying to identify the compiler version used by a game, the build stamp embedded in the binary is the authoritative source, not the CW package label.
- GC CW 1.2.5 is associated with Super Mario Sunshine and potentially Wind Waker.
- GC CW 2.7 (`Version 2.4.7 build 108`) is the latest GameCube-era compiler and the most commonly referenced "too new" version when attempting to identify a game's compiler.
- Games using later Wii compilers (`4.3 build 172+`) have different BSS ordering behavior which complicates linking.
- One tool used by contributors for quick experimentation is an online CodeWarrior sandbox at `cexplorer.red031000.com`.

### Known Compiler Bugs

- The `!!` double-negation optimization has a pointer type confusion bug: when the right-hand type is a pointer (not a bool), the optimizer can incorrectly elide the `!!`. This was traced to `IroTransform.c` in the MWCC source.
- Early GC CW 1.2.5 (build 163) had a branch-related codegen bug that is absent from the slightly earlier build 159. This distinction matters for byte-exact matching.
- At `-O3,p`, certain function prologues are generated differently than at `-O4,p` — contributors encountered this unexpectedly when trying intermediate optimization levels.

---

## 2. objdiff

### Setup and Configuration

- objdiff reads a project configuration from `objdiff.yml` (or `objdiff.json`). Projects are encouraged to ship this file so contributors do not need to configure paths manually.
- The tool can be configured to call a custom build command (e.g., `ninja`, `make`) for both the base (expected) and target (built) objects.
- `objdiff.yml` can specify supported game versions and associated `configure.py` commands, enabling version switching inside the tool.
- When files have suffixes like `.s.o` and `.c.o` for asm vs. C objects of the same logical unit, objdiff may not match them automatically — projects work around this by adjusting their build system or using the config file.
- Deleting `%APPDATA%\objdiff` (Windows) fixes startup failures caused by stale config state. This was a recurring fix reported multiple times.

### Diffing Behavior

- objdiff infers symbol sizes from labels: if a symbol has no explicit size (e.g., just `.global myfunc`), it sizes it to the next label. This produces incorrect diffs. The recommended fix is to use size-aware macros such as `.fn myfunc, global` / `.endfn myfunc` (supported by ppcdis and dtk-generated asm).
- "Gap" symbols (padding between functions) appear in the diff and can be confusing. Contributors treat them as safe to ignore but maintainers planned to hide them in a future release.
- Data sections (`sdata`, `sdata2`, `rodata`) do not show match percentages by default in older objdiff versions; this was a known limitation.
- Data is only counted as "matched" in reports when an entire data *section* matches 100% — individual matching data entries within a section do not contribute to the matched data percentage.
- The `-sym on` MWCC flag embeds debug symbols into objects, but objdiff does not always handle these correctly and may display incorrect diffs when this flag is active.
- For jump table and relocation verification in data, the workaround is `readelf -Wr` for manual comparison, since objdiff did not support this natively.

### Symbol Handling

- objdiff has a built-in demangler for CW-style C++ names. However, the demangler fails on certain symbols — in particular, compiler-generated thunk symbols with `@offset@` prefixes and some Sunshine-specific mangled names.
- Right-clicking a symbol in the diff view allows copying the mangled version — useful for projects without a symbol map where contributors must name functions manually.
- A separate demangling utility window exists within objdiff for ad-hoc queries.
- Common symbols (`.comm`) appear in objdiff diffs but are benign.

### Integration with Build Systems

- objdiff watches the filesystem and rebuilds objects when they change — in v0.5.1+ this also covers externally-changed files, so the build system does not need to be invoked via objdiff at all.
- Projects using dtk-template benefit from `ninja baseline` / `ninja changes` targets that help agents and contributors detect regressions in shared headers.
- objdiff's `report generate` subcommand (CLI) produces a JSON report artifact. This is uploaded in CI and consumed by decomp.dev for progress tracking.
- A plain-text diff mode for agent consumption was discussed and planned by the tool author, to allow AI agents to paginate diffs using standard CLI tools.

### Common Pitfalls

- A function is in one of three states: matching, non-matching, or failing to compile. objdiff does not distinguish all three reliably without proper build system integration.
- If the expected object has no symbol sizes, objdiff will guess sizes from padding, which can hide real mismatches.
- `R_PPC_ADDR16` relocations (as opposed to `R_PPC_ADDR16_HA`/`R_PPC_ADDR16_LO`) are not always shown correctly in older objdiff versions when SDA-relative addressing is involved.

---

## 3. decomp-toolkit (dtk)

### Core Workflow

- dtk automates DOL/REL splitting into per-object `.s` files, symbol extraction, and relocation reconstruction. The main entry points are `dtk dol split` and `dtk rel info`.
- The `config.yml` file controls splitting behavior. After running `dtk dol split`, the output feeds a `configure.py` which generates `build.ninja`.
- dtk uses extab/extabindex sections to autosplit individual functions that would otherwise land in the wrong translation unit — this is required for MWLD to link without crashing.
- `dtk elf fixup` patches assembled object files to produce ELF output compatible with the original linker.

### Known Errors and Fixes

- **`Failed: File exists (os error 17)`** — occurs when re-running `dtk dol split` without clearing the output directory. Solution: delete the generated `asm/` directory before re-splitting.
- **`Conflicting size for <symbol>`** — a warning that appears when two analysis passes disagree on function size. Usually safe to proceed; log the discrepancy and check the function boundary manually.
- **`Unpaired epilogue`** — an analyzer bug triggered by unusual control flow (e.g., overlapping functions in SADX RELs, or complex tail-call patterns). Fixed in dtk by adding more tail-call heuristics and using ctors/dtors entries as boundary hints.
- **`Unaligned symbol entry`** — caused by data symbols whose addresses are not aligned to the expected word boundary. Reported for Puyo Pop Fever; tracked as a dtk bug.
- **`Missing symbol section`** — appears in `dtk elf fixup` when the assembled object lacks a section symbol. Can be worked around by ignoring that specific file if it is not linked anyway.
- **`Failed: Unknown DWARF attribute type`** — DWARF 1.1 debug info in some older REL files uses attribute kinds unknown to dtk's DWARF parser. Filed as a bug; non-fatal if the relevant sections are not needed.
- **`internal linker error: File: 'ELF_PPC_EABI.c' Line: 1402`** — a MWLD Wii linker bug. MWLD 2.7+ requires a `.comment` section in any TU containing common BSS symbols and very specific setup for `__init_cpp_exceptions`. dtk can generate these automatically.
- **Wii Party alignment warning:** `Alignment for auto_08_... expected 8, but starts at 8:...` — generally safe to ignore.

### REL Handling

- RELs are more complex than DOLs: symbol tables often lack section symbols, making automatic splitting unreliable.
- dtk REL merge (`dtk rel merge`) combines multiple RELs for linking. This is slow for games with many RELs (100+) and had bugs with the first reported REL in a sequence; fixed in later dtk releases.
- MWLD 2.7+ requires every linked TU to have a file symbol named exactly `__init_cpp_exceptions.cpp` when exception handling is used — this is a linker quirk with no obvious workaround other than dtk generating a synthetic TU.
- Some RELs have no `_prolog` symbol but still contain ctors/dtors sections, creating apparent contradictions in the splitting logic.

### DWARF Debug Info Extraction

- dtk can parse DWARF 1.1 debug sections from debug builds of SDK libraries (e.g., `osD.a`). These produce compilation unit paths, source file names, and function boundaries that help seed `splits.txt`.
- The DWARF parser logs verbose output under `RUST_LOG=debug` that shows attribute kinds and values, useful for diagnosing parse failures.
- Debug ELFs from `debugging.games` can be used to cross-validate dtk's function boundary analysis against known-good splits.

### Analyzer Internals

- dtk's initial analysis finds function boundaries by tracking `blr`, `rfi`, and branch targets. It then splits the DOL into per-TU object files.
- The `quick_analysis` option trades accuracy for speed but can hit different analysis bugs on pathological inputs.
- Symbol hashing (for SDK library matching) uses a relocation-aware approach: relocations are generalized by numbering symbols per function so that two functions with different external references but identical structure can still match.

---

## 4. m2c Decompiler

### Input Format and Context Files

- m2c prefers `doldisasm` or `reldisasm` style output (address-labeled asm). Raw `objdump` output does not work directly — the `@ha`/`@l` high/low relocation annotations are often mangled by objdump in ways m2c cannot handle.
- Context files (`--context file.c`) dramatically improve output quality: without a prototype for a called function, m2c infers argument types from register usage and often gets it wrong.
- m2c uses `pycparser` to parse C context files. Common failure modes:
  - `#ifndef` / `#ifdef` preprocessor guards are not supported — m2c errors with "Directives not supported yet".
  - Structs containing function pointers cause an `AssertionError: Struct can not contain a function`.
  - Binary integer constants (e.g., `0b1010`) confuse the parser.
- The recommended workaround for large contexts is to compile the project headers with `-E` (preprocessor only) and feed the output to m2c, stripping include guards.
- For decomp.me, the context must be a single flattened file since the website cannot run the preprocessor. Keeping a local preprocessed context is the standard approach.

### Output Quality and `--reg-vars`

- The `--reg-vars` flag makes m2c use named variables for saved registers instead of generic `temp_rN` names. Most contributors find this improves readability, especially for MWCC-compiled code where saved registers map clearly to named locals.
- Without `--reg-vars`, `temp_r28` (assigned once) is generated instead of a proper named variable, making the output harder to refactor into matching C.
- For `-O0` (unoptimized) code, contributors suggested an "unoptimized-code" mode that would suppress aggressive constant folding and leave variable assignments intact — this was proposed but not yet implemented at time of analysis.
- The `M2C_STRUCT_COPY` output macro means m2c detected an unrolled struct copy pattern. The macro expands to `memcpy` for compilation purposes, but the intent is for the contributor to replace it with `*dst = *src` or similar. Confirming the correct form requires checking whether the compiler uses `lwz/stw` (word-aligned struct copy) or `lfs/stf` (float-member struct copy).
- MWCC's threshold for switching from inline struct copy to a loop copy is approximately 17 bytes — below this, the copy is fully unrolled; above, a loop is emitted.

### Jump Table Handling

- m2c requires a label beginning with `jtbl`, `jpt_`, `lbl_`, or `jumptable_` to appear in the same basic block as a `bctr` instruction for jump table resolution to work. Without this, it emits "Unable to determine jump table".
- If the label exists but with a different naming scheme, renaming it in the asm before running m2c resolves the issue.

### C++ Context Limitations

- m2c has partial C++ context support, but complex C++ types (virtual dispatch tables, multiple inheritance, template instantiations) often cause parse errors or silent misinterpretation.
- Melee's workaround for polymorphic GObj types uses `#ifdef M2CTX` guards in headers: the `M2CTX` branch uses distinct structs per concrete type for better m2c inference, while the non-`M2CTX` branch uses typedefs that preserve correct codegen. On decomp.me this distinction is lost.
- Nested inline functions require correct context to resolve — m2c will generate separate calls for each inline expansion rather than collapsing them if prototypes are absent.

### Known Bugs and Limitations

- `psq_l` (paired-single load, a GC-specific instruction) is not supported. m2c will error on it; contributors work around by suppressing the error or removing the instruction for decompilation purposes.
- Certain CR bit comparisons (e.g., `bne cr7, label`) from non-default condition registers are not handled correctly — m2c expects CR0 comparisons.
- Functions that begin immediately with a label (no preceding instructions) are sometimes misidentified as rodata rather than code.
- Yoda-notation float comparisons (e.g., `0.0f < x`) are not always correctly converted to the canonical form.

### Improvement Proposals (Community-sourced)

A contributor compiled a detailed feature wish list from the Mario Party 4 decomp, including:
- Detecting pre/post increment patterns in `-O0` output.
- Recognizing ternary expressions.
- Using `++`, `+=`, `-=` operators instead of explicit assignment.
- Automatically naming `arg8`/`arg9` from register convention.
- Replacing `var_rxx = saved_reg_rxx;` with direct use of the argument name.
- Proper array notation (`[0].x` instead of `->x`) when the type is an array.
- Automatic detection of stack structs when passed to functions.

---

## 5. Ghidra

### Recommended Build

- The community uses a custom fork of Ghidra (maintained via `ghidra-ci`) rather than mainline Ghidra. This fork includes:
  - Improved PowerPC decompiler analysis (better int-to-float conversion handling).
  - Correct paired-single instruction decoding.
  - Bug fixes for float argument passing (mainline Ghidra incorrectly passes float args in GPRs in some decompiler views).
- The GC/Wii loader (`Ghidra-GameCube-Loader`) is maintained separately and must match the Ghidra version. The build at `github.com/encounter/ghidra-ci/releases` bundles both.
- Ghidra 11.1+ changed its internal storage format, so upgrading requires an exclusive checkout and a coordinated team migration.

### SDA21 Limitations

- Ghidra does not support `R_PPC_EMB_SDA21` relocations. This is a long-standing open issue. External symbols referenced via SDA21 produce relocation failures.
- The community fork partially mitigates this by allowing local SDA21 relocations while still failing on external ones.

### Practical Usage in Decomp Projects

- Ghidra is used primarily for exploratory analysis and struct discovery, not as a primary decompiler for matching. m2c is preferred for generating matching-ready C.
- Contributors use Ghidra's decompiler output as a "first pass" to understand logic, then switch to m2c or manual decompilation for actual matching.
- Importing a game's symbol map into Ghidra requires removing the `Offset` column from the map file format — newer map formats added this column and break the Ghidra importer.
- For C++ games, vtable structures are entered manually. Scripting via Ghidra's Java API or Python scripting is the recommended approach for bulk vtable import.
- The Ghidra C struct parser is described as "sensitive" — contributors recommend adding one struct at a time rather than importing large context files.
- Bitfield display in the decompiler view is not supported as of analysis time; bitfield structs show correctly in the Data Type Manager but not in the decompiler.

### Shared Ghidra Server

- The community operates a shared Ghidra server at `ghidra.decomp.dev` for collaborative struct and symbol work.
- A gRPC API was developed to allow programmatic user and permission management for this server, working around Ghidra's reflection-based private APIs.
- Multi-user sessions require exclusive checkout when upgrading the project's Ghidra version.

---

## 6. AI-Assisted Decompilation

### Current Community State (as of April 2026)

- AI assistance for decompilation is actively used across multiple projects. The dominant tools are Claude Code (CLI) and GitHub Copilot's agentic mode, with experimentation ongoing using GPT-5.3-Codex, Qwen 3.5, and local models via Ollama.
- Community sentiment is mixed: many contributors support AI as a *tool accelerator* for tedious or mechanical matches, while objecting to AI-generated PRs submitted without human review.
- Frontier models (Claude Opus, GPT-5.3-Codex) are effective at decompilation but expensive. At a `$20/month` GitHub Copilot subscription, the per-request model means a single autonomous agent can run for hours without exhausting the quota.
- The factual nature of matching decompilation (100% match or not) is noted as an advantage: AI hallucinations that produce non-matching code are immediately detectable and discardable.

### Effective Workflows

- **One-shot matching:** The simplest pattern is to provide a model with the target assembly, the current C stub, and the objdiff output, then ask it to produce matching C. This works well for functions under ~100 instructions.
- **Iterative agent loop:** An orchestrator agent (`/execute`) spawns specialized subagents for Ghidra exploration, initial C scaffolding, and iterative matching attempts. Each agent returns "matching tips" that are accumulated in an `AGENTS.md` file.
- **Skills / slash commands:** Decomp-specific skills define tool boundaries for the agent: how to build, how to diff, which Ghidra instance to query. Skills are stored as `.pi` files or Claude Code slash command definitions.
- **Hybrid race:** One project runs Claude Code and the permuter tool simultaneously on the same function; whichever finds a match first wins.
- A two-model pipeline was proposed and tested: a cheaper, faster model (GPT-5.3-Codex) handles initial implementation; a more capable model (Claude Opus) handles difficult residual mismatches. This was found to be more cost-effective than using Opus for everything.

### Token and Cost Management

- Claude Opus is the most capable model for this domain but consumes tokens aggressively. A contributor found that context compaction quality is poor for decomp work.
- Disabling web search in agent mode saves tokens with no apparent quality loss.
- Claude Code's subagent spawning does not count as separate API requests in some configurations, enabling long-running multi-agent sessions within a fixed budget.
- One-shot prompting (feeding all context upfront and allowing the model to run without interruption) is more efficient than interactive iteration.
- A typical initial exploration phase before the first code attempt consumes 10–30k tokens.
- Local models (Qwen 3.5 235B, run on machines with 400GB RAM) were being evaluated but were not yet competitive with frontier models on decompilation accuracy.

### Model Comparison Notes

- Claude Opus 4.6 has strong context retention and is best for multi-step reasoning across large code contexts.
- Claude Sonnet 4.6 is considered a strong balance of quality and cost for most matching tasks.
- GPT-5.3-Codex uses significantly fewer "thinking tokens" for the same quality level, making it more economical for the iterative compile-diff-fix loop.
- Older models knew *about* matching decompilation in general terms; Claude Opus 4.6 was noted as able to use correct domain-specific terminology and patterns confidently.
- Very small models (sub-1B parameter) were tested and found unable to execute basic shell commands reliably.

### Platform Considerations

- Windows + WSL creates friction: agents typically assume Linux tooling, while the GUI for objdiff requires Windows. Contributors running both simultaneously had to maintain separate configuration directories.
- All agents should run inside a VM or container to prevent filesystem damage from tool-calling errors.
- The `build.ninja` regeneration path (detecting `configure.py` changes) works well in CI but can confuse agents running across a WSL/Windows boundary.

### Known Limitations

- Agents struggle with the MWCC register allocation problem — the specific pattern of expressing C so that `r31` is assigned to a particular variable (and not another) requires understanding the compiler's internal virtual register numbering, which no model reliably derives from assembly alone.
- Functions requiring knowledge of the game's domain (what a particular data structure means) remain difficult even for capable models.
- Context window exhaustion is a real risk on large functions or when Ghidra DWARF dumps are included directly in the prompt.
- Claude has on occasion produced correct-looking C code that uses internal SDK symbol names it could not legitimately know; contributors treat such output with suspicion.

---

## 7. decomp.dev

### Progress Tracking Architecture

- decomp.dev consumes `report.json` artifacts uploaded by GitHub Actions CI using the `objdiff report generate` command.
- The report artifact must be named `VERSION_report` (e.g., `GALE01_report`) for decomp.dev to process it. The project must be registered on the site with the matching game code.
- A project must reach **0.5% matched code** to appear publicly on decomp.dev.
- The JSON schema for reports is defined in `objdiff-core/protos/report.proto` using ProtoJSON format (64-bit numbers as strings; default-value fields are omitted).

### Progress Metrics Explained

- **`matched_code_percent`**: The percentage of code bytes covered by perfectly byte-matching functions.
- **`fuzzy_match_percent`**: Functions that are partially matching (e.g., 80% of instructions match). This is the number shown in the diff view's percentage indicator.
- **`complete_code_percent`**: Code that is fully linked (both matched and all dependencies resolved) — the "linked" percentage.
- Data matching only counts when an *entire* data section matches 100%. This means projects with mostly matching data but one mismatched symbol show near-zero data match percent. A fuzzy data match percentage was proposed but not yet implemented.

### decomp.dev API

The site exposes a documented REST-like API:
- `https://decomp.dev/<owner>/<repo>.json?mode=measures` — current match metrics (small, fast)
- `https://decomp.dev/<owner>/<repo>.json?mode=report` — full function-level report (large)
- `https://decomp.dev/<owner>/<repo>.json?mode=history` — all historical measurements
- `https://decomp.dev/<owner>/<repo>.svg?mode=shield` — progress badge for README embedding

Query parameters `?category=` and `?unit=` scope results to a subsection of the project.

### decomp.dev vs decomp.me

- These are distinct services. decomp.me is an online workspace for creating and sharing individual function "scratches" (matching attempts). decomp.dev is a project-level progress tracker.
- decomp.me requires compiler presets to be added by site administrators (not via PR). Each preset specifies compiler flags and associates scratches with a game.
- The similarity of the domain names caused ongoing confusion in Discord — contributors frequently linked to the wrong site.

### PR Bot Integration

- The community uses a bot that downloads objdiff reports from CI artifacts on PRs and posts a structured comparison comment. The comment format includes:
  - Matched code delta (bytes and percentage)
  - Newly matched functions (sorted by size)
  - Improved functions (sorted by bytes improved)
  - Regressed functions (highlighted distinctly, ideally in a collapsible `<details open>` block)
- The bot updates the comment as the PR is revised.

---

## 8. Training Repository

### Purpose

- The `doldecomp/decomp-training` repository provides guided exercises for learning matching decompilation. Contributors work through progressively complex functions and verify matches using objdiff against a reference answer directory.
- A "training scratch" on decomp.me is also maintained for contributors who prefer the web interface.

### Curriculum Philosophy

- The primary skill being taught is **equivalence thinking**: recognizing that `* 0.5f` and `/ 2.0f` produce identical assembly, or that a single complex expression must be split into multiple assignments to match MWCC's codegen.
- Training includes:
  - Compiler flag and version guessing exercises (given assembly, identify which MWCC version produced it)
  - Common MWCC idioms: `use_lmw_stmw`, data pooling, register save/restore conventions
  - Medium-complexity functions with inlining and register allocation challenges

### Organizational Notes

- The training repository moved to the `doldecomp` organization for long-term maintenance continuity.
- A procedurally generated training system ("decomp training roguelike") was proposed but not implemented at time of analysis.

---

## 9. General Tooling Patterns

### Disassembler Ecosystem

Several disassemblers coexist in the community:

| Tool | Status | Notes |
|------|--------|-------|
| `dadosod` | Active but being superseded | Rust, GC/Wii DOL/REL disassembler; dtk largely replaces it |
| `ppcdis` | Active | Python, GC/Wii; smarter relocation inference, supports Wii RELs |
| `dtk` (decomp-toolkit) | Dominant | Rust, most actively maintained; replaces dadosod entirely |
| `ppc2cpp` | Early stage | C++, focuses on equivalency checking and control flow analysis |
| `ppcdisasm-cpp` | Library | C++, instruction-level disassembler for embedding in other tools |

- The community consensus is that dtk has effectively superseded dadosod. Projects starting fresh use dtk.
- ppcdis is still preferred by some projects for its DOL→analysis→object pipeline, especially for games already using it.

### Build System Recommendations

- **Ninja** is strongly preferred over Make on Windows: build times improved from ~30s to ~5s in at least one project after switching.
- On Windows, avoid requiring MSYS2 — use native Ninja and ship prebuilt Rust binaries instead.
- WSL builds and native Windows builds use different `config/` directories and cannot share the same `build.ninja`. Contributors with both environments maintain separate configurations.
- The `build.ninja` contains logic to detect changes to `configure.py` and re-run it with the same flags, which is important for objdiff's auto-rebuild behavior.

### Tooling Language Choice

- The community standardized on **Rust** for new tools (dtk, cwparse, ppcdisasm-cpp). Reasons cited: cross-platform static binaries require no runtime; rich ecosystem for ELF/Mach-O/PE parsing via the `object` crate; no need for users to install a C compiler toolchain.
- Python is used for project-level scripting (`configure.py`, `calcprogress.py`, context generation) but not for core tool development.

### CW Map File Parsing

- A Rust library (`cwparse`) was released for parsing CodeWarrior map files. It supports Melee, Pikmin, Pikmin 2, Super Monkey Ball, and Metroid Prime map files with test coverage. Python bindings were planned.
- Map file parsing is used for: progress calculation, detecting symbol order mismatches, and generating `objdiff.csv` for the diff workflow.

### asm-differ Integration

- `asm-differ` remains in use for quick diffs, particularly in projects not yet using objdiff. Its `--write-asm` flag produces output that m2c cannot directly consume; contributors preprocess it manually.
- The `@ha`/`@l` high/low offset annotations are mangled by objdump and require post-processing before feeding into m2c.

---

## 10. mwcc-debugger

### What It Does

- mwcc-debugger is a tool that hooks into the running MWCC binary (via the Windows Debugger Engine) and extracts internal compiler IR at specific compilation stages. The primary use case is diagnosing register allocation mismatches.
- It outputs multiple log files per compilation: `frontend-00-*.txt` (initial AST), `frontend-01-ast-after-optimizations.txt` (post-optimization AST), `backend-00-initial-code.txt` (unoptimized backend IR), and `gpr-pass-1-all.txt` / `assigned.txt` (register allocation state).
- A newer version (`mwcc-inspector`) uses C# with `ClrDebug` to read internal MWCC memory structures directly and render a clickable IR viewer.

### Register Allocation Debugging

The tool has enabled the community to precisely diagnose why a variable ends up in the wrong register. Key insights extracted from the channel:

- Variables receive "virtual register numbers" at creation time. Lower virtual register numbers are given **lower** priority in the coloring pass, meaning they get allocated later and receive higher-numbered physical registers.
- The "pressure threshold" for spilling is 29 neighbors (for 30 allocatable GPRs). When a variable has fewer neighbors than this, it stays in the first coloring pass.
- The "coalescing bug": MWCC attempts to merge (coalesce) a temporary with a physical register (e.g., merge `r42` into `r3` for a function call argument). Even when coalescing succeeds, the original virtual register is not removed from the interference graph, so it still counts as a neighbor of other variables. This inflates neighbor counts, which can be exploited to push variables into higher-priority positions.
- `opt_propagation` (enabled at `-O4`) replaces constant sub-expressions inline, eliminating some coalesced temporaries that `-O0` would retain. This is why register allocation can differ between debug and retail builds even when the logical code is identical.
- Practical fix strategies:
  - Declare a variable earlier in the function to give it a lower virtual register number (and hence higher coloring priority).
  - Use an intermediate assignment `(void)param;` or `(void)0;` (as found in debug builds) to introduce a coalesced temporary that inflates neighbor counts, shifting other variables into different priority bands.
  - Replace struct field accesses with temporaries to change the order in which backend-generated temps are created.
  - Use arrays or structs on the stack to force the backend to generate specific temporary patterns.

### Setup Notes

- mwcc-debugger requires WinDbg to be installed on Windows.
- A `retrowin32` emulation layer was an alternative approach, but hit OOM errors (`heap size 1800000 oom 80054`) on certain large functions.
- The tool works best on GC compiler versions. Extending to Wii versions requires adapting to different internal struct layouts.
- AI agents given a mwcc-debugger skill were able to invoke it but did not reliably interpret the output to derive actionable code changes; human analysis of the IR logs was still required.

---

## Cross-Cutting Patterns

### The "75% Offline" Problem

Information in these Discord channels is ephemeral and often the only place where game-specific compiler flag configurations, specific pragma combinations that fix mismatches, and build error workarounds are documented. Multiple contributors observed that knowledge not captured in GitHub issues or documentation is effectively lost. This motivates the existence of this repository.

### Community-Defined Standards

- **Matching threshold for PRs:** While no formal `CONTRIBUTING.md` exists in most projects, the de facto standard discussed in Discord is that a function must be at 100% in objdiff (byte-exact) before it can replace its `.s` counterpart. Fuzzy matches are acceptable as intermediate states but not for promotion.
- **Commit message format:** Projects use short imperative-mood messages naming the function(s) decompiled. GitHub PR comments from the bot make the percentage change visible.
- **Code review:** Reviewers check for: correct struct types (not `unk_t` placeholders unless unavoidable), correct function signatures, and that no non-matching assembly lines remain in the `.c` file.

### Toolchain Evolution Notes

- dtk's rapid pace of development means bug fixes arrive frequently. Contributors should update dtk before reporting analyzer issues — many "bugs" are already fixed in HEAD.
- objdiff v3 introduced breaking changes to the report format and the `NON_MATCHING` label filtering. Projects upgrading from v2 need to regenerate their configurations.
- GitHub Actions CI templates from `dtk-template` are the recommended starting point for new projects. The example workflow at `.github.example/workflows/build.yml` covers splitting, building, SHA1 verification, and report upload.

---

*Confidence: High for tool-specific details (sourced from thousands of conversations with reproducible technical content). Medium for community practices (derived from patterns in discussions, not formal policies).*  
*Last updated: 2026-04-17*
