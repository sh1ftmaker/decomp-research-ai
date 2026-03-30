# Register Allocation: Solving the #1 Matching Problem

*Why your perfect C code compiles to different bytes than the original, and how to fix it.*

---

## 🤔 The Problem Explained

**Register allocation** is the compiler's decision about which CPU registers to use for which variables.

PowerPC has 32 general-purpose registers (`r0`-`r31`). The compiler must assign each temporary variable to a specific register. Metrowerks CodeWarrior uses a specific algorithm that's hard to predict.

### Example

Your C code:
```c
void example(int a, int b, int c, int d) {
    int x = a + b;
    int y = c + d;
    int z = x + y;
    return z;
}
```

Expected assembly (what you want):
```asm
add r3, r4, r5    # x = a + b (r3=return, r4=a, r5=b)
add r6, r7, r8    # y = c + d
add r3, r3, r6    # z = x + y
blr
```

But CodeWarrior might produce:
```asm
add r6, r4, r5    # x in r6 instead of r3
add r3, r7, r8    # y in r3
add r6, r6, r3    # z in r6 then moved to r3
```

Even though the logic is identical, the **register assignments differ**, causing a byte mismatch.

---

## 🔍 Diagnosing Register Allocation Issues

### objdiff tells you

When you have register differences, objdiff will highlight:

```
Function: d_aie_eai_init
  12:   addi r3, r4, 0x10    vs    addi r5, r4, 0x10
  15:   mr r6, r3            vs    mr r3, r6
```

**Key indicators**:
- Same instructions, different registers
- Instructions appear in same order, just registers swapped
- Often affects multiple instructions (systematic permutation)

### Assembly inspection

Open the `.s` file in `build/asm/` and look at the function. If your C's variable names seem reasonable but registers differ systematically, it's allocation.

---

## 🛠️ Fix Strategies (In Order of Preference)

### Strategy 1: Change Variable Names and Order

**Why it works**: Metrowerks assigns registers based on variable order and name length (historical quirk). Changing variable names or reordering them can change the compiler's register assignment.

**Example**:

```c
// Before (doesn't match)
void func(void) {
    int temp1 = ...;
    int temp2 = ...;
    int result = temp1 + temp2;
    return result;
}

// After (matches!)
void func(void) {
    int t = ...;          // shorter name
    int temp = ...;       // reordered
    int result = t + temp; // different assignment order
    return result;
}
```

**Systematic approach**:
1. Look at the target assembly: Which registers hold which values?
2. Rename your variables to "suggest" that assignment to the compiler:
   - Use single letters (`a`, `b`, `c`) for variables that should be in low-numbered registers
   - Use longer names (`temp`, `counter`, `index`) for high registers
   - Order variables to match the assembly's apparent "importance"

**Experience**: For simple functions with 3-5 locals, changing variable order/names often achieves perfect match in 5-10 tries.

---

### Strategy 2: Use Wrapper Functions (Split the Function)

**Why it works**: Smaller functions have less register pressure, and the compiler makes more predictable decisions.

If you have a 200-instruction function with 8 local variables that won't match, consider:

```c
// Original (stuck)
void big_function(/* many params */) {
    int a, b, c, d, e, f, g, h;  // 8 locals = complex allocation
    // ... 200 lines
}

// Split version (may match easier)
static void helper1(int a, int b, int c) {
    // Subset of logic
}

static void helper2(int d, int e, int f) {
    // Other subset
}

void big_function(/* many params */) {
    int a, b, c, d, e, f;
    // Now only 6 locals in main function
    helper1(a, b, c);
    helper2(d, e, f);
}
```

**Caveat**:
- Adds function calls (might affect inlining)
- May change performance slightly (but matching is priority)
- Must match original's function boundaries (can't add new functions arbitrarily)
- Use only within the same `.c` file where splitting makes sense

---

### Strategy 3: Use `decomp-permuter`

**What it is**: A tool that automatically tries different variable name assignments to find one that yields matching register allocation.

**Installation**:
```bash
cargo install decomp-permuter
```

**Workflow**:
1. Write your function with generic variable names: `var1`, `var2`, `var3`, ...
2. Generate permutation config:
   ```bash
   decomp-permuter generate -f function_name -o permutations.cfg
   ```
   This creates a config mapping `var1,var2,...` to potential names
3. Run search:
   ```bash
   decomp-permuter search --objdiff ./objdiff
   ```
   The tool tries different variable name assignments, rebuilds, and checks objdiff automatically
4. When it finds a match, it tells you the winning variable name mapping

**Best for**: Functions with 4-12 named local variables where you're close but registers are permuted.

**Not for**: Functions with complex struct pointers or where variable names matter semantically (you still want readable code after matching). You can rename post-match if needed (but be careful - renaming can break matching again!).

---

### Strategy 4: Add or Remove Temporary Variables

**Why it works**: Adding explicit temporary variables can change how the compiler allocates registers, sometimes achieving the desired assignment.

**Example**:

```c
// Before (won't match)
int result = a * b + c * d;

// After (might match)
int temp1 = a * b;
int temp2 = c * d;
int result = temp1 + temp2;
```

**Why?** The added `temp1` and `temp2` force the compiler to allocate intermediate values to specific registers, which can constrain the allocator to match the original pattern.

**Reciprocal**: Sometimes removing intermediate variables (computing directly in one expression) also changes allocation. Try both directions.

---

### Strategy 5: Use Volatile or Statement Boundaries

**More advanced**: Insert `volatile` keyword or empty `asm("" ::: "memory")` statements to prevent compiler optimizations across certain boundaries.

```c
int a = compute1();
asm("" ::: "memory");  // Compiler won't reorder across this
int b = compute2();
```

**Warning**: This changes semantics slightly (memory barrier), so it should only be used when the original assembly shows actual memory operations. Rarely needed for simple register allocation issues.

---

### Strategy 6: Manual Code Rearrangement

Sometimes the issue is not variable names but the **structure** of the code. The compiler's control flow decisions (loop unrolling, if/else ordering) affect register allocation.

**Common patterns**:

1. **If/else ordering**:
   ```c
   // Try swapping branches
   if (condition) {
       // path A
   } else {
       // path B
   }
   ```
   Swap the two blocks and invert condition (`if (!condition)`). Recompiling may yield different register usage in each path.

2. **Loop structure**:
   ```c
   while (1) {
       if (cond) break;
       // body
   }
   ```
   vs
   ```c
   for (;;) {
       if (!cond) {
           // body
       } else break;
   }
   ```
   Subtle changes can affect register allocation before/after the loop.

3. **Switch statement ordering**:
   Match the original's case order exactly (see [SWITCHES guide](switches.md)).

---

## 📚 Understanding Metrowerks CodeWarrior Allocation

### The "Name Length" Quirk (Historical)

Older CodeWarrior versions (the ones used for GameCube) assigned registers partly based on **variable name length**:
- Short names (1-4 chars) → lower registers (`r3-r10`)
- Medium names (5-8 chars) → mid registers (`r11-r18`)
- Long names (9+ chars) → high registers (`r19-r26`)

This is why you see patterns:
- `i`, `j`, `k` in `r3-r5`
- `temp` in `r11-r14`
- `counter` in `r15-r18`
- `some_long_variable_name` in `r20+`

**Note**: Not 100% deterministic, but a strong tendency.

### Register Classes

| Registers | Typical Use | Volatile? |
|-----------|-------------|-----------|
| `r0` | Special (often zero or assembler temp) | Special |
| `r1` | Stack pointer | N/A |
| `r2` | TOC pointer (runtime) / reserved | - |
| `r3-r4` | Return values, parameter passing | Volatile |
| `r5-r10` | Parameter passing, temporaries | Volatile |
| `r11-r12` | Volatile temporaries | Volatile |
| `r13` | Small data area pointer (SDAP) | - |
| `r14-r31` | Callee-saved (preserved) | Non-volatile |

**For matching**: Don't worry about semantics; match whatever the original does. But understanding which registers are typically used for what can guide your variable naming.

---

## 🎯 Step-by-Step: Fixing a Register Mismatch

Let's walk through a real example:

**You see in objdiff:**
```diff
-  mr r3, r4
+  mr r4, r3
   addi r5, r3, 0x10
-  addi r6, r4, 0x20
+  addi r6, r3, 0x20
```

**Step 1: Examine the full function**
Look at the target assembly. Which variables end up in which registers?

**Step 2: Map your variables to target registers**
Based on target assembly:
- `r3` holds variable `foo`
- `r4` holds variable `bar`
- etc.

**Step 3: Rename your variables accordingly**

Before:
```c
void func(int a, int b) {
    int result = a + b;    // you called it 'result'
    return result;
}
```

After:
```c
void func(int a, int b) {
    int foo = a + b;    // renamed to 'foo' to get r3
    return foo;
}
```

**Step 4: Rebuild and check**

If still mismatched, try also reordering variables:

```c
void func(int a, int b) {
    int bar = b;        // declare early, might get r4
    int foo = a + bar;
    return foo;
}
```

**Step 5**: Use permuter if systematic attempts fail.

---

## ⚠️ Common Pitfalls

### Pitfall 1: Changing Variable Names After Matching

**Don't do this**:
1. Spend hours matching a function
2. Then rename `temp1` to `meaningful_name` for readability
3. Rebuild → No longer matching!

**Why**: The new name changes register allocation.

**Solution**: After achieving match, **don't touch that code**. Add comments explaining what variables mean instead of renaming. Or, if you must rename, use `//` comments:
```c
int temp1 = ...;  // actually: actor_id
```

---

### Pitfall 2: Over-Splitting

Splitting a function into too many helpers can change the register allocation globally because:
- Different function boundaries
- Different parameter passing
- May affect inlining decisions

**Rule**: Split only if the original assembly has separate functions (check `.s` file for other function labels). Don't invent new functions that don't exist in the binary.

---

### Pitfall 3: Ignoring Inlined Context

If a function is **inlined** at multiple call sites, register allocation at each call site must match exactly. You can't just match the inline function once; you must match it in the context of each caller.

This is the hardest scenario. See [INLINES guide](inlines.md).

---

### Pitfall 4: Not Considering Stack Slots

Sometimes variables are **spilled** to the stack (stored in memory, not registers). The pattern of stack slots matters too.

If your C has fewer locals than the assembly's stack frame size, you're missing something. The compiler might be using extra stack space for temporaries. Add dummy variables to match:

```c
// Assembly shows 0x20 byte frame, but you only have 3 ints (12 bytes)
// Add padding:
int pad1[2];  // fill up stack
```

**Better approach**: Use `m2c --stack-structs` to see the exact frame layout.

---

## 🧪 Practice Exercises

### Exercise 1: Simple Match

Given target assembly:
```asm
addi r3, r4, 0x14
addi r5, r3, 0x10
mr r6, r5
blr
```

What C variables should you use to match this register pattern?
- `r3` and `r4` → parameters (common for first two args)
- `r3` modified and used → likely a local named something short
- `r5` intermediate
- `r6` return value

Try: `void f(int a, int b) { int temp = a + 0x14; int result = temp + 0x10; return result; }` (Check: would `temp` be in `r3`? Maybe rename to `t`)

---

### Exercise 2: Reorder Parameters

Function has 4 parameters. Target assembly uses:
- `r4`: first parameter
- `r5`: third parameter
- `r6`: second parameter
- `r7`: fourth parameter

Your C: `void f(int a, int b, int c, int d) { ... }`

What order of variable usage would produce this pattern? Try different ordering in the function body to influence allocation.

---

## 🎯 Advanced: When All Else Fails

Sometimes register allocation just won't match no matter what you try. Reasons:

1. **Compiler version mismatch**: You're not using the exact CodeWarrior version the project expects. Check `configure.py` for compiler requirements.

2. **Different optimization flags**: `-O2` vs `-O3` or different `-inline` thresholds. Some projects use custom `CFLAGS`. Match exactly.

3. **Undocumented compiler behavior**: CodeWarrior has weird heuristics. Find a similar function in the project that already matches and **copy its variable structure exactly**. If they used `short`, `mid`, `long` naming patterns, follow that.

4. **The function is actually impossible**: Rare but happens. Some functions have "non-matching" status in splits.txt for a reason. Mark as `NonMatching` and move on. The community has experts who may solve it later.

---

## 📊 Success Rate

- **Simple functions (≤20 instructions)**: 95% matchable with variable name/order tweaks
- **Medium functions (20-100 instructions)**: 80% matchable with splitting/permuter
- **Complex functions (100+ instructions, C++)**: 60% matchable; some remain `NonMatching` long-term
- **Inline-heavy**: 40% matchable (often require `Equivalent` status)

---

## 🤝 Getting Help

If stuck for >2 hours:

1. Share in Discord:
   - Target assembly (from `build/asm/`)
   - Your C code
   - objdiff diff output
   - What you've tried

2. Ask: "Register allocation won't match for this function, any hints on variable ordering?"

3. **Don't ask for complete solution** - ask for guidance. The community is generous but wants you to learn.

---

## 📚 Further Reading

- [decomp-permuter GitHub](https://github.com/encounter/decomp-permuter) - Automated permutation tool
- [zeldaret Regalloc Guide](https://github.com/zeldaret/tww/blob/main/docs/regalloc.md) - Game-specific examples
- [PowerPC ABI Documentation](https://refspecs.linuxfoundation.org/elfspec/ppc64/PPC-elf64abi.html) - Register usage conventions
- [Metrowerks CodeWarrior Manual](https://archive.org/details/CodeWarriorC_C++AssemblyLanguageReference) - Official docs (PDF)

---

*Next guide: [Inline Functions](inlines.md) - The sneakiest matching challenge*

*Remember: Register allocation is 80% of matching headaches. Master this and you'll be 10x more productive!* ⚡

---