# Automated Decompilation Agent: Architecture & Findings

## Overview

We built `decomp_agent/` — a Python automation pipeline that systematically processes
GameCube decompilation functions through a state machine, using algorithmic tools
for 90% of the work and cheap AI only when needed.

**Location**: `/home/selstad/Desktop/DecompAgent/decomp_agent/`
**Target**: Super Smash Bros. Melee (doldecomp/melee), 1845 unmatched functions

## Architecture

```
decomp_agent/
├── config.py            # All paths, thresholds, API config
├── state_db.py          # SQLite state tracking per function
├── target_selector.py   # Parse report.json, rank by difficulty
├── source_editor.py     # Extract/insert functions in .c files
├── build_diff.py        # ninja + objdiff-cli, diff classification
├── m2c_runner.py        # Run m2c for initial decompilation
├── permuter_runner.py   # Auto-setup + run decomp-permuter
├── ai_fixer.py          # Minimal prompt generation + Anthropic API
├── prompts.py           # Prompt templates (~1500 tokens each)
└── orchestrator.py      # Main loop, parallel dispatch by unit
```

## Key Design Decisions

### 1. AI gets minimal context (~1500 tokens per call)
- Only the function's assembly, current C, diff summary, and 1 matched example
- Never the whole file or project context
- Budget: ~$5 for all 1845 functions on Haiku

### 2. Permuter handles register allocation, not AI
- When size matches but registers differ → auto-setup permuter directory
- Uses objdiff.json for exact compiler flags
- 10-minute timeout per function

### 3. State machine prevents wasted work
```
UNSELECTED → DECOMPILING → BUILDING → CLASSIFYING
                                          ↓
                          ┌── MATCHED (done!)
                          ├── REGALLOC_ONLY → PERMUTER → AI → SKIPPED
                          ├── SIZE_MISMATCH → AI_LOGIC_FIX → SKIPPED
                          └── COMPILE_ERROR → AI_SYNTAX_FIX → SKIPPED
```

### 4. Parallelism by translation unit
- Different .c files process in parallel (ThreadPoolExecutor)
- Same .c file serialized (shared .o build target)

## Empirical Findings

### From running the pipeline on the top-ranked functions:

| Function | Size | Initial Match | Classification |
|----------|------|--------------|----------------|
| __THPHuffDecodeDCTCompY | 1660b | 100.0% | REGALLOC_ONLY (2 diffs) |
| fn_80186080 | 312b | 99.3% | REGALLOC_ONLY (10 diffs) |
| mpJointListAdd | 1300b | 100.0% | REGALLOC_ONLY (5 diffs) |
| fn_801EF60C | 460b | 99.8% | REGALLOC_ONLY (5 diffs) |
| ftCh_Damage2_Anim | 208b | 100.0% | REGALLOC_ONLY (1 diff) |

**Key insight**: The top-ranked functions are almost all REGALLOC_ONLY. The logic is already
correct — only register assignment differs. This is exactly what the permuter is designed for,
but it needs more time or PERM macros to crack them.

### From manual decompilation attempts:

| Function | Technique | Result |
|----------|-----------|--------|
| lbArq_80014BD0 (348b) | Variable reuse (`intr` for busy-wait return) | 39% → 91% |
| lbArq_80014BD0 | Merge `tail`/`prev` into single variable | Size matched (348=348) |
| ftColl_8007891C (124b) | Direct `->user_data` vs `GET_FIGHTER` | No improvement |
| ftColl_8007891C | Various inline/scoping changes | Stuck at 93.1% |

### MWCC Register Allocation Tricks (ranked by effectiveness):

1. **Variable reuse** — Reusing a variable for multiple purposes (e.g., `intr` for both interrupt state and function return) dramatically improves matching
2. **Variable merging** — Using one pointer variable for both list traversal and removal operations
3. **Declaration order** — First declared long-lived variable → r31, second → r30, etc.
4. **Temp variable addition/removal** — Changes which values stay in registers
5. **Pointer reload pattern** — Re-reading `gobj->user_data` instead of reusing local
6. **const qualification** — Adding/removing const changes allocation
7. **Type differences** — `int` vs `s32`, cast tricks
8. **MWCC load hoisting** — The `-O4,p` flag aggressively hoists loads before function calls; very hard to suppress

## Usage

```bash
cd /home/selstad/Desktop/DecompAgent

# See top targets
python3 -m decomp_agent.target_selector

# Dry run (no changes)
python3 -m decomp_agent.orchestrator --dry-run --limit 10

# Process 5 functions
python3 -m decomp_agent.orchestrator --limit 5 --workers 1

# Full parallel run
python3 -m decomp_agent.orchestrator --workers 4

# Short permuter timeout for testing
python3 -m decomp_agent.orchestrator --limit 20 --permuter-timeout 120
```

## Estimated Cost for Full Run

| Resource | Cost |
|----------|------|
| Haiku API calls (~1845 functions × 3 attempts) | ~$5 |
| CPU time (permuter, 10min × 500 functions) | ~83 hours |
| With 4 parallel workers | ~21 hours |

## Future Improvements

1. **PERM macros in permuter** — Currently using PERM_RANDOMIZE; manual PERM_GENERAL for declaration ordering would be more effective
2. **Context file for permuter base.c** — Use the project's .ctx files for better type information
3. **Incremental builds** — Skip ninja if .c file hasn't changed
4. **Better AI prompts** — Include register mapping from target asm in regalloc prompts
5. **Discord knowledge integration** — Feed community tips into the AI prompt templates
