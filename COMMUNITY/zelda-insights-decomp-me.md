# Zelda Decompilation Discord: #decomp-me Channel

**Overview**: Analysis of the `#decomp-me` channel (~8,300 messages, 2021–2022). Documents the entire design, architecture, and development process of decomp.me — the online collaborative decompilation platform that lets contributors work on matching functions in a browser without local toolchain setup.

---

## Origin & Motivation

- Conceived mid-2021 by the OoT decomp community
- Core insight: most new contributors struggle with local toolchain setup; a browser-based scratchpad dramatically lowers onboarding friction
- Inspired by Compiler Explorer (godbolt.org) but purpose-built for matching decompilation
- Name "decomp.me" chosen by founder; "scratchpad" terminology used throughout early development
- Initial team: ~5-7 contributors with mixed frontend/backend experience

---

## Architecture Decisions

### Technology Stack (Final)
- **Backend**: Django (Python) + PostgreSQL
- **Frontend**: React with Monaco editor (same as VS Code's editor)
- **Diff engine**: `diff.py` (asm-differ) running server-side
- **Compiler sandboxing**: nsjail (same as Compiler Explorer), later evaluated
- **Compiler distribution**: Docker images per compiler; IDO via `simonlindholm:ido` image

### Key Design Debates

**ASM input format**: Whether users should paste raw text asm or upload `.o` files
- Consensus: text asm (objdump output) for MVP; `.o` files considered for forward compatibility
- `--write-asm` helper flag added to diff.py: runs objdump equivalent, outputs copyable text
- Target asm stored server-side; re-assembled via original assembler to produce `.o` for diffing

**Scratch vs. scratchpad-less mode**: 
- "Scratch" = a saved session with slug, C code, target asm, compiled asm
- Scratchless mode: just compile and view asm output, no persistence
- Both modes supported; PATCH for saves, compile-only endpoint for live typing

**Context files**:
- Context holds struct definitions, prototypes needed to compile the function
- Stored separately from C code in database; collapsible UI pane
- Problem: context changes when struct names/signatures are renamed — no automatic sync with repo
- Compromise: users manage context manually; `m2ctx.py` / `decompctx.py` tools generate it from project source

**Compiler configuration**:
- Initially dropdown of presets; presets added per project/game as maintainers stabilize their flags
- `compile_script`: a shell command template using `$INPUT`/`$OUTPUT` env vars
- Example: `tools/gcc/cc1 -O2 "$INPUT" | tools/gcc/as -o "$OUTPUT"`
- Multiple-binary compilers (IDO: `cfe` → `uopt` → `as1`) expressed as chained commands

### Database Schema (Early Design)
```python
class Compiler(models.Model):
    shortname = CharField(primary_key=True)
    name = CharField()

class Assembly(models.Model):
    hash = CharField(primary_key=True)  # sha256 of asm text
    data = TextField()

class Scratch(models.Model):
    slug = ...
    c_code = ...
    target_asm = ...  # FK to Assembly
    compiled_asm = ...  # updated per compile
    compiler = ...  # FK to Compiler
```

---

## Compiler Sandboxing

- **nsjail**: Linux seccomp-based sandbox; same tool Compiler Explorer uses
- Initial MVP: ran compiler directly without sandboxing ("good faith" assumption)
- Security concern acknowledged: nothing to gain from hacking a decomp site, but still needed
- Docker isolation used as primary layer; nsjail as inner layer
- Filesystem: compiler binaries mounted into container rather than baked into image (faster dev iteration)
- IDO compiler: distributed via `permuter@home` Docker image or per-project tools directory

---

## diff.py Integration

- `diff.py` runs as a subprocess or local HTTP server (`--web` mode rewrite in progress during development)
- Register coloring, branch annotation, and levenshtein matching all available on the site
- Target asm sent with every compile request (not cached long-term in early design)
- `.o` files either stored in DB and re-objdumped per diff, or objdump output stored directly
- Score and diff both returned to client; client renders via Monaco diff pane

---

## Milestone 1 (Scratchpad MVP)

### Scope
- Single-function scratchpad with target asm input
- Live compilation on keystroke (debounced)
- Diff view with register coloring
- Save/load via slug URL
- Basic compiler preset selector

### Timeline Pressures
- Milestone 1 deadline set ~2 weeks from planning; shipped approximately on time
- "Even if every part is ripped out, at least we have parts we can rip out" — pragmatic early approach
- SQLite acceptable for MVP; PostgreSQL required for production scale

### Technical Debt Accepted at Launch
- No mobile support (layout not designed for small screens)
- No function search or browsing
- No project integration (no automatic PR generation)
- No symbol renaming support
- Rodata/strings not diffed initially

---

## Post-MVP Expansion

### Project Support
- Projects created by maintainers; functions "pushed" to site (not auto-pulled from repos)
- Partial matches tracked on site separately from project repo state
- PR integration: maintainers manually merge matched functions (or with comment crediting the matcher)
- Claim system: informal; function pages show who is working on a scratch

### Multi-Platform Support (2022)
- **GBA support** added and announced as beta 2022-01-01
- **DS support** added simultaneously (beta)
- Both had known instability at launch; community feedback requested

### Compiler Catalog Growth
- GC/Wii MWCC compilers added after initial N64/IDO focus
- Each new compiler requires: Docker image or binary, `compile_script` template, preset flags
- TWW preset held back intentionally: maintainer wanted project to stabilize before public access

---

## Community Impact

### Adoption Pattern
- Contributors new to decomp could submit a function match before ever running a local build
- Dramatically reduced "first match" time for newcomers
- Experienced contributors used it for hard functions where context needs to be narrowed (iterating faster than local build)
- Some maintainers concerned about context drift (site context out of sync with repo headers)

### Limitations Acknowledged
- Score of 0 doesn't guarantee a clean match (symbol differences, section ordering not checked)
- Functions with GFX macros, audio DSP, or game-specific custom types need significant context engineering
- No way to share or fork a scratch in early versions

---

## Confidence Levels

✅ **Confirmed** (from founders and primary contributors):
- nsjail sandboxing approach
- Django + React + PostgreSQL tech stack
- `compile_script` template model for compiler integration
- GBA/DS support launched 2022 as beta

⚠️ **Inferred** (from conversation patterns):
- TWW preset delay: awaiting project stability
- ~50% of early scratchpad usage was for functions already partially worked on locally

---

*Source: Discord exports from #decomp-me (Zelda Decompilation server), ~8,300 messages, 2021–2022. All usernames anonymized.*
