# Discord Insights: General Community Channel

**Source:** Discord server general channel archive (doldecomp community)  
**Coverage period:** ~2021 – early 2026  
**Total messages analyzed:** ~718,000 lines  
**Confidence:** Medium–High (direct community observation)  
**Status:** Captures knowledge that does NOT appear in public GitHub documentation

---

## 1. Community Onboarding Patterns

### How Veterans Welcome Newcomers

- The server actively encourages newcomers to post their GitHub link or current progress publicly, even at 0% (assembly-only). Admins will allocate a dedicated channel once a project has a long-term lead committed to it.
- No need to "ask to ask" — the culture explicitly supports posting technical questions directly, even partial or naive ones. Contributors are told this is a space for anyone to post questions.
- Newcomers are pointed to the `#match-help` channel pins, which contain training files and the IBM PowerPC Compiler Writer's Guide (CWG) as the primary beginner resources. There is no organized written onboarding guide; the pins serve this purpose.
- Veterans consistently recommend starting with small `.s` files (few instructions, simple logic), specifically by sorting `.s` files by line count and picking the shortest ones. Some projects provide a sorted list in their tooling.
- For a game with preserved symbols or an ELF shipped on disc, newcomers are told to load that map first in Ghidra before doing anything else — it dramatically speeds orientation.

### What Veterans Warn Beginners About

- The first 1–2% of any project is typically the hardest because you are still determining the correct compiler version and flags. This phase is expected to feel frustrating. Veterans explicitly say not to despair.
- Beginners are warned not to nitpick register allocation issues early on. Focus on getting basic functions matching first; regalloc problems can be revisited once momentum is established.
- Hardcoded addresses are strongly discouraged even when they produce a matching binary, because they result in unshiftable, unportable code. Always use `extern` or move data into the source file.
- Newcomers should not start a new decomp project unless they can commit sustained effort to it or hand it off to someone who can. Projects that stall below 10% were seen by community leadership as actively harmful to the scene because they fragment contributor attention.
- Tutorials (especially video tutorials) are considered unreliable over time because the toolchain evolves rapidly. Beginners are pointed to the pinned reference documents and to studying merged PRs rather than following third-party guides.

---

## 2. PR Submission and Code Review Standards

### What Gets a PR Accepted

- The **build as a whole must match** (byte-for-byte identical DOL). Individual functions within a PR do not each need to be 100% matching, but nonmatching functions must be wrapped in the standard `#ifdef NONMATCHING` guard (or the project-specific equivalent). Commenting out a function with `// ...` or `#if 0` is explicitly rejected.
- Projects do not maintain a public `CONTRIBUTING.md` at the time of this archive. Review standards are enforced informally by project leads through code review on GitHub.
- One project lead described moving away from checking every individual changed line as "too strict and inefficient," suggesting informal trust-building with experienced contributors over time.
- Pull requests against empty or newly started repos may fail mechanically on GitHub (the site did not allow PRs to empty repos). Projects recommend making at least one initial commit before inviting PRs.

### Common Review Feedback Patterns

- Symbol naming conventions are checked — functions should follow the naming style used in the rest of the file, which is usually derived from the map or from inferred Nintendo naming conventions (CamelCase for methods, lowercase for C functions, etc.).
- Alignment directives (`.balign 8`) are required at the start of sections when decompiling files that contain data sections; missing these causes relocation mismatches on newer toolchains.
- Leaked SDK source code is treated differently from leaked compilers: the community has an ongoing (unresolved) debate about using leaked SDK headers, with different projects drawing the line differently. Using Metrowerks compilers that were leaked is broadly accepted; using leaked SDK source is not.

---

## 3. Platform Setup: WSL, macOS, and Linux

### WSL (Windows Subsystem for Linux)

- WSL is slower when accessing files on the Windows NTFS drive (the "virtual mounted drive"). Projects should be stored within the WSL filesystem (`/home/...`), not `/mnt/c/...`, for acceptable build performance.
- Legacy WSL (WSL1) cannot run 32-bit applications even with `wine32` or `wibo`, making it unable to run `mwcceppc.exe` or `mwldeppc.exe`. WSL2 is required.
- Some contributors found they needed Wine specifically inside WSL for the linker (`mwldeppc.exe`) even when `wibo` worked for the compiler, due to linker-specific compatibility gaps.

### wibo vs. Wine

- The community consensus is: **use wibo instead of Wine whenever possible**. wibo (https://github.com/decompals/wibo) is a lightweight x86 Win32 emulator that runs the Metrowerks toolchain without full Wine overhead.
- Benchmarks shared in the channel showed wibo building Super Monkey Ball in approximately half the time Wine took (~12s vs ~25s for a full build). This is a significant quality-of-life improvement for iteration speed.
- wibo has some known gaps — it does not support reading Windows string resources (used when checking compiler build dates), for which Wine is still needed. For that specific operation, contributors fall back to Wine.
- wibo versions before 0.14 had regressions for certain projects — always check the release notes when upgrading.
- wibo is downloaded automatically by most dtk-template-based build systems; contributors typically do not need to install it manually.

### macOS (including Apple Silicon M1/M2)

- At the time of this archive, wibo had no macOS support. Contributors on Apple Silicon (M1, M2) were working around this by SSHing into a Linux VPS or running builds inside Docker via Wine.
- macOS ARM cannot natively run 32-bit x86 Windows executables. The recommended workflow for macOS users is to use a remote Linux build environment or Docker.
- Compiling Twilight Princess from a clean state on a Mac Air was benchmarked informally in the channel — contributors were comparing it to WSL build times.

### DevkitPPC Versioning Issue (Critical Historical Note)

- DevkitPPC **r40 introduced a linker behavior change** that broke DOL matching on multiple projects. The community announcement explicitly stated: downgrade to r39-2 or earlier if you cannot produce a matching DOL on Linux with a recently updated devkitPPC.
- This was later partially revised: the root cause was repos not strictly enforcing alignment directives, which a newer binutils exposed. The fix is to update the repo (add proper `.balign` directives), not to stay on old devkitPPC permanently.
- Old devkitPPC versions (r39 specifically) are archived at `https://wii.leseratte10.de/devkitPro/devkitPPC/r39%20(2021-05-25)/` and GBATemp. The official devkitPro does not maintain old versions, so these community archives are the only source.

---

## 4. decomp.me Usage Patterns and Best Practices

### How the Community Uses decomp.me

- decomp.me was integrated with GC/Wii compiler support in late 2021. Contributors in this channel actively requested that project leads submit exact compiler flags and versions so a "preset" for their project could be added to the site. The workflow for adding a preset: contact a decomp.me maintainer with the exact `mwcceppc` version string and full flag set.
- The typical use pattern: create a scratch on decomp.me, paste the target assembly, and iterate on C code until the diff reaches 0. The scratch preserves context and can be shared with others for collaborative help.
- For larger functions, contributors are reminded to configure scratch settings (optimization level, flags) to match the project's actual build flags. A scratch using default settings will not produce the correct codegen.
- Scratches are commonly shared in `#match-help` and similar project channels when a contributor is stuck. Others can clone and continue working on the same scratch.
- decomp.me was seen as an accelerant for collaboration — it allows someone unfamiliar with the local build environment to help with function matching without cloning the full repo.
- A contributor recommended the following order of operations for a new project wanting decomp.me access: (1) get a working public repo others can join, (2) see if there is community interest, (3) only then submit a PR to decomp.me. Solo projects without community interest do not need decomp.me support.

### CExplorer (cexplorer.red031000.com)

- CExplorer is the GC/Wii community's alternative to Godbolt, specifically supporting Metrowerks PPC compilers. It was the go-to tool before decomp.me had GC/Wii support and continues to be used alongside it.
- Contributors regularly share CExplorer links when asking about compiler flag effects or testing whether a different compiler version produces the target output.
- Note: the CExplorer domain experienced downtime during the archive period. It is not as reliably available as decomp.me.

---

## 5. Progress Tracking and Milestone Culture

### How Progress Percentages Are Calculated

- Progress percentage is calculated by summing the **byte sizes of functions that still remain as `.s` (assembly) files**, using addresses embedded in those files. Functions that have been decompiled to `.c`/`.cpp` are counted as complete. This method was explained explicitly when newcomers asked.
- Some projects also track "linked percentage" separately from "matched percentage" when linker file ordering is still incomplete even after all code is matched.
- The community has a custom `calcprogress` script that evolved over time. An update was noted where the original version missed static init symbols and functions with more than one template instantiation due to lack of regex handling. Projects using forks of the original script were explicitly advised to update.
- "Shiftable" is a distinct milestone from "matching": a shiftable build is one where all pointers recalculate correctly regardless of load address, meaning no hardcoded addresses remain. A project can match its DOL hash without being shiftable.

### Community Milestones and Their Significance

- **DOL rebuildability**: The project can be assembled back into a DOL from all `.s` files. This is the baseline "it builds" milestone.
- **DOL shiftability**: All pointers use relocations, no hardcoded addresses. Enables modding and porting.
- **Full disassembly**: The entire DOL plus any REL files are disassembled and shiftable. RELs are described as a major additional effort.
- **10% matched**: Mentioned as a meaningful community threshold — some project leads said they preferred keeping projects private until this milestone to avoid fragmentation.
- **Completion (near 100%)**: The community announcement explicitly celebrated four GC decomps reaching ~99%+ ("99% matched counts") as a watershed moment, noting that skepticism about any GC/Wii decomp ever completing was common early on.
- One admin announcement specifically celebrated the Twilight Princess team reaching near-completion, calling it the largest game ever decompiled (11.5MB of code), with nearly 70% decompiled in a single year.

### Community Attitude Toward Stalled Projects

- Projects below 10% with no active contributors were explicitly called out as "hurting the scene" by at least one community lead. The concern is that stalled projects do not release useful artifacts while consuming community mindshare.
- The recommended path: either commit to sustained effort, actively recruit contributors, or acknowledge the project is inactive so others can start fresh.

---

## 6. Compiler Identification and Flags

### Determining the Correct Compiler

- The first step for any new project is identifying the compiler version. Community-documented methods (in order of reliability):
  1. Check the MetroTRK version string embedded in the binary (`Metrowerks Target Resident Kernel for PowerPC` or similar) — this often correlates with a specific CodeWarrior version.
  2. Check the SDK version strings embedded in the binary (e.g., `<< Dolphin SDK - CARD release build: Apr 5 2004 >>`) — these pin the game's build date range.
  3. Try small, simple functions using CExplorer or decomp.me with different compilers until the output matches.
  4. Use the game's release date as an upper bound — it could not use a compiler released after the ship date.
- The MetroTRK string and compiler version do not always have a 1:1 relationship. Community members noted specific mismatch cases.

### Common Flag Patterns Shared in Channel

- Several concrete flag sets appeared in discussion for well-known projects. These represent real compiler invocations for matching builds:
  - Paper Mario TTYD: `-Cpp_exceptions off -proc gekko -fp hard -O4,p -nodefaults -msgstyle gcc -sdata 48 -sdata2 8 -inline all,deferred -use_lmw_stmw on -enum int`
  - Super Mario Galaxy: uses `-O4,s` (size-optimized), while NW4R library code uses `-O4,p` (performance-optimized). This distinction matters because the two produce different instruction orderings.
  - A Wii game example: `-nodefaults -proc gekko -DRELEASE -Cpp_exceptions off -gccinc -O4,s -fp hardware -enum int -sdata 4 -sdata2 4 -lang=c99 -align powerpc -inline auto -W noimplicitconv -DEPPC -DHOLLYWOOD_REV -DTRK_INTEGRATION -DGEKKO -DMTX_USE_PS -MMD -rtti off -ipa file`
- The `-ipa file` flag enables interprocedural analysis (smarter inlining decisions across a translation unit). Several games use it and it affects inlining behavior significantly.
- Per-file compiler flag overrides (in Makefile) are the standard workaround when a single file needs different flags than the project default — e.g., `-sdata 0 -sdata2 0` for a specific file that would otherwise place data in the wrong section.

### Compiler Version Distinctions That Matter

- MWCC 1.2.5 vs. 1.3.2 produce different register allocation for the same source in some cases (documented example: `HuDecodeFslide`). Projects targeting the wrong sub-version can get "close but not matching" results that are hard to diagnose.
- Some functions in some games produce different code under `-O4,s` vs. `-O4,p` even at the same overall optimization level. When a function stubbornly does not match, toggling this flag is a known diagnostic step.
- LTO (`-ipa program`) is mentioned as making per-function matching essentially impossible. Games using whole-program IPA require full-program compilation to match, which is incompatible with the incremental file-by-file approach.

---

## 7. Toolchain Ecosystem and Automation

### dtk (decomp-toolkit) as the Modern Standard

- By mid-archive period, `dtk` had become the community-recommended foundation for new projects, replacing the older Python-based disassembly script (`doldisasm.py`) and various Makefile approaches.
- dtk handles: initial disassembly from DOL/ELF, section splitting, symbol map reading, DWARF v1 debug info extraction, and `.sjiswrap` processing for Shift-JIS source files.
- `dtk elf fixup` is used to normalize object files from the GNU assembler to match CodeWarrior linker expectations.
- `objdiff` integrates with dtk-based projects for local diff visualization. The tool was specifically created by the same maintainer to improve the local iteration workflow. Several contributors said they use `objdiff` exclusively for matching work, only going to decomp.me when asking for help.
- The community goal articulated by one veteran: "ideally the only two tools needed for a decomp are dtk for project management, and the recompiled compiler once it's available." This reflects the direction of tooling consolidation.

### Build System Evolution

- Older projects used Makefile + custom Python scripts. The main pain point was Makefiles not scaling well when splitting a DOL into thousands of individual function files (argument list too long error at ~9,000 files).
- dtk-template-based projects use Ninja as the build runner, which handles large numbers of translation units more gracefully.
- Most CI configurations that exist for these projects run in GitHub Actions with wibo pre-installed automatically. The community infrastructure (via `files.decomp.dev`) hosts the compilers archive that CI systems download.

### Shared Ghidra Server

- The community maintains a shared Ghidra server at `ghidra.decomp.dev` (migrated from `ghidra.complexplane.dev`). Projects on the server have all REL files loaded with cross-references resolved to the DOL — a significant advantage over working locally without that context.
- Projects can request access to existing game projects on the server. Adding a new project or user requires contacting a moderator. The server is useful for initial orientation but is not a substitute for the matching build environment.

---

## 8. Common Technical Problems and Known Solutions

### Linker Errors (mwldeppc)

- `Can not mix BSS section '.sbss2' with non-BSS section '.sbss2'`: Caused by using an older linker that does not support `.sbss2`. The `elf2dol` `wii`/`gamecube` distinction controls this — use `wii` mode if the game has `.sbss2` even on a GC game.
- `Missing runtime file '__init_cpp_exceptions.cpp'` and `global_destructor_chain.c`: These errors appear when the linker command file does not reference the correct runtime support objects, or when the wrong linker version is used. Most projects use the 2.7 linker specifically for BSS compatibility even when compiling with an older `mwcceppc`.
- `Relocation out of range` for float constants: When a nonmatching function uses float constants that end up in `.rodata`, the linker may place them out of SDA range. Workaround: ensure the float is in the correct section or use a fake volatile variable to force different codegen.
- `Argument list too long` when linking: Occurs when a project has thousands of `.o` files. Solution is to either use a response file for the linker or generate partially linked intermediate ELFs.

### Assembly and Disassembly Quirks

- `.balign 8` is required at the start of the first ASM file following a file that has data sections. Omitting it causes relocation mismatches when building with newer binutils. This was a source of confusion for many newcomers.
- GAS (GNU Assembler) does not directly support Metrowerks SDA-relative addressing syntax. The `postprocess.py` script (present in doldecomp projects) handles translation of these annotations for GAS compatibility.
- Shift-JIS source files (common in Japanese studio code) require preprocessing before compilation. `dtk sjis` handles conversion. The convention is to store source files in Unicode in the repo and convert at compile time.
- Gekko-specific instructions (`psq_l`, `psq_st`, paired-singles) require specifying `-mgekko` to the GNU assembler. Without this flag, the assembler rejects these instructions.

### Matching-Specific Patterns

- **Register allocation problems**: The #1 class of non-matching issues. Swapping variable declaration order or adding/removing temporaries can change register assignment. Without a PPC permuter (which did not exist at the time of this archive), contributors resolve these manually or skip them.
- **Inline function ordering**: Inline functions defined in headers appear at the end of a compilation unit when the header is included from a separate file. Inline functions defined inside the class body appear in the order the class is defined. Getting this ordering right requires understanding which header files are included and in what order.
- **`-O4,s` vs. `-O4,p` inlining**: The `s` (size) variant is more aggressive about inlining when it saves space; the `p` (performance) variant inlines more speculatively. The resulting code can be meaningfully different for the same function.
- **`volatile` workaround**: In at least one documented case, wrapping a variable as `const volatile` was needed to reproduce the compiler's exact codegen. The community noted this is a hack and not necessarily what the original developers wrote, but it is accepted practice for matching.
- The CodeWarrior compiler can strip `asm` functions at optimization level `-O4` if it determines they are unused. Wrapping with `#pragma optimizewithasm` or the relevant attribute prevents this.

---

## 9. Community Meta-Discussions

### On the Decomp Scene's Health

- Community leadership expressed concern that too many projects starting and stalling below 10% is fragmenting contributor attention. The preference is for fewer, more active projects over many dormant ones.
- Conversely, progress on existing mature projects accelerated noticeably once tooling (dtk, objdiff, wibo) stabilized. The period of rapid tooling improvement significantly reduced per-function iteration time.
- The community is explicitly welcoming and trans-inclusive (stated in server rules by current owner). The rules also prohibit discussion of piracy and leaked game assets, while community practice generally allows using leaked Metrowerks compilers.

### On AI-Assisted Decompilation

- Multiple discussions occurred about using neural networks, ChatGPT, and AI-assisted decompilation. The consensus circa 2022–2023:
  - AI models (including ChatGPT) can help explain assembly patterns, suggest C implementations, and reason about algorithm structure. Contributors reported using ChatGPT to help decode switch statement logic by explaining the format context.
  - The core problem with AI-generated matching code is **nonsense functions**: code that compiles to the correct binary bytes but is logically meaningless. A human verification step is considered non-negotiable.
  - A practical proposed workflow: AI generates candidate C functions → compiler produces assembly → byte comparison checks match → human reviews for semantic plausibility. This is essentially the decomp-permuter approach applied to LLM outputs.
  - The quality of AI decomp output is highly dependent on having good assembly context (calling convention, type information, surrounding code). Raw assembly without context produces poor results.
  - The real bottleneck identified is training data format: matching (assembly, C source) pairs in the correct schema for fine-tuning are difficult to collect at scale from public sources.

### On Legal Risk

- The community's general consensus: Nintendo has the legal capacity to pursue any of these projects if they choose to, and community members cannot afford individual legal defense. This is accepted as a known risk and does not deter participation.
- Projects avoid distributing game assets; the repos contain only assembly, C source, build tooling, and headers. This is considered the minimum risk posture.
- The community explicitly does not argue legal theory in the main channel (a stated rule).

---

## 10. Infrastructure and Resources (Official)

### Hosted by the Community at files.decomp.dev

The following resources are maintained at `files.decomp.dev` and are always-current links:
- `compilers_latest.zip` — complete archive of all GC/Wii Metrowerks compiler versions used by community projects
- IBM PPC Compiler Writer's Guide (CWG) — the single most-referenced document for understanding unusual assembly patterns
- Gekko User Manual (GameCube)
- Broadway User Manual (Wii)
- Standard PowerPC ISA reference

### Key Online Tools

| Tool | URL | Purpose |
|------|-----|---------|
| decomp.me | https://decomp.me | Collaborative matching scratchpad with GC/Wii compiler support |
| CExplorer | https://cexplorer.red031000.com | PPC compiler explorer (sometimes down) |
| ghidra.decomp.dev | https://ghidra.decomp.dev | Shared Ghidra server for community projects |
| decomp.dev | https://decomp.dev | Progress tracking and community hub |
| YAGCD | https://www.gc-forever.com/yagcd/ | GameCube hardware documentation |

### Key Local Tools

| Tool | Source | Purpose |
|------|--------|---------|
| decomp-toolkit (dtk) | github.com/encounter/decomp-toolkit | Project management, disassembly, splitting |
| objdiff | github.com/encounter/objdiff | Local binary diff and match verification |
| wibo | github.com/decompals/wibo | Lightweight Wine alternative for Metrowerks tools |
| decomp-permuter | github.com/simonlindholm/decomp-permuter | Random C mutation for register-allocation matching (MIPS/C only at time of archive; PPC C++ support absent) |
| gc-wii-binutils | github.com/encounter/gc-wii-binutils | Cross-platform `powerpc-eabi` binutils builds |

---

## 11. Known Gaps Still Requiring Discord Access

Topics that came up but for which the public record remains incomplete:

- **PPC permuter**: The decomp-permuter does not support PowerPC C++ at the time of this archive. It is a repeatedly expressed community pain point. No public release of a PPC permuter exists.
- **Exact CI/CD configuration**: Most projects do not have their GitHub Actions workflows in the public repo or they 404. The community runs CI, but the exact setup is shared informally.
- **Per-project code review checklists**: What specific things project leads check on PRs is not documented. It varies by project and is learned through submitted PRs.
- **WSL ARM64 compatibility**: Whether WSL on ARM64 Windows machines (e.g., Surface Pro X, Snapdragon laptops) can run the toolchain was mentioned but not resolved in this archive.
- **Build error reference**: There is no central troubleshooting guide. Error diagnosis is done by posting in the channel and waiting for community response.

---

*Extracted: April 2026*  
*Source: General channel archive, doldecomp Discord server*  
*Method: Targeted keyword grep analysis across ~718K lines, manual context review of high-signal hits*  
*Confidence: High for factual tool and workflow claims (direct quotes from multiple contributors); Medium for community sentiment and meta-discussions (reflects channel tone, not formal policy)*
