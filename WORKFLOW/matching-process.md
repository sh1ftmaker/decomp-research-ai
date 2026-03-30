# The Matching Process: Achieving Byte-for-Byte Identical Binaries

*The core methodology behind successful GameCube/Wii decompilation*

---

## 🎯 What is "Matching"?

**Matching** means your decompiled C code, when compiled, produces **exactly the same bytes** as the original game binary (DOL or REL).

Not "same functionality" → **byte-for-byte identical**.

This is crucial because:
- Ensures 100% accuracy (no guesswork)
- Guarantees original game behavior (no bugs introduced)
- Preserves the authentic experience (no changes)
- Enables mods/ports by having clean source

---

## 🔬 How Do We Verify Matching?

The verification pipeline:

```
Original Game DOL/REL
         ↓
    [dtk dol split]
         ↓
    Target .o files (build/asm/)
         ↓
Your decompiled C code
         ↓
    [Ninja + CodeWarrior-compatible compiler]
         ↓
    Recompiled .o files (build/src/)
         ↓
    [objdiff comparison]
         ↓
    ✅ Zero byte differences = Matching
    ❌ Any difference = Non-Matching
```

---

## 📊 Anatomy of an Object File

Each `.o` file contains:

| Section | What It Has | What You're Matching |
|---------|-------------|---------------------|
| `.text` | Machine code instructions | Exact instruction encoding (binary opcodes) |
| `.rodata` | Read-only data (strings, constants, jump tables) | Exact byte values |
| `.data` | Initialized writable data | Exact initial values |
| `.bss` | Zero-initialized data | Size only (no content to match) |
| `.rel.*` | Relocations (fixup addresses) | Exact relocation targets and offsets |

**Matching focuses on `.text`, `.rodata`, `.data`** - these must be identical byte-for-byte.

---

## 🔍 The Matching Checklist

When objdiff shows differences, it categorizes them:

### 1. Instruction Differences

```
Original:  addi r3, r4, 0x10
Yours:    addi r3, r4, 0x14  ← differs by immediate
```

**Causes**:
- Wrong constant in C code
- Different arithmetic expression
- Compiler generated different instruction

**Fix**: Look at the instruction encoding in objdiff's hex view. What immediate value is needed? Adjust your C.

---

### 2. Register Allocation Differences

```
Original:  mr r3, r4
           mr r5, r6
Yours:    mr r5, r6
           mr r3, r4  ← registers swapped
```

This is the **#1 most common issue** in decompilation.

**Causes**:
- Compiler chose different register assignment
- Variable ordering in your C affects compiler decisions
- Metrowerks vs GCC register allocation (even with same flags)

**Fixes**:
- Try different variable names/ordering (affects compiler's internal numbering)
- Use `decomp-permuter` to search permutations
- Split into smaller functions (reduces register pressure)
- Use temporary variables to force allocation

See [REGISTER ALLOCATION guide](../CHALLENGES/register-allocation.md) for detailed strategies.

---

### 3. Order of Statements

```
Original:  a = 1; b = 2; c = 3;
Yours:    a = 1; c = 3; b = 2;  ← b and c swapped
```

**Causes**:
- Independent assignments may be reordered by you or the compiler
- Different if/else branch ordering

**Fixes**:
- Reorder your C statements to match the assembly flow
- Compiler may move non-dependent instructions; use `volatile` or separate blocks
- In switch cases: order matters! Follow the assembly case order exactly

---

### 4. Data Differences (Constants, Jump Tables)

```
.rodata diff:
Offset 0x10: Original 0x3F800000 (1.0f), Yours 0x3F000000 (0.5f)
```

**Causes**:
- Wrong constant in your code
- Different array initialization
- Jump table entry order/values

**Fixes**:
- Find the constant in your C and correct it
- For jump tables: m2c may have mislabeled entries; check with `--visualize`
- Use objdiff's "literal diff" mode to pinpoint exact byte location

---

### 5. Relocation Differences

```
Relocation at 0x1234: Original points to func_A, Yours points to func_B
```

**Causes**:
- Symbol ordering in final link changed
- Inline function placed in different header location
- Weak symbols deduplicated differently

**Fixes**:
- Enable "Relax relocation diffs" in objdiff settings (often okay to ignore)
- Check weak symbol ordering in linker script
- Inline location matters: put in header vs `.c` file affects placement

---

## 🧩 Common Matching Patterns

### Pattern 1: The Easy Win (0-20 instructions)

**Characteristics**:
- Simple arithmetic or data movement
- No function calls
- No loops or only simple loops
- Likely matches after 1-3 iterations

**Strategy**:
- Use m2c directly
- Clean up the output
- Verify with objdiff
- Usually done in 10-30 minutes

---

### Pattern 2: The Function Call Chain (20-100 instructions)

**Characteristics**:
- Multiple calls to other functions
- Stack setup/teardown
- Parameter passing via registers/stack
- May include library/SDK calls

**Strategy**:
1. Identify which library functions are called
2. Check if stubs exist in `doldecomp/sdk_*` repos
3. Decompile inner functions first (bottom-up) OR
4. Decompile outer functions first using stubs (top-down)
5. Once callees match, caller should match easier

---

### Pattern 3: The Control Flow Monster (100+ instructions)

**Characteristics**:
- Nested loops, complex conditionals
- Switch statements with many cases
- Multiple nested if/else chains
- Often an entire game loop or scene manager

**Strategy**:
1. **Break it down**: Add `#pragma region` comments to separate logical sections
2. **Match sub-sections independently**: Don't try to get whole function at once
3. **Use m2c's `--gotos-only` mode** to see raw control flow
4. **Reconstruct switch statements carefully** (see [SWITCHES guide](../CHALLENGES/switches.md))
5. **Render control flow graph** with `m2c --visualize` to understand structure
6. **Match innermost blocks first**, work outward

---

### Pattern 4: The Inline Nightmare

**Characteristics**:
- Function appears in multiple call sites
- No function prologue/epilogue
- Code appears in multiple places in assembly
- compiler aggressively inlined it

**Challenges**:
- Must match *exactly* at each call site
- Different contexts may require different variable names
- Register allocation affected by inlining
- Changing it in one place may break others

**Strategy**:
1. **Find all occurrences**: Search `.s` file for the code pattern
2. **Create inline function** with proper header placement
3. **Use `static inline`** in header (most common)
4. **Match each call site** separately with inline present
5. **If impossible**: Mark as `Equivalent` (last resort; see CONTRIBUTING)

**Key Insight**: Inline functions must appear in exactly the same order relative to other functions as in the original map file. See [INLINES guide](../CHALLENGES/inlines.md).

---

## 🔧 Tool-Specific Matching Techniques

### Using m2c Effectively

```bash
# Start with primitive modes if confused:
m2c.py --gotos-only -t ppc-mwcc-c func.s

# Once structure is clear, try normal mode:
m2c.py -t ppc-mwcc-c -f func -context types.h func.s > func.c

# If switch statement looks wrong:
m2c.py --no-switches -t ppc-mwcc-c func.s

# If ternary operator causing issues:
m2c.py --no-andor -t ppc-mwcc-c func.s

# Combine options:
m2c.py --no-switches --no-andor -t ppc-mwcc-c -f func func.s
```

**Context files are critical**: Provide header files with struct definitions so m2c knows types. Missing context = poor output.

---

### Using objdiff's Advanced Features

**Literal Diff Mode**:
```
Settings → Function diff mode → Literal diff
```
Shows exactly which byte differs. Use to:
- Find wrong constant (see hex value, convert to float/int)
- Locate misplaced instruction
- Identify data vs code differences

**Relax Relocations**:
```
Settings → Function relocation diffs → Relax
```
Allows same instruction with different symbol reference. Often needed for inlines.

**Custom Compare**:
You can write scripts to auto-apply fixes if pattern is predictable.

---

### Using decomp-permuter

When register allocation won't match:

```bash
# Let permuter search for correct variable ordering
decomp-permuter generate permutations.cfg
decomp-permuter search --objdiff ./objdiff
```

This tries different variable name assignments to change compiler's register allocation decisions.

**Best for**: Functions with 4-8 local variables where you're close but registers are permuted.

---

## 📈 The Progress Curve

Expect this progression:

```
Week 1-2: Learning
  - Setup, tools, basic workflow
  - First 5-10 functions matched (small, easy)
  - Understanding codebase structure

Week 3-4: Acceleration
  - 20-50 functions matched
  - Working on medium objects (complete .c files)
  - Beginning to recognize patterns

Month 2-3: Proficiency
  - 100+ functions matched
  - Tackling complex control flow
  - Helping newcomers

Month 4+: Leadership
  - Major objects complete
  - Reviewing PRs
  - Architecture decisions
  - Mentoring
```

**Typical rates**:
- Simple functions: 5-30 minutes each
- Medium objects (complete .c file, 200-500 LOC): 4-10 hours
- Large objects (1000+ LOC, complex): 20-100 hours
- Inline-intensive code: Very time-consuming, may take weeks

---

## 🎯 The Matching Mindset

### What to Aim For

✅ **Perfect match**: objdiff shows 0 differences, build succeeds, ensure you're the right person for this.

❌ **"Good enough"**: Close but not byte-identical → **Not acceptable**

⚠️ **"Equivalent"**: Byte-different but functionally identical → Only with explicit permission and justification, mark as such

### Common Misconceptions

❌ "If it compiles and runs, it's fine"
→ **Wrong**: Must match original bytes exactly

❌ "I can fix it later"
→ **Wrong**: Match as you go; later is harder

❌ "This is just a style difference"
→ **Wrong**: Style affects compiler output → must match exactly

✅ "I'll look at the original assembly and make my C produce the same machine code"
→ **Correct!**

---

## 🔄 Iteration Strategy

When stuck on a function:

1. **Simplify**: Can you match a subset (first half, a loop body)?
2. **Divide**: Break into smaller functions manually, match separately
3. **Restart**: Try m2c with different flags (`--gotos-only` first, build structure)
4. **Compare**: Look at similar functions that already match; follow their pattern
5. **Ask**: Share objdiff screenshot in Discord, ask for hints (don't ask for complete solution)
6. **Sleep**: Often fresh eyes reveal obvious issues

---

## 📊 When to Move On vs. Persist

| Situation | Action |
|-----------|--------|
| Small diff (1-5 bytes), clear fix | Persist! You're close |
| Medium diff (20-50 bytes), unclear | Post in Discord, ask for guidance |
| Large diff (100+ bytes) on complex function | Consider splitting into sub-functions |
| Same function stuck for >8 hours | Ask for code review, may need different approach |
| Entire object stuck for >40 hours | Make partial progress, move to easier tasks, come back later |

**Rule**: Don't let one hard function block all progress. The community has a "stuck function" fund where experts can help on tough ones.

---

## 🏆 Milestones & Recognition

### Contribution Ladder

- 🌱 **First Function** - Welcome! You've joined the ranks
- 🌿 **First Object** - Decompiled complete `.c` file (small milestone)
- 🌳 **100 Functions** - Regular contributor status
- 🏅 **10% of a Game** - Major milestone; often celebrated on Discord
- 🚀 **50% of a Game** - Halfway club (rare, impressive)
- 👑 **90%+ of a Game** - Core team status

Each project has its own recognition system. Most Discord servers have roles:
- `@contributor` (any PR merged)
- `@regular` (5+ PRs)
- `@maintainer` (reviewer rights)
- `@matching-guru` (high completion % on a game)

---

## ⚡ Speed Tips

Once experienced:

1. **Hotkey objdiff reload**: Ctrl+R or set auto-reload
2. **VS Code integration**: objdiff extension shows diffs inline (experimental)
3. **Batch decompile**: `python tools/decomp.py --all` but verify manually
4. **Template functions**: Copy structure from similar matched functions
5. **Know the SDK**: Familiarity with JSystem/Dolphin SDK patterns speeds everything up
6. **Use m2c cache**: `.m2c` files mean second run on same assembly is instant

---

## 🐛 Advanced Troubleshooting

### "Compiler produces different code even though my C is identical"

**Cause**: CodeWarrior compiler version differences, or subtle environment issues.

**Solution**:
- Check `configure.py` uses correct `-sdata` thresholds
- Verify `wibo` is using right GCC version (should be 4.9.4 for most projects)
- Some projects have specific `CFLAGS` that must match

---

### "Build worked before, now objdiff shows new diffs"

**Cause**: Either you changed code, or `splits.txt`/`symbols.txt` got updated.

**Solution**:
- `git diff` to see what changed
- Rerun `python configure.py` to update objdiff.json
- Sometimes `splits.txt` updates are intentional (better splitting)

---

### "Function won't match, I'm 99% sure it's correct"

**Hidden issues**:
- Check alignment padding (`.p2align` directives)
- Verify section placement (`.section .rodata` vs `.section .text`)
- Look for compiler-generated thunks (function stubs)
- NVRAM/disk save functions may have different ordering

**Last resort**:
- Compare full objdump: `objdump -d build/src/foo.o > mine.txt`
- `objdump -d build/asm/foo.o > orig.txt`
- `diff -u mine.txt orig.txt | less`
- Inspect hex bytes directly with `xxd`

---

## 🎓 Beyond Matching: The Recompilation Perspective

Once you have matching code, you can:

1. **Create native ports** (like Animal Crossing PC port):
   - Replace SDK calls with cross-platform libraries
   - Implement platform-specific backends
   - Keep same C source, different backend

2. **Apply mods easily**: Just edit C and recompile

3. **Analyze game logic**: Readable C > assembly

4. **Port to other platforms**: Switch, modern consoles

But **matching comes first** - without that, you're just guessing.

---

## 📚 Further Reading

- [zeldaret TWW Decompilation Guide](https://github.com/zeldaret/tww/blob/main/docs/decompiling.md) - Best-in-class tutorial
- [decomp-toolkit README](https://github.com/encounter/decomp-toolkit) - Tool reference
- [m2c Documentation](https://github.com/matt-kempster/m2c) - Decompiler options
- [objdiff Documentation](https://github.com/encounter/objdiff) - Diffing techniques
- [Advanced Decompilation](https://www.youtube.com/watch?v=VideoGameEsoterica) - Video series (YouTube)

---

*Remember: Every matching function is a victory. The game is played one byte at a time.* 🎮

---

*Next: [Common Challenges](../CHALLENGES/register-allocation.md)*