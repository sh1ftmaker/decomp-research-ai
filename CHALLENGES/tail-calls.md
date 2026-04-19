# Tail Calls: The Silent Killer of Matching

*Why functions that end with a call to another function break matching, and how to handle them.*

> **See also (Discord-sourced detail):**
> - `COMMUNITY/discord-insights-match-help.md` §"Tail Calls" — confirms MWCC pre-3.0a3 does **not** emit tail calls
> - `COMMUNITY/discord-tribal-knowledge.md` §"MWCC Build Stamp Registry" — full version-to-game mapping

---

## 🧭 First Question: Could Your Compiler Even Have Emitted This?

A `b symbol` (unconditional branch to another function) at the end of a function instead of `bl symbol` + `blr` is a tail-call optimization. Crucially:

> **MWCC versions before 3.0a3 do not generate tail calls at all.**

If your project uses MWCC 1.2.5n, 1.3.2, 2.4.2, 2.6, 2.7, etc., and you see a `b funcB` at the end of a function, **it is not a tail-call optimization** — the splitter is wrong, or the function legitimately ends there and `funcB` is the next separate function. Don't waste hours trying to coerce a non-tail-calling compiler into emitting one.

If your project uses MWCC 3.0a3, 3.0a5, or later (most Wii titles), tail calls are real and you'll need the splitting workarounds in this guide.

A useful corollary: if a binary contains genuine tail calls, you can **lower-bound the compiler version** at 3.0a3.

---

## ⚠️ What Is a Tail Call?

A **tail call** occurs when a function's **last action** is to call another function, and it **immediately returns** that function's return value.

### Example

```c
int wrapper(int x) {
    return real_function(x);  // tail call
}

// Assembly (optimized):
wrapper:
  b real_function  // just branch, no bl (branch and link)
```

Not a tail call:
```c
int wrapper(int x) {
    int y = real_function(x);
    return y + 1;  // not tail: extra work after call
}
```

---

## 🔍 Why Tail Calls Ruin Matching

### They Confuse Function Boundary Detection

The decompilation tools' function boundary analyzer sees:
- Function A's prologue
- Then immediately `b` (branch) to function B
- No function epilogue (no `blr`)

**Misdetection**:
- dtk might think A and B are one function (merged)
- Or think A's code is part of B
- Or miss A entirely

This causes:
- Wrong splitting (functions merged or split incorrectly)
- Assembly view shows wrong function boundaries
- m2c decompiles wrong chunk
- Matching becomes impossible until splitting fixed

---

## 🕵️ Detecting Tail Calls

### 1. Assembly Pattern Look for:

```asm
funcA:
  # Function prologue (if any)
  mflr r0
  stw r0, 0x8(r1)
  # ... maybe some setup
  b funcB      # ← Direct branch, NOT bl (branch and link)
  # No code after b
  # Function A ends here
```

**Key**: `b` instruction instead of `bl`. `bl` calls and links (saves return address). `b` just jumps.

If you see `blr` (branch to link register) after the `b`, that's the function epilogue for funcA but it's part of funcB? Actually no: a tail call typically looks like:

```asm
funcA:
  addi r3, r4, 0x10
  b funcB   # tail call - no blr in funcA
```

`funcB` will have its own prologue/epilogue. But because `b` doesn't link, the return from funcB goes to funcA's caller directly.

---

### 2. objdiff Shows Strange Diffs

If you're trying to match a "function" that:
- Is only 5 instructions long
- Ends with a branch to another function
- objdiff shows the target function's code in the diff

That's a tail call. The tool merged them incorrectly.

---

### 3. Missing Functions in objdiff

Some functions simply don't appear in `objdiff.json` because the splitter merged them with their tail-call target.

**Check**: Search `objdiff.json` for function name; not there? Likely merged.

---

## 🛠️ Fixing Tail Call Detection

### Option 1: Update `splits.txt` (Recommended)

Most projects use `splits.txt` or `symbols.txt` to override automatic detection.

**Format** (varies by project, but typical):
```
# Each line: address function_name
0x80001234 funcA
0x8000123c funcB
```

If `funcA` ends at `0x8000123c` and that's also where `funcB` starts, the splitter knows they're separate.

**How to find boundaries**:
- Use Ghidra or `dtk` to analyze the binary
- Look for where control flow changes from one function to another
- `b` target label = next function start
- `funcA` end = address of that `b` instruction

**Add explicit split**:
```txt
# Address (from .s file), function name
0x80003450 funcA
0x80003458 funcB   # funcA's tail call lands here
```

Then rerun `dtk dol split` or `python configure.py`.

---

### Option 2: Use `--force-thunk` (if available)

Some dtk versions have a flag to force certain branches to be recognized as function calls:
```bash
dtk dol split config.yml --force-thunk 0x80001234
```

Check `dtk dol split --help` for options.

---

### Option 3: Manual `.o` Editing (Advanced)

If all else fails, you can manually edit the generated `.o` file's symbol table, but that's fragile.

Better: Improve `.s` file generation or let the project maintainers handle complex cases.

---

## 🧩 Tail Call Patterns in Games

### Pattern 1: Wrapper Functions

Common for SDK functions that are just forwarding to real implementations:

```c
// In header
extern int OSReport_printf(const char* fmt, ...);

// In some file (just a stub)
int OSReport(int priority, const char* fmt, ...) {
    return OSReport_printf(fmt, ...);  // tail call
}
```

**Why?** Historical: Nintendo added extra parameters later and kept compatibility via wrappers.

---

### Pattern 2: Constructor/Destructor Patterns

```c
void Actor_init(Actor* this) {
    // setup...
    return BaseClass_init(this);  // tail call to parent constructor
}
```

Very common in C++ compilers (tail call optimization for base class constructor).

---

### Pattern 3: Getter/Setter Passthroughs

```c
int get_flag(Actor* this) {
    return this->flags & 0xFF;  // not a tail call
}

// BUT:
int get_health(Actor* this) {
    return this->health_getter(this);  // could be tail call if just forwarding
}
```

---

## 🎯 Decompiling a Function with Tail Call

**Scenario**: You want to decompile `funcA` but it's just a tail call to `funcB`.

**Assembly**:
```asm
funcA:
  addi r3, r4, 0x10  # maybe compute something
  b funcB
```

**Options**:

1. **Decompile as wrapper**:
   ```c
   int funcA(int x) {
       return funcB(x + 0x10);  // if arg was transformed
   }
   ```
   But this compiles to a `bl` (branch and link), not a tail `b`. So you'd need:
   ```c
   int funcA(int x) {
       return funcB(x + 0x10);
   }  # Compiler will likely use bl, not tail b
   ```

   To force tail call, you'd need:
   ```c
   __attribute__((must_tail_call))
   int funcA(int x) {
       return funcB(x + 0x10);
   }
   ```
   But Metrowerks may not support that, and assembly shows a naked `b`.

2. **Mark as non-matching or equivalent**: If `funcA` is trivial and just forwards, it might be considered "don't care" for overall matching. Some projects allow marking such thin wrappers as `Equivalent` because they don't affect gameplay logic.

3. **Split correctly**: Ensure `splits.txt` defines `funcA` as separate from `funcB`. Then decompile `funcA` as:
   ```c
   // funcA - wrapper, not matching due to tail call optimization
   // Equivalent status accepted
   static int funcA(int x) {
       return funcB(x);  // conceptual; actual assembly is just b
   }
   ```
   And it stays as `NonMatching` or `Equivalent`. The important logic is in `funcB`.

**Takeaway**: Tail-call wrappers are often low priority for matching. Focus on `funcB` (the actual work).

---

## 📊 When Tail Calls Cause Major Problems

### The "Everything Merged" Scenario

If the splitter **fails** to detect any function boundaries, you might get one giant function containing the entire game's code.

**Symptoms**:
- Only a handful of object files instead of thousands
- `objdiff` shows enormous mismatches
- Build produces one massive `.o` file
- Progress percentage stuck at 0%

**Fix**: This is a splitting configuration issue. Projects that use `decomp-toolkit` typically don't have this problem because dtk's boundary detection is good. But edge cases exist.

**Solution**:
1. Update dtk to latest version
2. Run `dtk dol split` with `--force-functions` or provide manual `splits.txt`
3. Split manually at obvious `b` boundaries (functions that start with `stwu r1, -...(r1)` prologue)

---

## 🧪 Diagnostic Commands

### Inspect object file sections
```bash
# Use dtk to analyze
dtk dol info orig/GAMEID/sys/main.dol
```

### Disassemble a suspected merged function
```bash
powerpc-eabi-objdump -d build/asm/merged.o | less
```
Look for multiple function-like blocks with no `blr` between them.

### Check objdiff.json
```bash
grep -A5 '"func_name"' objdiff.json
```
See if `size` and `vram` make sense. Overlapping VRAM? Merged.

---

## 📚 Project-Specific Notes

### zeldaret (TP, TWW)
They have excellent manual splitting for tail calls. If you find a missed one, open an issue with `.s` snippet.

### doldecomp (Melee, Sunshine)
Heavily automated. Tail call detection incorporated in dtk. Rare issues.

### PrimeDecomp
Custom splitting script (Python). Some tail calls still problematic; they rely on manual `symbols.txt` entries.

---

## ✅ Resolution Checklist

- [ ] Identified tail call (branch instruction `b` instead of `bl` at function end)
- [ ] Verified callee exists as separate function in objdiff.json
- [ ] If not, added manual split entry in `splits.txt` or `symbols.txt`
- [ ] Reran `dtk dol split` or `python configure.py`
- [ ] Confirmed objdiff now shows separate functions
- [ ] Decompiled callee (real function) instead of wrapper
- [ ] Marked wrapper as `NonMatching` or `Equivalent` if appropriate
- [ ] No regressions in neighboring functions

---

## 🎯 When to Bother vs. Ignore

**Bother**:
- Tail call is masking a real function (so you can't decompile the real thing)
- It's affecting many functions (global splitting problem)
- It's in a critical path (main game loop, rendering)

**Ignore / Mark Equivalent**:
- Simple wrapper that just forwards arguments (like `OSReport` → `OSReport_printf`)
- Functions with no logic (1-2 instructions)
- Project already has `NonMatching` status for that function

**Rationale**: Tail-call wrappers don't contain game logic. Matching them yields minimal benefit. Focus your energy on functions with actual computation.

---

## 📈 Statistics

In typical GameCube game:
- 10-15% of functions are tail-call optimized by Metrowerks
- Most are trivial wrappers or constructors
- Only ~2% are complex tail calls that cause splitting issues

---

## 🔧 Manual Splitting Example

**Given** `.s` file:
```asm
# Unknown function at 0x8000
80001234:   stwu r1, -0x20(r1)
            mflr r0
            stw r0, 0x24(r1)
            ... 
            b 80005678   # tail call to another function

# Next function appears to start at 80005678 but wasn't detected
80005678:   stwu r1, -0x30(r1)   # prologue! This should be separate
...
```

**splits.txt entry**:
```txt
# VRAM address or file offset? Use VRAM from .s labels
0x80001234 func_wrapper
0x80005678 func_real_target
```

Reconfigure → dtk split → now they're separate objects.

---

## 🎓 Understanding the Why

Why does CodeWarrior tail-call? **Optimization**: Eliminates unnecessary stack frame and call overhead.

But for decompilation, it obscures boundaries. That's why tools must look for:
- `b` instructions to non-local labels
- Functions ending without `blr`
- Prologues that don't match expected start patterns

dtk does this. But edge cases exist where the `b` target is also a tail call (chains). Manual intervention needed.

---

## 📚 Further Reading

- [decomp-toolkit Boundary Analysis](https://github.com/encounter/decomp-toolkit#function-boundaries) - Tool docs
- [Metrowerks Optimization Guide](https://archive.org/details/MetrowerksCodeWarriorOptimization) - Why/when tail calls happen
- [PowerPC Calling Convention](https://openpowerfoundation.org/wp-content/uploads/2016/07/ABI64BitOpenPOWERv1.1_16July2015_pub4.pdf) - Tail call ABI details

---

*Next guide: [Symbol Resolution](symbols.md) - Finding function names and data labels*

*Tail calls: they seem helpful, but for decompilation they're the assassin that makes you question reality.* (╯°□°)╯