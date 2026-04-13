# PROJECT_NARRATIVE.md

This file is the living "how we thought" story of build-with-ai.
Each entry covers a founding decision, a wall hit, a pivot, or an
insight that shaped the project. It is not a changelog, it is the
reasoning behind the reasoning.

The CaseStudyPanel in the demo fetches this file live from the GitHub
raw content API. What you read in the app is always this file.

---

## Entry 001: The Founding Session
**Date**: 2026-04-10
**Phase**: Bootstrap

### The problem

Across five real projects, including an options trading bot, an
autonomous research agent, a Kalshi prediction markets bot, an SEO
content engine, and a job application bot, the same failure modes
kept appearing. Not model failures. Architecture failures.

No external memory that survived context compaction. No cost controls
before an API call ran away. No delegation policy, so every task
competed for the same context window. No regression safety, so a fix
in one place silently broke something else. No record of why decisions
were made, so the next session started from scratch.

Each project had some of these. None had all of them. And the ones
that were missing were always the ones that caused the incident.

### The insight

The practices that prevent these failures have formal names: ADRs,
FinOps, OWASP, the Well-Architected Framework, TDD. But they live
in engineering culture, not in PM/strategist culture. A product
manager who understands what to enforce, and why, and how to
delegate enforcement to agents. That is a different kind of
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

That brief was then handed to a fresh executor context, a new
Claude Code session with no accumulated state, as a precise,
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
cannot be applied to its own creation is not a methodology, it
is a description of one.

### What was built in this session

In order, with the reasoning preserved:

1. **`.gitignore` committed first.** Before README, before structure,
   before anything. Secrets in git history require history rewriting.
   Prevention is cheaper than recovery. The sequencing makes it
   unconditional.

2. **Single repo, two subdirectories.** `framework/` and `demo/`
   together. The demo fetches real framework files via the GitHub raw
   API. Separate repos would introduce sync drift and split the story
   across two URLs. The repo itself is the artifact.

3. **GitHub Actions over gh-pages package.** Path filtering means
   framework file changes don't trigger unnecessary demo rebuilds.
   No extra branch, no extra dependency. Native to the platform.

4. **Vite over CRA or Next.js.** CRA is deprecated. Next.js adds
   SSR complexity a static demo doesn't need. Vite is fast, current,
   and pairs cleanly with static hosting.

5. **`CLAUDE.md` before content files.** The session protocol is
   infrastructure, not documentation. It runs every session. It
   belongs in the repo before the files it governs.

6. **`PROJECT_STATUS.md` as the self-bootstrap mechanism.** A fresh
   Claude Code session pointed at this repo reads `CLAUDE.md`,
   `PROJECT_STATUS.md`, and `DECISIONS.md` in order and knows exactly
   where to pick up. No verbal context required. The repo carries
   its own continuity.

### What this is for

This repo is a portfolio piece for PM/strategist roles: Product
Manager, AI Product Strategist, Operations/Automation Lead. It
demonstrates not software engineering skill but architectural
thinking, the ability to take an idea from ambiguity to execution
with the rigor of an architect and the communication skills of a
strategist.

The demo app makes the methodology interactive. The framework files
make it inspectable. The commit history makes it verifiable. The
narrative makes it human.

---

*Future entries will cover: src/core/ module design, RETROFIT_GUIDE
construction, and any walls hit during remaining build.*

---

## Entry 002: The Wall Protocol in the Wild
**Date**: 2026-04-10
**Phase**: Demo build

### What happened

During the OrchestratorPanel build, a decision fork appeared: the
React app needed an API key to call Claude, but browser-side API
calls expose the key to anyone with DevTools. Two options:

1. Direct browser call: key in build artifact, acceptable for a
   controlled demo, zero infrastructure overhead
2. Cloudflare Worker proxy: key server-side, correct production
   approach, adds a second deployment and CORS configuration

The agent surfaced both options with tradeoffs, made a recommendation
with explicit justification, and asked for confirmation before
proceeding. It did not pick one silently. It did not refuse to
continue without more information. It resolved the fork at the right
layer, the human decision point.

### Why this belongs in the narrative

This was not a wall. No blocker was hit. But it was the Wall
Protocol working correctly on a decision fork rather than a
blocker, which is actually the more common use case.

The Wall Protocol is usually described as "what to do when stuck."
The better framing: it is what disciplined agents do at any decision
point with non-obvious consequences. Surface options. Show reasoning.
Ask for confirmation. Proceed only when the decision is made by the
right person.

The tradeoff is now documented in three places: a comment directly
above the API call in OrchestratorPanel.tsx, ADR-005 in DECISIONS.md
with a trigger for revisiting, and this narrative entry.

Three places is not redundant. Each one is for a different reader:
the comment is for whoever opens that file next, the ADR is for
whoever is making a related architecture decision, and this entry
is for whoever wants to understand how the project thinks.

### The meta-observation

The fact that the agent paused at this fork, rather than just
calling `dangerouslyAllowBrowser: true` and moving on, is
evidence of the thing the framework is trying to demonstrate.
An agent that proceeds without surfacing tradeoffs is fast but
untrustworthy. An agent that surfaces tradeoffs, explains them,
and asks is the one you want building things that matter.

That distinction is not a Claude feature. It is a prompt
architecture feature. The Wall Protocol is in `CLAUDE.md`.
The behavior follows from having written it down.

---

## Entry 003: This Session Is the Proof of Concept
**Date**: 2026-04-10
**Phase**: Reflection

### The structure of the build session

This project was built in two stages that perfectly mirror the
orchestrator/subagent pattern the framework describes:

**Stage 1: The orchestrator conversation** (claude.ai)
A long, exploratory, context-rich brainstorming session. Goals were
unclear at the start. The conversation ranged across positioning,
repo structure, demo architecture, public framing, file structure,
and methodology. Context accumulated. Decisions were made. Tradeoffs
were weighed. By the end, the shape of the project was clear.

**Stage 2: The executor session** (Claude Code, this session)
Received `SATURDAY_BRIEF.md`, a single, self-contained handoff
document produced by the orchestrator conversation. No access to
the full brainstorming history. No need for it. The brief contained
exactly what was needed: goals, structure, decisions already made,
open questions, and the first task.

The executor read the brief, confirmed understanding, and built
the repo from scratch, incrementally, one confirmed task at a time,
with the session-end protocol updating the files that the next
session will read.

### Why the structure matters

The orchestrator conversation is gone. Its context is not recoverable.
But `SATURDAY_BRIEF.md` survived it, and from that document, a fresh
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

A PM/strategist who understands how to run a high-context
orchestrator conversation to resolve ambiguity, produce a minimal
handoff document, delegate execution to a fresh agent context with
no state bleed, use external memory rather than conversation memory,
and apply the Wall Protocol at decision forks rather than just
blockers, can take a project from a vague idea to a live, deployed,
self-documented artifact in a single Saturday session.

The methodology is not theoretical. This session is the receipt.

---

## Entry 004: The Combination Failure
**Date**: 2026-04-10
**Phase**: Post-build review

### What happened

Two individually reasonable decisions were made in sequence:

1. **Option 1: direct browser API call** was chosen over a Cloudflare
   Worker proxy. Reasoning: portfolio demo, deployer controls access,
   proxy adds infrastructure complexity not justified for this use case.
   Documented in ADR-005. Comment added to source. Looked thorough.

2. **Public GitHub Pages deployment** was the stated goal from the
   start. Wired via GitHub Actions. Discussed throughout the session.

Neither decision was wrong in isolation. Together they created a
latent exposure: had the Anthropic API key been added as a GitHub
Actions secret (the obvious next step to make the demo work on the
live URL), it would have been embedded in the public JS bundle,
readable by anyone with DevTools.

Neither Claude Code nor the orchestrator caught the interaction.
The ADR documentation made the first decision look considered.
The deployment infrastructure made the second decision look routine.
The gap was in the combination.

### The actual current exposure

The key was never in the deployed bundle. The GitHub Actions workflow
builds `demo/` without injecting secrets: `VITE_ANTHROPIC_API_KEY`
is undefined at build time, so the panel shows an error on the live
URL. The exposure was latent: one "add it as a GitHub Actions secret"
step away from real.

The key was rotated as a precaution. The architecture was redesigned.

### Why the ADR made it worse

ADR-005 documented the tradeoff and included a trigger for revisiting:
"if this demo becomes publicly accessible with open access, add the
proxy." That language implies the two decisions are sequential,
first deploy, then assess. The problem is they were simultaneous.
The trigger was already met the moment we wired GitHub Actions.

Documentation that looks thorough can create false confidence.
This is the more dangerous failure mode, not ignorance, but
documented ignorance that passes review.

### The fix

Redesign OrchestratorPanel to accept a user-supplied API key in
the UI. The key lives in component state only, never in the bundle,
never committed, never transmitted except to the API it calls.
This is strictly better than the original approach. No key appears
in build artifacts. No proxy infrastructure is needed. The visitor
uses their own key, so nothing is hardcoded on the deployer's side,
and the demo becomes self-serve for anyone who wants to try it.

### The protocol fix

Before any deployment step, run this checklist:

1. Does this deployment make anything public that was not public before?
2. If yes, what secrets are now in scope of the public surface?
3. Are any secrets baked into build artifacts (JS bundles, config files)?
4. Is any secret one natural-next-step away from being in scope?

Question 4 is the one this session missed. "One step away" is close
enough to treat as already exposed.

This checklist is now in `SECURITY.md`.

### What this entry is for

The methodology includes writing down failures, not just decisions.
A project narrative that only records successes is marketing.
This one records the gap, the cause, the actual exposure level,
the fix, and the protocol change it produced.

That is the difference between documentation and accountability.

---

## Entry 005: The Sequence Inversion
**Date**: 2026-04-10
**Phase**: Post-build review

Entry 004 describes what went wrong technically. This entry names
the structural reason it was possible.

In the first build session, we violated the framework we were
building. A deployment step was executed without running the
pre-deployment security checklist because the checklist hadn't
been written yet. The protocol was designed to prevent this class
of error. We shipped the deployment pipeline before we shipped
the security gate that should precede it.

Correct sequence: security gates first, deployment pipeline second.

### Why this happened

The build order followed natural momentum: scaffold the repo,
wire the demo, get it deployed. Security documentation was
treated as a parallel track, important, but not blocking.

The framework's own sequencing rules say otherwise. `SECURITY.md`
is infrastructure, not documentation. It belongs in the repo before
the deployment pipeline that it governs, by the same logic as
`.gitignore` being the first commit. A security gate written after
the thing it was meant to gate is not a gate. It is a record of
what should have been prevented.

### Why this is a better portfolio story than a clean build

A framework that describes hypothetical risks is a checklist.
A framework that catches a real error on the project that built
it, and documents the catch, is evidence.

The pre-deployment checklist in `SECURITY.md` exists because this
session needed it and didn't have it. The sequence rule exists
because this session inverted it. The threat model table exists
because the gap it describes was real, not theoretical.

Every item in this framework that says "do this before X" was
written by someone who did X first. That is the most honest
possible provenance for a methodology.

### The transferable rule

For any project using this framework:

Security gates are written before the infrastructure they govern.
The `.gitignore` before the first file. `SECURITY.md` before the
deployment pipeline. The pre-deployment checklist before the first
deployment step. The budget guard before the first API call.

Sequence is not a stylistic preference. It is the mechanism by
which the protection is unconditional rather than aspirational.

---

## Entry 006: Decision Point: Demo API Key Architecture
**Date**: 2026-04-10
**Phase**: Security remediation

Three approaches were considered in sequence before arriving at
the correct architecture. The progression is worth documenting
because each rejection teaches something different.

### Approach 1: Build-time env var (VITE_ANTHROPIC_API_KEY)

Initially accepted with an ADR (ADR-005). A comment was added to
the source. The tradeoff was documented. It looked considered.

Rejected when we recognized that "portfolio demo" plus "public
deployment" plus "key in JS bundle" combine into a live exposure.
Each decision looked reasonable in isolation. The combination did
not. The ADR documented the tradeoff without resolving it, which
is the more dangerous failure mode: documented ignorance that
passes review.

### Approach 2: User-supplied key field in the UI

Proposed as the fix. A text input in the panel: the visitor pastes
their own Anthropic key, it lives in component state only, never
in the bundle.

Rejected because it creates friction and looks suspicious to a
first-time visitor. A portfolio demo that asks for your API key
before you can see it work is solving the deployer's security
problem by creating a trust problem for the visitor. Wrong trade.

### Approach 3: Cloudflare Worker proxy (chosen)

Key stored as a Cloudflare Worker secret, never in the bundle,
never in the repo, never client-side. Visitor experience is
seamless. Rate limiting (10 requests/IP/hour) prevents abuse.
Hard spend cap in Anthropic Console ($20/month) is the final
backstop. Haiku is the cheapest model at approximately $0.001
per run. Portfolio demo traffic is effectively free.

This is also the architecture documented in
`INFRASTRUCTURE_POLICY.md`: the demo runs on its own security
framework. The proof of concept proves the framework it describes.

### Key lesson

Two individually reasonable decisions combined to create a
security gap that neither the orchestrator nor the subagent
caught in real time. The pre-deployment security checklist exists
to catch exactly this class of error. We built the deployment
pipeline before we built the security gate.

Correct sequence: security gates first, deployment second.

This is Case Study 1, Entry 1, the framework catching its own
violation on its first build day. The methodology is not
theoretical. This session is the receipt.

---

## On Human Oversight

This build required active human judgment at several points that
no agent caught independently, the API key exposure being the
clearest example. The agents reasoned well locally. They missed
the combination. A human connecting the dots across the full
context caught it.

The framework is not an automation of software development. It is
a structure for human-AI collaboration where the human's role is
explicit: define scope, review decisions, catch cross-cutting
risks, ask uncomfortable questions. The agents handle execution.
The human handles judgment.

That division is not a limitation of the current tools. It is the
correct architecture for this stage of the technology.

---

## On the Bootstrap Exception
**Date**: 2026-04-10
**Phase**: Reflection

This framework was built in a single long Claude Code session rather
than delegated atomic tasks. That was the correct approach for this
specific project: the framework itself was the shared context, and
every decision was interdependent. No clean seams existed to delegate
along until the structure was established.

The compaction occurred late, after most core work was complete. One
compaction for a full framework bootstrap is an acceptable outcome.

The atomic task delegation philosophy applies to all projects built
*using* this framework. It could not be fully applied to the project
that *defined* it. This is the bootstrap exception, noted,
understood, and not repeated.

---

## Session Protocol Going Forward
**Date**: 2026-04-10
**Phase**: Session close

This session established the framework but was built as one long
compacting context, necessary for bootstrap, not the pattern
going forward.

All future sessions follow this process:

1. Open `PROJECT_STATUS.md` and read the handoff document
2. Open a fresh Claude Code session
3. Paste the first atomic task only, nothing else
4. Confirm output before proceeding
5. Commit after each completed task
6. Update `PROJECT_NARRATIVE.md` with any decisions or lessons from that task
7. Paste next atomic task
8. Repeat

Session conversations are disposable.
The committed files are the memory.
GitHub is the source of truth, not conversation history.
Close each session once its work is committed.

This is the orchestrator/subagent pattern applied to Claude Code
sessions themselves: each session is a fresh subagent,
`PROJECT_STATUS.md` is the handoff document, and the repo is the
external memory that survives every context boundary.

---

## First Live Demo Run: PBJ Decomposition
**Date**: 2026-04-10

First real output from the live demo: "make a pbj."

The framework returned Simple complexity tier, assigned Haiku to
all three phases, and flagged allergen risk as the only non-trivial
consideration. Ingredient availability and cut angle standardization
were noted. First atomic task: place two slices of bread on a
cutting board.

This was the right output.

A framework that correctly identifies a sandwich as Simple, and
that doesn't invent unnecessary phases, assign expensive models, or
manufacture architectural concerns, is more credible than one
that does. Calibration matters more than impressiveness. The
tendency to over-engineer is the failure mode this framework
exists to prevent. It would be embarrassing if the demo exhibited
that failure on its first run.

It didn't.
