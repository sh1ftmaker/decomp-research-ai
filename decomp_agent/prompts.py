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

Common MWCC fixes: if/else branch swap, switch case reorder, PAD_STACK(N), __assert("file.c", LINE, "expr"), inline vs direct field access.

Return ONLY the fixed C function, no explanation."""

REGALLOC_FIX = """Fix register allocation for MWCC GameCube function. Logic is correct (same size) but registers differ.

CURRENT C CODE:
```c
{current_c}
```

{diff_details}

MWCC tips:
- Declaration order maps to r31 (first), r30 (second), etc.
- Add/remove temp variables changes allocation
- Reuse variables for multiple purposes
- const changes allocation
- int vs s32 differ

Return ONLY the fixed C function with reordered declarations."""

SYNTAX_FIX = """Fix this C code so it compiles with Metrowerks CodeWarrior for GameCube (PowerPC).

```c
{current_c}
```

COMPILER ERROR:
{error}

Return ONLY the fixed C function."""
