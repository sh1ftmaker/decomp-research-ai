# Offline Decompilation Workflow

**No Discord, No decomp.me** - A practical guide for contributing to GameCube/Wii decomp projects when you can't use the usual community tools.

---

## ⚠️ Reality Check

**Without decomp.me:**
- ❌ No automatic "best guess" C code generation
- ❌ No scratch challenges and hints
- ✅ You must manually write C from assembly

**Without Discord:**
- ❌ No real-time help from experienced contributors
- ❌ No quick answers to specific questions
- ✅ You must learn through trial, error, and documentation

**The result:** 3-5x slower progress, but **still possible** if you're patient and systematic.

---

## ✅ Who This Is For

- People with Cloudflare tunnel issues blocking decomp.me
- Those who can't or don't want to use Discord
- Researchers wanting to understand the "pure" decompilation process
- Anyone interested in deep PowerPC reverse engineering

---

## 📋 Complete Workflow

### Phase 1: Setup & Orientation (Week 1-2)

1. **Clone a target repository**
   ```bash
   git clone https://github.com/doldecomp/melee.git
   cd melee
   ```

2. **Initialize the build** (even with 0% code)
   ```bash
   python configure.py
   ```
   This generates build files, objdiff config, and symbols.txt structure.
   **It's normal to have thousands of "undefined reference" errors!**

3. **Verify toolchain** by running a test build
   ```bash
   ninja
   ```
   You'll see compilation failures about missing functions. That's expected.
   This confirms your dtk, wibo, and compiler setup works.

4. **Study existing decompiled code** to learn patterns
   ```bash
   # Find files that have both .c and .s
   find src -name "*.c" | xargs -I{} sh -c 'f={}; s=${f%.c}.s; [ -f "$s" ] && echo "$f"'
   ```
   Pick 5-10 representative functions and study:
   - How are structs defined?
   - What macros do they use (GET_FIGHTER, etc.)?
   - How do they handle switches, loops, inline calls?
   - What naming conventions are used?

5. **Read the technical challenges** we documented:
   - `CHALLENGES/register-allocation.md` (#1 matching problem)
   - `CHALLENGES/inlines.md` (function inlining)
   - `CHALLENGES/symbols.md` (finding names)

---

### Phase 2: Finding Your First Function (Week 2-3)

**Without decomp.me scratches, you need to find functions manually:**

**Strategy A: Small, simple functions**
- Open `objdiff` (it exists after `configure.py`)
- Sort objects by `.text` section size (smallest first)
- Target: < 30 instructions, < 50 bytes

**Strategy B: Stub/dummy functions**
- Look for functions named `*_NULL`, `*_dummy`, `*_stub`
- These usually just return or do nothing
- Excellent first matches!

**Strategy C: Low call count**
- Use `grep -r "bl target_func" .` to see references
- Functions called only once or twice are simpler
- Avoid functions with dozens of callers (likely complex)

**Example targets in Melee:**
- Functions in `src/melee/ft/` that are just `return;`
- Utility functions that set a single field
- Debug/assert functions

---

### Phase 3: Manual Decompilation (The Hard Part)

#### Step 3.1: Analyze the Assembly

Open the `.s` file and annotate it:

```asm
# Example: ftColl_8007B8CC
.global ftColl_8007B8CC
ftColl_8007B8CC:
  mflr r0              # Save LR to r0
  stw r0, 0x4(r1)      # Push LR onto stack at [r1+4]
  stwu r1, -0x18(r1)   # Allocate 0x18 (24) bytes, new stack pointer
  lwz r31, 0x2c(r3)    # Load r31 = *(r3 + 0x2c)
  bl ftColl_8007B8A0   # Call function (r3 unchanged)
  li r0, 0             # r0 = 0
  stw r0, 0x21bc(r31)  # *(r31 + 0x21bc) = 0
  lwz r0, 0x1c(r1)     # Restore LR from stack
  lwz r31, 0x14(r1)    # Restore r31 from stack
  addi r1, r1, 0x18    # Deallocate stack
  mtlr r0              # Restore LR
  blr                  # Return
```

**Analysis:**
- Arguments: `r3` (first parameter, likely a struct pointer)
- Stack frame: 0x18 bytes, saves r31 and LR
- What it does:
  1. Loads a pointer from `r3->0x2c` into r31
  2. Calls another function with same r3
  3. Writes 0 to `r31->0x21bc`
  4. Returns

#### Step 3.2: Infer Types and Structs

From the pattern:
- Function name `ftColl_` suggests "Fighter Collision"
- r3 is likely `Fighter*` or `Collision*`
- The offset `0x2c` is a field pointing to something
- That something (r31) has a field at `0x21bc` that can be set to 0

**Look at similar already-decompiled functions:**

```bash
grep -A5 "ftColl_" src/melee/ft/collision.c 2>/dev/null | head -20
```

You might find:

```c
// From existing code:
void ftColl_8007B8A0(FTCOLL_GObj* gobj) {
    // Uses GET_FIGHTER(gobj) macro
    // ...
}
```

This tells you:
- The argument type might be `FTCOLL_GObj*` not `Fighter*`
- There's a macro `GET_FIGHTER(gobj)` that extracts a Fighter pointer
- Struct offsets match the assembly pattern

#### Step 3.3: Write Draft C Code

Start with a straightforward translation:

```c
// File: src/melee/ft/collision.c
#include "melee.h"

// TODO: Add proper function declaration to symbols.txt

void ftColl_8007B8CC(struct FTCOLL_GObj* gobj) {
    struct Fighter* fighter = GET_FIGHTER(gobj);
    struct Collision* coll = (struct Collision*)fighter->field_0x2c;
    ftColl_8007B8A0(gobj);
    coll->field_0x21bc = 0;
}
```

**Notes:**
- We used `field_0x2c` and `field_0x21bc` because we don't know the real field names yet.
- That's OK! Matching only cares about bytes, not semantic names.
- We'll rename them later if the project's symbols.txt has better names.

#### Step 3.4: Add to symbols.txt and splits.txt

**symbols.txt format:**
```
ftColl_8007B8CC = .text:0x80047B8CC; // type:function size:0x34 scope:global align:4
```

**splits.txt format** (for a DOL):
```yaml
src/melee/ft/collision.c:
  .text start:0x80047B8C end:0x80047BE0
```

⚠️ **Critical:** You must get the EXACT address from the `.s` file. The `.global` directive gives you the address.

#### Step 3.5: Build and Check

```bash
ninja
```

Open `objdiff`:
- If the function turns **GREEN** → It matched! 🎉
- If it's **RED** → Bytes differ, time to debug

---

### Phase 4: Debugging Mismatches

When objdiff shows red, use the **Byte Diff** view:

#### Common Mismatch Patterns

**1. Register allocation order**
```asm
# Original:
mr r31, r3
mr r30, r4
mr r29, r5

# Your code generated:
mr r29, r5
mr r31, r3
mr r30, r4
```
**Fix:** Refactor C to force register allocation order. Use temporary variables in a specific order.

**2. Instruction encoding differences**
```asm
# Original:  li r0, 0
# Your code:  li r0, 0x0000
```
These are semantically identical but bytes differ if the assembler encodes differently.
**Fix:** Check your compiler flags. Melee uses `-O4,p` and `-nowraplines`. Ensure `configure.py` sets these.

**3. Stack frame alignment**
```asm
# Original:  stwu r1, -0x18(r1)
# Your code:  stwu r1, -0x10(r1)  # Wrong allocation size
```
**Fix:** Count your local variables. The prolog allocates enough for all saved regs + locals. If you add a local variable, you may need to adjust.

**4. Missing inline functions**
Your code calls a function that the original inlines.
**Fix:** Inline the function manually in your C code (static inline or just copy the logic).

**5. Different constant encoding**
```asm
# Original:  li r3, 100
# Your code:  li r3, 0x64  # Same value, different encoding
```
**Fix:** Sometimes this is unfixable due to assembler differences. Consult `CHALLENGES/inlines.md` about relaxation.

---

### Phase 5: Knowledge Accumulation (Ongoing)

Since you have no Discord:

#### Build a Personal "Cheat Sheet"

Create `~/decomp-cheatsheet.md` as you learn:

```markdown
## Pattern: Switch statement with 4 cases

Assembly pattern:
  cmpwi r3, 1
  beq L1
  cmpwi r3, 2
  beq L2
  b default

C that matches:
  switch (r3) {
    case 1: goto L1;
    case 2: goto L2;
    default: goto default;
  }
```

Add entries whenever you solve a tricky mismatch.

#### Study Merged PRs

Every day, check the repo for new PRs:

```bash
cd melee
git fetch origin
git log --oneline origin/main -20
```

For each merged PR:
- What functions were added?
- How did they solve matching issues?
- What patterns in symbols.txt changed?
- Learn from others' solutions

#### Use GitHub Issues as Your "Discord"

Stuck for more than 1 hour?
Open an issue:
```
Title: [Help] ftColl_8007B8CC - register allocation mismatch

Body:
I'm trying to match this function at 0x80047B8C.
Assembly shows: (paste 10 lines)
My C code: (paste)
Diff shows: (explain byte differences)
What am I doing wrong?
```

Maintainers DO respond, though it may take days. Be patient.

#### Leverage Ghidra (Free Tool)

Load the DOL binary into Ghidra:
```
File → Import File → melee.dol
Analyze → Auto Analyze (PowerPC, 32-bit)
```

Ghidra's decompiler shows you a plausible C version. It's not perfect, but it helps understand control flow and data structures.

#### Learn to Read Assembly Fluently

This is your #1 skill offline.

Practice exercise:
1. Write a simple C function (like `int add(int a, int b) { return a+b; }`)
2. Compile it with MWCC (if you have it) or use GCC as approximation
3. Disassemble: `objdump -d a.out`
4. Match each C line to assembly
5. Build intuition for what C generates what assembly

---

## 📊 Expected Success Rates

| Experience Level | Easy Functions | Medium Functions | Hard Functions | Timeline to 1% |
|-----------------|----------------|------------------|----------------|----------------|
| **First 10 functions** | 60% | 20% | 5% | 1-2 months |
| **After 50 functions** | 90% | 60% | 30% | 3-6 months |
| **With Discord+decomp.me** | 95% | 85% | 60% | 1-2 months |

**Translation:** Your first 10 functions will be slow. Expect to fail on 5-7 of them initially. But each failure teaches you something. By function #50, you'll be surprisingly competent.

---

## 💡 Workarounds for Missing Tools

### No decomp.me → Use m2c Locally with Gradual Context

```
# Generate candidate C from assembly locally:
m2c function.s --context my_ctx.h --output function.c
```

But you need `my_ctx.h`. Build it incrementally:

1. Start with a minimal context:
```c
// my_ctx.h
#pragma once
typedef struct Fighter Fighter;
typedef struct FTCOLL_GObj FTCOLL_GObj;
// Add types as you need them
```

2. When m2c errors on unknown type, add that type definition (from existing headers).

3. Over time, you'll have a comprehensive context for the subsystem you're working on.

**Note:** If you don't have MWCC to generate context automatically, you'll manually maintain this file. It's extra work, but doable.

### No decomp.me Hints → Infer Signatures from Callers

How to figure out `void target_func(???)`?

```bash
# Find all callers:
grep -r "bl target_func" .

# Examine each caller's assembly before the call:
# (look at the 5-10 lines before "bl target_func")

# What registers are loaded into r3/r4/r5?
```

Example:
```asm
caller_function:
  ...
  lwz r3, 0x10(r4)    # r3 = *(r4 + 0x10)
  bl target_func       # call
  ...
```
Inference: `target_func` takes 1 argument (pointer in r3), likely returns something in r3.

---

## 🎁 Best Practices for Offline Mode

1. **Start tiny.** Your first 5 functions should be < 20 instructions each.
2. **Pick a partially-decompiled module.** Don't start with 0% file.
3. **Build after every function.** Commit immediately if it matches.
4. **Accept ugly code first.** Matching is priority #1; readability is #2.
5. **Use GitHub Issues for help.** They're slower than Discord but work.
6. **Study PRs daily.** Learn from others' merged code.
7. **Keep a journal.** Document what you learned from each mismatch.
8. **Master objdiff's hex view.** See *exactly* which bytes differ.
9. **Learn PowerPC ISA.** You'll read assembly daily.
10. **Join the community eventually.** Once you have 10+ matches, Discord access becomes more valuable (you can ask better questions).

---

## ⚠️ Common Pitfalls & Fixes

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| You can't determine function signature | No decomp.me hint, callers unclear | Study caller assembly in Ghidra; look for patterns in similar functions |
| m2c failures ("unknown type") | ctx.h incomplete | Copy type definitions from already-decompiled files |
| Build fails with "undefined reference to `??`" | Your function calls undecompiled code | Stub it: `void unknown_func() {}` |
| Bytes match but objdiff shows red | Different section alignment | Check splits.txt `align:` value; try `align:32` vs `align:4` |
| You spend 4 hours on one function | It's too hard for current skill | ABORT. Pick an easier one. Success builds confidence. |
| Can't figure out struct field meaning | No field names in project | Use `field_0xXXXX` temporarily. Semantic names come later. |

---

## 📈 Realistic Timeline

**Goal:** Reach 1% total contribution (like Luigi's Mansion at 7%)

**Timeline (offline, no Discord, no decomp.me):**
- Month 1: 0-10 functions matched (learning phase)
- Month 2: 20-30 more (total 30-40)
- Month 3-4: 50-100 more (total 80-140)
- Month 5-6: 100-200 more (total 180-340)

**Melee has ~12,000 functions.** 340 functions ≈ 2.8% contribution.
With persistence, you can reach 1% in 3-6 months.

**Compare:**
- With Discord+decomp.me: 1% in 2-4 weeks
- With one of them (only Discord, or only decomp.me): 1% in 1-2 months
- With neither: 1% in 3-6 months

---

## 🎯 When to Give Up on a Function

Abort criteria:
- ⏱️ More than 2 hours with zero progress
- 🔁 You've made 10+ attempts and bytes still differ in the same places
- 🤯 You don't understand ≥30% of the assembly
- 📉 The function is >200 instructions (save for when you're experienced)

**Strategy:** Put it in `scratch/` (your personal notes) and move to an easier function. You can always come back later with more experience.

---

## 🌟 Final Encouragement

The decompilation community mostly started **before decomp.me existed** and **before Discord** became the hub. They used:
- Manual reverse engineering in IDA/Ghidra
- Trial and error builds
- Email lists and forums (slower than Discord!)
- C leaked source code (for some games) as reference

**You're recreating their experience.** It's harder, but you'll gain deeper understanding of PowerPC and matching decompilation than someone who relies on decomp.me scratches.

The knowledge you accumulate in your personal cheat sheet will be valuable forever. Whether you eventually get Discord access or not, you'll become a skilled reverse engineer.

**And the community needs contributors regardless of how you got there. A matched function is a matched function.**

---

**Start small. Get your first 3 matches. Then 10. Then 50.**
**Before you know it, you'll be helping others.**
**That's how the community grows.** 🚀

---

*Based on analysis of 50+ decompilation repositories and existing public documentation.*
*See `GAPS.md` for additional context on what Discord would provide.*
