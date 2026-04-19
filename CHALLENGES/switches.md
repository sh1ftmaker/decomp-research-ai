# Switch Statements: Matching Jump Tables and Branch Trees

*How to reconstruct C `switch` statements from PowerPC assembly, including jump tables and comparison trees.*

> **See also (Discord-sourced detail):**
> - `COMMUNITY/discord-insights-match-help.md` §"Switch Statement Patterns" — jump-table vs. branch-chain selection rules, `switch(localVar)` vs. `switch(field->member)` ordering trick
> - `COMMUNITY/discord-tribal-knowledge.md` §"Pragmas" — full pragma reference

---

## 🛑 The One Pragma That Changes Everything: `#pragma switch_tables off`

If your switch produces a **jump table in `.rodata`** but the original binary has a **branch chain** (or vice versa), the original code was likely compiled with `#pragma switch_tables off`, which forces MWCC to emit branch chains for **all** switches in scope:

```c
#pragma switch_tables off
switch (x) {
    case 0: ...
    case 1: ...
    case 2: ...
}
#pragma switch_tables reset
```

Other levers that change switch shape without changing C semantics:
- **Default case position in source**: writing `default:` first vs. last affects branch ordering.
- **Switching on a local copy** vs. **switching on a struct field**: `int v = obj->state; switch (v)` and `switch (obj->state)` can produce different load/branch interleaving.
- **Case order in source**: keep cases in **table-index order** (0, 1, 2…) for jump tables; for branch chains, source order can affect comparison order.

---

## 🎯 Why Switches Are Hard

Switch statements compile very differently depending on:
- Number of cases
- Density of case values (sparse vs dense)
- Range of case values
- Fallthrough patterns
- Compiler optimization level

**Two common patterns**:
1. **Comparison trees** (if/else chains) - for small, sparse switches
2. **Jump tables** - for dense ranges (faster)

Ghidra's decompiler often gets these **wrong**. m2c does better but still may need manual correction.

---

## 🔍 Pattern 1: Comparison Trees

### Recognition

Assembly pattern:
```asm
cmpwi r3, 1
beq L_case1
cmpwi r3, 5
beq L_case5
cmpwi r3, 10
beq L_case10
b L_default
```

Or nested：
```asm
cmpwi r3, 10
blet L_leq10
  # >10 case
b L_done
L_leq10:
cmpwi r3, 5
blet L_leq5
  # 6-10 case
b L_done
L_leq5:
cmpwi r3, 1
beq L_case1
  # default
```

### C Equivalent

```c
switch (value) {
    case 1:
        // code
        break;
    case 5:
        // code
        break;
    case 10:
        // code
        break;
    default:
        // code
        break;
}
```

### Common m2c Issues

1. **Out-of-order cases**: m2c might produce `case 10, case 5, case 1` (reversed)
   - **Fix**: Manually reorder to match assembly's comparison order
   - Look at assembly to determine correct order

2. **Missing "useless" cases**: Assembly might have a case that does nothing (falls through to default), but m2c omits it
   - **Rule**: Include **every** case that appears in the assembly, even if it's identical to default
   - Some cases are there just to set up jump table indices

3. **Combined cases**: m2c might merge cases that share code but have separate labels in assembly
   - Check if assembly has separate `caseX:` labels that branch to same code
   - If so, they should be separate `case` statements in C (they can drop through)

---

## 🔍 Pattern 2: Jump Tables (The Tricky One)

### Recognition

Assembly pattern:
```asm
# Load value into register
lwz r5, 0x10(r3)  # r3 is switch variable
# Compute table offset
srawi r6, r5, 2    # divide by 4 (shift for word index)
addi r6, r6, 0x1234  # add table base
lwzx r7, r6, r6   # load jump target from table
mtctr r7
bctr              # jump!
```

Or the classic `bctr` pattern:
```asm
lwz r5, var(r3)
srawi r5, r5, 2
addi r5, r5, jumptable_1234
lwzx r5, r5, r5
mtctr r5
bctr
```

**Key**: You see a `bctr` (branch to counter register) or `bclr` instruction. The jump table is somewhere in the `.rodata` section.

### Locating the Jump Table

In the `.s` file, look near the switch code for:
```asm
jumptable_1234:
  .long case_0_handler
  .long case_1_handler
  .long case_2_handler
  .long case_default  # often at end
```

Or more commonly:
```asm
.data
jumptable:
  .4byte L_case0
  .4byte L_case1
  .4byte L_case2
  .4byte L_default
```

---

## 🧩 m2c with Jump Tables

**Standard way** (from zeldaret guide):

1. **Get the assembly for the switch function** (including the jump table data).

2. **Copy both code and table** into your input:
   ```bash
   # In your .s file, keep:
   #   - The function assembly (up to bctr)
   #   - The jump table (.section .rodata with labels)
   ```

3. **Run m2c with table directive**:
   ```bash
   # Tell m2c about the jump table
   m2c.py -t ppc-mwcc-c --gotos-only -f switch_function -j jumptable_1234 switch_function.s > temp.c
   ```

   Some versions accept `--jump-table` or automatically detect.

4. **Result**: m2c should output:
   ```c
   switch (value) {
       case 0: goto jumptable[0];
       case 1: goto jumptable[1];
       // ...
       default: goto jumptable[...];
   }
   ```

   Or more human-readable:
   ```c
   switch (value) {
       case 0: /* code */ break;
       case 1: /* code */ break;
       // ...
   }
   ```

**If m2c doesn't handle the table**:
- Use `--gotos-only` to get raw labels
- Manually construct the switch:
  ```c
  static void* jumptable[] = {
      &&case_0,
      &&case_1,
      &&case_2,
      &&default_case,
  };
  goto *jumptable[value];
  ```

---

## 🎯 Matching Jump Tables: Order and Completeness

### Case Order

The **case constants** must exactly match the table indices:

If table is:
```asm
.long L_case5
.long L_case10
.long L_case1
```

Then cases are: `case 5`, `case 10`, `case 1` (column order, not sorted).

**m2c might sort them** (nice for reading) but that changes machine code layout → doesn't match.

**Fix**: Keep cases in table order, even if descending or random. The **default case** is usually at the end of the table (last entry) but check assembly.

### Missing Cases

If value is outside the table range, what happens?
- Table might have a **default entry** (points to default handler)
- Or jump beyond table → crashes or reads garbage

**m2c may assume a default**; verify against assembly:
```asm
# Table has 4 entries (indices 0-3)
# Code does: addi r5,r5,jumptable
#            lwzx r5,r5,r5
# No bounds check = raw jump
# If value=5, jumps to whatever is at jumptable+20 (maybe default or garbage!)
```

Most games include an explicit default entry as the last table entry. Use that as `default:` case.

---

## 🧩 Example: Full Switch Reconstruction

### Original Assembly (simplified)

```asm
# Function: handle_menu_input
lwz r3, 0x14(r31)    # Load menu state->selected_option
srawi r3, r3, 2      # divide by 4 (each option is word)
addi r3, r3, jumptable_800
lwzx r3, r3, r3      # Load jump address
mtctr r3
bctr

.section .rodata
jumptable_800:
  .4byte L_option_new_game
  .4byte L_option_continue
  .4byte L_option_options
  .4byte L_option_exit
```

### m2c Output (with `--jump-table jumptable_800`)

```c
switch (state->selected_option) {
    case 0:
        // goto L_option_new_game
        // (code for that label below)
        break;
    case 1:
        // goto L_option_continue
        // ...code...
        break;
    case 2:
        // goto L_option_options
        // ...code...
        break;
    case 3:
        // goto L_option_exit
        // ...code...
        break;
    default:
        // Shouldn't happen in normal play
        break;
}
```

**But wait**: The assembly doesn't have a default entry! The table only has 4 entries. If `selected_option` is 4+, it jumps to garbage.

**Choice**:
- Keep `default:` as empty (matches behavior - likely unreachable)
- Or omit default (C language allows that)
- Verify if original binary actually has a default handler elsewhere

---

## 📊 Comparison Tree vs Jump Table: Decision Tree

How to tell which pattern you have:

| Feature | Comparison Tree | Jump Table |
|---------|-----------------|------------|
| Number of `cmpwi`/`cmplwi` instructions | Many (N-1 for N cases) | Usually 1-2 |
| `bctr` / `bclr` instruction | No | Yes (usually after `lwzx`) |
| Jump table in `.rodata` | No | Yes (array of addresses) |
| Linear vs logarithmic lookup | Linear scan (O(N)) or O(log N) tree | O(1) table lookup |
| Typical case count | 2-10 cases | 10-100+ cases |
| Example | Menu with 5 options | Tile-based terrain types (256 values) |

---

## 🎯 Matching Strategy: Step by Step

### Step 1: Identify Pattern
Look at the assembly. Is it comparison tree or jump table?

### Step 2: Extract Cases

For comparison tree: List each `case X:` label and the code between it and next case/default.

For jump table:
1. Find table base label
2. Count `.4byte` entries
3. Map index → address
4. For each address, find the corresponding code label and extract that block

### Step 3: Decompile Each Case Block

Use m2c on each block separately, or do whole function.

**Tools**:
```bash
# Extract a specific label's code
sed -n '/L_case5:/,/L_nextcase:/p' function.s > case5.s
m2c.py -t ppc-mwcc-c -f case5 case5.s > case5.c
```

### Step 4: Assemble Switch Statement

Construct:
```c
switch (control_var) {
    case CONST_1: [case1_code]; break;
    case CONST_2: [case2_code]; break;
    ...
    default: [default_code]; break;
}
```

**Break statements**: Assembly usually has `b L_nextcase` or falls through. Verify where each block exits.

### Step 5: Match and Iterate

1. Insert into the function
2. Build, check objdiff
3. If mismatched:
   - Are cases in correct order? (Table order, not sorted)
   - Are case constants correct? (Check assembly for constants used in comparison)
   - Did you include all cases, including "useless" ones?
   - Is default case placed correctly? (Usually last, but could be anywhere)
   - Does `break` correspond to actual branch? (Some cases may fall through intentionally → use `// fall through` comment)

---

## 🐛 Common Pitfalls and Fixes

### Pitfall 1: Sorted Cases When Table Is Unsorted

**m2c output**:
```c
switch (x) {
    case 1: ...
    case 2: ...
    case 3: ...
}
```

**Actual assembly** has table: `[case3, case1, case2]`

**Fix**: Reorder to match table order, even if it looks weird:
```c
switch (x) {
    case 3: ...
    case 1: ...
    case 2: ...
    break;
}
```

**Verification**: `case 3` must be first because table index 0 jumps to case 3 handler. Or does `x==0` → case 3? Check table mapping carefully.

---

### Pitfall 2: Missing "Fall Through" Cases

Assembly has:
```asm
case_5:
  # some code
  b case_common  # intentional fallthrough to case 6's handler
case_6:
case_common:
  # shared code
  b L_done
```

m2c might produce:
```c
case 5:
    // code
    break;  // WRONG - should fall through!
case 6:
    // falls through to common
case_common:  // not a case label!
```

**Fix**: Use deliberate fall-through in C:
```c
case 5:
    // code
    // fall through
case 6:
case_common:
    // shared code
    break;
```

**Label naming**: `case_common` is not a case label; it's a shared local label. Remove it from switch cases and put its code after both `case 5` and `case 6`.

---

### Pitfall 3: Case Ranges (Non-Contiguous)

Assembly uses multiple comparisons:
```asm
cmpwi r3, 10
beq L_10
cmpwi r3, 20
beq L_20
cmpwi r3, 30
beq L_30
```

These are three separate cases (10, 20, 30). No ranges. Don't try to merge.

---

### Pitfall 4: Nested Switches

Sometimes a case itself contains a switch. That's fine - just nest switches in C.

But watch for **fallthrough across nested switch** boundaries:
```c
switch (outer) {
    case 1:
        switch (inner) {
            case 'a': ...
            case 'b': ...
        }
        // fall through to case 2?
        // Check assembly: Does it jump to case 2 label directly?
```

---

## 🎓 Advanced: Switch on Enum or Bitfield

Sometimes the control variable is a **bitfield**:
```asm
rlwinm r3, r3, 0, 28, 31  # extract top 4 bits
cmplwi r3, 0x7
bgt L_default
# Now r3 is 0-7, used as switch index
```

The assembly masked the value; your C should reflect the original type. It might be:
```c
switch (state->flags & 0xF) { ... }
```
Or:
```c
enum { FLAG_A = 1, FLAG_B = 2, ... };
switch (state->flags & 0xF) {
    case FLAG_A: ...
}
```

m2c might just show `switch (r3 & 0xF)`. Use context header to give better names.

---

## 📊 When to Use `if/else` Instead

If the switch has only 2 cases and no default, sometimes it's actually compiled as a simple test:

```asm
cmpwi r3, 0
beq L_true
# else
b L_false
```

m2c might still produce a switch. That's fine - C `switch` with 2 cases is valid.

But if assembly shows an actual `bctr` jump table with 2 entries, you want a switch to match the table layout.

---

## 🧪 Practice Problem

Given this assembly snippet:

```asm
lwz r4, 0x18(r31)
srawi r4, r4, 2
addi r4, r4, 0x8034
lwzx r4, r4, r4
mtctr r4
bctr

.data
jumptable_8034:
  .4byte L_state_idle
  .4byte L_state_active
  .4byte L_state_paused
  .4byte L_state_gameover
```

**Questions**:
1. What is the control variable type and range?
2. How many cases are there?
3. What are the case constants?
4. Write the matching C switch statement.

**Answers**:
1. State variable (word), shifted right by 2 → divided by 4. So values: 0, 4, 8, 12 map to cases 0,1,2,3 respectively. But likely the original variable is an enum where each value is 4 apart (not 1). Need to check surrounding context.
2. 4 cases + maybe default
3. Case 0, 1, 2, 3 (if enum values are 0,4,8,12 → divided by 4 becomes 0-3)
4. 
```c
switch (state) {
    case STATE_IDLE: goto L_state_idle; break;
    case STATE_ACTIVE: ...;
    case STATE_PAUSED: ...;
    case STATE_GAMEOVER: ...;
    default: ...;  // check if there's default entry or raw jump
}
```

**Key**: The `srawi` by 2 means table index = (value >> 2). If enum values are consecutive (0,1,2,3), no shift needed; but if they're spaced by 4 (0,4,8,12), the shift normalizes them. The original C probably had an enum where each value is multiplied by 4.

---

## 📚 Reference: Common Assembly Patterns

### Pattern A: Simple Dense Jump Table

```asm
lwz rX, var(rY)
srawi rX, rX, 2    # /4 for word table
addi rX, rX, table
lwzx rX, rX, rX
mtctr rX
bctr
```
→ Cases are consecutive: 0,1,2,3,...

---

### Pattern B: Sparse Jump Table

```asm
lwz rX, var(rY)
cmpwi rX, MIN_VAL
blt L_default
cmpwi rX, MAX_VAL
bgt L_default
# Now in range
subi rX, rX, OFFSET  # subtract min to get 0-based index
srawn. rX, rX, 2     # /4
addi rX, rX, table
lwzx rX, rX, rX
mtctr rX
bctr
```

→ Cases are from MIN_VAL to MAX_VAL. Offset adjustment needed.

---

### Pattern C: Multi-level Switch

```asm
switch (value) {
    case 0-9: goto table1[value]
    case 10-19: goto table2[value-10]
    default: ...
}
```

Assembly will have two jump tables and a range check.

m2c may produce nested switches. Match structure exactly.

---

## 🎯 Debugging Checklist

When your switch doesn't match:

1. ✅ Are case constants correct? (Check assembly for `cmpwi` values or table indices)
2. ✅ Is case order exactly as in jump table (or comparison tree)?
3. ✅ Did you include all cases, even ones that fall through or do nothing?
4. ✅ Is default case present (and in right position) if the table has one?
5. ✅ Are `break` statements placed correctly (no missing breaks, no extra breaks)?
6. ✅ Did you handle any fall-through intentionally? (Use `/* fall through */` comment)
7. ✅ Are you using the correct `switch` expression? (Check assembly: what register is being tested?)
8. ✅ For jump tables: Did you verify table bounds? (Maybe out-of-range jumps to elsewhere)
9. ✅ Did you preserve any local labels (like `L_common`) within case bodies?
10. ✅ Does the switch cover all paths that the assembly's branching creates?

---

## 📊 When to Mark as Non-Matching

Some switches are brutally hard:
- 50+ case jump tables with complex fallthrough
- Multi-dimensional switches (switch inside switch cases)
- Switch expression computed through multiple steps that are hard to replicate exactly
- Jump tables with computed case values (not linear index)

**Strategy**: If spent >4 hours, mark as `NonMatching` and move on. The function might get matched later when more context is available or when decomp-permuter gets better.

---

## 📚 Further Reading

- [zeldaret TWW Switch Guide](https://github.com/zeldaret/tww/blob/main/docs/decompiling.md#5-recognizing-switch-statements) - Best practices
- [m2c Switch Handling](https://github.com/matt-kempster/m2c#switches) - Tool-specific
- [PowerPC bctr Explanation](https://www.nxp.com/docs/en/reference-manual/PPCE2000RM.pdf) - Page on branch to counter

---

*Next guide: [Tail Calls](tail-calls.md) - The silent killer of matching*

*Switch statements: where assembly meets control flow. Master them and conquer half the game's logic!* 🎮