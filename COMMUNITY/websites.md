# Community Resources: Websites, Discords, and Collaboration

*Where to find information, ask questions, and collaborate on GameCube/Wii decompilation. Note: Discord content is currently inaccessible for bulk extraction.*

---

## 🌐 Essential Websites

### Primary Hubs

| Site | Purpose | URL |
|------|---------|-----|
| **decomp.dev** | Central aggregator for all active decompilation projects | https://decomp.dev |
| **decomp.me** | Collaborative scratch platform for tackling hard functions | https://decomp.me |
| **doldecomp GitHub** | Home of major projects (Melee, Sunshine, TTYD) | https://github.com/doldecomp |
| **zeldaret GitHub** | Zelda decompilations (TP, TWW, SS, OoT) | https://github.com/zeldaret |
| **PrimeDecomp GitHub** | Metroid Prime series | https://github.com/PrimeDecomp |

---

### Documentation & Wiki

| Resource | Content | URL |
|-----------|---------|-----|
| **decomp-toolkit README** | dtk usage, installation, examples | https://github.com/encounter/decomp-toolkit |
| **objdiff docs** | Matching tool guide, troubleshooting | https://github.com/encounter/objdiff |
| **m2c documentation** | Decompiler usage, options, targets | https://github.com/matt-kempster/m2c |
| **zeldaret TWW Wiki** | Best-in-class tutorials, architecture deep-dives | https://github.com/zeldaret/tww/blob/main/docs/ |
| **sdbg/dolphin wiki** | Dolphin emulator internals, debugging | https://github.com/sdbg/dolphin/wiki |
| **Melee Decomp Discord** | Community hub (invite in README) | — |
| **doldecomp Discord** | General GC/Wii decomp (invite in README) | — |

---

### Type Archives & SDKs

| Resource | What It Provides | URL |
|----------|------------------|-----|
| **doldecomp/sdk-dolphin** | Dolphin SDK headers, function stubs | https://github.com/doldecomp/sdk-dolphin |
| **doldecomp/sdk-JSystem** | JSystem library (Nintendo engine) | https://github.com/doldecomp/sdk-JSystem |
| **zeldaret/common** | Shared types, RTTI, structs for Zelda games | https://github.com/zeldaret/common |
| **dolphin-source** | Original Dolphin SDK source (limited) | https://github.com/dolphin-emu/dolphin/tree/master/Source |

---

### Tools & Releases

| Tool | Platform | URL |
|------|----------|-----|
| **decomp-toolkit (dtk)** | Windows/macOS/Linux | https://github.com/encounter/decomp-toolkit/releases |
| **objdiff** | Windows/macOS/Linux | https://github.com/encounter/objdiff/releases |
| **m2c** | Python (any) | https://github.com/matt-kempster/m2c |
| **wibo** | Linux (Wine alternative) | https://github.com/decompals/wibo |
| **Ghidra (community fork)** | Cross-platform | https://github.com/encounter/ghidra-ci/releases |
| **Ghidra (mainline)** | Cross-platform | https://ghidra-sre.org/ |
| **gc-wii-binutils** | Cross-platform | https://github.com/encounter/gc-wii-binutils |
| **cwparse** | Rust library | CW map file parsing with Python bindings planned |
| **Dolphin Emulator** | Cross-platform | https://dolphin-emu.org/ |
| **decomp-permuter** | Rust cargo | https://github.com/encounter/decomp-permuter (⚠️ PPC C++ support absent) |

---

### Shared Infrastructure

| Resource | URL | Purpose |
|-----------|-----|---------|
| **files.decomp.dev** | https://files.decomp.dev | Compilers archive, CWG, Gekko/Broadway manuals |
| **ghidra.decomp.dev** | https://ghidra.decomp.dev | Shared Ghidra server — contact moderator for access |
| **decomp.dev API** | `https://decomp.dev/<owner>/<repo>.json?mode=measures` | Progress metrics; `.svg?mode=shield` for badges |
| **CExplorer** | https://cexplorer.red031000.com | PPC compiler explorer (sometimes down) |
| **YAGCD** | https://www.gc-forever.com/yagcd/ | GameCube hardware documentation |
| **MusyX 2.0 SDK** | https://archive.org/details/musyx-2003-01-09 | MusyX audio middleware source reference |

### Community SDK Repositories

| Repo | SDK Version | Notes |
|------|------------|-------|
| [doldecomp/dolsdk2001](https://github.com/doldecomp/dolsdk2001) | Dolphin SDK May 2001 | Melee / Super Monkey Ball era |
| [doldecomp/dolsdk2004](https://github.com/doldecomp/dolsdk2004) | Dolphin SDK 2004 | Late GC era |
| [doldecomp/sdk_2009-12-11](https://github.com/doldecomp/sdk_2009-12-11) | RVL SDK Dec 2009 | Last widely-distributed Wii SDK |
| [doldecomp/dolcp-apr2001](https://github.com/doldecomp/dolcp-apr2001) | Character Pipeline Apr 2001 | — |

---

## 💬 Discord Servers (Public Invites)

**Important**: Most projects have Discord servers. They contain the "tribal knowledge" that isn't written down. Invite links are typically in each project's README or website.

### Major Servers

| Server | Focus | Approx Members | Invite (check README) |
|--------|-------|----------------|---------------------|
| **Melee Decomp** | Super Smash Bros. Melee | 2,000+ | `discord.gg/meleedecomp` |
| **doldecomp** | General GameCube decomp (Sunshine, TTYD, etc.) | 3,000+ | `discord.gg/doldecomp` |
| **Zelda Decomp** | Zelda series (TP, TWW, OoT) | 1,500+ | `discord.gg/zeldaret` |
| **PrimeDecomp** | Metroid Prime trilogy | 500+ | `discord.gg/PrimeDecomp` |
| **decomp.dev** | Meta discussion, tool support | 1,000+ | `discord.gg/decompdev` |
| **sm64coopdx** | SM64 cooperative mod (different but related) | — | — |

### What's in Discord?

- **Real-time help** (`#help`, `#support` channels)
- **Announcements** (new builds, tool updates)
- **Code review** (pre-PR feedback)
- **Scratch challenges** (decomp.me integration)
- **Off-topic** (gaming chat, memes)
- **Voice chat** for pair debugging

**Channels you'll use**:
- `#newcomers` - Ask basic questions
- `#decompilation` - Technical discussion
- `#tool-support` - objdiff, dtk, m2c issues
- `#game-name` - Game-specific (e.g., `#melee`, `#sunshine`)
- `#scratch` - decomp.me challenges
- `#progress` - Milestone celebrations

---

## 🎯 Discord Knowledge: Now Captured

The doldecomp Discord archives (~1.8M lines, 20+ channels) were analyzed in April 2026. The tribal knowledge has been synthesized into this repository.

**Primary documents:**
- `COMMUNITY/discord-tribal-knowledge.md` — Master synthesis (all channels)
- `COMMUNITY/discord-insights-match-help.md` — Register tricks, pragmas, float patterns
- `COMMUNITY/discord-insights-tools.md` — Compiler registry, objdiff, dtk, m2c, AI workflows
- `COMMUNITY/discord-insights-games.md` — Melee, Animal Crossing, MKDD, Mario Party 4
- `COMMUNITY/discord-insights-libraries.md` — JSystem, EGG, MusyX, Dolphin SDK
- `COMMUNITY/discord-insights-general.md` — Community standards, platform setup, CI/CD

**Previously Discord-only knowledge now captured:**
1. ✅ Full MWCC compiler version registry with build stamps
2. ✅ Confirmed compiler flags per game
3. ✅ Peephole optimizer bug (`asm {}` disables peephole for rest of file)
4. ✅ Undocumented pragmas (found by searching compiler binary)
5. ✅ SDK build date timeline per game and per module
6. ✅ EGG/MusyX/JSystem version identification methods
7. ✅ PR standards, code review expectations
8. ✅ Platform setup (WSL, macOS, devkitPPC r40 breaking change)
9. ✅ AI-assisted decompilation workflows
10. ✅ mwcc-debugger register allocation analysis technique

---

## 🔄 How to Capture Discord Knowledge Without API

Since the constraint says "No Discord Access", here are strategies to still get that knowledge:

### 1. Manual Curation (Human-in-the-loop)

- **Join the Discord** yourself (user 'buddas' likely already is)
- **Search channels** for relevant discussions using Discord's search
- **Copy-paste** key insights into your md files
- **Screenshot** useful objdiff comparisons (but not ideal for text repo)

**Time**: Manual, slow, but gets quality content.

---

### 2. Discord Chat Export (Limited)

- Use Discord's **"Save Data"** feature (Settings → Data Privacy → Request Data)
- This gives **your own** message history, not the entire server
- Could search your own past questions/answers and extract

**Limitation**: Only your own messages, and only channels you've participated in.

---

### 3. Community Wiki Contribution

- Many Discords have **#wiki** or #information channels where knowledge is summarized
- Copy that content (with permission)
- Some servers have Google Docs or GitHub repos linked

---

### 4. Ask Specific Questions, Document Answers

Instead of trying to extract everything:

1. **Identify knowledge gaps** in your public documentation
2. **Ask targeted questions** in Discord
3. **Save the answer** as a new markdown file

Example:
- Gap: "How do I handle Actor creation patterns in TWW vs TP?"
- Ask in `#tww` channel
- Get answer: "They use fopAc_create, but parameters differ. See attached ghidra project"
- Write `GAMES/zelda-tww/actor-creation.md`

**Build a corpus** one Q&A at a time.

---

### 5. Scrape Public bot.commands Channels

Some servers have `#bot-commands` or `#help` channels where people ask tool questions. Those may be more "documentable" because they're about tool usage (general) rather than specific functions (ephemeral).

But Discord's ToS restricts automated scraping. Do not violate.

---

## 📚 Recommended: Start with Public Sources

Given the constraint, here's what you **CAN** get without Discord:

1. **GitHub repos** → READMEs, wikis, issues (public)
2. **GitHub discussions** → Q&A
3. **Project websites** → decomp.dev aggregates
4. **YouTube videos** → decompilation tutorials (search)
5. **Blog posts** → Personal dev blogs (search)
6. **Reddit** → r/ReverseEngineering, r/Gamecube
7. **Archive.org** → Old CodeWarrior manuals, SDK docs (if leaked)
8. **Project wikis** → Some have extensive documentation (TWW wiki is excellent)
9. **Issues and PRs** → Search closed issues for solved problems
10. **Tool documentation** → Already covered in our TOOLS/ section

**This will get you 60-70% of the way**. Discord fills the remaining 30% (specific function advice, current tool bugs, community norms).

---

## 🎯 Search Strategy for Public Sources

### GitHub Issues/PRs

```bash
# Find questions about register allocation
site:github.com/doldecomp melee "register allocation"
site:github.com/zeldaret tww "m2c"

# Find help requests (often labeled "question" or "help-wanted")
https://github.com/doldecomp/melee/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22

# Closed issues often contain solutions
https://github.com/zeldaret/tww/issues?q=is%3Aissue+is%3Aclosed
```

**Tip**: Use GitHub's search operators: `language:python dtk`, `in:body objdiff`, `commenter:username`.

---

### Archive.org for SDK Docs

Search:
- "Metrowerks CodeWarrior for GameCube"
- "Dolphin SDK reference"
- "JSystem library manual"
- "AX Interim Interface"

Maybe some PDFs exist.

---

### YouTube

Search for:
- "GameCube decompilation"
- "decomp.me tutorial"
- "zeldaret tww"
- "Super Mario Sunshine decomp"

Video creators: moogly, Acidic, koitsu, etc.

---

### Reddit

Subreddits:
- `r/ReverseEngineering`
- `r/Gamecube`
- `r/emulation`
- `r/Decompile`

Search: `decompilation site:reddit.com`, `melee decomp`

---

## 🤝 Collaborative Knowledge Capture

**Idea**: Create a `COMMUNITY/Q&A.md` file where you document specific questions and answers you find.

Format:
```markdown
## Q: How do I fix "relocation diff" errors in objdiff?

**Asked by**: @user123, 2025-03-15
**Context**: Trying to match function `d_aie_eai_init`, objdiff shows relocation to `gCommonData` mismatched.

**Answer** (from @maintainer):
Relax relocation diffs in objdiff settings. The symbol order changed when you added a new variable to `common.c`. This is expected. Enable `Settings → Function relocation diffs → Relax`.

**Related**: See also [REGALLOC.md](CHALLENGES/register-allocation.md) for register permutation fixes.

**Source**: Discord #tool-support, message https://discord.com/channels/.../123456789012345678
```

This way you **cite** Discord without bulk-exporting it.

---

## 📊 Knowledge Source Attribution

When writing documentation, attribute sources:

```markdown
According to the zeldaret TWW wiki[^1] and discussions on the doldecomp Discord[^2], ...

[^1]: https://github.com/zeldaret/tww/blob/main/docs/decompiling.md
[^2]: Discord server: https://discord.gg/doldecomp; channel: #tww; date: 2025-03-20
```

This gives readers a trail to verify or ask follow-ups.

---

## ✅ Public vs Private Content Decision

**What goes in public .md files**:
- ✅ Tool usage (dtk, objdiff, m2c)
- ✅ Workflow procedures (step-by-step)
- ✅ General challenges and fixes (register allocation, switches, etc.)
- ✅ Architecture overview (PowerPC, DOL format)
- ✅ Project status (public info from GitHub)
- ✅ Technical concepts (RTTI, inlines, tail calls)

**What stays in Discord** (or is ephemeral):
- ❌ Specific function hints (too localized)
- ❌ "Today I fixed X by doing Y" (but the fix technique is generalizable)
- ❌ Current tool bugs (use GitHub issues instead)
- ❌ Personal progress updates (use website)
- ❌ Off-topic chat

**Goal**: Extract **generalizable knowledge** from Discord into your md files, leaving the specific Q&A in Discord.

---

## 🔄 Continuous Knowledge Capture

**Process**:

1. **Weekly review**: Scan Discord channels you're in for notable insights
2. **Pattern recognition**: If the same question comes up 3+ times, document it
3. **Create template**: For recurring formats (e.g., "How do I set up on macOS?")
4. **Link, don't copy**: Reference Discord discussions without quoting bulk
5. **Ask**: If you see a gem in Discord, ask the poster "Can I include this in public docs?" (Usually yes, with attribution)

---

## 🚀 Getting Started as a Researcher

**Day 1**:
1. Join all relevant Discords (links in GitHub READMEs)
2. Read the pinned messages and #rules
3. Introduce yourself in `#newcomers`: "Hi, I'm building a research knowledge base, happy to share back!"
4. Lurk and observe the community norms

**Day 2**:
1. Start with public docs (our README, GAMES/projects-overview)
2. Try to answer a newcomer question (you'll learn)
3. Note down any gaps between public docs and Discord answers

**Week 1**:
1. Build a small test project (Luigi's Mansion or Mario Party 4)
2. When stuck, ask in Discord
3. Document the answer in an appropriate .md file
4. Create `COMMUNITY/FAQ.md` collect common questions

---

## 📈 Success Metric

By the end, `decompresearch/` should contain:

- **Core guides** (10-15 md files): Tools, workflow, challenges, porting
- **Game-specific notes** (one directory per major game): Status, quirks, common issues
- **Community resources**: This file, plus curated external links
- **FAQ**: 30-50 Q&A pairs distilled from Discord

**Coverage**: Someone using only your research repo (no Discord access) should be able to:
- Set up environment
- Match first function
- Understand major challenges
- Contribute to a project
- Know where to get more help

That's 70% of the battle. Discord fills the remaining 30% with real-time, personalized help.

---

## ⚠️ Legal & Etiquette

- **Do not scrape Discord** without permission (violates ToS)
- **Respect privacy**: Don't quote DMs or private channels
- **Attribute**: Always link back to source when possible
- **Opportunity**: Offer Discord maintainers co-authorship or credit in your knowledge base
- **License**: Choose an open license for your docs (CC-BY-SA 4.0 recommended) so others can contribute

---

## 📚 External Knowledge Bases

Some community members maintain their own notes:

- **Personal blogs**: Search for "GameCube decomp blog"
- **Notion/Github Pages**: Some maintainers have public notes
- **Gist**: Code snippets with explanations
- **YouTube comments**: Sometimes gold

Aggregate these links in this file.

---

## 🎯 Conclusion

You cannot (and should not try to) extract an entire Discord server. Instead:

1. **Use public sources** to build 70% foundation
2. **Join Discords** yourself and manually curate insights
3. **Document general patterns** and link to specific Discord discussions
4. **Become a bridge** between the ephemeral chat and durable docs

The community appreciates good documentation! By creating this research repo, you're doing valuable work that will help future newcomers.

---

*Remember: The most valuable Discord knowledge is the stuff that's asked repeatedly. Capture that pattern, not the one-off answers.* 📝