# Zelda Decompilation Discord: #ido-decomp Channel

**Overview**: Analysis of the `#ido-decomp` channel (~6,600 messages, 2020+). Documents the effort to reverse-engineer the IDO (IRIX Developer's Option) compiler — the MIPS compiler used for all N64 games. Understanding IDO internals enables more accurate decompilation, faster matching, and eventually native (non-qemu) use of IDO on modern platforms.

---

## Background: What IDO Is

- IDO = IRIX Developer's Option; SGI's compiler suite for IRIX (Silicon Graphics workstations)
- N64 SDK used IDO 5.3 and 7.1 for C compilation
- Binary executables: `cc` (driver), `cfe` (C frontend), `uopt` (optimizer), `ugen` (code generator), `as1` (assembler), and others
- Written in MIPS assembly and C; big-endian 32-bit MIPS ELF binaries
- Currently runs only via `qemu-irix` (Linux) — no native Linux/macOS binary

---

## Compiler Pipeline (IDO Internals)

### Process Chain
```
Source.c → [cpp] → [cfe] → [uopt] → [ugen] → [as1] → Object.o
```

- `cc` = driver/wrapper; detects language, calls appropriate subtools
- `cfe` = C frontend; produces ucode intermediate representation
- `uopt` = optimizer; works on ucode; uses graph-coloring register allocation
- `ugen` = code generator; ucode → MIPS assembly
- `as1` = assembler; MIPS assembly → relocatable ELF
- `ddopt` runs after frontend but before uopt/umerge (documented in Indy dump man pages)

### Intermediate Representation: Ucode
- Custom bytecode format used between pipeline stages
- Data structures documented in `/usr/include/cmplrs/` header files from IRIX Indy dump
- `Uopcode` typedef: `typedef unsigned char Uopcode;` — conflicts with `enum Uopcode` causing confusing analysis output
- `Statement` structure: `{ opc (Uopcode), unk1 (bool), unk2 (bool), unk3 (bool), expr (Expression*), next (Statement*) ... }`
- Ucode read/write utilities use big-endian byte order; major obstacle for porting to x86

### Register Allocation
- `uopt` uses graph-coloring allocation (Chaitin-style)
- Symbol names visible in `uopt` binary suggest algorithm names (e.g., interference graph operations)
- `ugen` and `as1` both have instruction scheduling/reordering passes (affects delay slots, pipeline efficiency)
- The non-deterministic register ordering that plagues matching decompilation originates in `uopt`'s graph-coloring choices

---

## IRIX / IDO Extraction

### Getting the Binaries
- Source: IRIX CD-ROM ISO images (e.g., `IRISDevelopmentOption7.1.1forIRIX6.4_02-97_812-0625-002.iso`)
- CD format: EFS (Extent File System) — not mountable directly on Linux
- Extraction tool: `efs2tar` (Go, install via `go get github.com/sophaskins/efs2tar`)
- After extraction: IDB files (IRIX package database) list the actual file paths
- Script by community contributor (`camthesaxman/dcc60d98f152b4fed32dfc18d7246551`) automates extraction

### Obtaining IDO 7.1 vs. 5.3
- IDO 7.1.1 used by later N64 titles; IDO 5.3 used by earlier ones
- 5.3 `uopt` has slightly different common variable ordering vs. 7.1
- `libp.a` (Pascal library) rare; not always present in available IDO collections
- New 64-bit compilers (IRIX 6.0+) separate from the 32-bit ones used for N64

---

## Running IDO (qemu-irix)

### qemu-irix Setup
- Fork of QEMU with IRIX syscall emulation added
- Linux-only; macOS users must use VM or Bootcamp
- Key commit adding Linux support: `n64decomp/qemu-irix@235970053f1664c9e50f45047548417d2e385cf7`
- Built targets: `--target-list=irix-linux-user,irixn32-linux-user,irix64-linux-user`
- Requires custom library paths: `qemu-irix -L ./tools/ido7.1_compiler/ ./tools/...`

### qemu-mips Alternative
- `qemu-mips` (standard QEMU userland) can run IDO if recompiled for MIPS-Linux
- Community member recompiled `uopt` for `qemu-mips` (Linux), eliminating the IRIX syscall dependency
- Tradeoff: loses IRIX syscall compatibility; only works for the recompiled executables
- Setup: `mips-linux-gnu-gcc -static -o binary-static source.c` + `qemu-mips ./binary-static`

### macOS Limitations
- `qemu-mips` (userland) not supported on macOS; only `qemu-system-*` targets available
- Contributors on macOS use: Bootcamp (Windows), Linux VM, or WSL2 (Windows Subsystem for Linux)
- ARM64 macOS (M1/M2) adds another layer: QEMU for ARM64 host not available for IDO targets as of archive date

---

## Decompilation Approach

### Goal: Not Matching, but Understanding
- Explicit community consensus: IDO decomp is **not** a matching decompilation project
- Goal: understand compiler internals well enough to run IDO natively (without qemu-irix)
- Intermediate goal: functional equivalence — same input/output behavior, not byte-identical binaries
- Testing method: feed IDO and re-decompiled version same N64 game source; compare outputs

### Split Methodology
- Each binary split into multiple `.s` files (one per function)
- `.s` files assembled and linked with `gcc` (not MIPS tools) to produce working executable
- Custom disassembler produces `.s` files with: `.gpword`, `.size`, `.type` macros, symbol references
- `glabel` macro compatibility with PIC (Position-Independent Code) required fixes for local labels

### Global Offset Table (GOT) / PIC Issues
- IDO binaries compiled as PIC (shared libraries): all globals accessed via GOT
- `gp` register after prologue points to current `.so`'s GOT
- Pattern: `lw tx, global_variable_offset(gp)` → `lw tx, 0(tx)` for global variable access
- Linker handles `gp` initialization via `R_MIPS_32` relocations
- GNU assembler (`as`) uses different GOT format for static variables than IDO's `as1`; workaround required in `.s` files

### Endianness & Platform Portability
- Ucode format is big-endian; porting to x86 requires byte-swapping all integer reads
- Struct layouts in Ucode utilities assume big-endian; pointer values serialized differently
- Proposed path to native x86: decompile → replace syscall layer → recompile for x86; not yet complete
- Alternative: static binary rewriting (MIPS instructions → C operations); would also help permuter performance

---

## Languages in the IDO Source

- Primary: C (most of `uopt`, `cfe`, `ugen`)
- **Ratfor**: preprocessor for FORTRAN allowing C-like flow control; invented by Brian Kernighan
- **Pascal**: some components (Pascal Programming Guide copyright 1991-93 SGI); `libp.a` is Pascal runtime
- Assembly: startup code, some low-level routines
- **Community reaction**: little interest in learning Pascal; Pascal components deprioritized

---

## Key Resources

- **Indy dump**: IRIX system dump with header files at `/usr/include/cmplrs/` — essential reference
- **IDO wiki**: `n64decomp/ido/wiki/uopt-split` — documents the uopt split progress
- **cc man page**: archived at `cocky-wescoff-177c47.netlify.app/cc_manual.html`
- **Pascal guide**: `irix7.com/techpubs/007-0740-030.pdf`
- **IRIX Pascal Programming Guide**: `https://web.archive.org/web/*/techpubs.sgi.com/...`
- **Ghidra fix** (for large decompilation payload): custom build shared by community; addresses "Decompiler results exceeded payload limit of 50 MBytes" error

---

## Confidence Levels

✅ **Confirmed** (from primary contributors and maintainers):
- `cfe → uopt → ugen → as1` pipeline order
- Graph-coloring register allocation in uopt
- qemu-irix Linux support key commit
- EFS extraction requires `efs2tar`
- Non-matching decompilation goal (functional equivalence only)

⚠️ **Inferred** (from patterns):
- Full native IDO on x86 is years away; qemu-mips recompilation is nearer-term path
- ~60-70% of `uopt` binary is standard library code; only core routines need decompilation

---

*Source: Discord exports from #ido-decomp (Zelda Decompilation server), ~6,600 messages, 2020+. All usernames anonymized.*
