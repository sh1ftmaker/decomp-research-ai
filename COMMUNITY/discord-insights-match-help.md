# Discord Insights: Match Help Channel

**Source:** doldecomp Discord — `#match-help` channel archive  
**Archive lines:** ~583,000  
**Extraction date:** 2026-04-17  
**Confidence methodology:** Pattern counted across number of independent conversation threads discussing the same technique. All author names anonymized to roles (contributor, maintainer, tool author). No verbatim quotes of conversation are reproduced.

---

## Table of Contents

1. [Register Allocation Tricks](#1-register-allocation-tricks)
2. [Inline Function Patterns](#2-inline-function-patterns)
3. [Switch Statement and Jump Table Patterns](#3-switch-statement-and-jump-table-patterns)
4. [Float and Integer Conversion Patterns](#4-float-and-integer-conversion-patterns)
5. [Struct Layout and Alignment Tricks](#5-struct-layout-and-alignment-tricks)
6. [Compiler Flags and Their Effects](#6-compiler-flags-and-their-effects)
7. [Pragmas That Affect Code Generation](#7-pragmas-that-affect-code-generation)
8. [Error Patterns and Solutions](#8-error-patterns-and-solutions)
9. [Compiler-Generated Code Recognition Patterns](#9-compiler-generated-code-recognition-patterns)
10. [Key Discoveries and Aha Moments](#10-key-discoveries-and-aha-moments)

---

## 1. Register Allocation Tricks

**Confidence: High** — Register swap issues appeared in dozens of distinct conversations throughout the archive.

### General Principles

- MWCC allocates non-volatile registers from the top down: the first variable declared in a function typically gets the highest available register (r31), with each subsequent variable taking the next lower register. If your generated code uses registers in the wrong order, reordering variable declarations is the first thing to try.

- Adding or removing a `const` qualifier on a pointer variable can cause the compiler to allocate a different register for it. Removing `const` from a pointer and adding an explicit cast to `void*` forces the compiler to treat it as a new variable, potentially giving it a different register slot. This is a documented technique used specifically to fix one-off register swaps.

- Using the `register` keyword on local variables can force the compiler to allocate specific register positions, but this is brittle — it interacts with other variables and can shift everything else around. Use sparingly when one variable needs to land in a specific float or integer register.

- Explicitly storing function results in intermediate named variables (rather than using return values directly in expressions) affects how the compiler tracks liveness and can shift register assignments throughout the function.

- Adding a cast — even a semantically no-op cast like `(void*)` — forces the compiler to consider a new register for the variable, even when the underlying type is compatible. This technique was confirmed effective in multiple threads for fixing single-register swaps.

### Specific Patterns

- When a pointer comparison generates `cmplw` with the arguments in the wrong order, check whether the pointer types match exactly. Casting `(char*)` vs. `(u32*)` on pointer arithmetic generates `cmplw` with swapped argument registers.

- In cross-product and vector math functions, failing to declare local variables for all intermediate register values (including r0, r1, r2 temporaries) causes the compiler to keep those registers live for longer than the original, producing register allocation that differs from the target.

- If a function uses `stmw` / `lmw` (multi-register store/load), the lowest register saved determines what stmw stores from. If the generated code saves one more or one fewer register than expected, adjusting how many non-volatile registers your C code uses (by adding or removing variables) changes which register the stmw starts from.

- Introducing a local struct that groups multiple variables can change their register assignments as a unit, which is sometimes needed when individual volatile / const tricks are insufficient.

---

## 2. Inline Function Patterns

**Confidence: High** — Inlining questions were the single most common category of questions in the archive, appearing in well over 100 distinct threads.

### Recognizing Inlined Code

- If a function appears in the symbol map but shows zero callers, it is likely inlined everywhere it is used. Check the symbol table before assuming a function is standalone.
- When the same assembly sequence appears identically in multiple functions, it is almost certainly a shared inline or macro rather than code duplication by the programmer.
- If `__LINE__` numbers embedded in string arguments to assert-like calls are the **same** across all call sites, the code was written as an inline function (the line number is fixed at the definition site). If the line numbers differ per call site, it was a macro (each expansion captures its own line). This is a reliable distinguishing technique.
- Double branch patterns at the start of a function (such as `beq` followed immediately by `beq`) often indicate an inlined destructor from a parent class.

### Getting Inlining to Occur

- The compiler flag `-inline auto` enables automatic inlining based on the compiler's heuristics. `-inline noauto` disables automatic inlining but still respects the `inline` keyword. `-inline off` disables all inlining including explicit `inline` declarations.
- `#pragma always_inline on` forces inlining even when `-inline auto` would not normally inline a function. This is useful when the original binary clearly inlines a function that the compiler refuses to inline under normal settings.
- Defining a function body directly in the header file (making it a weak symbol) causes it to be automatically inlined at call sites when the compiler deems it appropriate, even without the `inline` keyword.
- Empty destructor bodies defined directly in the header (`~MyClass() {}`) are automatically inlined, which is the correct approach when the target assembly does not show a `bl` to the destructor but does execute its body.
- There is an inlining depth limit in MWCC. A small function that appears not to be inlined may actually be failing to inline because its only caller calls another inline, and the chain exceeds the compiler's inline depth limit.
- `#pragma auto_inline on` and `#pragma auto_inline off` can be used in push/pop pairs to control which functions get inlined automatically without changing the global flag.
- `-ipa file` (inter-procedural analysis at the file level) significantly changes inlining behavior. It allows the compiler to inline functions across translation unit boundaries within a single file, and can flip the order in which inlined code is emitted. Many games require `-ipa file` to match. Note that `-ipa file` is only supported in MWCC 3.0 and later; earlier compilers require `-ipa function` or the pragma equivalent.
- `#pragma defer_codegen on` delays code emission, which interacts with inline expansion ordering.

### Preventing Unwanted Inlining

- Removing the `inline` keyword from a function declaration does **not** prevent MWCC from auto-inlining it when `-inline auto` is active. The only reliable way to prevent inlining is `-inline off` or `#pragma auto_inline off` around specific functions.
- `__attribute__((never_inline))` can prevent inlining in some compiler versions as a last resort.
- When a function must not be inlined but the project uses `-inline auto`, compiling that specific translation unit with `-inline noauto` (via makefile per-file flags) is the cleanest solution.

### The Peephole Bug and Inline Assembly

- There is a known bug in MWCC 1.2.5 (and related versions): when the compiler encounters any inline assembly (`asm { }`) in a source file, it **disables the peephole optimizer for all subsequent functions in the same file**, even if those functions contain no inline assembly. This causes those subsequent functions to generate different code (missing branch-to-return folding, missing `mr.` combinations, etc.).
- The fix is to add `#pragma peephole on` immediately after each inline asm block, or around the non-asm functions that need peephole active.
- The recommended pattern is:

  ```cpp
  asm void myAsmFunc() { /* ... */ }

  #pragma push
  #pragma peephole on
  void myNormalFunc1() { /* ... */ }
  void myNormalFunc2() { /* ... */ }
  #pragma pop
  ```

- This bug also manifests when an inline asm function defined in a **header file** is included before other functions; the peephole bug activates at the point of inclusion.

---

## 3. Switch Statement and Jump Table Patterns

**Confidence: High** — Switch identification and ordering issues appeared throughout the archive in over 50 threads.

### When the Compiler Generates a Jump Table

- MWCC generates a jump table (stored in `.rodata`) only when the switch has a relatively dense set of case values. A switch with cases 0–9 generates a table; a switch with cases 0 and 9,999,999 does not.
- Small switches (roughly under 4–6 cases, though the exact threshold varies) generate a chain of branches rather than a table. This is sometimes called a "binary search switch."
- The pragma `switch_tables off` prevents jump table generation entirely, forcing all switches to use branch chains.

### Branch-Chain Switch Recognition

- A sequence of `bge` / `beq` / `b` instructions where each branch compares against a literal constant is the pattern for a binary-search switch on a contiguous or near-contiguous range.
- Ghidra tends to invert the condition logic and reverse if/else ordering for these patterns. The MWCC-generated order often places the "check the midpoint first" branch earlier, corresponding to the `default` case appearing first in the source when written as a C switch.

### Getting Switch Order to Match

- The order in which the compiler lays out case blocks affects which branch is "taken" vs. "not taken" in the generated code. Reordering cases in the source, including placing `default` before or after numbered cases, changes the branch layout.
- Using `switch(localVar)` instead of `switch(field->member)` can change branch ordering because the compiler may evaluate the condition differently.
- For switches where the default case comes first in the target assembly's branch chain, try placing `default:` as the first case in the source.
- Sparse switches with many shared outcomes often match when written with multiple fall-through cases sharing the same body.

---

## 4. Float and Integer Conversion Patterns

**Confidence: High** — Float conversion and FPU instruction patterns appeared in many threads.

### Floating-Point Comparison: fcmpo vs. fcmpu

- `fcmpo` (Float Compare Ordered) is generated when the comparison can raise a floating-point exception on NaN. `fcmpu` (unordered) is generated when it cannot. Using a standard `if (a < b)` with `float` or `double` generates `fcmpo`. If the target uses `fcmpo`, standard comparisons are correct.

### The cror Pattern for NaN-Aware Comparisons

- Sequences of `fcmpo` followed immediately by `cror 2, 1, 2` (or `cror EQ, GT, EQ`) are used to implement "is unordered or greater-than" tests. This is equivalent to a `>=` comparison that also returns true when either operand is NaN. The C source is a standard `>=` on floats; the `cror` is compiler-generated for the NaN case and does not require special C syntax to reproduce.

### Float-to-Integer Conversion via Stack

- Converting a float to an integer in MWCC at certain optimization levels goes through the stack: the compiler performs `fctiwz` (float-convert-to-integer-word-with-truncation), stores the result to the stack with `stfd`, then loads the integer part back with `lwz` from the upper word of the stored double. This pattern appears frequently in JMath sinf/cosf lookup table indexing.
- The full sequence is: `fctiwz fN, fM` → `stfd fN, offset(r1)` → `lwz rX, offset+4(r1)`. The `+4` offset is because the integer result occupies the lower 32 bits of the stored double on a big-endian system; `lwz` of the upper word (`offset`) gets the integer value.

### fmadds / fmsubs (Fused Multiply-Add)

- The compiler generates `fmadds` (fused multiply-add single) instead of separate `fmuls` + `fadds` only when the flag `-fp fmadd` (or `-fp_contract on`) is active. Without this flag, two separate float operations are emitted. If the target shows `fmadds`, the project must be compiled with both flags.
- `fmadds` and `fmsubs` correspond to expressions of the form `a*b + c` and `a*b - c` respectively, where all three operands are single-precision (`float`). The compiler will contract these automatically when the flags are set.

### frsp and Single-Precision Results

- `frsp` (round to single-precision) appears when a double-precision intermediate is rounded back to single. If the target does not contain `frsp` but your generated code does, the computation is staying in double precision when the original used single-precision intrinsics. Using `fmuls` (single-precision multiply) instead of `fmul` (double-precision) avoids the `frsp`.
- Casting with `(float)` alone is insufficient to suppress `frsp` in some expressions; the original code may have used a single-precision intrinsic or a specific inline that bypassed the rounding step.

### frsqrte (Reciprocal Square Root Estimate)

- `frsqrte` is a hardware instruction for fast (but approximate) reciprocal square root. It returns a double-precision estimate. When the target uses `frsqrte` followed by `fmuls` (single-precision multiply), the result stays in single precision without `frsp`. If `fmul` (double-precision) is used instead, an `frsp` appears.
- The pattern `frsqrte` + `fmuls result, estimate, input` appears in custom `sqrtf` implementations. Using inline assembly with `register float` variables is sometimes necessary to reproduce the exact register assignment for this sequence.

### Volatile for Float Stack Bouncing

- When the compiler needs to convert between double and single precision through the stack (store as double, reload as float), wrapping the intermediate value in `volatile float` forces the roundtrip through memory. This technique was successfully used to reproduce an unusual `stfs` / `lfs` stack-bounce pattern in a fast-distance function.

### Integer Absolute Value Pattern

- The compiler implements `abs()` on integers using the sequence `srawi rA, rX, 31` / `xor rB, rA, rX` / `subf rB, rA, rB`. This is a branchless absolute value. If you see this sequence, write `abs(x)` in the C source; do not use a manual conditional.

### Boolean-to-Integer Patterns (cntlzw)

- An equality comparison to zero (`x == 0`) often compiles to `cntlzw rX, rX` followed by `srwi r3, rX, 5`. This produces 1 if the input was 0 (count leading zeros of 0 is 32, shifted right by 5 gives 1) and 0 otherwise.
- The expression `(unsigned char)(x == 0)` generates `cntlzw` + `extrwi` (extracting 8 bits). The exact mask in `rlwinm` encodes the bit-width of the boolean output type.
- To reproduce `srwi` instead of `srawi` on a boolean result, the input must be cast to an unsigned type before the shift.

---

## 5. Struct Layout and Alignment Tricks

**Confidence: Medium** — Struct layout issues appeared in many threads but often as secondary factors.

### Small Data Area (sdata / sdata2)

- The compiler places global and static variables smaller than a threshold size into `.sdata` (read-write) or `.sdata2` (read-only / const) sections, which are accessible via r13 and r2 respectively with a single instruction instead of the usual `lis` + `addi` pair.
- The threshold is controlled by `-sdata N` and `-sdata2 N` flags (default is 0 for most projects, but many GameCube games use `-sdata 8 -sdata2 8`). A variable of N bytes or smaller goes into the small data section.
- If generated code uses `lis` + `addi` to load a global but the target uses `r13` / `r2` offsets (the `@sda21` relocation), the `-sdata` / `-sdata2` threshold needs to be raised.
- The linker error "Small data relocation requires symbol to be in small data section" means a translation unit was compiled with different `-sdata` thresholds than the one that defined the symbol. All translation units in the project must use the same thresholds.

### lmw / stmw and the -use_lmw_stmw Flag

- `stmw rN, offset(r1)` saves all registers from rN through r31 to the stack in a single instruction. `lmw` restores them. MWCC only generates these when the flag `-use_lmw_stmw on` is set. Without this flag, the compiler emits individual `stw` instructions or calls the `_savegpr` / `_restgpr` helper stubs instead.
- `_savegpr_N` / `_restgpr_N` are size-optimization stubs. If the target uses `_savegpr`, either compile without `-use_lmw_stmw` or with `-O4,s` (optimize for space). If the target uses individual `stw` / `lwz` instructions but the compiler generates `stmw`, add `-use_lmw_stmw off` to the flags.
- The pragma `#pragma use_lmw_stmw off` / `#pragma use_lmw_stmw on` can selectively disable this optimization for individual functions.

### Struct Members and Register Ordering

- When a struct member is copied to a local variable before use, the compiler assigns it a register at declaration time. The order in which struct members are first accessed in the function affects which registers are assigned to them, which can affect instruction ordering.
- Wrapping multiple local variables in a local struct (anonymous or named) can group them into adjacent registers, which sometimes matches the register layout of the original when individual variable tricks fail.

### Pointer vs. Struct Returns

- Functions returning small structs (e.g., 8-byte `Vec` types) may pass the return via a hidden pointer parameter rather than in registers, depending on struct size and compiler version. If a function shows a hidden first argument being written to, the return type is likely a struct passed by address.

---

## 6. Compiler Flags and Their Effects

**Confidence: High** — Compiler flags were extensively discussed in the archive.

### Optimization Level (-O flags)

- `-O4,p` is optimize-for-speed at level 4. This is the most common setting for GameCube game code and is the most aggressive optimizer. It aggressively unrolls loops, inlines, and schedules instructions.
- `-O4,s` is optimize-for-space at level 4. This is used in some projects and produces slightly different code: it tends not to unroll loops as aggressively and may produce `_savegpr` stubs instead of `stmw`.
- `-O2` (or `#pragma optimization_level 2`) applies a much weaker optimizer. Functions compiled at O2 are recognizable by simpler register allocation and less instruction reordering. Use `#pragma push` / `#pragma optimization_level N` / `#pragma pop` to compile individual functions at different levels.
- The `-opt` flag accepts fine-grained sub-options: `-opt level=4,speed,peephole,schedule` is equivalent to `-O4,p`.

### Instruction Scheduling

- MWCC reorders instructions within basic blocks to hide memory latency according to the target processor's pipeline model. The `-proc gekko` flag sets the scheduler for the GameCube's Gekko processor (PPC 750CL).
- `#pragma scheduling off` disables instruction scheduling for subsequent functions. This is useful when the target has instructions in an unexpected order that cannot be reproduced with scheduling active. However, disabling scheduling also affects the prologue and body, not just the epilogue.
- There is a known quirk in some MWCC versions where epilogue instructions (stack restore, `mtlr`, `blr`) are scheduled differently than the body, causing the early stack restore pattern that appears in some functions. This was identified as a compiler bug that Metrowerks apparently acknowledged and partially fixed, but the exact patch version changed which functions are affected.
- `#pragma scheduling 750` forces scheduling for the PPC 750 specifically, which differs slightly from the generic Gekko schedule.

### Floating-Point Flags

- `-fp hard` uses hardware floating-point instructions. `-fp software` uses software emulation. Nearly all GameCube games use `-fp hard`.
- `-fp_contract on` allows the compiler to contract `a*b + c` into `fmadds`. This flag is required to reproduce fused multiply-add instructions.
- `-fp fmadd` is an older form of the same feature and may be needed for some compiler versions.
- `-fp hardware` is a synonym for `-fp hard` used in some project makefiles.

### Inter-Procedural Analysis (-ipa)

- `-ipa file` enables inter-procedural analysis at the file (translation unit) level. This allows the compiler to make inlining and optimization decisions based on all functions in the file simultaneously. It significantly affects inlining behavior and can change register allocation globally.
- `-ipa file` is available only from MWCC 3.0 onward. For earlier compilers (1.2.5, 1.3.2, 2.x), use `-ipa function` or no IPA.
- Adding or removing `-ipa file` can sometimes fix or break a match because it changes the order in which inlined function bodies are emitted. If a function matches on decomp.me but not locally, check whether decomp.me's context includes `-ipa file`.

### Inline Flags

- `-inline auto` enables automatic inlining based on compiler heuristics (function size, call frequency).
- `-inline noauto` disables automatic inlining but respects explicit `inline` keyword declarations.
- `-inline off` disables all inlining.
- `-inline deferred` processes inlines in reverse file order (bottom-up), which can flip the order in which inline bodies are emitted.

### String and Data Flags

- `-rostr` places string literals in read-only data (`.rodata` or `.sdata2`). Without this flag, string literals may go in `.data`.
- `-str reuse` allows the compiler to deduplicate identical string literals. Whether this is set affects how many copies of a string appear in the binary.

### Common Full Flag Sets Observed

From actual project discussion, the following flag combinations appeared for specific games:

- Pikmin 2 (Kando): `-Cpp_exceptions off -proc gekko -RTTI off -fp hard -fp_contract on -rostr -O4,p -use_lmw_stmw on -sdata 8 -sdata2 8 -nodefaults -msgstyle gcc`
- Super Mario Galaxy (approximate): `-c -nodefaults -proc gekko -DHOLLYWOOD_REV -DEPPC -enum int -fp hard -Cpp_exceptions off -rtti off -ipa file -DEPPC -DGEKKO -O4,p -inline auto`
- Paper Mario TTYD (inferred from pragma discussion): `-O4,p` with `#pragma defer_codegen on`, `#pragma inline_depth(3)`, `#pragma auto_inline on`, `#pragma inline_bottom_up off` applied project-wide.

---

## 7. Pragmas That Affect Code Generation

**Confidence: High** — Pragmas were among the most-discussed topics, with many confirmed working combinations.

### Optimization Control

- `#pragma optimization_level N` (N = 0 to 4) sets the optimizer level for subsequent functions. Use with `#pragma push` / `#pragma pop` to apply to individual functions.
- `#pragma O` is a shorthand that sets optimization to the default level (equivalent to the command-line `-O` flag).
- `#pragma optimize("O4,p", on)` and `#pragma optimize("O2,p", on)` are alternate forms that control both level and speed/space tradeoff simultaneously.
- `#pragma optimizewithasm off` disables optimization for functions that contain inline assembly.

### Scheduling Control

- `#pragma scheduling off` disables instruction scheduling.
- `#pragma scheduling 750` forces scheduling for the PPC 750 processor model.
- `#pragma scheduling on` re-enables scheduling after it has been disabled.

### Inlining Control

- `#pragma always_inline on` forces all inline-declared functions to always be inlined.
- `#pragma auto_inline on` / `#pragma auto_inline off` enables/disables automatic inlining.
- `#pragma inline_depth(N)` sets the maximum inlining depth (chain length).
- `#pragma inline_bottom_up off` controls bottom-up vs. top-down inline processing order.
- `#pragma defer_codegen on` defers code generation to the end of the translation unit, affecting inlining order.

### Peephole Optimizer

- `#pragma peephole on` re-enables the peephole optimizer. This is most important after inline asm blocks (see section 2).
- `#pragma peephole off` disables the peephole optimizer for subsequent functions.

### Jump Table Control

- `#pragma switch_tables off` prevents the compiler from generating jump tables for switch statements, forcing all switches to use branch chains.

### Section Control

- `#pragma section code_type ".init"` places subsequent functions in the `.init` section instead of `.text`. Used for startup code.
- `#pragma force_active on` prevents the linker from stripping a function as dead code. Required when a function appears unreferenced but must be preserved.

### Data Initialization Control

- `#pragma use_lmw_stmw on` / `off` enables or disables the use of `stmw` / `lmw` instructions for saving/restoring nonvolatile registers.

### Undocumented Pragmas

- `#pragma gecko_float_typecons on` is an undocumented pragma discovered by searching the compiler binary for pragma strings. It affects how float type conversions are handled in certain expressions. Enabling it was confirmed to change code generation for specific float conversion patterns.
- `#pragma opt_propagation off` may prevent certain constant propagation optimizations.
- `#pragma scheduling 401` through `#pragma scheduling 860` select specific processor pipeline models for scheduling purposes. The relevant value for GameCube is `750` or `gekko`-equivalent.

### Using Push/Pop for Function-Level Control

The standard pattern for applying a pragma to only one function:

```cpp
#pragma push
#pragma <some_setting>
void myFunction() { /* ... */ }
#pragma pop
```

This is preferable to using on/off pairs because it restores all prior settings atomically.

---

## 8. Error Patterns and Solutions

**Confidence: High** — Error resolution discussions appeared throughout the archive.

### "Small data relocation requires symbol to be in small data section"

**Cause:** Two translation units were compiled with different `-sdata` / `-sdata2` thresholds. One unit placed a symbol in the small data section; another references it expecting it to be in normal data (or vice versa).  
**Fix:** Ensure all translation units use the same `-sdata N -sdata2 N` values. If a symbol must be in normal data, lower the threshold below its size.

### stmw/lmw Generated When Individual stw Expected (or Vice Versa)

**Cause:** The `-use_lmw_stmw` flag is set incorrectly for this function.  
**Fix:** For functions using individual `stw` / `lwz` to save registers: add `-use_lmw_stmw off` (or `#pragma use_lmw_stmw off`). For functions using `stmw` / `lmw`: add `-use_lmw_stmw on`. If the target uses `_savegpr_N` stubs, try `-O4,s` instead of `-O4,p`.

### beqlr / bnelr Not Generated (or Unnecessary beq + blr Generated Instead)

**Cause:** The peephole optimizer is either on or off when it should be the other state. Peephole converts `beq some_label` where `some_label` is an immediately-following `blr` into the single `beqlr` instruction.  
**Fix:** If the target has `beqlr` / `bnelr` but the generated code has `beq` → `blr`: peephole is off; add `#pragma peephole on` above the function. If the target has `beq` + `blr` but the generated code collapses them: peephole is on; add `#pragma peephole off`.

### Function Mismatches Immediately After an asm {} Block

**Cause:** The peephole bug (see section 2). The inline asm block disabled the peephole optimizer for all subsequent functions in the file.  
**Fix:** Add `#pragma peephole on` immediately after the inline asm block.

### Unexpected stmw in a Simple Function

**Cause:** The compiler decided to save enough nonvolatile registers that using `stmw` becomes profitable over individual stores.  
**Fix:** Use `#pragma use_lmw_stmw off` around the specific function, or reduce the number of nonvolatile registers used (by simplifying the function's logic).

### Functions Not Inlining Despite inline Keyword

**Cause:** Either `-inline noauto` or `-inline off` is set globally, or the inline depth limit is exceeded.  
**Fix:** Use `#pragma always_inline on` around the function and its callers, or change the project flags to `-inline auto`. If using `-ipa file`, note that this mode handles inlining differently and may require `#pragma always_inline on` to force specific inlines.

### cmplwi Instead of cmplw 0

**Cause:** The compiler's optimizer prefers the immediate form `cmplwi r, 0`. The original code may have been compiled at a lower optimization level or with an earlier compiler version that generated `li r0, 0` + `cmplw rX, r0`.  
**Fix:** Use `#pragma optimization_level 0` or `#pragma optimization_level 1` around the function, or use a different variable type (signed vs. unsigned changes which compare instruction is chosen).

---

## 9. Compiler-Generated Code Recognition Patterns

**Confidence: High** — These patterns were repeatedly identified and confirmed across many threads.

### Prologue/Epilogue Patterns

- Standard function prologue: `stwu r1, -framesize(r1)` / `mflr r0` / `stw r0, framesize+4(r1)` / `stmw rN, offset(r1)` (or individual `stw` instructions for nonvolatile registers).
- A function without calls (a "leaf function") may omit `mflr`/`mtlr` entirely, saving the link register only if it calls another function.
- Some functions show the `stwu` (stack allocation) appearing after the first few floating-point operations. This is the scheduler moving the stack allocation down to fill pipeline slots, and is intentional compiler behavior, not an error in the code.

### Loop Patterns

- A loop that starts with a `b` to the condition check (with the body below) is a `for` or `while` loop. A loop where execution falls through to the body first is a `do-while` loop. MWCC places the condition check at the bottom by default for `for` and `while`, branching to it from the top.
- `mtctr rX` + `bdnz` is generated for counted loops where the loop counter is not otherwise needed inside the body. This pattern appears in matrix operations and other tightly-counted loops.
- Loop unrolling at `-O4,p` can produce multi-copy loop bodies. Recognizing unrolled vs. non-unrolled variants requires checking whether the same basic operations repeat N times with constant offsets.

### Boolean and Comparison Patterns

- `cntlzw` + `srwi` is generated for `== 0` comparisons returning a 0 or 1 integer value.
- `srawi rA, rX, 31` / `xor rB, rA, rX` / `subf rB, rA, rB` is the absolute value pattern.
- `clrlwi rX, rY, N` is `rlwinm rX, rY, 0, N, 31`, clearing the top N bits. Used for masking to unsigned sub-word types.
- `clrlwi.` (with the dot) also sets the condition register. Used when the masked result is immediately compared to zero.
- `rlwinm` with non-trivial mask/shift values is often used for bit extraction from packed fields. The shift and mask parameters encode the field position and width.

### Virtual Function Dispatch

- Virtual function calls generate: `lwz r12, 0(rX)` (load vtable pointer) / `lwz r12, offsetN(r12)` (load function pointer from vtable slot) / `mtctr r12` / `bctrl` (call through counter register). The vtable offset encodes the slot number.

### Inline/Macro Detection via Code Duplication

- If an identical 3–10 instruction sequence appears verbatim in two or more functions, it is an inlined function or macro expansion. The same pattern with different register numbers is the same code applied to different variables.

### Tail Call Recognition

- A `b` (unconditional branch) to another function's symbol at the very end of a function (instead of `bl` + `blr`) is a tail call. MWCC pre-3.0a3 does not generate tail calls. If the target binary contains tail calls, the compiler version is 3.0a3 or later.

---

## 10. Key Discoveries and Aha Moments

**Confidence: Medium** — These were confirmed solutions to specific hard problems; applicability varies by game.

### The Peephole/Inline-Asm Connection

The most commonly celebrated discovery in the archive: the realization that a single `asm { }` block in a file causes all subsequent C functions in that file to silently use a degraded optimizer. Many contributors spent hours debugging "wrong branch instruction" or "missing mr." issues that were instantly resolved by adding `#pragma peephole on`.

### Const Removes a Register

Adding or removing `const` on a pointer type changes which register the compiler assigns to it. The compiler must prove the value cannot alias before it can keep it in a register across other operations. A `const void*` is treated differently than `void*`, causing a register slot change. This was the key to resolving many one-register-swap residuals.

### Volatile Forcing Stack Roundtrip

Declaring an intermediate `volatile float` variable forces the compiler to store it to the stack and reload it, reproducing unusual `stfs` + `lfs` pairs that appear in optimized float-to-float identity operations or precision-narrowing steps.

### ipa file Flipping Inline Order

Functions that matched on decomp.me but not locally were traced to decomp.me including `-ipa file` by default. Adding this flag to the local build fixed the ordering of inlined code blocks.

### Macro vs. Inline Identification via Line Numbers

When an assertion or error-reporting call shows the same line number in every call site, it is an inline function (line number is fixed at the definition). When each call site shows a different line number, it is a macro. This deterministic test resolved repeated "is this a macro or an inline?" debates.

### The geckoFloatTypeCons Pragma

An undocumented pragma was discovered by text-searching the compiler binary for pragma keyword strings. `#pragma gecko_float_typecons on` affects float type conversion code generation in a way not documented in any official manual. This was confirmed to change generated code for specific float patterns.

### switch_tables off Forcing Branch Chains

When a switch generates a jump table but the target binary shows a branch chain (no table in `.rodata`), `#pragma switch_tables off` directly forces the branch-chain representation regardless of case density.

### Identifying Inline Depth Limits

A function that appears to inline everywhere except one specific caller was traced to the call chain: the caller itself was already inside an inlined function, and the additional inlining depth exceeded MWCC's limit. The solution was `#pragma always_inline on` or restructuring the call site.

---

*This document was extracted and synthesized from the doldecomp Discord match-help channel archive. All authorship has been anonymized. Patterns are described in general terms without reproducing verbatim conversation.*

*Confidence levels refer to how many independent threads corroborated each insight:*
- *High: Appeared in 10+ distinct threads*
- *Medium: Appeared in 3–9 distinct threads*
- *Low: Appeared in 1–2 threads (not included in this document)*
