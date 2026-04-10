# PROJECT_NARRATIVE.md

This file is the living "how we thought" story of build-with-ai.
Each entry covers a founding decision, a wall hit, a pivot, or an
insight that shaped the project. It is not a changelog — it is the
reasoning behind the reasoning.

The CaseStudyPanel in the demo fetches this file live from the GitHub
raw content API. What you read in the app is always this file.

---

## Entry 001 — The Founding Session
**Date**: 2026-04-12
**Phase**: Bootstrap

### The problem

Across five real projects — an options trading bot, an autonomous
research agent, a Kalshi prediction markets bot, an SEO content
engine, and a job application bot — the same failure modes kept
appearing. Not model failures. Architecture failures.

No external memory that survived context compaction. No cost controls
before an API call ran away. No delegation policy, so every task
competed for the same context window. No regression safety, so a fix
in one place silently broke something else. No record of why decisions
were made, so the next session started from scratch.

Each project had some of these. None had all of them. And the ones
that were missing were always the ones that caused the incident.

### The insight

The practices that prevent these failures have formal names — ADRs,
FinOps, OWASP, the Well-Architected Framework, TDD. But they live
in engineering culture, not in PM/strategist culture. A product
manager who understands what to enforce, and why, and how to
delegate enforcement to agents — that is a different kind of
practitioner than either a traditional PM or a traditional engineer.

The framework is that synthesis. Not invented here. Discovered
through trial and error, then mapped to the formal names. That
mapping process is itself evidence of understanding.

### The design conversation

The framework was designed in a single high-context orchestrator
conversation before a line of code was written. That conversation
produced a complete project brief: the file structure, the demo
architecture, the core principles, the agent delegation policy,
the model selection rules, and the session protocols.

That brief was then handed to a fresh executor context — a new
Claude Code session with no accumulated state — as a precise,
self-contained handoff document. The executor read it, confirmed
understanding, and built the repo from scratch.

This is the orchestrator/subagent pattern in practice. The
orchestrator conversation stayed lean. The executor started clean.
The handoff document was the interface between them.

The best proof that a methodology works is that the tool
demonstrating it was built using it.

### The self-referential structure

The brainstorming session that designed this framework was itself
an example of the framework: a high-context orchestrator
conversation producing a minimal, precise handoff document for a
fresh executor context.

This is not a coincidence. It is the point. A methodology that
cannot be applied to its own creation is not a methodology — it
is a description of one.

### What was built in this session

In order, with the reasoning preserved:

1. **`.gitignore` committed first** — before README, before structure,
   before anything. Secrets in git history require history rewriting.
   Prevention is cheaper than recovery. The sequencing makes it
   unconditional.

2. **Single repo, two subdirectories** — `framework/` and `demo/`
   together. The demo fetches real framework files via the GitHub raw
   API. Separate repos would introduce sync drift and split the story
   across two URLs. The repo itself is the artifact.

3. **GitHub Actions over gh-pages package** — path filtering means
   framework file changes don't trigger unnecessary demo rebuilds.
   No extra branch, no extra dependency. Native to the platform.

4. **Vite over CRA or Next.js** — CRA is deprecated. Next.js adds
   SSR complexity a static demo doesn't need. Vite is fast, current,
   and pairs cleanly with static hosting.

5. **`CLAUDE.md` before content files** — the session protocol is
   infrastructure, not documentation. It runs every session. It
   belongs in the repo before the files it governs.

6. **`PROJECT_STATUS.md` as the self-bootstrap mechanism** — a fresh
   Claude Code session pointed at this repo reads `CLAUDE.md`,
   `PROJECT_STATUS.md`, and `DECISIONS.md` in order and knows exactly
   where to pick up. No verbal context required. The repo carries
   its own continuity.

### What this is for

This repo is a portfolio piece for PM/strategist roles: Product
Manager, AI Product Strategist, Operations/Automation Lead. It
demonstrates not software engineering skill but architectural
thinking — the ability to take an idea from ambiguity to execution
with the rigor of an architect and the communication skills of a
strategist.

The demo app makes the methodology interactive. The framework files
make it inspectable. The commit history makes it verifiable. The
narrative makes it human.

---

*Future entries will cover: methodology panel content decisions,
Claude API orchestrator design, case study selection, and any walls
hit during build.*
