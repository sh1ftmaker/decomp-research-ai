# Automated Decompilation Agent: Architecture & Findings

## Overview

`decomp_agent/` is a Python automation pipeline that systematically processes
GameCube decompilation functions through a state machine, using algorithmic tools
for 90% of the work and AI (Claude API) only when needed.

**Location**: `decomp_agent/` (this repo)  
**Primary target**: Super Smash Bros. Melee (doldecomp/melee), 1845 unmatched functions  
**Designed for**: Any doldecomp-style project with `report.json` + `objdiff.json`

> **⚠️ Setup note**: `decomp_agent/config.py` currently has hardcoded paths pointing to
> `/home/selstad/Desktop/DecompAgent/melee`. Update `melee_root` and related paths to
> match your local clone before running.

---

## Architecture

```
decomp_agent/
├── config.py            # Paths, thresholds, API config (edit before use)
├── state_db.py          # SQLite state tracking per function
├── target_selector.py   # Parse report.json, rank by difficulty/value
├── source_editor.py     # Extract/insert functions in .c files
├── build_diff.py        # ninja + objdiff-cli, diff classification
├── m2c_runner.py        # Run m2c for initial decompilation
├── permuter_runner.py   # Auto-setup + run decomp-permuter
├── ai_fixer.py          # Prompt generation + Anthropic API calls
├── prompts.py           # Prompt templates (~1500 tokens each)
└── orchestrator.py      # Main loop, parallel dispatch by translation unit
```

---

## State Machine

```
UNSELECTED → DECOMPILING → BUILDING → CLASSIFYING
                                          ↓
                          ┌── MATCHED ✅ (done!)
                          ├── REGALLOC_ONLY → PERMUTER → AI → SKIPPED
                          ├── SIZE_MISMATCH → AI_LOGIC_FIX → SKIPPED
                          └── COMPILE_ERROR → AI_SYNTAX_FIX → SKIPPED
```

Classification logic (`build_diff.py`):
- **MATCHED**: objdiff reports 100% match
- **REGALLOC_ONLY**: size matches + ≤4 logic diffs + at least 1 arg diff → register order issue
- **SIZE_MISMATCH**: byte count differs → logic error
- **COMPILE_ERROR**: ninja build failed

---

## Key Design Decisions

### 1. Minimal AI context (~1500 tokens per call)
- Only: function assembly, current C, diff summary, 1 matched nearby example
- Never the whole file or project context
- Models: `claude-haiku-4-5-20251001` (cheap), `claude-sonnet-4-6-20250514` (expensive)
- Budget limit: `max_logic_fix_attempts=3`, `max_regalloc_fix_attempts=2`, `token_budget_per_func=50000`

### 2. Permuter handles register allocation, not AI
- REGALLOC_ONLY → auto-setup permuter directory using project's `objdiff.json` flags
- 10-minute timeout per function; if no match, escalate to AI then SKIPPED

### 3. Parallelism by translation unit
- Different `.c` files process in parallel (ThreadPoolExecutor)
- Same `.c` file serialized (shared `.o` build target)

### 4. Target scoring (`target_selector.py`)
```
score = size_score × match_bonus × unit_bonus × 10000
```
- `match_bonus`: 5.0 for ≥95%, 3.0 for ≥80%, 2.0 for ≥50%, 0.3 for 0%
- `unit_bonus`: 1.0–2.0 based on how complete the translation unit already is
- Prefers near-matches in already-active files

---

## AI Prompts (`prompts.py`)

Three prompt templates, each under ~1500 tokens:

| Prompt | Inputs | Goal |
|--------|--------|------|
| `LOGIC_FIX` | asm + current C + diff + 1 matched function | Fix logic errors producing wrong size |
| `REGALLOC_FIX` | current C + diff details | Reorder declarations to shift register assignment |
| `SYNTAX_FIX` | current C + compiler error | Fix compile errors from MWCC |

**Discord-informed tips now incorporated** (from `COMMUNITY/discord-tribal-knowledge.md`):
- Declaration order → register order (first declared long-lived → r31)
- `const` qualifier shifts allocation
- `(void*)` casts force new register slots
- `#pragma peephole on` after any `asm {}` block
- Variable reuse and merging for REGALLOC_ONLY cases

---

## Empirical Findings

### Top-ranked functions tested on Melee:

| Function | Size | Initial Match | Classification |
|----------|------|--------------|----------------|
| `__THPHuffDecodeDCTCompY` | 1660b | 100.0% | REGALLOC_ONLY (2 diffs) |
| `fn_80186080` | 312b | 99.3% | REGALLOC_ONLY (10 diffs) |
| `mpJointListAdd` | 1300b | 100.0% | REGALLOC_ONLY (5 diffs) |
| `fn_801EF60C` | 460b | 99.8% | REGALLOC_ONLY (5 diffs) |
| `ftCh_Damage2_Anim` | 208b | 100.0% | REGALLOC_ONLY (1 diff) |

**Key finding**: Top-ranked functions are almost all REGALLOC_ONLY. Logic is already correct —
only register assignment differs. This is the permuter's job, but may need PERM macros.

### Manual decompilation reference:

| Function | Technique | Result |
|----------|-----------|--------|
| `lbArq_80014BD0` (348b) | Variable reuse (`intr` for busy-wait return) | 39% → 91% |
| `lbArq_80014BD0` | Merge `tail`/`prev` into single variable | Size matched (348=348) |
| `ftColl_8007891C` (124b) | `->user_data` vs `GET_FIGHTER` macro | No improvement |

---

## MWCC Register Allocation Techniques (ranked by effectiveness)

1. **Variable reuse** — Same variable for multiple purposes forces register sharing
2. **Variable merging** — One pointer for both traversal and mutation
3. **Declaration order** — First declared long-lived variable → r31, second → r30, etc.
4. **Temp variable add/remove** — Shifts what stays live in registers
5. **Pointer reload** — Re-read `gobj->user_data` instead of caching in local
6. **`const` qualification** — Adding/removing `const` shifts register assignment
7. **Type tricks** — `int` vs `s32`, cast variations
8. **`-O4,p` load hoisting** — Aggressive; very hard to suppress without restructuring

---

## Usage

First, update `decomp_agent/config.py` with your local paths. Then:

```bash
cd /path/to/repo

# See top targets ranked by score
python3 -m decomp_agent.target_selector

# Dry run (no file changes)
python3 -m decomp_agent.orchestrator --dry-run --limit 10

# Process 5 functions single-threaded
python3 -m decomp_agent.orchestrator --limit 5 --workers 1

# Full parallel run (4 workers)
python3 -m decomp_agent.orchestrator --workers 4

# Quick test with short permuter timeout
python3 -m decomp_agent.orchestrator --limit 20 --permuter-timeout 120
```

---

## Estimated Cost (Melee, 1845 functions)

| Resource | Estimate |
|----------|----------|
| Haiku API (×1845 functions × 3 attempts) | ~$5 |
| CPU time (permuter, 10min × 500 functions) | ~83 hours |
| With 4 parallel workers | ~21 hours |
| Sonnet fallback for hard cases (10%) | ~$15 additional |

---

## Future Improvements

1. **PERM macros** — Use `PERM_GENERAL` for declaration ordering instead of random permutation
2. **Context files for permuter** — Pass project `.ctx` files for better type info
3. **Incremental builds** — Skip ninja if `.c` hasn't changed since last run
4. **Register mapping in prompts** — Include virtual→physical register map from target asm
5. **Multi-game support** — Generalize `config.py` to accept CLI `--game` flag
6. **Adaptive token budgets** — Spend more on near-matches (95%+), less on 0% matches
