# Zelda Decompilation Discord: #tools-other Channel

**Overview**: Analysis of the `#tools-other` channel (~6,400 messages, 2020+). Covers tools not warranting their own channel: `diff.py`/asm-differ, Ghidra, IDA Pro, `n64split`, `capstone`, the N64 ROM format, compression formats (Yaz0/Yay0), and cross-project community tooling.

---

## diff.py / asm-differ

### Overview
- Written by the primary IDO decomp contributor; upstream at `simonlindholm/asm-differ/`
- Used for: assembly diffing, matching verification, permuter scoring
- Each N64 decomp project pins its own copy; changes must be manually synced

### Key Flags
| Flag | Effect |
|------|--------|
| `-w` | Watch mode; live re-diff on file change |
| `-mwo` | Multi-window output; side-by-side diff |
| `--base-asm` | Compare against text asm instead of `.o` file |
| `--write-asm` | Output objdump-format text asm (for copy-paste to decomp.me) |
| `--stack-diffs` | Include stack frame in diff score |
| `--no-andor` | Disable `&&`/`||` detection (when CFG is unusual) |
| `--levenshtein` | Use levenshtein edit distance for scoring (more accurate; slower) |

### Known Bugs & Fixes
- **`jal` normalization**: `jal` imm should be prefixed with `0x` when not already; fix: `if before.strip() == "jal" and not imm.startswith("0x"): imm = "0x" + imm`
- **Whitespace in line comparison**: off-by-one normalization; fix: `rstrip()` on both sides before comparison
- **Regalloc diff color**: when both sides differ only by register, diff.py should mark as regalloc-colored (different color than structural diff); fixed via `normalize_imms` logic
- **Scroll position**: `-w` mode resets scroll to top on every change; requested fix (keep position) not yet implemented
- **Levenshtein default**: levenshtein algorithm requires a C library; added as optional default, falls back to built-in if library absent

### Three-Way Diffs
- Experimental support pushed to upstream for comparing: original asm, new asm, and a third reference (e.g., demo version vs retail)
- Use case: verify that a change didn't break a previously matching version
- Design: markers at start/end of third column to avoid scrolling through identical sections

### Delay Slot Display
- Delay slot lines shown in gray by default
- Requested: showing difference between two diffs (not just one diff)

---

## Ghidra

### N64-Specific Setup
- **Zelda64Loader**: plugin for loading N64 ROM segments with correct memory map
  - Latest release: `Random06457/Zelda64Loader/releases/tag/v1.7` (as of archive)
  - Supports unaligned segments (needed for some games)
- **Japanese string rendering**: Ghidra decompiler only supports Unicode; Japanese Shift-JIS strings cause display errors in decompiler view (not disassembly view)
- **Large function limit**: "Decompiler results exceeded payload limit of 50 MBytes" error on very large functions; custom Ghidra build with increased limit shared by community

### Shared Ghidra Server
- GoldenEye team ran a shared Ghidra server: git-like check-in/checkout with merge
- Read-only Ghidra server for TWW with pre-loaded types: `ghidra.decomp.dev`
- Loading `framework.map` from Kiosk Demo reveals inline symbols
- GameCube PowerPC plugin required for GC/Wii analysis (separate from MIPS plugins)

### Limitations for Matching Decomp
- "Ghidra is not designed for matching decompilation, so you really can't compare them exactly"
- No struct inheritance model; workaround: manually copy struct hierarchy fields
- IDA/Ghidra both produce output too high-level to be used directly; m2c closer to compiler behavior

### Useful Ghidra Scripts
- Script for dumping class member offsets directly to clipboard (integration with repo editing)
- `ichaindis.py`: N64 init chain disassembler — takes ROM + address, outputs InitChainEntry array
- Custom PPC plugin: `encounter/ghidra-ci` provides maintained builds for GC/Wii

---

## IDA Pro

### Usage Context
- Used alongside Ghidra; some contributors prefer IDA for initial analysis
- MIPS decompiler available as of IDA 7.5 (Hex-Rays add-on)
- Python API for batch extraction: iterate segments → functions → chunks → heads
- Output used as input to m2c (after cleanup); see m2c channel for known IDA-specific issues

### Known Output Issues for m2c
- Malformed `lwl`/`lwr` pairs (same instruction written differently)
- Pseudoinstruction expansion differences (`addu` vs. `ori` for `move`)
- `la` (load address) expansion differs from what m2c expects
- Macro instruction display (`sw $t6, dword_XXXX` instead of offset form)

---

## n64split

### Purpose
- N64 ROM splitter: extracts code/data segments from ROM, writes linker config
- Language/platform: C (primary) + Python scripts
- Historically SM64-biased; took work to support other games

### Overlay Support
- Major blocker for Paper Mario: overlays not supported initially
- Contributors manually added overlay sections to linker scripts as workaround
- Overlay support added to main branch by one contributor; required verification for each game
- Overlapping sections in config cause issues during re-split

### capstone Integration Issues
- n64split used libcapstone for disassembly; capstone emits pseudoinstructions differently from IDO `as`
- `move` → `ori $t, $zero, $t` in modern `as` vs. `addu $t, $t, $zero` in IDO `as`
- Some `li` instructions encoded wrong
- Community: "just submit a PR to capstone to fix it" — complicated by needing to maintain backward compatibility
- Result: several projects wrote custom MIPS disassemblers to avoid capstone issues

---

## N64 ROM Format

### Cartridge Header
- ROM header: standard 64-byte format documented at `en64.shoutwiki.com/wiki/ROM#Cartridge_ROM_Header`
- Key fields: image name, libultra version (letter code: 'I', 'L', etc.), RAM entry point, CRC, CIC version
- CIC version affects bootloader behavior (different memory initialization)
- "Release address" field (0x0F byte): purpose unclear; collecting from multiple games to find pattern

### CIC Versions
- CIC x105: sets specific register values before entry (`r4300_gpregs[11]`, `[29]`, `[31]`)
- CIC affects where `1080°` EU version falls in the detection table

### Code Loading (PIF + DMA)
- PIF bootrom copies 1MB from cart to RAM at startup: `W;0x10001000;0x25c00;0x100004`
- Game then uses its own DMA system for loading overlays/assets
- `BGCOPY`, `FastCopy`, `SLOWCOPY` string patterns useful for finding DMA functions
- Project 64 emulator: JavaScript scripting API available for DMA event listeners

---

## Compression: Yaz0 / Yay0

### Formats
- **Yaz0**: Nintendo LZSS-based compression used in N64 and later games
- **Yay0**: alternate Nintendo compression; fewer games use it
- **Vpk0**: another variant; used by specific N64 titles

### Matching Compressor Problem
- Nintendo used a specific compression implementation; matching compressor needed to reconstruct exact byte-for-byte ROMs
- Matching Yaz0 compressor confirmed to exist (written by `Zoinkity` in Python)
- Nintendo changed their Yaz0 compressor at some point; older and newer compressed data differ in algorithm
- C# reference: `Daniel-McCarthy/Mr-Peeps-Compressor` for Yay0
- Community advice: "don't brute-force; tune parameters, compare block-by-block, break on first match"

---

## Compiler Explorer Integration

### Community Requests (Tracked)
1. `cat`-like feature for diffing (needs comment-stripping example script first)
2. Fix `mips64-elf-gcc` building
3. Enable "compile to binary" for IDO (allows assembly output from IDO compiler)
4. `clang-format` integration as a tool option

### IDO on Compiler Explorer
- `permuter@home` Docker image (`simonlindholm:ido`) provides the IDO binaries
- Sandboxing via nsjail (same as their other compilers)
- Main question: call chain `cpp → cc1 → as` vs. single `gcc`; each step needs separate sandbox entry

---

## Function Signature Database (Proposed)

- Long-term vision: central database of function signatures keyed by compiler + compiler flags
- Use case: identify which functions in a new game are libultra or other pre-compiled library code
- Immediate use: FLIRT signatures for identifying compiler version
- Building block: per-project `assist.py` that finds similar functions by code pattern similarity
- No public database existed as of archive; each project maintained private FLIRT `.sig` files

---

## VS Code Extension Discussion

- Community discussions about a VS Code extension to streamline decomp workflow
- Concerns: limiting tools to one IDE reduces accessibility
- Counter: most active contributors already use VS Code
- Current approach: command-line scripts that work in any terminal; no IDE integration
- "Making better scripts is a better time investment than making an IDE extension"

---

## Confidence Levels

✅ **Confirmed** (direct announcements and linked commits):
- `Zelda64Loader v1.7` release
- `simonlindholm/asm-differ` upstream location
- capstone pseudoinstruction encoding differences are real and documented
- Yaz0 matching compressor exists (Python, by Zoinkity)

⚠️ **Inferred** (patterns and community discussion):
- ~40% of projects used custom disassemblers instead of capstone due to pseudoinstruction issues
- Compiler Explorer IDO integration remained pending throughout archive period

---

*Source: Discord exports from #tools-other (Zelda Decompilation server), ~6,400 messages, 2020+. All usernames anonymized.*
