"""Minimal prompt templates for AI-assisted decompilation fixes."""

LOGIC_FIX = """Fix this GameCube decompilation function for MWCC (Metrowerks CodeWarrior, PowerPC, -O4,p).

TARGET ASSEMBLY:
```
{asm}
```

CURRENT C CODE (compiles but doesn't match):
```c
{current_c}
```

DIFF: target={target_size}b compiled={compiled_size}b delta={delta}b
{diff_details}

NEARBY MATCHED FUNCTION (same file):
```c
{nearby_c}
```

Common MWCC fixes:
- if/else branch swap (compiler chooses branch order by probability or fall-through)
- switch case reorder, or force with `default:` placement
- PAD_STACK(N) for explicit stack frame padding
- __assert("file.c", LINE, "expr") for assertion macros
- inline vs direct field access (inlining changes instruction ordering)
- asm{} block in same file silently disables peephole optimizer — add `#pragma peephole on` after it
- -O4,p aggressively hoists loads before function calls; restructure to match

Return ONLY the fixed C function, no explanation."""

REGALLOC_FIX = """Fix register allocation for MWCC GameCube function. Logic is correct (same size) but registers differ.

CURRENT C CODE:
```c
{current_c}
```

{diff_details}

MWCC register allocation rules (from compiler internals research):
- Declaration order determines non-volatile register assignment: first declared long-lived variable → r31, second → r30, etc.
- Reusing one variable for multiple purposes (e.g., same variable holds interrupt state AND return value) forces register sharing
- Merging two pointer variables into one changes which values stay live simultaneously
- Adding or removing a temporary variable shifts all subsequent allocations
- Adding/removing `const` on a pointer changes its allocation class
- `(void*)` casts create a new register slot for the cast result
- `int` vs `s32` can produce different allocation even with same bit width
- Re-reading `ptr->field` instead of caching in a local forces a reload (matches when original did the same)
- `-ipa file` flag (MWCC 3.0+) changes inline ordering; may explain decomp.me vs local discrepancies

Return ONLY the fixed C function with reordered/restructured declarations."""

SYNTAX_FIX = """Fix this C code so it compiles with Metrowerks CodeWarrior for GameCube (PowerPC).

```c
{current_c}
```

COMPILER ERROR:
{error}

Common MWCC syntax issues:
- No C99 features: no `//` comments in C mode, no VLAs, no designated initializers
- `register` keyword is accepted but ignored by MWCC
- `__declspec(section "name")` for custom sections
- Forward declarations required (no implicit function declarations)
- Implicit int return type not supported in strict mode

Return ONLY the fixed C function."""
