# Discord Insights: Libraries & SDK Channels

**Source:** Discord archives from the `#jsystem`, `#egg`, `#musyx`, and `#sdk` channels  
**Extracted:** 2026-04-17  
**Confidence:** High for cross-confirmed facts; Medium for inferred patterns  
**Note:** Author identities anonymized. No verbatim quotes reproduced.

---

## Table of Contents

1. [JSystem](#jsystem)
2. [EGG Library](#egg-library)
3. [MusyX Audio Library](#musyx-audio-library)
4. [Dolphin SDK / RVL SDK](#dolphin-sdk--rvl-sdk)

---

## JSystem

Nintendo's JSystem is the primary GameCube-era engine library, used across virtually all first-party GC titles. It is written in C++ and contains subsystems for memory management, DVD access, 2D/3D rendering, audio, input, font, and scripting.

### Version Landscape

- There is no single authoritative JSystem. **Every game has a slightly different version** of the library, making a monolithic JSystem repository impractical. The community recommendation is to add sub-libraries to a shared repo only once they are fully matched in a game repository.
- The earliest known JSystem versions appear in the GC BIOS and Luigi's Mansion. Luigi's Mansion and Super Mario Sunshine appear to share a nearly identical JSystem version.
- Animal Crossing (DnM+) contains a very early version, predating SMS in some sub-libraries (e.g., `JUTGamePad` lacks virtual functions that appear in later versions).
- Twilight Princess contains a later, more mature version (J2D 2.0, JPA 2.10, JMessage, JStage). TP has full symbols and a debug build, making it the best reference for inlining and internal structure.
- Pikmin 2 is another strong reference: it is fully split and shiftable, and `JSupport` in Pikmin 2 was the first JSystem sub-library to be fully match-decompiled.
- Super Mario Galaxy no longer uses JSystem; by the Wii era the library was split into NW4R (NintendoWare for Revolution) and EGG.
- The evolution chain: JSystem (GC) → NW4R + EGG (Wii) → NW4C (3DS) → NW4F (Wii U) → libnn (Switch).

### Library Packaging

- Early games (SMS era and before) ship JSystem as a single monolithic archive: `JSystem.a`. The symbol map lists all JSystem TUs under this single archive name.
- Later games (TWW era and after) split JSystem into discrete archives: `JKernel.a`, `JUtility.a`, `JSupport.a`, `jaudio.a`, etc. This correlates with both toolchain maturity and which sub-libraries a given game needed.
- Luigi's Mansion organizes code by developer name, so some JSystem-equivalent code lives under developer-prefixed directories (e.g., `PSystem`) rather than a `JSystem` folder.

### Sub-Library Overview and Game Coverage

| Sub-library | Key Games | Notes |
|------------|-----------|-------|
| JKernel | AC, LM, SMS, MKDD, TP, Pikmin 1/2 | Core heap/archive/DVD/thread system; most widely used |
| JUtility | AC, TP, MKDD, Pikmin 2 | Console output, color, palette, gamepad |
| JSupport | Pikmin 2 (100% matched), TP | Streams, lists; authorship attributed to Yamashita dev |
| J2D | SMS (early version), TP (J2D 2.0) | 2D graph library; version differs between SMS and TP |
| J3D | TP, MKDD | 3D model rendering |
| JAudio | Pikmin 1 (old JAudio 1, needs `-proc 750` not gekko), Pikmin 2, MKDD | At least four distinct JAudio versions; JAudio2 has a debug build |
| JDrama | SMS only | Scripting system; considered an early bad idea; bad ideas continued in JStudio |
| JStudio | TP, MKDD | Cutscene/animation scripting; successor to JDrama |
| JStudio_JMessage | Pikmin 2 (partially done) | Sub-library of JStudio for message handling |
| JMessage | TP, Pikmin 2 | BMG message system; very sparse outside TP and Pik2 |
| JFramework | TP (debug console), MKDD | Used for debug console; remove `JUT_Validate` lines to match non-debug versions |
| JGadget | TP, MKDD, LM (uncertain) | Templated vector/list with `Vector_void`/`List_void` non-template backing TUs |
| JParticle | TP (JPA 2.10), Skyward Sword | On Wii, JParticle likely uses EGG heaps/vectors |

### Matching Strategies for JSystem

- **Compiler flags matter per sub-library.** JSystem is not compiled uniformly. For example, in MKDD, release builds optimize for size (`-O4,s`) for most sub-libraries, but inlined functions (header-only) are compiled for speed. JAudio in MKDD release is optimized for speed. Debug builds are a mixed bag: some sub-libraries use speed, others size.
- **Pikmin 1's old JAudio 1** is unique in requiring `-proc 750` rather than `-proc gekko`. This is the only known case where the processor flag differs from the rest of the game.
- **Vtable ordering is the dominant matching problem** for J2D and any class hierarchy that inherits across multiple files. The rule: declare virtual functions in the same order as the vtable and it will match every time. J2D in TP has a known vtable ordering issue in `J2DAnmLoader` that remains non-matching.
- **Version differences cause silent mismatches.** A function that matches in one game's version of JSystem may not match in another due to subtle differences in optimization or added/removed code. Always identify which version the target game uses before borrowing a match from another project.
- **Static class variables** are a persistent BSS ordering problem. Static class member variables receive global linkage, causing them to appear later in BSS than expected when linked as individual object files rather than as part of the full JSystem blob. The workaround is to declare the static class variable later in the translation unit, but this only works for simple globals, not class statics.
- **JKRExpHeap::create** is a common test case. Using `#pragma optimize_for_size off` on this function was required to match in some games. In MKDD it matches by default; in Pikmin it does not without the pragma.
- **The `sincosTable` in JMATrigonometric.cpp** is 0x4000 bytes (2048 entries of `{f32 sine, f32 cosine}` pairs). The linker map reports a misleadingly large size for the first BSS entry in a TU because it includes the total size of all common BSS in that TU, including stripped symbols.

### RTTI and Class Hierarchies

- **RTTI is present in Animal Crossing (GC)**, which surprised contributors — it was not expected for an early game. Later games (TP, MKDD) also have RTTI where debug builds are available.
- Animal Crossing has a **different vtable layout for JKRHeap** compared to Pikmin 2.
- **JGeometry::TVec3f** in TP inherits from `Vec` (the base float vector). The `s16` and `double` variants do not use inheritance; they have separate implementations. MKDD uses the same header arrangement.
- **TParamT and TParamBase** appear in Luigi's Mansion and Sunshine. SMS has `TBaseParam`, `TParamT<>`, and `TParamRT<>` for basic types (int, float, short, unsigned char). LM's `TParamRT` vtables are identical to their TParamT counterparts, suggesting a near-identical version.
- **JGadget's template design**: The implementation pattern is `Vector_void` / `List_void` (non-template, has a proper TU with code) plus `Vector_pointer` / `List_pointer` (templates on top of the void versions). This layered pattern is consistent across all games where JGadget appears.

### Key File Paths (from "hagi" ports of SMG and Pikmin 2)

```
JSystem/System/JKernel/src/JKRAram.cpp
JSystem/System/JKernel/src/JKRAramArchive.cpp
JSystem/System/JKernel/src/JKRExpHeap.cpp
JSystem/System/JKernel/src/JKRHeap.cpp
JSystem/System/JUtility/src/JUTPalette.cpp
JSystem/JAudio/JASystem/Player/src/JASSeqParser.cpp
JSystem/JStudio/JStudio/src/stb.cpp
JSystem/System/JUtility/src/JUTCacheFont.cpp
```

### Known Gaps

- No single "canonical" JSystem repository exists. One requires identifying which game's version to target.
- JAudio internal structure is complex; it has at least four distinct generations. Sub-components include JAD (1 file), JAI (39 files), JAL (2 files), JAS (58 files), and JAU (17 files), plus a DSP component.
- JAudio in Pikmin 1 uses some `libultra`-style symbol names, suggesting early N64-era lineage.
- JMessage outside of TP and Pikmin 2 is largely uncharted. Pikmin 2 appears to be the only game with a fully decompiled JMessage.

---

## EGG Library

EGG (likely "EAD Game G___" — the last word is unknown to the community) is Nintendo EAD's Wii-era middleware library. It is a direct descendant of JSystem, providing memory management, threading, I/O, math, graphics, audio, and scene management for first-party Wii titles. NW4R (NintendoWare for Revolution) was provided to all third-party developers; EGG was kept internal to EAD.

### Games That Use EGG

Confirmed EGG users (from RTTI strings, heap signatures, and build strings):
- Mario Kart Wii
- New Super Mario Bros. Wii
- Wii Sports, Wii Sports Resort
- Wii Fit, Wii Fit Plus
- Wii Play, Big Brain Academy: Wii Degree
- Animal Crossing: City Folk
- The Legend of Zelda: Skyward Sword
- All "Pack Project" (Wii Party, etc.) games
- New Play Control! Pikmin and Pikmin 2

Games that do NOT use EGG: Super Mario Galaxy (uses a different internal framework), some non-EAD first-party titles.

**Detection method**: The presence of `EGG::ExpHeap::create` is the most reliable indicator. This function always emits two adjacent `rlwinm` instructions. Searching for `eggExpHeap` strings or `ExpHeap::create` in a binary is a quick confirmation. `EGG::Thread` initializes using `OSGetCurrentThread()`; absence of that pattern at system init implies no EGG thread/heap system.

### Inheritance Hierarchy

EGG inherits from NW4R in its math types:
- `EGG::Vector2f` inherits from `nw4r::math::VEC2`
- `EGG::Vector3f` inherits from `nw4r::math::VEC3`
- `EGG::Quatf` inherits from `EGG::Vector3f` (not from any nw4r quaternion type — this was considered a design mistake)

The `EGG::Disposer` pattern is foundational: scenes, heaps, and many managers inherit `EGG::Disposer` to register themselves for automatic cleanup. Notably, `EGG::HeapScene` inherits `EGG::Disposer` directly rather than going through `EGG::Scene`, which is an unexpected design choice confirmed by RTTI.

### Heap Subsystem

EGG has four heap types:
- `EGG::ExpHeap` — expanding heap (most common)
- `EGG::FrmHeap` — frame heap (stack-like allocation)
- `EGG::UnitHeap` — fixed-size block allocator
- `EGG::AssertHeap` — small heap (256 bytes) used as a buffer for assert console output

All wrap the Revolution SDK's `MEMiHeapHead` infrastructure. The base `EGG::Heap` constructor:
1. Stores the `MEMiHeapHead*` handle
2. Initializes a child list (using `nw4r::ut::List_Init` with offset `8`)
3. Asserts that `sIsHeapListInitialized` is true
4. Locks `sRootMutex` and appends `this` to the global heap list

`EGG::Heap::alloc` uses `_savegpr_27` (saves registers r27+), which is a useful matching fingerprint.

`sizeof(EGG::Heap)` is `0x3C`. `sizeof(EGG::ExpHeap)` adds the MEM heap extension header (`0x38` bytes reserved at the start of the heap block for the `ExpHeap` object itself, then the `MEMiExpHeapHead` at that offset).

The `create__Q23EGG7ExpHeapFPvUlUs` function is notoriously difficult to match because of subtle alignment arithmetic that generates specific `subf` and `rlwinm` instruction sequences.

The three overloaded `operator new` forms EGG provides:
```cpp
void *operator new(size_t size);                        // alloc(size, 4, NULL)
void *operator new(size_t size, int align);             // alloc(size, align, NULL)
void *operator new(size_t size, EGG::Heap *heap, int align); // alloc(size, align, heap)
```

### Compiler Flags for EGG

EGG is compiled with specific flags that differ from game code. Confirmed for MKW:
```
-lang=c99 -use_lmw_stmw=on -ipa function -rostr
```
`eggHeap.cpp` additionally uses `-ipa file`. The compiler version is `4201_127` (CodeWarrior Wii). The `-rostr` flag is responsible for some surprising behavior in how string constants are placed.

In debug vs. release builds, EGG exhibits different string counts inside functions like `Heap::dumpAll` — debug versions have more assert strings, providing useful anchors for identifying function boundaries.

### RTTI Patterns in EGG

EGG RTTI layout for a class with inheritance follows the standard MWCC layout:
1. `__vt__<classname>` — vtable object
2. String object containing the class name
3. Pointer to base class RTTI (if any)

For `EGG::ColorFader` (inherits `EGG::Fader`), the layout in the binary is:
- `__vt__Q23EGG10ColorFader`
- String object for `EGG::ColorFader`
- `__vt__Q23EGG5Fader`
- String object for `EGG::Fader`

A class with no inheritance has only a string pointer followed by `nullptr`. The vtable's first word is the pointer to the RTTI typeinfo block; the second word is the virtual base offset.

Size inference technique: a debug constructor of size `0x4` implies just a default constructor calling the inherited constructor (no vtable assignment); size `0x34` implies one layer of inheritance with a vtable assignment.

### EGG Class File Map (Confirmed)

```
core/eggHeap.cpp         — EGG::Heap (base)
core/eggExpHeap.cpp      — EGG::ExpHeap
core/eggFrmHeap.cpp      — EGG::FrmHeap
core/eggUnitHeap.cpp     — EGG::UnitHeap
core/eggDisposer.cpp     — EGG::Disposer
core/eggThread.cpp       — EGG::Thread
core/eggTaskThread.cpp   — EGG::TaskThread
core/eggAllocator.cpp    — EGG::Allocator
core/eggColorFader.cpp   — EGG::ColorFader (abstract base: EGG::Fader)
core/eggGraphicsFifo.cpp — EGG::GraphicsFifo
audio/eggAudioMgr.cpp    — EGG::SimpleAudioMgr
audio/eggAudioSystem.cpp — EGG::AudioSystem
audio/eggAudioHeapMgr.cpp — EGG::SoundHeapMgr
audio/eggAudioArcPlayerMgr.cpp — EGG::ArcPlayer
audio/eggAudioExpMgr.cpp — EGG::SimpleAudioMgrWithFx
audio/eggAudioFxMgr.cpp  — EGG::AudioFxMgr
```

### Version Differences Between Games

EGG::Archive's `mount()` function signature differs between versions. In the earlier version (BBA-era games), it takes `(void*, Heap*)`. In later games (NSMBW and beyond), it takes `(void*, Heap*, int align)`. A `#define EGG_VERSION 200704L` style guard was used in community documentation to track this.

`EGG::Screen` in BBA is named `EGG::Screen`; in Wii Fit U it becomes `EGG::eggScreen`. `EGG::Frustum` similarly has naming changes. MKW appears to reimplement `nw4r::ut::List` as `EGG::utList` rather than using the shared NW4R version.

Skyward Sword's EGG is more advanced than NSMBW's. SS uses `-inline noauto` throughout EGG, making it easier to match (no unexpected inlining). SS EGG has some functions that do not exist in NSMBW (e.g., two forms of `ExpHeap::create` with different signatures).

### Gotchas

- `EGG::Quatf` does not inherit from any nw4r quaternion — it inherits `EGG::Vector3f`. This is unusual and was a design mistake acknowledged in the community. The x/y/z components of the quaternion are accessed via the inherited Vector3f members.
- `EGG::Math<f>::maxNumber()` requires `std::numeric_limits<T>::max()` — using the SDK's `<limits>` header causes compilation errors in some setups. Use a direct float constant as a workaround.
- `fromQuat` and `makeQ` in `EGG::Matrix34f` both do the same thing mathematically but produce different assembly — they are distinct functions and cannot be deduplicated.
- `EGG::Mutex` wraps `OSMutex` with a simple virtual destructor — it is a trivial wrapper but must be declared correctly to get the vtable generated.
- The `EGG::SimpleAudioMgr` class uses multiple inheritance: `IAudioMgr`, `SoundHeapMgr`, `ArcPlayer`, `AudioSystem`. RTTI confirms this and the vtable is segmented to account for the multiple base class offsets.

---

## MusyX Audio Library

MusyX (formerly MoSysFX, originally developed by Factor 5) is a third-party audio middleware used across many GameCube titles. It provides DSP voice management, SFX, sequencer, and streaming audio. The library has been successfully fully match-decompiled for multiple versions.

### Versions and What They Mean

MusyX has a clearly versioned history. Community-confirmed versions:

| Version | Key Changes |
|---------|-------------|
| 1.5 | Base streaming; `CheckOutputMode` used directly in `streamHandle` |
| 1.5 patch 3 | Fixed mono SFX volume bug; `lastPSFromBuffer` accessible |
| 1.5 patch 4 (1.5.4) | Added `SetupVolumeAndPan` and `SetHWMix`; replaces direct `CheckOutputMode` call |
| 2.0.0 | Major revision; patch note PDF included in distribution |
| 2.0 patch 2 | `SND_PARAMETER::ctrl` widened from `u8` to `u16`; added Virtual Sample API for ARAM streaming |
| 2.0 patch 3 | Updated tools to VC.NET 2003; fixed sequencer `sndFXCheck` bug; `synthFXStart` gained extra `key` argument |

**Game-to-version mapping (confirmed or strongly inferred):**
- Metroid Prime: 1.5 patch 3 (with `-proc 750`/GC 1.2.5n compiler)
- Mario Party 4: a version between 1.5.3 and 1.5.4 (has `SetHWMix`, lacks `lastPSFromBuffer` assignment in `streamHandle`)
- Metroid Prime 4 (MP4): uses MusyX, but compiler behavior differs from mainline (descending register order in REL files)

### How to Identify a Game's MusyX Version

1. Look for the build date string in the binary (every patch version contains one).
2. Check whether `SetHWMix` is present — it only exists in version ≥ 1.5.4.
3. Check whether `lastPSFromBuffer` is assigned in `streamHandle` — absent in MP4's version.
4. Try replacing the game's MusyX object files with known-version debug objects from the MusyX SDK; if it compiles and links cleanly, the version matches.
5. Version guards in the decomp source use the pattern:
   ```c
   #if MUSY_VERSION < MUSY_VERSION_CHECK(1, 5, 4)
       /* old code path */
   #else
       /* new code path */
   #endif
   ```

### Matching Strategy

- **Match release first, then check debug.** Debug builds of MusyX occasionally have register swap differences that do not appear in release. Getting release to match 100% is the primary goal; debug close-enough is acceptable.
- **Use debug builds as references** for understanding structure. The 2.0.0 debug build is the best reference for `salBuildCommandList`.
- **`salBuildCommandList` is the hardest function** in the entire library. It manages DSP voice processing and has ~50 local variables spanning the stack from `r1+0x8` to `r1+0xE4`. Many variables reuse the same name (multiple `size`, `bn`, `bo`, `localNeedsDelta`) at different stack offsets. The function is 0x3C04 - 0x10B8 = 0x294C bytes long.
- **Assert style affects matching.** The assert macro form `((cond) || (MUSY_PANIC(...), 0))` must be used in exactly the same form as the original code. Using a different form can cause an entire function to not match because MWCC's expression optimizer behaves differently.
- **Version guards for globals**: Whether version-specific globals are placed inside `#if` guards or stripped does not matter for release builds (they are dead-stripped anyway), but it is good practice for documentation.
- **DSP command list structure**: `salBuildCommandList` writes to a 16-bit DSP command buffer. The global state includes `dspCmdCurBase`, `dspCmdPtr`, `dspCmdMaxPtr`, `dspCmdLastLoad`, `dspCmdLastBase`, `dspCmdFirstSize`, `dspCmdLastSize`, `salFrame`, `salAuxFrame`, and a static `voices[64]` array.

### Hardest Remaining Functions (as of community activity)

At the time of Discord discussion, the three hardest functions in MusyX 2.0.0 were:
1. `salBuildCommandList` (hw_dspctrl) — massive function, complex stack layout
2. `_GetInputValue` (snd_midictrl) — register allocation issues
3. `streamHandle` (stream) — register swaps; otherwise structurally matched

All three were eventually matched for at least one version. Adding new version variants (e.g., 2.0.3) after the first version is matched is described as straightforward.

### Architecture Notes

- MusyX is a C library (no C++ classes), consistent across all versions.
- The library is divided into several translation units: `seq`, `stream`, `synth`, `hw_dspctrl`, `snd_midictrl`, and supporting modules.
- `sal` (Simple Audio Library) is a general helper layer within MusyX. MusyX avoids using most standard library functions; CLAMP, MAX, and similar macros come from within the library or platform headers, not from the SDK. SDK macros must not leak into MusyX's include chain.
- The GameCube Wii home menu audio library uses NW4R, not MusyX.
- The MusyX 2.0 SDK disc is available on archive.org: `https://archive.org/details/musyx-2003-01-09`

---

## Dolphin SDK / RVL SDK

The Dolphin SDK (GameCube era) and Revolution SDK / RVL_SDK (Wii era) provide the base hardware abstraction layer for all GameCube and Wii software.

### Version Identification

**Primary method:** The SDK embeds a build string in each sublibrary. These strings can be extracted by scanning the DOL binary for ASCII patterns:

- GC format: `<< Dolphin SDK - <MODULE>    release build: <DATE> (0x<COMPILER_VER>) >>`
- Earlier GC format: `Dolphin OS $Revision: <N> $.  Kernel built : <DATE>`
- Wii format: `<< RVL_SDK - <MODULE>     release build: <DATE> (0x<COMPILER_VER>) >>`
- Wii patch format: `RVL_SDKVERPATCH : 11Dec2009Patch00`

The compiler version field encodes the CodeWarrior version: `0x2301` = GC MW 2.3.0 Build 1; `0x4199_60831` = Wii MW 4.1 Build 60831; `0x4201_127` = Wii MW 4.2.0 Build 127.

**Important caveat:** SDK modules within the same game can have different build dates. GX, OS, DVD, and AX are frequently updated independently. Always check per-module dates rather than assuming one date covers the whole SDK.

### Known GC SDK Build Date Timeline

| Date | Notable Coverage |
|------|-----------------|
| Dec 17, 2000 | Beta HW2 SDK (very early, different data structures) |
| May 22, 2001 | DolphinSDK2001 (Super Monkey Ball, Melee era) |
| Sep 8, 2001 | Slightly later 2001 build |
| Dec 17, 2001 | Another 2001 revision |
| Sep 5, 2002 (0x2301) | Most common mid-lifecycle SDK; Biohazard Zero, SADX, TWW OS |
| Apr 17, 2003 | Heroes era (0x2301) |
| Apr 5, 2004 | Shadow the Hedgehog era (0x2301) |
| May 21, 2004 | "05Sep2002Patch2" reference still appears; DolphinSDK2004 |
| Nov 10, 2004 | Late GC; GX and OS updated |

Key game SDK versions:
- **Luigi's Mansion**: OS Revision 37
- **Super Monkey Ball / Melee**: OS Revision ~37, May 2001 SDK; these two games use nearly the same SDK version
- **Pikmin 1 / SMB**: Likely same SDK version; SMB's headers can be reused for Pikmin 1
- **Twilight Princess**: OS Rev 58 (Sep 5, 2002 build date for OS); `<< Dolphin SDK - OS.release build: Sep 5 2002 05:32:39 (0x2301) >>`
- **Pikmin 2**: Later than TP in some modules

### Known Wii SDK Build Date Timeline

- **Sep 2006** (0x4200_60422): Earliest Wii launch-era SDK seen in retail games
- **Nov 2006** (0x4199_60831): Launch window; Top Trumps Adventures
- **Aug 2007** (0x4199_60831): Mario Kart Wii core modules (AI, AX, DSP, DVD, EXI, SI, THP, VI)
- **Dec 2007** (0x4199_60831): MKW GX and NAND
- **Jan 2008** (0x4199_60831): MKW OS
- **Jan 2008** (0x4201_127): MKW RFL
- **Dec 11, 2009** (various): Last widely distributed GC+Wii SDK; Just Dance 2022 still uses this
- **Aug 23, 2010**: Korean Wii Party; Skyward Sword

Current community repos:
- [Dolphin SDK 2001](https://github.com/doldecomp/dolsdk2001)
- [Dolphin SDK 2004](https://github.com/doldecomp/dolsdk2004)
- [Revolution SDK 2009](https://github.com/doldecomp/sdk_2009-12-11)
- [Character Pipeline April 2001](https://github.com/doldecomp/dolcp-apr2001)

### NW4R (NintendoWare for Revolution)

NW4R was distributed to all Wii developers with full source code. It provides:
- `nw4r::ut` — utility list, allocator
- `nw4r::math` — VEC2, VEC3, MTX34, SPHERE, LINE3, QUAT
- `nw4r::snd` — AX-based audio (replacement for MusyX on Wii)
- `nw4r::g3d` — 3D model/animation rendering (has its own RTTI implementation)
- `nw4r::lyt` — layout/2D UI
- `nw4r::ef` — effects

Games past Super Mario Galaxy increasingly rely on NW4R rather than JSystem for 3D rendering. SMG appears to be a transitional title.

**NW4HBM** is a fork of NW4R bundled specifically inside `homebuttonLib.a`. It uses namespace `nw4r` internally but includes its own copy to avoid version conflicts with the host game's NW4R. Functions carry the string `"NW4HBM:..."` in their assert messages, distinguishing them from mainline NW4R.

NW4R also implements its own RTTI in `nw4r::ut` and `nw4r::g3d` independently. This is separate from and coexists with MWCC's built-in RTTI mechanism.

### OS Module Matching Notes

- **`OSGetTime`** is implemented using `mftbu`/`mftb`/`mftbu` with a loop to handle the carry case. The raw encoding is `7C6D42E6 7C8C42E6 7CAD42E6`. Standard Linux assemblers do not recognize `mftb` in gekko mode; use `devkitPPC`'s assembler or encode as `.4byte` literals.
- **OSThread.c** is the largest file in the OS module. It uses macro-expanded queue operations (`ENQUEUE_THREAD`, `DEQUEUE_THREAD`, `ENQUEUE_THREAD_PRIO`) that are written out inline — the compiler did not have them as real macros in all versions. The original devs mixed pointer-vs-NULL and pointer-vs-0 comparisons inconsistently, which affects code generation.
- **Assert style in OS**: Some asserts use `OSPanic` directly, others use `ASSERTMSGLINE`, and some use a custom `ASSERTREPORT` pattern (`OSReport` + `OSPanic("")`). MWCC 1.2.5 does not support `__VA_ARGS__` in the standard way — the `-gccext on` flag enables the GCC `, ##__VA_ARGS__` extension if needed.
- **OSThread data structures**: Early SDK versions (2001) lack per-thread specific fields present in later versions. The thread state machine uses constants: state `0` = detached/dead, `1` = ready, `2` = running, `8` = waiting for join.
- **Two developers touched OSThread.c** based on different assert styles (some use format-string asserts, others use combined OSReport+OSPanic). The inconsistency is in the original source.

### GX Module

- GX data structures are significantly different in early (2001) SDK builds compared to later builds. Retro Studios reportedly had access to GX source code during MP3 development, which explains why DKC Returns has an anomalous GX build date.
- **GXStubs.c** is a real translation unit containing `__GXSetRange` and related internal stubs.
- **GXDraw.c** contains the unknown draw functions that call GXBegin. Functions in it do not call `OSPanic`; later versions do.
- The GX `operator new` / placement new conflict: `nw4r::snd` and `nw4r::lyt` include an inline placement new in their headers (since they cannot see EGG). Game code that includes both EGG and NW4R headers encounters a conflicting declaration. The resolution is to ensure inclusion order or use separate compilation units.

### SDK Repository Strategy (Community Consensus)

The recommended approach for SDK code sharing:
1. Use **git branches or tags per SDK version** (e.g., a `melee` branch for the 2001 SDK, a `2004` branch for the mid-cycle SDK).
2. Use **build date integers** as version identifiers (e.g., `#define DOLPHIN_SDK 20010522`).
3. Keep **per-sublibrary version tracking** because GX, OS, AX, and DVD often have different build dates within the same game.
4. Most games used the SDK as shipped without mixing sublibrary versions, but exceptions exist.
5. `#ifdef` versioning at the top of each TU is the long-term goal but is impractical early in decomp — start with per-game branches, migrate to version guards later.

### Common SDK Matching Gotchas

- **VIGetTvFormat return type**: GC compilers treat `u32` and `uint` as equivalent in switch cases but the Wii compiler generates `cmplwi` for unsigned comparisons vs. `cmpwi` for signed, causing mismatches if the return type is incorrect.
- **`OSPhysicalToCached`** is a macro in later SDK versions but is an actual function in some early versions. Using the macro form where a function is expected will cause a mismatch.
- **SI vs. PAD**: `SetSamplingRate` was moved from the PAD module to the SI module at some point in the SDK lifecycle.
- **OSFont** contains mostly unused functions for most games. Only `OSGetFontEncode` tends to be linked.
- **PAPER MARIO TTYD modified some SDK-provided libs** rather than using them as shipped. This is uncommon but does happen.
- **TTYD** and some other games used `OSReport` + assert false patterns in the same function, meaning the original dev was inconsistent about whether to use the assert macro or call `OSPanic` directly.

---

*Document compiled from Discord archive analysis. All information derived from public discussion among decompilation contributors. No proprietary SDK materials included.*
