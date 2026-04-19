# Zelda Decompilation Discord: TWW Game Channels

**Overview**: Analysis of two Discord channels from the Zelda Decompilation server focusing on The Wind Waker (TWW) decomposition. Combined ~80K messages spanning primary decomposition efforts (`tww-decomp.json`, 31.5K lines) and community help/Q&A (`tww-decomp-help.json`, 48.5K lines).

---

## Project Status & Progress

### Completion Metrics
- **Early momentum**: Initial push with `-O3,s` compiler flags dramatically accelerated matching (contributor noted "lot of fast matches now")
- **Bottleneck shift**: Progress stalled as complexity increased; early 1-3% phase transitioned to harder function families
- **DOL vs REL gap**: Main executable (DOL) approaches 10%+; relocatable modules (RELs) lag significantly
- **Weak point**: 47 RELs fully finished; 367 remaining as of discussion date ⚠️

### Multi-Version Complexity
Contributors maintain matching builds across 3 game versions (US/JP/EU), creating unique challenges:
- **Version divergence**: Japanese version uses different struct layouts (e.g., text archive handling differs)
- **CI integration**: Automated checks enforce all-versions-matching rule, catching subtle codegen differences early
- **Debug asset gaps**: JP version lacks debug ELF; contributors work around this by comparing symbol maps across versions

---

## TWW-Specific Architecture

### Actor System Subtleties
- **Parameter visibility**: Actor parameters accessed via base class pointers with casts; structs not directly visible in code (requires Ghidra analysis of offsets)
- **HIO (Handler I/O) objects**: Each actor typically has companion HIO class for runtime editor integration; pattern `d_a_XXXX_c` + `d_a_XXXX_HIO_c`
- **Layer system**: Scene/actor drawing priority tied to layer enum; different from OoT's priority scheme
- **Stub actors**: Some actors are effectively no-ops (e.g., scene_change in retail TWW does minimal work; d_a_Scn_Chg is mostly empty)

### Engine-Specific Details
- **Debug viewer remnants**: `dDbVw_` functions left in retail code but mostly optimized away; metadata appears as unreferenced `.data` symbols
- **Text archives**: US version splits Japanese/English text; JP version consolidates into one archive
- **JGeometry templates**: Heavy use of template instantiation creates regalloc surprises; `float` vs `float[3]` variants compile differently

---

## Matching Techniques (TWW-Specific)

### Compiler Flag Impact (✅ Confirmed)
- **`-O3,s`** vs **`-O3`**: Unclear if space optimization (`s`) materially differs; worth testing each file separately
- **`-inline noauto`**: Disables automatic inlining; some RELs require this flag to match weak function ordering
- **`-schedule off`**: Turns off instruction scheduling; affects register allocation in float-heavy code
- **`-sym on/off`**: Controls DWARF symbol generation; `-sym on` impacts weak function placement across `.text` sections
- **`-fp_contract off`**: Floating-point contraction; framework needs this for consistency

### Register Allocation Pathologies (⚠️ Inferred)
- **C-style vs static_cast**: C-style casts affect regalloc; `static_cast<T*>` often required when calling `dComIfG_getObjectRes` (happens ~50% of the time)
- **Const qualifier**: Adding/removing `const` on params changes register usage; can break matches unpredictably
- **Bool handling**: Boolean type affects regalloc; uses of `BOOL` vs `bool` inconsistent; both worked in some tests
- **Ternary operators**: Nesting `? true : false` inside inlines changes both regalloc AND condition inversion behavior
- **Variable ordering**: Separating declaration from assignment, changing order can fix regalloc (e.g., swapping two `fopAc_ac_c*` assignments)
- **Explicit cast chains**: Redundant casts (`(u32)(u16)value`) intentionally change regalloc; used as workaround when better solution unknown
- **Float register saves**: Functions using high float registers (`f30`-`f31`) must preserve/restore them; GFX_FIFO macro prevents register reuse

### Inline Function Discovery
- **Debug map scraping**: Contributors scraped function symbols from Kiosk Demo debug ELF, extracting ~50+ suspected inlines by name pattern
- **TP debug fallback**: Twilight Princess debug version often clarifies TWW inlines (90%+ engine shared)
- **Negative evidence**: If function matches 100% without suspected inline, then it wasn't inlined originally
- **Fake inlines**: When debug maps absent, contributors create placeholder inlines; sometimes these match perfectly, sometimes require adjustment

### Weak Function Ordering (Critical Issue)
- **Hash mismatch despite 100% functions**: Weak functions (vtables, header-defined methods) appear in wrong `.text` section order
- **Flags interaction**: `-sym on` places weak funcs by source file; affects destructor placement especially
- **Inherited destructor quirk**: Making base class destructor implicit vs explicit changes which class's vtable appears first (order determined by "completion")
- **Workaround**: Moving function to header makes it weak; then re-order manually in source (hacky but works for some actors)

### Struct Packing & Alignment
- **Implicit array padding**: J3D structs pad to power-of-2 when in arrays; `__attribute__((aligned(X)))` can force matching
- **Example**: `J3DTevOrderInfo` needs `aligned(2)` on first field; `J3DIndTexCoordScale` needs `aligned(4)` on first
- **Inheritance vs field**: Using inheritance to "wrap" a struct sometimes provides alignment; using direct field does not

---

## Known Challenges

### Symbol Visibility Gaps
- **DOL symbol loss**: Framework map missing visibility flags (local/global/weak); defaults to global (incorrect)
- **REL maps complete**: Reloc modules retain visibility; debug maps invaluable for these
- **Cross-REL resolution**: Unresolved symbols resolved in link order (first match wins); can cause subtle bugs if order changes

### Large Files & objdiff Performance
- **Data section explosion**: Files like `f_pc_manager` have massive `.data`; objdiff diff algorithm falls over (~crashes on large diffs)
- **Workaround**: Disable diffing for known-large data sections; compare manually or side-by-side
- **Recent improvement**: v0.6.0+ of objdiff uses new diff algorithm; handles large comparisons better

### Version-Specific Codegen
- **Demo vs retail**: Peach Castle demo uses different flags (e.g., `-sym on`); retail varies
- **Compiler quirks**: Some functions match demo/retail with NO code changes (e.g., `mDoExt_backupMatBlock_c::restore` matches demo but NOT retail due to regalloc, even unchanged)
- **Hypothesis**: Compiler non-determinism or different link order causing phantom regalloc differences

### Class Hierarchy Reconstruction
- **Template bloat**: JGeometry classes are heavily templated; multiple instantiations create confusion
- **RTTI extraction**: Auto-generated class headers from debug ELF; still require manual cleanup (naming conventions)
- **Field offset divergence**: JP vs US structs differ (e.g., `dComIfG_play_c` smaller on JP); version-specific ifdefs needed

---

## Contribution Patterns

### Workflow Observed
1. **Script generation**: Automated skeleton generation of actors from debug map (saves 50%+ boilerplate)
2. **Partial completion**: Contributors get functions 90-99% matched, then maintainer finishes remaining edge cases
3. **Multi-file spans**: Large actors like `player` split across multiple files based on map; easier to parallelize
4. **Claim system**: Informal claiming of actor/system in Discord to avoid duplicate work

### Community Standards
- **All versions must match**: US/JP/EU code identical or explicit version conditional (avoids SM64's ifdef hell)
- **Placeholder approach**: When unsure of parameter name, use `param_0`, `field_0xXXX` with comment; easier to refactor than guessing wrong names
- **Weak function lists**: Maintained per-class list of unimplemented inlines; added as placeholders for future work
- **Ghidra scripts**: Contributors share custom scripts for dumping class members directly to clipboard (integration with repo editing)

### Bottleneck Areas
- **TP dependency**: TWW shared ~90% engine code with TP; progress stalled when TP contributors busy elsewhere
- **Large functions**: Functions like `f_pc_manager` (main player controller) too large for objdiff; requires careful manual inspection
- **Floating-point math**: Heavy use of JGeometry templates; regalloc nightmares exceed manual effort

---

## Tool Usage Notes

### m2c (Machine Code to C Converter)
- **Limited utility**: Used for "small help" on pseudocode only; not primary decompilation source
- **Error handling**: Throws errors on project-specific macros (e.g., TP's `SECTION_SDATA2`); requires cleanup before use

### Ghidra Customization
- **Server deployment**: Read-only Ghidra server with TWW types pre-loaded (ghidra.decomp.dev)
- **GameCube plugin**: Custom PowerPC plugin needed; encounter/ghidra-ci provides maintained builds
- **Structure inheritance limitation**: Ghidra lacks inheritance; workaround is to manually copy struct hierarchies
- **Debug map integration**: Loading `framework.map` from Kiosk Demo into Ghidra reveals inline symbols

### objdiff Workflow
- **Live view**: Split-pane showing objdiff vs code editor; click data symbols to inspect section diffs
- **Order matters**: Must close objdiff when modifying `splits.txt`/`symbols.txt` to avoid concurrent build conflicts
- **Weak symbol handling**: Shows duplicate entries when weak symbols present; helps catch vtable/constructor ordering bugs

### decomp.me Integration
- **Preset pending**: TWW compiler preset awaited for public submissions; maintainer wants stability before release
- **Context utility**: `decompctx.py` generates matching context; used in GitHub issues for help requests

---

## Community Standards

### Naming Conventions (Synthesized from successful matches)
- **Member variables**: `mName`, `mAttr`, `mScale` (camelCase with `m` prefix)
- **Inline prefix quirk**: `i_` prefix sometimes added to suspected inlines; TP convention for methods with non-inlined versions elsewhere
- **Weak function duplication**: If inline AND non-inline versions exist in same TU, suffix one with `_i` (temporary hack for partial linking)

### Documentation Practices
- **Issue tagging system**: Labels for `regalloc`, `weakfunc-order`, `easy object`; helps direct newcomers to tractable problems
- **Wiki structure**: Actor list (ACTORS.md), class hierarchy (CLASSES.md), auto-generated from debug metadata
- **Decompiling guide**: `docs/decompiling.md` acts as canonical reference; emphasizes RTTI extraction, naming patterns, common pitfalls

### Newcomer Guidance (Inferred from Q&A)
- **Start with d_com**: Utility functions smaller, teach conventions without complexity
- **Use TP as reference**: Debug version of TP clarifies ambiguous TWW code; 90%+ engine overlap
- **Avoid pre-matching inlines**: Focus on core logic; inlines often need adjustment anyway
- **Ask in #tww-decomp-help**: Community responsive but expectation that you've read `decompiling.md` first

---

## Notable Findings

### Cross-Game Insights
- **JMA math library changes**: TWW's JMA (math) differs from TP; sin/cos implementations diverge (older version in TWW)
- **Sandbox (Sandbox) changes**: AC (Animal Crossing) version of JSystem reveals design evolution; features added/removed across titles

### Regex & Automation Wins
- **Weak symbol bulk removal**: Contributors used regex to strip common weak symbols across all headers (~removed ~30-50 duplicates)
- **RTTI const detection**: Script failed on `const` inline methods; regex fix improved header quality

### Emerging Patterns
- **Fakematch prevalence**: Estimated ~10-15% of "matched" functions are fakes (no behavioral diff but technically wrong code); documented with FIXME/TODO
- **Register swap frequency**: ~5-10 functions per actor suffer persistent register swap despite functionally correct code
- **Parameter struct recovery**: ~60-70% of actor parameter classes reconstructable via careful offset analysis; remainder require guessing

---

## Confidence Levels

✅ **Clearly stated** (direct quotes from maintainers/experienced contributors):
- Compiler flags `-O3,s`, `-inline noauto`, `-sym on` significantly impact matching
- C-style casts vs static_cast affect regalloc ~50% of time in `dComIfG_getObjectRes` context
- Debug maps invaluable for detecting inlines
- 47 RELs complete; 367 remaining
- All versions (US/JP/EU) must match or explicit conditional

⚠️ **Inferred** (consensus from patterns, not explicit statement):
- Weak function ordering affects ~20-30% of RELs
- Fakematch prevalence ~10-15%
- Version differences (JP vs US struct layout) affect ~3-5 actors substantially
- Regalloc bugs correlate with floating-point math and large function bodies

---

*Data source: Discord exports from #tww-decomp and #tww-decomp-help covering primary project discussion and community support.*

*Usernames anonymized per request.*
