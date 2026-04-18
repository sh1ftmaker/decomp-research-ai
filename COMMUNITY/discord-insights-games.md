# Discord Insights: Game-Specific Channels

**Source:** Discord archives from game-specific channels (smash-bros-melee, animal-crossing, mario-kart-double-dash, mario-party)
**Extracted:** 2026-04-17
**Confidence:** Medium-High (direct channel archives, anonymized)
**Coverage:** Actionable technical insights only — no verbatim quotes, no usernames

---

## Table of Contents

1. [Super Smash Bros. Melee](#super-smash-bros-melee)
2. [Animal Crossing](#animal-crossing)
3. [Mario Kart: Double Dash](#mario-kart-double-dash)
4. [Mario Party 4](#mario-party-4)

---

## Super Smash Bros. Melee

### Architecture

- The DOL is split into two major regions: game code (first half of the text section) and CW PPC / Dolphin SDK library code (second half). The boundary between game code and library code can be identified by splitting the main text section.
- The sysdolphin layer (`HSD_*` functions) has confirmed file boundaries mapped to specific address ranges. Key files include `mobj.c`, `aobj.c`, `lobj.c`, `cobj.c`, `fobj.c`, `pobj.c`, `jobj.c`, `displayfunc.c`, `initialize.c`, `video.c`, `pad.c`, `objalloc.c`, `id.c`, `wobj.c`, `fog.c`, `perf.c`, `list.c`, and `object.c`. Exact address ranges for each were determined by contributors.
- The `hsd_gobj` file is actually split across at least three separate `.c` translation units. The name `hsd_display` maps to `displayfunc.c`, and `hsd_init` maps to `initialize.c`. These names can be cross-referenced using debug symbols from Bloody Roar: Primal Fury.
- Stage-specific code is organized into roughly 28 stage files, plus approximately 20 menu-related files. Fighter special moves are split on a per-move basis rather than per-character — the naming convention follows `ft[fighterJPName]special[n/s/hi/lw/etc].s`.
- Fighters are identified internally by their Japanese names (e.g., Jiggs = Purin). All fighter function naming should follow this convention.
- The fighter struct's action state system uses a table of function pointers for interrupt, draw, and other callbacks. The `OnLoad` function pattern per character is well-established via the m-ex and UnclePunch modding communities.

### Compiler Flags and Configuration

- The primary compiler is **MWCC Build 156/158** (early 2001 vintage, approximately version 1.1). The game does NOT appear to have been compiled with `-proc gekko` despite targeting the Gekko CPU — evidence suggests the `__PPCGEKKO__` preprocessor define is absent, meaning they may have used `-proc 750` or even `-proc generic`.
- Confirmed working base flags: `-O4,p -fp hard`. The `-proc gekko` flag is optional and may cause epilogue ordering differences.
- **sysdolphin** uses a potentially different flag set than game code. Evidence points to `-proc 750 -O4,p` for the library layer, and possibly `-vector on` (passed as a compiler flag, not pragma).
- `-O4,p` and `-O4` are not the same: `-O4,p` optimizes for speed while `-O4` is the generic form. Using the wrong variant causes register swap differences.
- Pragma-level opt control works: `#pragma optimize_for_size off/on` can toggle between speed and size optimization mid-file, and `#pragma opt_level 2` can apply per-function. Adding or removing these pragmas around specific functions has resolved previously-stuck nonmatchings.
- `-inline deferred` or `-inline smart` can cause functions elsewhere in the same file to suddenly start matching or stop matching. Context-dependent inlining is a significant source of cross-function interference.
- `-fp_contract on` does not work as a compiler flag for enabling `fmadds`; use `#pragma fp_contract on` instead.
- `-vector on` must be passed as a compiler flag, not via pragma.

### Matching Challenges

- **Register allocation** is the most common mismatch source. Even simple functions (e.g., a 3-element float vector add) produce register order differences that are hard to force. Changing the typedef or the order of struct fields has been observed to affect register allocation.
- **Stack variable placement** is a chronic issue. The compiler allocates extra stack space for variables that get optimized out, making the stack frame size larger than expected. Introducing temporary "junk" variables at specific opt levels (e.g., `O2`) has been used to coerce the correct stack frame size.
- **Inlined functions** create complex matching situations. When a small accessor like `GetNext()` is marked `inline`, the compiler may or may not expand it depending on context. Declaring the inline in a header and including it in the same TU as the caller is required — the inline flag is a suggestion, not a guarantee.
- **HSD_FObjRemoveAll** is a well-documented example of inline interaction: multiple nested inlined calls were required to reproduce the correct register order in the caller.
- **`sqrtf`** is inlined and includes a `volatile` local variable. Reproducing this pattern requires matching the exact volatile placement.
- **Epilogue ordering** has been observed to differ based on `-proc` target. Most files match on `-proc gekko`, but sysdolphin shows differences.
- **Math-heavy functions** are described as "almost impossible to match" because there are many valid algebraic rearrangements and the compiler can choose any of them under `-O4`.
- Adding new code to a file can cause previously nonmatching functions in the same file to suddenly match, due to `-inline deferred` re-evaluating the whole translation unit.
- **Nonmatching stubs**: The correct approach for functions that cannot be matched is to use `*(volatile int *)0 = 0;` writes to pad the function to the correct instruction count. Using inline ASM for the entire function works but is last resort due to ordering side effects.
- The `nofralloc` keyword (used in inline ASM) is not available in C compilation mode; it must be inside an `asm {}` block.

### Reference Games and Cross-Project Resources

- **Killer7** (HAL/Grasshopper Manufacture) uses the same sysdolphin library with minor version differences and leaked modified source files. Specific files like `displayfunc.c`, `initialize.c`, `mobj.c`, `pobj.c`, `tobj.c`, and `video.c` are available from this leak. Killer7's debug ELFs have no optimization, making them useful for pure struct layout analysis.
- **Bloody Roar: Primal Fury** (Eighting) uses sysdolphin with debug symbols, providing confirmed source file names for the HSD layer.
- **Zoids: Battle Legends** has portions of `HSD_Audio` and `HSD_Archive` not present in Melee's versions, useful for completing those modules.
- The **FRAY** project (a non-matching decomp by a community veteran) has accurate struct definitions for the Fighter struct, HSD objects, and many sysdolphin types. This is the recommended starting point for struct work.
- The **m-ex** fighter modding framework provides independently-derived fighter struct offsets that have been validated against the game.
- The community spreadsheet of addresses and struct layouts (Google Sheets) was assembled primarily by cross-referencing FRAY, m-ex, UnclePunch's Training Mode mod, and Killer7 debug data.

### Fighter-Specific Insights

- Fighter code (character `OnLoad`, special move functions) is significantly easier to match than sysdolphin or the main engine, partly because the modding community (m-ex, UnclePunch) has independently documented the fighter struct and action state tables.
- Clone characters share almost identical code in their `OnLoad` functions and many common actions.
- The `ftData` struct offset within the fighter/player structure is confirmed at `0x10C`.
- The `SET_ATTRIBUTES` macro pattern for copying character-specific attribute structs is used consistently across all character `OnLoad` functions and must be reproduced as a macro using a forced pointer struct-copy to avoid compiler unrolling.
- Fighter special moves use the Japanese character name in the file naming: e.g., `ftMario`, `ftFalco`, `ftseak` (Sheik).
- `ftCo` (common fighter code) and `ftAi` (AI) are among the identified fighter file prefixes.
- GNW (Game and Watch) was identified as likely the easiest fighter to match due to simple move set.

### Build System Notes

- Initially, the entire game was assembled as one massive `disasm.s` file (~50MB), which caused GitHub file size warnings and made linking slow (~28 seconds). Splitting into per-file `.s` objects dramatically reduced link times.
- When splitting `.s` files, cross-file label references are a concern — a function in `fighter2.s` may reference labels defined in `fighter1.s`. The solution is to verify links after each split.
- The build target SHA1 hash (for NTSC 1.02) is `08e0bf20134dfcb260699671004527b2d6bb1a45`.
- There is known incompatibility between LTO (link-time optimization) and matching decompilation — LTO must not be used.

---

## Animal Crossing

### Architecture

- Animal Crossing (GC) is architecturally a port of a Nintendo 64 game (`Doubutsu no Mori +`). The GC version was never redesigned from the ground up for GameCube hardware; it carries N64-era constraints throughout.
- The game contains **`emu64`**: a custom N64 F3DZEX2 → GameCube GX graphics translation layer. This is a complete software emulator of the N64 RSP graphics microcode, compiled on the GameCube. The three N64 versions (`DnM`, `DnM+`, `DnM e+`) each had different compilation flags for the emulator, providing three reference points for decomp.
- The game uses **N64 audio ROM format** on GameCube. There is a custom audio translation layer (`jaudio`) that converts N64 audio data to the GC DSP. The `jaudio` module is described as "100% customized" from its N64 origin and was identified as one of the hardest parts of the project.
- The `Famicom.a` library (in-game NES emulator for the included NES games) is a distinct large library component. This is separate from `emu64`.
- `JSystem` usage in AC is described as "minimal" compared to later Nintendo EAD games. AC uses only core kernel classes and a few utility and J2D classes.
- Module archive structure derived from the symbol map: `BBA` has `RevoSDKD.a` for all Dolphin SDK modules.
- The N64 SDK is a build requirement due to N64 graphics code being present.

### JSystem in Animal Crossing

- AC uses an older version of JSystem than most other GC Nintendo EAD titles. The version predates Pikmin 2's JSystem, and `e+` (the Japanese re-release) appears to use an upgraded version.
- **Separate compiler flags are required for JSystem vs. game code.** The confirmed JSystem flags are: `-fp hard -proc gekko -enum int -O4,p -Cpp_exceptions off` with implied `-inline auto`. Using DOL flags for JSystem causes mismatches.
- JSystem's `.sdata` threshold appears to be 8 bytes (not the default 4). This affects where small variables are placed.
- `-sym on` is required for JSystem compilation.
- RTTI string ordering was a persistent blocker. When JSystem C++ classes are compiled with wrong flags (e.g., using DOL flags instead of JSystem flags), the RTTI strings appear in wrong order in `.data`, causing section mismatches even when individual functions match.
- The `.ctors` section required `trim_ctors: true` in `disasm_overrides.yml` and proper `FORCEFILES` generation in the linker script to correctly handle C++ constructor pointers.
- A ppcdis bug caused 4 extra bytes to appear after certain `.ctors` entries; this was fixed in a later ppcdis update.
- `JKRDvdFile.cpp` required implementing `JKRThread`, `JKRDecomp`, and `JKRDvdRipper` before its ctors section would match.
- `JKRThread` has a notable quirk: the `run` method is marked as a `weak` virtual, which caused matching failures until identified.
- Pikmin 2's JSystem decompilation served as a key reference for AC's JSystem work, with TP debug providing additional coverage for functions not yet decompiled.

### N64 Cross-Reference Value

- The N64 (`DnM+`) version has **two symbol maps**: one detailed (with unused functions and linker info) and one trimmed. The detailed map shows unused functions that were stripped from the US GC release. The US GC (`AC`) only has the trimmed map.
- Comparing `DnM+` and `DnM e+` function sizes against AC helps identify what code was added, removed, or inlined across versions.
- Some N64 functions that appear inline-capable on N64 (using `IDO` compiler, which stubs used-but-unreferenced statics to `jr ra / nop`) are full functions on GC. The inverse is also true.
- Zelda-related N64 decomp projects (ZeldaRET) have documented version differences between N64 Zelda titles and DnM, providing additional cross-reference data.

### Hard-to-Match Patterns

- **`jaudio`** is considered the hardest module to match in the entire project. It is completely customized from the N64 audio library and has a complex conversion layer to the GC DSP.
- **`emu64`** (the N64 graphics emulator) was decompiled as non-matching initially. A contributor completed 100% of the emulator code but noted it required careful matching of GBI (Graphics Binary Interface) macros that were not yet implemented in the decomp.
- **N64 audio ROM → GC DSP translation layer** (`AC has a transition layer for N64 audio rom -> GC DSP`): This is a further-customized descendant of the N64 audio library. Its architecture is described as "100% the worst part of AC."
- Some branches in the codebase appear as empty `else` blocks: `if (cond) { // code } else { // body was optimized out but the branch remained }`. These must be reproduced by writing code that generates the branch instruction without any body, typically via a dead comparison.
- **`gutranslate`** was originally an assembly function on N64 — the GC version required matching an asm-to-C transition that wasn't immediately obvious.

### Compiler Flags (DOL)

- Confirmed DOL compiler flags from the codebase: `-fp hard -proc gekko -enum int -O4,p -Cpp_exceptions off`
- Linker flags include: `-fp hard -w off -maxerrors 1 -mapunused`
- A common early mistake was placing `-fp hard` only on the linker command line, not the compiler — causing the compiler to use `-fp soft` (default), resulting in mismatches in floating-point code.
- The REL compiler for associated modules (in the N64 graphics context) uses MWCC 1.3.2.

### Progress Notes

- The project reached 99% matching on the text section before the RTTI string ordering issue was resolved. The remaining blocker at that stage was two swapped RTTI strings in `.data`.
- The `libforest` library had only one file remaining (the graphics emulator) when a contributor noted the project was near completion of that section.
- `JSystem` progress was a major driver of overall DOL percentage due to its size (~10% of the DOL code section).

---

## Mario Kart: Double Dash

### Architecture and Module Organization

- MKDD's code is organized by **programmer name**. The symbol map reveals distinct archive libraries named after each programmer: `KaneshigeM.a`, `OsakoM.a`, `YamamotoM.a`, `SatoM.a`, `KamedaM.a`, `BandoM.a`, `InagakiM.a`, `KawanoM.a`, `ShirawaM.a`. Each library corresponds to one developer's code.
- `KaneshigeM.a` contains the largest portion of game-specific code including the core race manager (`RaceMgr.cpp`), kart logic, course code (`Course.cpp`), and UI (`RaceUsrPage`). It uses `O4,p` optimization throughout.
- `OsakoM.a` contains input handling (`kartPad.cpp`) and resource management (`ResMgr.cpp`, `LogoApp.cpp`).
- `YamamotoM.a` contains physics and camera code (`kartvec.cpp`, `KartPerCam.cpp`).
- `SatoM.a` contains math utilities including a custom `SpeedySqrtf` function.
- `BandoM.a` is 100% complete (very small).
- `JFramework` (100% complete early) and `JMath` (100% complete) within `JSystem` were the easiest JSystem sub-libraries.
- The game targets both a **Debug** and a **Release** (MarioClub_us) build. Both must be matched, and some functions differ between them in codegen, requiring separate implementations for the same function.

### Compiler Flags (Multiple Presets)

- MKDD uses **multiple compiler presets** within a single DOL, varying by programmer/module:
  - `Kaneshige`: `-O4,p` (optimize for speed)
  - `JMath` in release: `-O4,s -peephole off` (optimize for size, no peephole)
  - `JMath` in debug: `-O4,p`
  - `OsakoM` input handling: some files use `-O0`
  - The MSM audio library uses an older compiler (version 1.2.5) while the main game uses 2.6.
- The confirmed release compiler is **MWCC 2.6**. Debug uses a similar version but with debug flags active (assertions enabled, no stripping).
- JSystem in MKDD was built with `peephole off` for release.
- The game has at least 4-5 different `decomp.me` preset configurations needed to cover all its different compiler flag combinations.
- A JSystem "phantom compiler" issue was identified: two specific JSystem functions only match with MWCC 1.3.2 but not 2.6, while adjacent code in the same TU only matches with 2.6. This suggests a JSystem version fork within MKDD's build system.

### Kaneshige Code Style (Hardest Module)

- Kaneshige's code has a distinctive non-idiomatic boolean style that requires precise reproduction to match. Example: instead of `bool x = condition;`, the code uses an explicit `if (condition) x = true;` pattern with the boolean initialized to `false` first.
- Debug and release builds of the same Kaneshige function sometimes require **different C source code** to match. One example: `isDefaultCharCombi()` requires accessing `mKartCharacters` in a different field order between debug and release.
- Boolean return values in Kaneshige code almost universally follow the `ret = false; if (cond) ret = true; return ret;` pattern. Using a direct `return cond;` will not match.
- Kaneshige's loop code often has unusual early-exit or early-continue patterns that must be reproduced exactly.
- The `getKartInfo()` inline accessor differs between debug (direct field access with assert) and release (calls `mRaceInfo->getKartInfo(index)` method). A `#ifdef DEBUG` block is required.
- `RaceMgr.cpp` data (`sEventTable`) is placed in `.rodata` on decomp.me but ends up in `.data` locally — this is a known alignment/section placement issue that requires investigation.

### BSS and Linking Challenges

- MKDD has a **common BSS bug** where BSS symbols shared across multiple TUs cause the BSS section to become inflated. The root cause is a `JASFakeMatch.h` header that, when included, causes every including TU to get a spurious `sinit` and an array of 4 unused floats (more common in debug than release).
- BSS is split into two regions with TU ordering repeating — each TU's BSS contributes twice to the section, which must be accounted for in splits.
- To work around the common BSS inflation, a contributor suggested creating a fake TU for all common BSS symbols and linking it last.
- A specific BSS issue in `kartPad.cpp`: the `gKartPad1P` symbol is `0x98` bytes in the real binary but `0xb8` bytes when compiled from source, due to a `gKartPad1P` size difference from unresolved common BSS ordering.

### Inline Patterns

- CW (CodeWarrior) inlines methods defined inside class bodies even at `-O0` and even without the explicit `inline` keyword. This is an important behavior difference from GCC/Clang.
- The `testButton` and `testTrigger` inlines in `RaceMgr.cpp` differ between `O4,p` and `O4,s` — only one of them matches with each optimization level.
- Several functions have hidden inlines that are only discovered when a vector on the stack has unexpected size. The typical signal is a stack size mismatch with otherwise correct code.
- Prototype declaration scope matters: if a function prototype is included in a header but the header has a different name than expected, it will not match.

### sqrtf and Math

- MKDD uses two distinct fast-sqrt implementations: `stspeedy_sqrtf` (unused, in `SatoM.a stMath.cpp`) and `SpeedySqrtf__8KartMathFf` (used, in `YamamotoM.a kartvec.cpp`).
- The game uses MWCC's `std` namespace sqrtf with the NaN checks present (indicating MWCC 2.6 or compatible), but the static keyword was removed to match the symbol map even though that makes the symbol technically incorrect.
- `Instrtoul` required the pattern `count = value = *chars_scanned = 0;` (compound assignment in declaration) to match at `O0`.
- The `*dst++ = *s1++` pattern versus `*dst++ = *(s16 *)s1++` versus `*dst++ = *((s16 *)s1)++` all produce different codegen and only one will match.

### Progress Snapshots

- At project start, `BandoM` (100%) and small JSystem sub-libraries were the first completions.
- `JFramework` reached 100% early and served as a template for JSystem organization.
- `JMath` and `JSupport` reached 100% in the same push.
- At ~15% overall DOL progress, `JKernel` was ~50%, `Osako` was ~7%, and `Kaneshige` was still ~7%.
- A late-stage progress report showed `JKernel` at 100%, `JUtility` at 100%, `JMath` at 100%, `JSupport` at 100% — with `Kameda`, `Kawano`, `Shiraiwa`, and `Yamamoto` all essentially untouched.

---

## Mario Party 4

### Architecture

- Mario Party 4 uses **Hudson Soft's proprietary engine**. The DOL contains the engine core, and all game content (boards, minigames) lives in **REL files** (Relocatable ELF modules) that are loaded and linked at runtime. Hudson refers to these internally as "DLLs" — the files are named `bootDll.rel`, `m001Dll.rel`, etc.
- **Each minigame is a separate REL file.** Each board is also its own REL. There is a master table at `_ovltbl` (0x8012FDE0) listing all DLLs.
- String paths embedded in REL files reveal the original build directory: `e:\project\mpgce\prog\DLLS\bootDll\bootDll.elf` — each REL was compiled from a separate directory.
- `bootDll.rel` is the first REL loaded and contains bootstrap and Nintendo logo code. Uniquely, the compressed Nintendo logo graphic data is embedded directly in `bootDll.rel`'s `.data` section rather than being loaded from a file.
- Minigame naming follows an internal numbering scheme: `m1xx` = MP2-era minigames (ported), `m2xx` = MP3-era minigames, `m3xx` = partially-built placeholder DLLs (mostly empty), `m4xx` = new MP4 minigames. Several `m3xx` DLLs appear to be incomplete stubs from mid-development cleanup.
- The `m433Dll.rel` (beach volleyball) was ported forward to MP5 under the same filename.
- The data directory system uses 32-bit IDs: upper 16 bits = directory index, lower 16 bits = file index within that directory. The full directory-to-bin-file table is part of the DOL.

### REL Format

- MP4 uses **REL format version 2** (not version 3 as used by some other games). Version 3 allows "trimming" of self-referential and DOL-referential relocations to save memory (at the cost of not being able to unlink), while version 2 retains all relocation data.
- The REL header format v1 does not include module alignment or BSS alignment fields (offsets 0x40 and 0x44); v2 adds these.
- REL linking in MP4 is done **one REL at a time** (unlike some multi-REL setups in other games).
- `.ctors` and `.dtors` sections in RELs must have their data deleted (zeroed) in the section table; keeping them causes relocation failures. `.rodata` must be aligned to 8 bytes, and `.data` must also be aligned to 8 bytes.
- ASCII strings in REL assembly files must have their `.balign 4` directives removed and the string encoding fixed — this is a quirk of the Hudson REL disassembler.
- The `elf2rel` tool must be customized for MPDD's REL version. The TTYD version of `elf2rel` exists but needs a symbol file. The SMB1 makefile was cited as the best reference for multi-REL build setup.
- REL linking uses `mwldeppc.exe` with flags: `-lcf partial.lcf -nodefaults -fp hard -r1 -m _prolog`.
- When building all RELs in parallel with ninja, the linker map file write caused conflicts (concurrent writes to the same `.MAP` file). Running the REL link commands sequentially avoids this.

### Compiler and Build

- The confirmed compiler is **MWCC 2.6** (same as MKDD release). The MSM audio library (Hudson's custom audio library) uses an older compiler — **MWCC 1.2.5**. Some MSM functions had prologue ordering issues with newer compiler versions and required staying on 1.2.5.
- Switching from wrong compiler version to 1.3.2 for certain modules caused a large immediate jump in matched percentage (nearly +10% in one change).
- String pooling was enabled (`-pool on`) for the DOL.
- The DOL uses the Dolphin SDK version between Pikmin 1 and Pikmin 2.

### Hudson Engine Details

- The **HSF (Hudson Scene Format)** model format is the primary 3D asset format. It is completely different from Nintendo's standard GC formats. The main rendering translation unit is `hsfman.o`, and image data for reflections, toon maps, and highlights is the first content in it.
- Hudson rarely uses rodata except in libraries — game code almost never has explicitly declared rodata.
- The text encoding for MP4 (menus, board strings) follows the same system as Mario Party 3, documented at the PartyPlanner64 wiki.
- Hudson's memory system uses `HuMemDirectMalloc(heap_num, length)` for direct heap allocation, where `heap_num` identifies which of several custom heap pools to allocate from.
- The data compression format is a custom two-variant slide decompressor (similar to Yaz0 but with 32-bit flag words). One variant has an edge case with negative references into data before the start of the buffer.
- `HuDecodeData(src, dst, length, type)` dispatches to the correct decompressor based on the `type` field in the compressed data header.

### Hardest Modules

- `hsfdraw.c` and `player.c` are each approximately 4% of the entire DOL and were identified as the hardest/largest single-file challenges. One function in `hsfdraw.c` remained unsolved for an extended period.
- `mapspace.c` (board map logic) was the other explicitly-named hard file.
- `FaceDraw` was the last file to be completed before external libraries.
- The board code was surprisingly accessible: described as "not that hard for this game" compared to the rendering and player subsystems.

### Milestones

- Mario Party 4 is the **first GameCube game to reach 100% matched and 100% linked** decompilation. This was considered unlikely when the project started — the game was obscure enough that contributors were surprised it would be the first to complete.
- The project crossed 50% overall progress. At 80%+, the main remaining work was external libraries (MusyX, MSL, Dolphin SDK) and a few large DOL files.
- **MusyX** (the commercial audio middleware from Factor 5/Sndscape) was integrated as a submodule from another project's decompilation. Using it as a submodule provided a significant free percentage boost.
- Progress tracking was implemented via a custom Python script (`progress.py`) that compares `.text` section sizes. A GitHub Actions CI/CD integration was set up, making MP4 one of the first GC projects to have automated CI.
- The project maintained both a **1.00** and a **1.01** build target, with PAL as an additional goal.
- A characteristic difficulty was that the early and late percentages (first 1% and last 1%) were the slowest, with the middle portion moving quickly once the engine structure was understood.

### Tips for Contributors

- Decompile functions that call `HuMemDirectMalloc` early to establish struct sizes — the heap number and allocation size reveal the struct's byte size directly.
- Each REL's `.ctors`/`.dtors` sections must be explicitly handled in the linker script. Using `FORCEACTIVE` alone is not sufficient for REL builds; the linker may omit constructor pointers without explicit handling.
- The 0.5 and 3.0 double constants (as 64-bit IEEE 754) appear as the first items in `.rodata` for nearly every REL translation unit. This can be used to verify correct `.rodata` section generation.
- Hudson's code style is not exemplary — expect verbose, non-idiomatic patterns. The mp1-mp3 era code has "some nasty code" that was partially carried forward.
- When symbols or RTTI data are absent for C++ portions (as in MP5), the MP4 codebase serves as a fallback reference for function names and struct layouts.

---

*Document generated from Discord channel archives. All usernames have been anonymized. Confidence level: Medium-High for technical content, Medium for progress figures (which reflect snapshots from specific conversation dates, not current project state).*

*For current project status, see the live repositories and decomp.dev.*
