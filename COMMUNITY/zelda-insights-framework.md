# Zelda Decompilation Discord: #decomp-framework Channel

**Overview**: Analysis of the `#decomp-framework` channel (~2,100 messages, 2020). Documents the founding discussions of a shared N64 decomp infrastructure project — what became the common tooling foundation used by OoT, MM, Paper Mario, SM64, and others. Day-one debates shaped the entire N64 decomp ecosystem.

---

## Project Vision

- Goal: a common framework abstracting the shared problems across all N64 decomp projects
- Intended beneficiaries: every N64 game decomp team (avoiding duplicate tooling effort)
- Design principle: "each project lead can decide their own way of doing things"; framework should not mandate approach
- Main framers: ~5 contributors from existing N64 decomp projects (SM64, MM, Paper Mario, OoT)

---

## Founding Debates

### ASM in Repo vs. Generated ASM

The channel's first major debate; generated significant disagreement.

**Pro-committed-ASM** arguments:
- Not having to build to use a repo for documentation purposes
- Manual fixes required for disassembly can't always be automated
- Known issues: `capstone` pseudoinstruction bugs (`move` → `ori` vs `addu+ori`), `li` encoding differences
- Git history contains meaningful diffs (people can see what functions changed)

**Pro-generated-ASM** arguments:
- Committed ASM is copyrighted material being hosted
- Massive git history diffs when ASM updates
- Could be in `.gitignore` (not committed) and regenerated during repo setup

**Consensus reached**:
- Framework supports **three states** (project chooses):
  1. Transient (generated on setup, never committed)
  2. Static/manually-updated (committed, human-maintained)
  3. Static/disassembler-updated (committed, auto-updated via build process)
- Legal concern about hosting ASM: explicitly non-binding; "we're not lawyers"
- "To me there is no difference between compiled asm and extracted asm, since we literally advertise it's the same"

### Language Choice (Python vs. C)

- Scripting tools (ROM manipulation, build steps): Python preferred for rapid iteration, no compilation
- Performance-critical tools (disassemblers, linkers): C/C++ acceptable
- Python platform dependency real but manageable; "not actually worse than C in practice"
- Cross-platform C programs still have Windows `#ifdef` issues
- "Day 1 and decomp-framework has already devolved into language bikeshedding"
- Final stance: language up to each tool author; no mandate

---

## ROM Analysis Tooling

### ROM Header Structure
- Identified fields: image name, libultra version, RAM entry point, CIC version, language field
- Language detection approach debated: character bigram/trigram frequency model vs. neural network
- Bigram models: implementable in Python, output cosine similarity as confidence score
- Language detection must be per-file (different files compiled with different tools/languages)
- SM64 example: audio at `-O2`, Goddard system at `-g -mips1`, main code at `-g`

### Compiler Detection
- N64 games mix compilers: IDO (most C), libultra (pre-compiled), some GCC modules
- FLIRT signatures proposed for compiler identification; community members reported using them
- Long-term vision: central database of function signatures keyed by compiler + options
- "Find all `jr ra` and work backward" as naive function boundary detection start

### ROM Code Extraction
- Need to separate code segments from data before feeding to disassembler
- Dynamic analysis (emulator DMA log) proposed for initial setup:
  - Log format: `DIRECTION;CART_ADDR;DRAM_ADDR;LENGTH`
  - Examples: Paper Mario `W;0x10001000;0x25c00;0x100004`, MM `W;0x10001000;0x80000;0x100000`
  - PIF bootrom copies initial payload; DMA logs capture all subsequent code loads
- Halting problem concern: emulator-in-build-tools is problematic for automation
- Alternative: IDA/Ghidra headless for code segment detection
- Required formats: Yay0/Vpk0 compressors/decompressors in Python (pre-existing C versions available)

---

## Disassembler Design

### Requirements
- Must produce bit-correct output that reassembles to identical binary
- Must handle: jal targets, jalr, jump tables, symbolic hi/lo pairs, overlays
- Capstone library considered: provably correct, bindings for Python/C, but emits pseudoinstructions
  - `emit no pseudoinstructions` flag not documented
  - Custom assembly output format needed anyway
- Community disassembler (MM): written from scratch; handles hi/lo for symbols
- Key issue: modern `as` encodes `move` differently from IDO `as` (affects `ori` vs `addu`)

### Symbol Recovery
- Functions: detect `jr $ra` patterns; validate against DMA maps
- Labels: hi/lo pairs for each global reference; must be algorithm-detectable
- Manual fixes had been required in existing projects for: Majora's Mask, Paper Mario, Pokemon Snap
- "Not easy to write an algorithm that can figure out all symbols and use hi/lo for those for [MM]"

---

## Build System Architecture

### Core Design
- `romspec` format: N64 SDK ROM map definition format; essentially a custom LD script
- Loader module: "little N64 ROM manipulation library" for reading/writing ROM segments
- Build steps: extract → disassemble → (compile C) → assemble → link → check
- Framework should expose the extraction/splitting step as a configurable config file

### IDA/Ghidra Integration (Optional)
- Proposed: IDA or headless Ghidra as optional better disassembler
- Loader integration: IDA/Ghidra script defines ROM segment layout; same config used for splitting
- GoldenEye team ran shared Ghidra server (git-like check-in/checkout system)
- Concern: another large dependency; most projects opted to use project-specific disassemblers

### Overlay Support
- N64 overlays: code loaded at runtime, potentially relocated; critical for actor-heavy games
- `n64split` initially had poor overlay support; major blocker for Paper Mario
- Fix: manually adding overlay sections to linker script; automatic support added later

---

## Compiler Characteristics Documentation

Early in channel history, a collaborator started a Google Doc:
> "Compiler characteristics doc (pls contribute): [shared Google Docs link]"

This doc captured per-compiler knowledge:
- Which pseudoinstructions each compiler emits
- Known differences between compiler versions
- Flag effects on code generation
- This was the informal predecessor to what became more structured community documentation

---

## Key Lessons for GC/Wii Projects

Although the #decomp-framework channel focused on N64, several insights transfer directly:

1. **Three-state ASM model** is the right framework; GC/Wii projects (dtk-based) chose "no committed ASM" approach
2. **Per-file compiler detection** is essential; games use multiple compilers/flags per file
3. **Overlay support must be designed in** from the start; retrofitting is painful
4. **DMA logs** from emulator = reliable ground truth for ROM splitting; equivalent to `dtk` analysis
5. **Language bike-shedding** is universal; agree on "use what works per tool" early

---

## Confidence Levels

✅ **Confirmed** (from founding contributors):
- Three-state ASM model was explicit consensus
- Capstone pseudoinstruction issues real; manually verified across projects
- `n64split` overlay support was a blocker for Paper Mario

⚠️ **Inferred** (from patterns):
- Framework discussions directly influenced OoT/MM/PM decomp toolchain choices
- Google Doc compiler characteristics effort was informal; likely superseded by project-specific docs

---

*Source: Discord exports from #decomp-framework (Zelda Decompilation server), ~2,100 messages, 2020. All usernames anonymized.*
