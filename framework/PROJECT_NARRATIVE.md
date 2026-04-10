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

*Future entries will cover: src/core/ module design, RETROFIT_GUIDE
construction, and any walls hit during remaining build.*

---

## Entry 002 — The Wall Protocol in the Wild
**Date**: 2026-04-12
**Phase**: Demo build

### What happened

During the OrchestratorPanel build, a decision fork appeared: the
React app needed an API key to call Claude, but browser-side API
calls expose the key to anyone with DevTools. Two options:

1. Direct browser call — key in build artifact, acceptable for a
   controlled demo, zero infrastructure overhead
2. Cloudflare Worker proxy — key server-side, correct production
   approach, adds a second deployment and CORS configuration

The agent surfaced both options with tradeoffs, made a recommendation
with explicit justification, and asked for confirmation before
proceeding. It did not pick one silently. It did not refuse to
continue without more information. It resolved the fork at the right
layer — the human decision point.

### Why this belongs in the narrative

This was not a wall. No blocker was hit. But it was the Wall
Protocol working correctly on a decision fork rather than a
blocker — which is actually the more common use case.

The Wall Protocol is usually described as "what to do when stuck."
The better framing: it is what disciplined agents do at any decision
point with non-obvious consequences. Surface options. Show reasoning.
Ask for confirmation. Proceed only when the decision is made by the
right person.

The tradeoff is now documented in three places:
- A comment directly above the API call in OrchestratorPanel.tsx
- ADR-005 in DECISIONS.md with a trigger for revisiting
- This narrative entry

Three places is not redundant. Each one is for a different reader:
the comment is for whoever opens that file next, the ADR is for
whoever is making a related architecture decision, and this entry
is for whoever wants to understand how the project thinks.

### The meta-observation

The fact that the agent paused at this fork — rather than just
calling `dangerouslyAllowBrowser: true` and moving on — is
evidence of the thing the framework is trying to demonstrate.
An agent that proceeds without surfacing tradeoffs is fast but
untrustworthy. An agent that surfaces tradeoffs, explains them,
and asks is the one you want building things that matter.

That distinction is not a Claude feature. It is a prompt
architecture feature. The Wall Protocol is in `CLAUDE.md`.
The behavior follows from having written it down.

---

## Entry 003 — This Session Is the Proof of Concept
**Date**: 2026-04-12
**Phase**: Reflection

### The structure of the build session

This project was built in two stages that perfectly mirror the
orchestrator/subagent pattern the framework describes:

**Stage 1 — The orchestrator conversation** (claude.ai)
A long, exploratory, context-rich brainstorming session. Goals were
unclear at the start. The conversation ranged across positioning,
repo structure, demo architecture, public framing, file structure,
and methodology. Context accumulated. Decisions were made. Tradeoffs
were weighed. By the end, the shape of the project was clear.

**Stage 2 — The executor session** (Claude Code, this session)
Received `SATURDAY_BRIEF.md` — a single, self-contained handoff
document produced by the orchestrator conversation. No access to
the full brainstorming history. No need for it. The brief contained
exactly what was needed: goals, structure, decisions already made,
open questions, and the first task.

The executor read the brief, confirmed understanding, and built
the repo from scratch — incrementally, one confirmed task at a time,
with the session-end protocol updating the files that the next
session will read.

### Why the structure matters

The orchestrator conversation is gone. Its context is not recoverable.
But `SATURDAY_BRIEF.md` survived it — and from that document, a fresh
context with no prior history built a working demo, eleven framework
files, a live GitHub repo, and a GitHub Actions deploy pipeline.

That is the external memory principle in practice. The work is not
in the conversation. The work is in the files.

### Case Study 1

The demo's right panel fetches `PROJECT_NARRATIVE.md` and renders it
as a case study. Entry 001 of this file documents the construction
of the project that displays it.

The project's first case study is the project documenting its own
construction. The demo's proof of concept is the demo itself.

This is not a coincidence arranged after the fact. It is what
happens when the methodology is followed from the first keystroke.
The framework produced the artifact. The artifact demonstrates the
framework. They are the same thing.

### What this session proves

A PM/strategist who understands how to:
- Run a high-context orchestrator conversation to resolve ambiguity
- Produce a minimal, precise handoff document from that conversation
- Delegate execution to a fresh agent context with no state bleed
- Use external memory (files) instead of conversation memory
- Apply the Wall Protocol at decision forks, not just blockers

...can take a project from a vague idea to a live, deployed,
self-documented artifact in a single Saturday session.

The methodology is not theoretical. This session is the receipt.
