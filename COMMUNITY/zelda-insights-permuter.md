# Zelda Decompilation Discord: #permuter Channel

**Overview**: Analysis of the `#permuter` channel (~6,100 messages, 2020–2022). Discussion of the `decomp-permuter` tool — an automated code variation system that compiles random C mutations to find assembly-matching configurations. Primarily used for OoT/MM/Paper Mario at time of these discussions; concepts apply to GC/Wii projects.

---

## What the Permuter Does

The permuter applies randomized transformations to a C function and compiles each variant, scoring how closely its assembly matches the target. It does **not** understand semantics — it randomly changes things and measures assembly similarity.

### Core Loop
1. Load C source and compile it; compute score vs. target asm
2. Copy AST; mutate via randomization passes
3. Compile mutation; if score improves, keep as new base
4. Repeat; output best-scored candidates to file

**Important**: Taking m2c output and feeding it directly to the permuter is a bad strategy. The permuter only handles low-level transformations; m2c output often has structural issues that require human judgment first.

---

## Scoring & Algorithm

### Score Meaning
- Lower = closer match; 0 = byte-perfect
- Score is based on assembly diff, not C correctness — a function can match bytes while being behaviorally wrong (fakematch)
- `--stack-diffs` flag enables stack frame comparison; necessary for fixing variable layout mismatches
- Hash filter: previously stopped at score=0 and restarted; removed as unhelpful in practice

### Algorithm Details
- Maintains `_cached_shared_ast`: a single shared copy of the AST that is never mutated
- Mutations create new ASTs via `copy.copy` (shallow top-level) + `deepcopy` of the function body
- Reuses prior best candidate as starting point with ~30% probability
- `--show-timings` output: approximately `16% perm, 14% stringify, 67% compile, 3% score` — compile time dominates

### Threading Model
- `-j N` sets number of worker processes; uses Python `multiprocessing`
- Sending `Candidate` objects across process boundary via queue was expensive in Python 3.6; optimized later
- Single-threaded (`-j1`) takes a simpler code path and is often faster per-iteration on fast CPUs
- Multi-process mode shows overhead in `multiprocessing/queues` and `multiprocessing/reduction`
- CPU-bound: more cores help, but network latency (for permuter@home) can limit throughput

---

## PERM Macros (Randomization Controls)

### Available Macros
| Macro | Effect |
|-------|--------|
| `PERM_LINESWAP(line1, line2, ...)` | Randomly reorders the listed lines |
| `PERM_GENERAL(opt1, opt2, ...)` | Picks one option at random |
| `PERM_RANDINT(low, high)` | Generates a random integer (easy to add if not present) |

### PERM_LINESWAP Usage Notes
- **Critical**: `N` lines produces `N!` (N-factorial) possible orderings — more than 8 lines is practically infeasible
- Use PERM_LINESWAP first to get variable declarations roughly in correct order, before attempting other fixes
- Can be used with `--stack-diffs` to fix variable ordering on the stack
- Grouping lines within PERM_LINESWAP: modify `split_args_newline` in `src/perm/perm_gen.py` to split on different delimiter

### Undocumented Behavior
- `PERM_GENERAL(,PERM_GENERAL(u8, s8, u16, s16, u32, s32) pad0;)` — nested general with empty first option
- Order of declarations sometimes matters for register coloring even when logically identical

---

## Performance Optimization

### Profiling Findings
- 67% of time is in compilation; m2c output parsing accounts for ~25% at peak
- `get_source` (stringifying AST back to C) is measurable overhead; faster than parse
- Pickle-based AST caching: `3x` speedup demonstrated (34s → 12s on 1.4M line dump)
- 80% of time can be spent in pycparser C parsing when the C file is large; mitigate by trimming context

### Compile Farm (permuter@home, p@h)
- Project to distribute compilation workload across volunteer machines
- Built with Erlang backend, client/server architecture, authenticated crypto layer
- Architecture: `permuter master ↔ permuter client ↔ distcc/local compiler`
- Concern: network-bound for contributors with slow connections
- Docker image `simonlindholm:ido` can supply the IDO compiler within the farm
- Status as of archive: client/server code written; auth server and full integration incomplete

---

## Workflow Tips (Inferred from Q&A)

### Standard Workflow for Hard Functions
1. First attempt: run m2c → fix obvious errors → manually compile → check diff
2. If diff is small (regalloc only): use PERM_LINESWAP on variable declarations
3. If stack frame differs: run with `--stack-diffs` + PERM_LINESWAP
4. Use PERM_GENERAL to try type variants (`u32` vs `s32`, `int` vs `short`, etc.)
5. Only run many-line permutations on a powerful machine or via p@h overnight

### GFX Macro Workaround
- GFX display list macros (N64-specific) can't be parsed by the permuter's C parser
- Workaround: define stub functions for all GFX macros; use `compile.sh` or `#!/usr/bin/env python3` shebang for preprocessing
- Output will contain unexpanded macros in matched files — acceptable

### File Permissions (WSL Issue)
- `chmod -r 777` fails on WSL NTFS mounts; permissions are filesystem-level
- Fix: move permuter workspace to Linux filesystem (`~/` or `/tmp/`), not `/mnt/d/`
- `sudo python3 permuter.py` requirement indicates wrong permissions on output dir; investigate root cause

---

## Integration with Other Tools

### decomp.me Integration (Planned)
- Permuter described as an "optional way to create a scratch" on decomp.me
- Import flow: user provides function + target asm → permuter attempts to find matching C → sends best candidate to decomp.me scratch

### diff.py Integration
- Permuter uses diff.py internally for scoring; changes to diff.py normalization affect permuter behavior
- `%lo`/`%hi` normalization in diff.py must also be applied in permuter (separate codebase)
- Some whitespace normalization bugs required `rstrip()` fix applied in both tools

---

## Confidence Levels

✅ **Confirmed** (from primary author):
- `N!` complexity of PERM_LINESWAP; limit to 7-8 lines
- 67% compile-time; caching AST gives 3x speedup
- p@h in development with Erlang backend

⚠️ **Inferred** (from community patterns):
- m2c → permuter pipeline yields poor results without human cleanup first
- Most contributors use permuter only for final register/stack nudges, not primary decompilation

---

*Source: Discord exports from #permuter (Zelda Decompilation server), ~6,100 messages, 2020–2022. All usernames anonymized.*
