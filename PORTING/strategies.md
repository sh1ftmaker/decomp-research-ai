# Porting Strategies: From Decompilation to Native PC

*How to transform a matching GameCube/Wii decompilation into a cross-platform PC port, using the Animal Crossing PC port as a blueprint.*

---

## 🎯 What Is "Porting" vs "Decompilation"?

**Decompilation**: Recreate **identical** game binary from source code (byte-perfect match).

**Porting**: Modify that source code to run on **different platforms** (Windows/Linux/macOS) while preserving gameplay and content.

These are **separate phases**:
1. First, achieve 100% matching on original platform (GameCube/Wii)
2. Then, apply platform abstraction layers to enable PC

---

## 🔍 The Porting Architecture

### Layer Cake Model

```
┌─────────────────────────────────────────────┐
│     Game Logic Layer                         │  ← Pure C++, no platform calls
├─────────────────────────────────────────────┤
│     Platform Abstraction Layer (PAL)         │  ← Abstraction interfaces
├─────────────────────────────────────────────┤
│     Backend Implementations                  │  ← Platform-specific (GCN, Wii, PC)
├─────────────────────────────────────────────┤
│     OS / Hardware                            │  ← Actual system calls
└─────────────────────────────────────────────┘
```

**Key Principle**: Game logic should never directly call OS APIs. All platform-specific code goes through PAL interfaces.

---

## 🏗️ Step-by-Step Porting Process

### Phase 1: Foundation (Before Porting Starts)

**Prerequisites**:
- ✅ Decompilation 80-90% complete (core systems done)
- ✅ Build system works on Windows with CodeWarrior
- ✅ All major SDK functions stubbed/implemented (JSystem, JAudio, etc.)
- ✅ Game boots and runs (in Dolphin or on real hardware)

**Why wait?**:
- Changing platform early breaks matching
- You need accurate source to know what needs abstraction
- Many SDK calls are deeply embedded; you must see them all first

---

### Phase 2: Audit and Document Platform Dependencies

**Task**: Search codebase for any non-standard C library calls or hardware-specific code.

```bash
# Find direct system calls
grep -r "DVDOpen" src/
grep -r "VI" src/                    # Video Interface
grep -r "PI" src/                    # Parallel Interface
grep -r "EXI" src/                   # External Interface
grep -r "OS\(.*\)" src/              # Operating system calls
grep -r "__ppc" src/                 # PowerPC intrinsics
```

**Create a dependency matrix**:

| Module | Platform API | Count | Abstraction Needed? |
|--------|--------------|-------|---------------------|
| Audio  | `AX`, `DSP` | 150   | Yes (JAudio → SDL) |
| Video  | `GX`, `VI`  | 300   | Yes (GX→OpenGL/Vulkan) |
| Input  | `PAD`       | 50    | Yes (PAD→SDL/XInput) |
| File   | `DVDFile`   | 200   | Yes (DVD→std::fs) |
| Memory | `JKRHeap`   | 100   | Partial (malloc wrapper) |
| Thread | `OSThread`  | 80    | Yes (OSThread→std::thread) |
| Time   | `OSTime`    | 30    | Yes (OSTime→chrono) |

---

### Phase 3: Define Abstraction Interfaces

**Pattern**: Create pure virtual classes (interfaces) that game code uses.

**Example**: Input

```cpp
// Before (platform-specific):
extern "C" void PADRead(PADStatus* status);

// After (abstract):
class IInput {
public:
    virtual ~IInput() = default;
    virtual void poll() = 0;
    virtual ButtonState getButton(Button btn) = 0;
    virtual AnalogState getAnalog(Analog axis) = 0;
    virtual Vector2 getCursor() = 0;
};

// Game code uses IInput* (injected via dependency injection)
```

**Backend**:
```cpp
class GCNInput : public IInput {
    PADStatus pads[4];
public:
    void poll() override {
        PADRead(pads);
    }
    // ... map PADStatus to ButtonState
};

class PCInput : public IInput {
    SDL_GameController* controllers[4];
public:
    void poll() override {
        SDL_PollEvent(...);
    }
    // ... map SDL to ButtonState
};
```

**Factory**:
```cpp
IInput* createInput(Platform platform) {
    switch (platform) {
        case GCN: return new GCNInput();
        case PC:  return new PCInput();
    }
}
```

---

### Phase 4: Implement PC Backends

#### Audio: AX → OpenAL/ miniaudio

**GameCube AX** (Audio eXpansion) is a complex audio library:
- `.aw` files (ADPCM)
- `.bseq` (music sequences)
- `.bnk` (sound banks)
- Real-time effects, reverb, streaming

**Strategy**:
1. **Implement AX-compatible API** that loads original `.aw/.bseq/.bnk` files
2. **Translate AX calls** to miniaudio or OpenAL
3. **Preserve exact behavior**: Same mixing, same envelope, same sample rate (32kHz or 48kHz)

**Reference**: `nptt-utils` (Animal Crossing PC port team) wrote `ax2wav` converter initially, then implemented live AX emulation.

**Key functions**:
- `AXInit`, `AXQuit`
- `AXVoice` allocation
- `AXSetVoiceState`, `AXSetVoiceLoopAddr`
- `AXSetVoiceAdpcm` (decoder)
- `AXSetVoiceMatrix` (crossbar matrix mixing)

**Difficulty**: High. Audio timing must match frame-accurate.

---

#### Video: GX → OpenGL/Vulkan

**GameCube GX** (Graphics eXpress) is a fixed-function + programmable pipeline API (pre-Shader Model 3).

**Challenges**:
- Texture formats: `CI8`, `IA8`, `RGB565`, `RGBA32` (often need conversion)
- Display lists: GX uses display lists; OpenGL uses immediate/arrays
- Matrix stacks: GX has separate `P`, `MV`, `M` stacks; OpenGL has unified
- Texgen, culling, depth modes differ

**Two approaches**:

**A. Reimplement GX on top of OpenGL** (Animal Crossing used this):
```cpp
// Your GX wrapper:
void GXBegin(GXPrimitive type) {
    glBegin(convertPrimitive(type));
}

void GXSetVtxDesc(GXAttr attr, GXAttrType type, void* ptr) {
    // bind VBO, set vertex attrib pointers
    glVertexAttribPointer(...);
}
```
This lets you keep most game code unchanged (just recompile against your GX wrapper headers).

**B. Extract shaders and create modern renderer** (more work but cleaner):
- Analyze GX display lists to identify rendering passes
- Convert to Vulkan/OpenGL 4.0 shaders
- Rewrite rendering code to use modern APIs
- Benefit: Better performance, easier to maintain

**Trade-off**: Approach A is quicker to get running; Approach B is better long-term.

---

#### File I/O: DVD → std::filesystem

**GameCube DVD** API includes:
- `DVDOpen`, `DVDRead`, `DVDClose`
- Async reading (DVD commands)
- File system: `GameTDB` format, directory structure

**Strategy**:
1. **Replace `DVDOpen`** with `std::ifstream` or `SDL_RWops`
2. **Handle paths**: Game expects `./disc/...` but PC uses `./romfs/` or `./assets/`
3. **Async reads**: The DVD API had command queues. Replace with thread pool async reads.

```cpp
// GCN version:
DVDFile* f = DVDOpen("Arc/AAA.arc");
int bytes = DVDRead(f, buffer, size, offset);

// PC version:
std::ifstream f("romfs/Arc/AAA.arc", std::ios::binary);
f.seekg(offset);
f.read(buffer, size);
```

**Microcode**: Some games use custom file formats (`.arc`, `.rarc`, `.yaz0` compressed). You need to implement those decompression algorithms anyway (decomp-toolkit has them).

---

#### Threading: OSThread → std::thread

**GameCube OS** has lightweight threads (preemptive, priority-based).

**Implementation**:
```cpp
class GCNThread {
    OSThread thread;
public:
    void start(void (*func)(void*), void* arg) {
        OSCreateThread(&thread, func, arg, ...);
    }
    void join() { OSJoinThread(&thread); }
};

class PCThread {
    std::thread th;
public:
    void start(std::function<void()> func) {
        th = std::thread(func);
    }
    void join() { th.join(); }
};
```

**Challenge**: Some games use thread-local storage or specific stack sizes. Match those.

---

#### Time: OSTime → std::chrono

**GameCube `OSTime`** is a tick counter (usually 42MHz or 27MHz depending on clock).

**Replace**:
```cpp
// Old:
s64 ticks = OSGetTime();
float seconds = ticks / 42.0e6f;

// New (PC):
auto now = std::chrono::high_resolution_clock::now();
float seconds = std::chrono::duration<float>(now.time_since_epoch()).count();
```

But you must preserve **exact timing** for some games (speedruns, RNG). Consider scaling factor.

---

### Phase 5: Platform Detection and Build System

**Build System**:

Modify `configure.py` to support platform selection:

```python
# configure.py
parser.add_argument('--platform', choices=['gcn', 'wii', 'pc'], default='gcn')
args = parser.parse_args()

if args.platform == 'pc':
    CFLAGS += ['-DPLATFORM_PC', '-D__PC__']
    # Use GCC/Clang instead of CodeWarrior
    CC = 'gcc'  # or clang
```

**Conditional Compilation**:

In source code:
```cpp
#ifdef PLATFORM_PC
    #include "pc/PCInput.hpp"
    #define GX_BEGIN(...) /* nothing, or debug output */
#else
    #include "dolphin/GX.h"
#endif
```

**Alternative**: Use dependency injection (preferred) rather than `#ifdef`s everywhere. But some code is inherently platform-specific (startup code, hardware init).

---

### Phase 6: Testing and Validation

**Golden Reference**: Original GameCube/Wii binary (matching) is your truth.

**Tests**:
1. **Frame-accurate comparison**: Render same frame, compare screenshots pixel-perfect
   - Use `pngdiff` or `ImageMagick compare`
   - Allows small differences due to floating point (tolerance: 1/255)
2. **Memory comparison**: Compare game state structures after N frames
3. **Input replay**: Feed identical input sequences, verify identical outputs
4. **Performance**: PC version should run at 60fps (or target) without slowdown

**Issue**: Some differences are acceptable:
- Different RNG seed if time-based (use platform time consistently)
- Floating point differences (x87 vs SSE2 vs ARM NEON) - may diverge after many operations
- Uninitialized memory (PC fills with 0xCD, GameCube with other patterns) - use `memzero` or explicit init

---

## 🎯 Case Study: Animal Crossing PC Port

**Project**: `nptt` (New Horizons PC Port - actually it's a port of the original GameCube Animal Crossing, not NH)

**Steps they took**:

1. **Decompile**: First 50% of game (core systems) using dtk
2. **Identify AX audio**: Wrote `ax2wav` tool to convert `.aw` to `.wav` for prototyping
3. **Implement PAL**: Created `IPAL` interface for audio, graphics, file I/O
4. **GX wrapper**: Implemented subset of GX needed (not full) using OpenGL
5. **Replace DVD**: Used `std::filesystem` with `romfs/` directory structure
6. **SDL2**: Used for window, input, OpenGL context
7. **Threading**: Used `std::thread` for background loading
8. **Memory**: Kept JKRHeap (custom allocator) but backed with malloc

**Result**: Game runs at 60fps on PC, 4K resolution, uses original assets.

**Codebase changes**:
- 60% of code unchanged (pure game logic)
- 30% minor tweaks (paths, type sizes)
- 10% platform layer (new files: `pc/` directory)

---

## 🏗️ Porting Code Organization

```
nptt/
├── src/                    # Original decomp code (unchanged as much as possible)
│   ├── pe/
│   ├── dolphin/
│   └── JSystem/
├── pal/                   # Platform Abstraction Layer
│   ├── IPAL.hpp           # Pure virtual interfaces
│   ├── pal_impl.cpp       # Factory, platform detection
│   └── backends/
│       ├── gcn/           # GameCube backend (calls real GX, AX, etc.)
│       ├── wii/           # Wii backend
│       └── pc/            # PC backend (SDL, OpenGL)
├── platform/              # Platform-specific entries
│   ├── pc_main.cpp        # main() for PC
│   ├── pc_window.cpp      # SDL window management
│   ├── pc_renderer.cpp    # OpenGL/Vulkan renderer
│   └── pc_audio.cpp       # miniaudio/OpenAL audio
├── third_party/
│   ├──SDL2/
│   ├── miniaudio/
│   └── glm/               # OpenGL math
├── assets/                # Extracted game files (ROMFS)
└── configure.py           # Modified to detect --platform=pc
```

**Injection**:
```cpp
// pal_impl.cpp
IInput* gInput = createInput(currentPlatform);
IAudio* gAudio = createAudio(currentPlatform);
// Global service locator pattern, or use dependency injection through constructors
```

---

## 🎯 Common Abstraction Points Checklist

Mark ✓ when implemented:

- [ ] **Video** (`GX` → `IGraphics`)
  - [ ] Vertex submission (VAT, arrays)
  - [ ] Texture loading and formats
  - [ ] Display lists (convert or execute)
  - [ ] Matrix stacks
  - [ ] Fog, depth, alpha, blend modes
  - [ ] Texture environment (tev) stages
  - [ ] Framebuffer objects (EFB/XFB copy)

- [ ] **Audio** (`AX` → `IAudio`)
  - [ ] Voice allocation
  - [ ] ADPCM decoding (to PCM)
  - [ ] Mixing and effects
  - [ ] Streaming (BMS/BGMW/ADX)
  - [ ] Sample rate conversion (32kHz→44.1kHz if needed)
  - [ ] 3D audio positioning

- [ ] **Input** (`PAD` → `IInput`)
  - [ ] GameCube controller (SDL mapping)
  - [ ] Wii remote (if Wii game)
  - [ ] Keyboard + mouse fallback
  - [ ] Rumble (force feedback)

- [ ] **File I/O** (`DVD` → `IFileSystem`)
  - [ ] Directory enumeration
  - [ ] Async reads (thread pool)
  - [ ] Archive formats (.arc, .rarc decompression)
  - [ ] Compression formats (YAZ0, LZ77)
  - [ ] Path translation (GCN paths → PC paths)

- [ ] **Threading** (`OSThread` → `IThread`)
  - [ ] Thread creation and priorities
  - [ ] Mutexes/semaphores (OSSemaphore, OSMutex)
  - [ ] Message queues (OSMessageQueue)
  - [ ] Thread-local storage

- [ ] **Memory** (`JKRHeap`, `JKRExpHeap`) → keep as-is but use system malloc
- [ ] **Time** (`OSTime`) → `ITime`
- [ ] **Math** (`MTX` / `PSM` matrices) → Usually fine (just compile), but may need endian swap
- [ ] **Network** (EXI, Sockets) → `INetwork` (for Animal Crossing: replace with Steamworks?)
- [ ] **Display** (`VI`) → `IDisplay` (window management, vsync, resolution)

---

## 🎯 When to Stop Matching and Start Porting

**You don't need 100% matching to start porting**. Many projects start at 70-80%:

| Progress | Can start porting? | Notes |
|----------|-------------------|-------|
| 50-60%   | Early Phase       | Core systems (memory, thread, file) must be matched first |
| 60-75%   | Yes               | Enough to boot and get to title screen |
| 75-90%   | Full porting      | Stable enough for gameplay |
| 90%+     | Complete          | Port is same as original |

**Strategy**: Port incrementally alongside decompilation:
- Port the parts you've decompiled
- Keep matching on GCN for those parts
- As you decompile more, update PC backend

---

## 🐛 Common Porting Pitfalls

### Endianness

GameCube is **big-endian**. PC is **little-endian**.

**Problem**: Direct memory dumps of binary files (textures, models) appear byte-swapped.

**Solution**:
- Use `doldecomp` SDK's `endian.h` functions: `bsp2host`, `host2bsp`
- Implement these as no-ops on GCN, but swap bytes on PC
- Or convert assets offline using `tools/endian_convert.py`

```cpp
uint16_t color = READ_U16(ptr);  // swaps if PLATFORM_PC
WRITE_U32(dst, value);
```

**Never cast a big-endian binary file directly to a struct on little-endian** - that's undefined behavior. Always read field-by-field with swap.

---

### Struct Packing and Alignment

CodeWarrior packing differs from GCC/Clang:
```c
// GCN: 4-byte alignment (default)
struct Foo {
    uint8_t a;     // offset 0
    uint32_t b;    // offset 4 (not 1!)
};

// PC GCC: may pack tighter with #pragma pack(1) but performance suffers
// Solution: Use static_assert(sizeof(Foo)==expected_size) everywhere
```

Check `sizeof` in both platforms with test programs.

**Compiler-specific pragmas**:
```cpp
#ifdef _MSC_VER
  #pragma pack(push, 4)
#elif defined(__GNUC__)
  #define PACKED __attribute__((packed, aligned(4)))
#endif
```

---

### Floating Point Precision

GameCube uses **32-bit single-precision** FPU (no 80-bit x87 intermediates).

PC with x87 may produce slightly different results. Use:
```cpp
#ifdef __i386__
  #include <xmmintrin.h>  // SSE
  // Or compile with -mfpmath=sse -msse2
#endif
```

Or use `float` consistently and avoid `double` (which may use 80-bit on x87).

---

### Uninitialized Memory

GameCube: Stack/allocated memory may have **garbage** (previous task memory).

PC (debug builds): Fill with `0xCC` or `0xCD`.

**Bug symptoms**: Game relies on zero-initialized data that wasn't actually zeroed.

**Fix**: Use `memset` or default member initialization in structs. Or match the original's uninitialized reads (which are undefined behavior anyway). Usually safe to zero everything on PC.

---

### Hardcoded Paths

GameCube uses paths like:
```c
const char* ARC_PATH = "/Arc/";
```

PC wants `./assets/Arc/` or `romfs/Arc/`.

**Solution**: Centralize path constants:
```cpp
#ifdef PLATFORM_PC
  #define ARC_PATH "romfs/Arc/"
#else
  #define ARC_PATH "/Arc/"
#endif
```

Or better: use a configuration file or environment variable.

---

## 📊 Porting Effort Estimates

| Game | Decomp % | Estimated Port Effort | Notes |
|------|----------|----------------------|-------|
| Animal Crossing | ~70% | 1-2 years (3-4 devs) | First port; blazing trail |
| Mario Sunshine | ~30% | 2-3 years | C++ heavy, JSystem complex |
| Zelda TWW | ~15% | 3-5 years | Huge, many systems |
| Melee | ~20% | 2-3 years | Network code, physics |
| Luigi's Mansion | ~10% | 1 year | Smaller scale |

**Team needed**: 2-4 full-time developers for a 1-2 year port.

**Parallel track**: Decompilation continues while porting begins on stable subsystems.

---

## 🎯 What About 100% Matching After Port?

**No!** The port will **never match** the GameCube binary. That's not the goal.

**Goal**: Port is a **separate product** that runs the same game logic but compiled for x86_64, possibly with minor fixes/improvements.

**You can keep matching on GCN** while PC port diverges. That's fine! The decompilation repository maintains matching for original hardware; the port is a fork or separate repo that references that source.

---

## 📚 Resources

- [nptt repository](https://github.com/nptt) - Animal Crossing PC port (private? but public references exist)
- [dolphin emulator source](https://github.com/dolphin-emu/dolphin) - Reference implementations of GX, AX, PAD, etc.
- [ogws (Open-GameCube-Wii-SDK)](https://github.com/ogws/ogws) - Open-source SDK reimplementation (incomplete)
- [libogc](https://github.com/devkitPro/libogc) - Old open-source GCN libraries (C only)
- [retroarch-shaders](https://github.com/libretro/glsl-shaders) - For GX→GLSL translation examples

---

## ✅ Porting Readiness Checklist

Before starting PC port:

- [ ] Decompilation 70%+ complete on core systems (memory, file, audio, video, input)
- [ ] Build system works cleanly on Windows with CodeWarrior or wibo
- [ ] All SDK header locations identified (doldecomp/sdk_* repos cloned)
- [ ] Game boots to title screen on Dolphin (matching)
- [ ] PAL interfaces defined (IPAL, IGraphics, IAudio, IInput, IFileSystem)
- [ ] PC backend skeleton created (empty implementations)
- [ ] Build fragmentation: configure.py supports --platform=pc
- [ ] Team assembled with C++, graphics, audio experience
- [ ] Asset pipeline: How to get game files into PC build

**Then**: Implement one backend at a time, starting with file I/O (lowest dependency).

---

*Next: [Community Resources](community.md) - Where to find help and share progress*

*Porting is the reward for matching - you get to see your decompiled game running natively on modern systems!* 🎉