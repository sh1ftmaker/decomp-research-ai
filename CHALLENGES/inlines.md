# Inline Functions: The Sneakiest Matching Challenge

*Why functions that don't exist in the binary can be the hardest to match, and how to handle them.*

> **See also (Discord-sourced detail):**
> - `COMMUNITY/discord-insights-match-help.md` §"Inlining and IPA" — `-ipa file` (MWCC 3.0+), inline-depth pragmas
> - `COMMUNITY/discord-tribal-knowledge.md` §"Macro vs. Inline: The `__LINE__` Test" — quick distinction technique
> - `COMMUNITY/discord-insights-libraries.md` — JSystem/EGG header-only inline patterns and vtable-ordering pitfalls

---

## ⚡ Quick Distinction: Inline vs. Macro (`__LINE__` Test)

When you see an assert-like call site in `.rodata` strings, the embedded `__LINE__` value tells you which it is:

- **Same line number across all call sites** → it was an **inline function** (line fixed at the definition site).
- **Different line number per call site** → it was a **macro** (each expansion captures its own line).

This is a reliable, no-rebuild-required test. Use it before sinking time into either matching path.

---

## ⚠️ What Are Inline Functions?

**Inlining** is when the compiler replaces a function call with the function's body directly at the call site. The function doesn't exist as a separate machine code block.

### Example

```c
// Source code (INLINE)
static inline int square(int x) {
    return x * x;
}

void caller(void) {
    int a = square(5);  // Compiler replaces with: int a = 5 * 5;
    int b = square(10); // ...with: int b = 10 * 10;
}
```

**What ends up in the binary**:
- No separate `square` function
- `caller` contains two copies of the multiplication code
- Each occurrence may use different registers based on context

---

## 🔍 Why Inlines Are the Worst

### They Appear in Multiple Places

**Problem**: You must match the code at **every call site** separately. If you change the inline function, it affects all its occurrences simultaneously. Move it to a different header location, and all call sites change their assembly ordering.

### Register Allocation Context-Dependent

The same inline code might use different registers at different call sites because:
- Different surrounding variables affect allocation
- Different callers have different register pressures
- CodeWarrior allocates based on local context

### Location Matters

Where you place the inline function (header vs source file) determines **where** in the final binary its code appears relative to other functions. This affects link order and can break matching elsewhere.

---

## 🕵️ Detecting Inlined Functions

### 1. Missing Function in objdiff

You see a block of assembly that looks like a function but:
- Has no function prologue/epilogue
- Not listed in the symbol table
- Not part of any `.o` file's functions
- Appears at multiple places in the code

**Action**: This is an inline. You need to add it as a `static inline` function and match it at each location.

---

### 2. Map File Clues

If you have `.map` files (debug symbols from certain versions):

**Pattern**: The same function name appears at multiple addresses, each under a different parent in the linker tree, marked as `(inline)` or `(weak)`.

Example:
```
 caller.obj
   (funcA, weak)  ← inline!
   (funcB, weak)  ← another inline!
   (caller)       ← actual function
```

**Key**: An inline appears only **once** in the entire map file's tree (the "once per map" rule). If you see it under `caller`, it won't also appear under another function—it's a duplicate occurrence of the same inline location.

---

### 3. Ghidra Analysis

Ghidra may show:
- Code that looks like a function but isn't listed in the function list
- Identical code blocks appearing in multiple places
- "Duplicate code" warnings

**Action**: Create inline function, verify it matches at all sites.

---

## 🛠️ Handling Inlines: The Standard Workflow

### Step 1: Identify All Occurrences

Search the assembly `.s` file for the pattern.

```bash
# Grep for a unique instruction sequence
grep -n "stw r3, -0x10(r1)" game.s

# Or use m2c to extract candidate function
m2c.py --gotos-only -t ppc-mwcc-c --context-address 0xSTART_ADDR game.s > candidate.s
```

You should find **N copies** of essentially the same code (minor differences in registers/immediates).

---

### Step 2: Create the Inline Function

Add to a header (usually the game's common actor header or a shared library header):

```c
// In include/header.h (or src/.../header.h)
static inline int some_inline_function(int param1, int param2) {
    // Code from ONE of the occurrences
    // Use generic variable names (a, b, c) initially
    // Must match the PREDOMINANT pattern
}
```

**Where to put it**:
- If it's actor-specific: in that actor's header
- If it's SDK-wide: in a common include like `dolphin/export.h` or `JSystem/JSystem.h`
- If it's used across many games: in `doldecomp` SDK repos

**Why header?**: `static inline` should be in header to be visible at all call sites. (`.c` file would only be visible within that translation unit, which might not be where all callers are).

---

### Step 3: Replace Occurrences with Call

Now, in each `.c` file that originally had the inline code:

```c
// Before (hand-written assembly pattern):
int x = some_value * 2 + offset;  // This was the inline code

// After:
int x = some_inline_function(some_value, offset);
```

**But wait** - If you literally just replace the code with a function call, the compiler might **not inline it** again (or might inline differently). You need to preserve the exact pattern.

---

### Step 4: Ensure the Compiler Inlines It Again

**Critical**: Your inline function must be **inlinable** by CodeWarrior with the exact same result.

**Options**:

1. **`static inline`** - Most common. Should inline automatically at `-O2`.
2. **Force inline** (if needed):
   ```c
   static inline __attribute__((always_inline)) int func(...) { ... }
   ```
   Check if project uses `always_inline` macros (often `FORCE_INLINE`).

3. **Don't prevent inlining**: Avoid `__attribute__((noinline))`.

4. **Check `-ipa file` (MWCC 3.0+ only)**: Many Wii projects (Galaxy, MKW, EGG) compile with `-ipa file`, which enables inter-procedural analysis across the whole translation unit. This **changes the order in which inlined function bodies are emitted** and can flip whether a body is inlined at all. Symptom: a function matches on decomp.me but not in your local build (or vice versa). Check whether the project's flags include `-ipa file` — and remember it does **nothing** on MWCC 1.2.5/1.3.2/2.x. See `COMMUNITY/discord-insights-match-help.md` §"Inlining and IPA" for the per-game flag matrix.

**Test**: After replacing, rebuild and check assembly. The call should disappear and the inline's code should appear again **exactly** like before (except maybe registers).

If it doesn't inline, the compiler decided not to (due to complexity). Simplify the inline function (no loops, no complex expressions).

---

### Step 5: Match the Inline Function

Now you have a proper `static inline` function in a header, and callers use it.

**But wait** - You still need to make the inline's C code produce the same assembly at each call site! This is the tricky part.

**Approach**:

1. **Start with one call site**: Pick the "easiest" occurrence (simple context, few registers).
2. **Decompile that occurrence** using m2c into a candidate inline function.
3. **Replace the inline code** at that call site with the function call.
4. **Build and check objdiff**:
   - If that call site matches now ✅
   - But other call sites might have broken (different registers)
5. **Iterate**: Adjust the inline function's variable names, add conditionals, or split the inline into multiple variants to cover different contexts.

---

## 🎯 The "Once Per Map" Rule (Critical!)

This is the **most important insight** for inlines:

> In the original `.map` file (if available), an inline function appears **exactly once** in the entire linker tree, under one of its callers. All other call sites reference that same occurrence but are **not separately listed**.

**Implication**: The inline should be defined **in the header** at a location that corresponds to where it appears in the original map file. If you put it in the wrong header or wrong place in the header, all call sites after a certain point will shift in the binary order → breaking matching for everything that follows.

**How to find the right location**:
1. Obtain the `.map` file for the game version (Japanese kiosk demos often have them)
2. Find the inline's one appearance in the tree
3. Note which object file it's under
4. Note its position relative to other functions
5. Place the inline definition in your codebase at the **analogous location**:
   - Same header file (usually)
   - Same relative order among other functions
   - Might require creating new `.c` files or reordering includes

**If you don't have a `.map` file**:
- Trial and error: Move the inline definition around, rebuild, check if matching improves
- Look at similar projects (e.g., TWW shares code with TP; check their inline placement)
- Ask in Discord - someone might have mapped it already

---

## 🧩 Inline Variants: When One Size Doesn't Fit All

Sometimes the inline code is **slightly different** at different call sites:
- Different constants
- Different branches taken (based on parameters)
- Different register usage patterns

**Solutions**:

### 1. Parameterize the Differences

If two call sites have:
```asm
# Site 1: li r3, 0x10
# Site 2: li r3, 0x20
```

Make it a parameter:
```c
static inline void common_inline(int value) {
    // uses value instead of hardcoded constant
}
```
Call sites pass appropriate constant.

---

### 2. Use `if`/`else` Inside the Inline

If branches differ:
```c
static inline int conditional_inline(int x, int flag) {
    int result;
    if (flag) {
        result = x + 1;  // matches Site A when flag=1
    } else {
        result = x - 1;  // matches Site B when flag=0
    }
    return result;
}
```

At each call site, pass the appropriate flag (often a constant `0` or `1`).

**Caution**: This adds a branch. The compiler might generate different code if not careful. Test thoroughly.

---

### 3. Split into Multiple Inlines

If the variants are too different, maybe they're actually **different inlines** that just look similar.

Create:
```c
static inline int inline_variant1(...) { ... }
static inline int inline_variant2(...) { ... }
```

Use at respective call sites. This preserves exact match if the assembly patterns diverge significantly.

---

## 📊 Common Inline Patterns in GameCube/Wii Games

### Pattern 1: Simple Math Helpers

```c
static inline int clamp(int val, int min, int max) {
    if (val < min) return min;
    if (val > max) return max;
    return val;
}
```

**Challenge**: This gets inlined everywhere. Each call site has different register allocation based on surrounding code. May need multiple variants or careful variable naming in the inline.

---

### Pattern 2: SDK Assertions

```c
#define JUT_ASSERT(line, cond) \
    do { if (!(cond)) OSReport_printf(...); } while(0)
```

Often inlined because used extensively. Matching requires:
- Exact string formatting in the report (includes `__FILE__`, `__LINE__`)
- Register usage matching across hundreds of call sites

**Strategy**: Often marked `Equivalent` if too pervasive. Some projects have special `JUT_ASSERT` stubs that mimic behavior without exact matching.

---

### Pattern 3: Virtual Method Invocations

```c
inline void vtable_call(Base_class* obj) {
    obj->vtable->method(obj);
}
```

Complex because:
- Involves pointer dereferencing
- Register allocation depends on what `obj` is
- May have multiple variants for different vtable layouts

---

### Pattern 4: Getter/Setter Shortcuts

```c
static inline int get_some_flag(Actor* actor) {
    return actor->flags & 0x100;
}
```

Simple but appears in many places. Usually matches easily with good variable names.

---

## 🎯 Optimization: Inlines Are Often "Don't Care"

**Reality check**: Many inlines are so trivial (single line, simple math) that if you can't match them exactly, it's okay to:

1. Mark the containing object as `Equivalent` (if inline appears in a matched function)
2. Or accept a small diff in that area

**Why?**
- Inlines usually don't affect overall binary size significantly
- Functionality is identical
- The "last 10%" problem: spending days on one inline for 0.01% improvement isn't worth it

**Community practice**: Most projects have hundreds of inlines with `Equivalent` status. Focus on the core logic first.

---

## 📝 Template: Fixing an Inline

```
1. Identify inline pattern in assembly
2. Count occurrences (grep for unique instruction sequence)
3. Find ".map" file to locate canonical position
4. Create inline function in appropriate header
5. Replace code at each call site with inline() call
6. Rebuild, check objdiff
7. If mismatches at some sites:
   - Try variable name changes in inline
   - Add/remove parameters to differentiate variants
   - Split into multiple inlines
   - Use #ifdef to provide different versions
8. Once all sites match, commit!
```

---

## 🐛 Special Case: __attribute__((section))

Sometimes Nintendo used:
```c
inline void __attribute__((section(".text.init"))) init_func() { ... }
```

This places the inline in a specific section, affecting ordering. You must replicate the section attribute exactly or matching fails.

Check for:
- `__attribute__((section("...")))`
- `#pragma section`
- `#pragma code_region`

These affect placement and must be preserved.

---

## 🧪 Debugging Tips

### Use `objdump` to See What's Inlined

```bash
# Disassemble your compiled .o file
powerpc-eabi-objdump -d build/src/actor.o > mine.txt
# Disassemble target .o
powerpc-eabi-objdump -d build/asm/actor.o > orig.txt
# Compare
diff mine.txt orig.txt | less
```

Look for the inline code in both. Are the instructions identical but at different offsets? That's an ordering issue, not code issue.

---

### Check Compiler Flags

Some flags control inlining:
- `-inline` (threshold)
- `-O2` vs `-O3`
- `-minline` / `-maxinline`

Make sure `configure.py` uses the same flags as the original build. If a project has custom `CFLAGS`, use them.

---

### View Generated Assembly

To see if your inline is actually being inlined:

```bash
# Build with -S to generate assembly
ninja -v CFLAGS="-S"  # or check project's build flags
# Look at .s output file
```

If you see a `bl` (branch to link) instruction to your inline, it's **not inlined** → you need `static inline` or more aggressive inlining hints.

---

## 📚 Further Reading

- [zeldaret TWW Inline Guide](https://github.com/zeldaret/tww/blob/main/docs/decompiling.md#4-inline-functions--debug-maps) - Best practices from Zelda team
- [Metrowerks C++ Reference](https://archive.org/details/CodeWarriorC_C++AssemblyLanguageReference) - Inline semantics
- [GCC Inline Docs](https://gcc.gnu.org/onlinedocs/gcc/Inline.html) - For comparison (Metrowerks is similar but different)
- [C99 Inline Specification](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1256.pdf) - Language standard

---

## ✅ Inline Resolution Checklist

- [ ] Identified all occurrences of the inline pattern
- [ ] Located canonical position in map file (if available)
- [ ] Created `static inline` function with correct signature
- [ ] Placed in appropriate header file
- [ ] Replaced raw code at call sites with function call
- [ ] Verified compiler inlines it (no `bl` instructions)
- [ ] Match at all call sites (variable names may differ per site)
- [ ] If variants needed: parameterized differences correctly
- [ ] Full project builds successfully
- [ ] objdiff shows 0 diff for affected functions
- [ ] No regressions in other objects

---

*Next guide: [Switch Statements](switches.md) - How to match jump tables and switch logic*

*Inline functions: the bane of decompilers everywhere. Persist, and you'll master them!* (╯°□°)╯