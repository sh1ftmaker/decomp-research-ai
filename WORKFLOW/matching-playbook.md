# Matching Playbook: Systematic Decompilation Process

A step-by-step process for an AI agent to match GameCube functions, distilled from
community research, zeldaret/tww docs, doldecomp/melee wiki, and trial-and-error.

---

## Phase 1: Setup & Target Selection

1. Pick a function from objdiff (prefer: small size, in a nearly-complete file)
2. Read the target assembly from `build/GALE01/asm/<path>.s`
3. Read surrounding matched functions in the same `.c` file for patterns
4. Note the function size, register usage, and calling convention

**Target priority:**
- Tier 1: Empty stubs (just `blr`) — instant match
- Tier 2: <30 instructions, simple control flow
- Tier 3: 30-80 instructions, calls to known functions
- Tier 4: 80+ instructions, complex control flow or C++

---

## Phase 2: Initial Decompilation

1. Use **m2c** to generate initial C: `m2c -t ppc-mwcc-c <asm_file>`
2. Read the output — fix types, names, struct accesses using headers
3. If m2c fails, manually trace the assembly:
   - Map registers to arguments (r3-r10 = args, f1-f8 = float args)
   - Identify function calls (bl = call, b = tail call)
   - Map struct field accesses (lwz r0, 0xOFFSET(rN))
4. Write the C function in the source file

---

## Phase 3: First Compile & Diff

1. `ninja build/GALE01/src/<path>.o`
2. `objdiff-cli diff -u "main/<path>" <funcname> -o /tmp/diff.json --format json-pretty`
3. Parse the diff to determine:
   - **Size match?** Same byte count = correct logic
   - **Control flow match?** Same branches = correct structure
   - **DIFF_INSERT/DELETE?** Extra/missing instructions = wrong logic or inlines
   - **DIFF_ARG_MISMATCH only?** Register allocation problem

---

## Phase 4: Fix Logic Issues (if size doesn't match)

### Size too large (extra instructions):
- Check for unnecessary casts generating extra moves
- Check for `GET_FIGHTER()` macro vs direct `->user_data` access
- Check if an inline function is being called when it shouldn't be
- Check for extra temp variables the compiler can't optimize away
- Try `PAD_STACK(N)` if stack frame is wrong size

### Size too small (missing instructions):
- Missing assert (`__assert("file.c", LINE, "expr")`)
- Missing inline function call (should be inlined, not called)
- Missing `volatile` access pattern
- Missing stack padding

### Wrong control flow:
- if/else branches swapped (invert condition, swap blocks)
- Switch case order wrong (match jump table order, not sorted)
- for vs while loop structure
- Missing break in switch (intentional fallthrough)

---

## Phase 5: Fix Register Allocation (size matches, instructions differ)

This is the hardest part. Apply these techniques **in order**:

### 5a. Variable Declaration Order
MWCC allocates callee-saved registers r31 downward. First declared long-lived
variable gets r31, second gets r30, etc. Reorder declarations to match:

```
Target: r31=global, r30=intr, r29=list_ptr, r28=node
Declare: global first, then intr, then list_ptr, then node
```

### 5b. Temporary Variables
- **Add temps** to force a value into its own register
- **Remove temps** to let compiler recompute values
- **Reuse a variable** for multiple purposes (like the permuter found: `intr = lbArq_80014ABC(rp)`)

### 5c. Pointer Reload Pattern
If the target reloads a pointer from a struct (`lwz` from same offset twice),
the original code re-read the field:
```c
fp = gobj->user_data;    // first use
...
fp = gobj->user_data;    // reload! don't reuse local
```

### 5d. Inline Function Boundaries
A `lwz rN, 0x2c(rM)` (user_data reload) after a function call often signals
an inline function boundary. The inline takes the GObj and internally does
`fp = gobj->user_data`.

### 5e. const Qualification
Adding or removing `const` on local variables changes register allocation.
Experiment with both.

### 5f. Type Differences
- `int` vs `s32` produce different code in MWCC
- `(u64)` cast on array index changes instruction sequence
- C-style cast `(Type*)` vs assignment through typed variable

### 5g. volatile Keyword
Forces stack spill, changes register pressure. Use on variables that the
target stores to stack between uses:
```c
volatile int cached_flag;
```

### 5h. Pragma Controls
```c
#pragma push
#pragma dont_inline on    // prevent inlining
#pragma peephole on       // enable peephole optimizer
// ... function ...
#pragma pop
```

### 5i. Expression Restructuring
- Single-line complex expression vs multi-line with temps
- Ternary `a ? b : c` vs if/else
- `a && b` vs nested if
- Different assignment grouping

---

## Phase 6: Use decomp-permuter

When you're at ~90%+ match and only register diffs remain:

### Setup:
```
nonmatchings/<funcname>/
├── base.c        # Self-contained C with all declarations
├── target.o      # Copy from build/GALE01/obj/<path>.o
├── compile.sh    # Invoked as: ./compile.sh input.c -o output.o
└── settings.toml # compiler_type = "mwcc", func_name = "..."
```

### Manual PERM macros (most effective):
```c
PERM_GENERAL(
    int a; int b; int c;,
    int b; int a; int c;,
    int c; int a; int b;
)
```

### Random mode:
```
python3 permuter.py nonmatchings/<func>/ -j4 --stop-on-zero --best-only
```

### Interpreting results:
- Score 0 = perfect match
- Check `output-<score>-N/source.c` for the best variant
- Apply sensible changes back to the real source (don't blindly copy nonsense)

---

## Phase 7: Finalize & Link

Once objdiff shows 100% match for all functions in a file:

1. Change `Object(NonMatching, "path/to/file.c")` to `Object(Matching, ...)`
2. Run `ninja` — if DOL SHA1 matches, it's linked!
3. If linking fails:
   - Check data section ordering (`.rodata`, `.sdata2` float order)
   - Check symbol ordering in `symbols.txt`
   - Use "Function relocation diffs" in objdiff for diagnostics

---

## Common Patterns Reference

### Empty callback (just returns):
```c
void Callback_Anim(Fighter_GObj* gobj) {}
```
Compiles to single `blr` = 4 bytes. Always matches.

### Simple forwarding call:
```c
void wrapper(GObj* gobj) {
    real_function(gobj);
}
```

### Struct field access chain:
```c
Fighter* fp = gobj->user_data;
fp->field = value;
```
MWCC: `lwz rN, 0x2c(r3)` then `stw rM, OFFSET(rN)`

### Assert pattern:
```c
if (ptr == NULL) {
    __assert("filename.c", 0xLINE, "ptr");
}
```

### PAD_STACK usage:
```c
void func(GObj* gobj) {
    Fighter* fp = GET_FIGHTER(gobj);
    PAD_STACK(8);  // match original stack frame size
    // ...
}
```

---

## Anti-Patterns (Things That Waste Time)

1. Trying to match register allocation before logic is correct
2. Using `GET_FIGHTER()` when target uses direct `->user_data`
3. Sorting switch cases numerically when jump table has different order
4. Adding comments/documentation to code you're trying to match (changes line numbers in asserts)
5. Renaming matched variables for readability then rebuilding
6. Spending >2 hours on one function without trying the permuter
7. Ignoring nearby matched functions that show the coding style
