# Zelda Decompilation Discord: #m2c Channel

**Overview**: Analysis of the `#m2c` channel (~18,600 messages, 2020–2022+). Primary discussion forum for `mips_to_c` (later renamed `m2c`), the MIPS-to-C decompiler used across N64 decomp projects. Discussions span feature development, bug reports, usage patterns, and the eventual addition of PowerPC support.

---

## Tool Identity

### Name History
- Originally called `mips_to_c`, CLI invoked as `mips_to_c.py`
- Informally abbreviated to `m2c` (also retrofitted to mean "machine to code")
- Canonical repo: `matt-kempster/mips_to_c` (later transferred)
- A web version existed at `simonsoftware.se/other/mips_to_c.py`

### Intended Use
- Translates MIPS assembly (IDO-compiled N64 code) to readable C
- Not a push-button solution — output always requires human cleanup
- Context files (`.c` with struct definitions, prototypes) dramatically improve output quality
- Primary author streamed development sessions; videos are documented reference material

---

## Architecture & Internals

### Processing Pipeline
1. **parse_file** — tokenizes the `.s` input
2. **flow_graph.py** — builds control flow graph from MIPS blocks
3. **translate.py** — single-pass translation to IR; acknowledged as fundamentally wrong but functional
4. **if_statements.py** — reconstructs `if`/`while`/`for` from CFG; handles `&&`/`||` detection
5. Output via `get_function_text`

**Known weakness**: `translate.py` being single-pass limits type backpropagation. A full rewrite would be ideal but requires significant time investment.

### Register & Stack Handling
- Registers tracked as `Dict[Register, Expression]`; `sp` initialized to `GlobalSymbol("sp")`
- Saved registers initialized via `saved_reg_symbol`
- Stack argument resolution: when a call uses >4 args, args beyond `$a3` come from stack offsets; `StackInfo.get_argument` handles these
- `MIPS2C_ERROR(Unable to find stack arg 0xN)` indicates m2c cannot trace a stack-passed argument — common in functions with 8+ parameters

### Type Inference System
- Types flow forward through the function; limited backward propagation
- Known function signatures (from context) enable m2c to infer types of arguments passed to them
- `params_known` flag tracks whether a function's arg types are confirmed
- Struct member access: `unk_OFFSET` notation used when type is unknown; improving context resolves these
- Pointer arithmetic heuristic: single-use pointer loads avoided as temps
- Function pointer assignments propagate type info to the pointed-to function signature

---

## Control Flow & Common Issues

### Switch Statements
- Jump tables emitted as `goto **(&jtbl_ADDR + (temp * 4))` initially; later improved
- Bounds-check `if` is auto-generated before the table jump (compiler idiom)
- Cases occasionally appear misordered due to CFG reconstruction; workaround: `--gotos-only` for complex functions
- Default block hoisting: m2c moves `default:` to first position if it has no normal fallthrough

### Branch Likely Instructions
- N64 MIPS has "branch likely" variants where the delay slot instruction is **skipped** if the branch is not taken
- m2c had incomplete support for these; pattern: `branchlikely .label` + instruction in delay slot + duplicate instruction before label
- IDO rarely uses branch likelies directly; mostly appear in GCC-compiled code
- Fix: duplicating the delay slot instruction at all source sites and moving the label

### `&&`/`||` Detection
- `if_statements.py` attempts to detect short-circuit operators
- Can fail on complex control flow: `Complex control flow; node assumed to be part of &&/|| wasn't` error → use `--no-andor` flag as workaround

### Delay Slot Edge Cases
- `Label L80XXXXXX refers to a delay slot; this is currently not supported.` — occurs when a branch target lands inside a delay slot
- Fix: copy the delay slot instruction to all branch sources and move the label forward, or add a `nop`

### Likely Branches Causing Segfaults in uopt
- A specific branch-likely pattern could cause `uopt` (IDO optimizer) to segfault when fed m2c output
- Root cause: m2c emitting constructs that trigger a known uopt bug

---

## Usage Patterns

### Context File Strategy
- Provide struct definitions, function prototypes, and typedef aliases as context
- Context can include full `.c` files; m2c discards function bodies and only reads declarations
- Workaround for actor type confusion: replace `Actor*[]` array with `union { ActorListEntry actorList[12]; struct { char pad[]; Player* PLAYER; } fictive; };`
- Community generates context via `decompctx.py`; run against the full project source tree

### Common Error Messages
| Error | Cause | Fix |
|-------|-------|-----|
| `MIPS2C_ERROR(cfc1)` | FPU condition register read; no C equivalent | Manual: wrap in macro or treat as `u32` |
| `MIPS2C_ERROR(Unable to find stack arg 0xN)` | Stack-passed argument not traceable | Add parameter types to context |
| `Failed to evaluate expression -1 at compile time` | Array size uses non-constant expression | Add constant definition to context |
| `Failed to evaluate expression PLAYER_LIMB_MAX` | Enum value used as array size | Provide enum definition in context |
| `Complex control flow; node assumed to be part of &&/\|\|` | CFG has unusual `&&`/`\|\|` shape | Use `--no-andor` flag |

### Local vs. Web Usage
- Small functions: web version sufficient
- Large/complex functions: local preferred (avoids timeout, permits custom context)
- m2c does not understand GCC ABI by default; IDO-specific assumptions can produce wrong output for GCC-compiled code

---

## PowerPC Support (2022)

### Motivation
- MWCC (Metrowerks CodeWarrior) targets PowerPC; GC/Wii decomp community needed m2c support
- Branch `ppc2cpp` developed externally, then merged to mainline as `--target ppc`

### ABI Differences from MIPS
- PPC uses `$r3`-`$r10` for arguments (vs MIPS `$a0`-`$a3`); more registers before stack spill
- Virtual base class / vtable layout differs from MIPS IDO ABI
- `FunctionSignature` refactored to be ABI-based rather than API-based to handle both
- `lbl_80520AD0 + %sda21(0x4)` label syntax initially broke PPC parsing; fix: handle offset-from-label syntax

### Remaining Gaps at Merge
- `(rA|0)` patterns normalized in `normalize_instruction`
- Carry arithmetic flagged but output looks ugly
- `ElfFile` class limited to "small ELFs"; not production-grade
- `FunctionSignature` refactor held off until PPC merge completed

---

## Development Contributions & Workflow

### Contribution Points
- Randomization passes in the permuter were described as easy entry points for new contributors
- m2c codebase described as harder: type system non-obvious, translate.py messy, single-pass fundamental limitation
- Stream recordings explain architecture better than docs

### Known Limitations (Accepted, Not Fixed)
- Code reordering: m2c sometimes moves blocks in ways the compiler wouldn't; known issue, no complete fix
- `translate.py` single-pass architecture: type information can't fully backpropagate
- Duplicate `return` statements in switch cases: a known emission artifact

### Testing
- `tests/end_to_end/` contains reference test cases per feature (e.g., `gcc-division`, `modulo-by-power-of-two`)
- Regression tests run against known-good outputs; PPC and MIPS tested independently

---

## Cross-Project Insights

- Contributors across OoT, MM, Paper Mario, SM64, and GC/Wii all used the same tool; discussions reflect multi-game breadth
- IDA output often has quirks (malformed `lwl`/`lwr`, pseudo-instructions) that break m2c parsing; prefer clean disassembly
- Hex-Rays MIPS decompiler mentioned as competition (IDA 7.5+); not seen as a threat since m2c is free and matching-focused

---

## Confidence Levels

✅ **Confirmed** (from primary author and active contributors):
- Single-pass `translate.py` limitation is known and accepted
- Context files dramatically improve output
- `--no-andor` flag workaround for complex CFG
- PPC support merged 2022

⚠️ **Inferred** (from patterns across messages):
- ~30-40% of m2c output requires non-trivial cleanup before compiling
- Delay slot label errors are rare but occur in games using unusual compiler output

---

*Source: Discord exports from #m2c (Zelda Decompilation server), ~18,600 messages, 2020–2022+. All usernames anonymized.*
