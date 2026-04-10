# USER_MANUAL.md

How to use this framework to start and run an AI-native project.

---

## What this framework is

A set of files that go into every project repo and govern how Claude
Code sessions are run. The files are:

- **Session protocols** — what Claude reads at the start and end of
  every session, so no verbal context is required
- **Policy files** — how decisions get made, how code gets changed,
  how secrets are handled, how money gets spent
- **State files** — where the project currently is, what decisions
  have been made, and why

Once installed, a fresh Claude Code session pointed at the repo knows
where to pick up without being told. That is the goal.

---

## Installing the framework into a new project

### Option 1 — bootstrap.sh (recommended)

Run the bootstrap script from inside your new project directory:

```bash
bash /path/to/build-with-ai/bootstrap.sh
```

This copies all framework files into `framework/` in your current
directory and creates the `src/core/` Python module stubs.

After running it, three things remain:

1. Fill out `framework/PROJECT_BRIEF_TEMPLATE.md` and rename it to
   match your project (e.g., `PROJECT_STATUS.md` already exists —
   the brief is your pre-session planning document)
2. Edit `framework/CLAUDE.md` — change the project name at the top
3. Commit the `framework/` directory as the first substantive commit
   (after `.gitignore`)

### Option 2 — manual copy

Copy the `framework/` directory from this repo into your project.
Remove or replace any content specific to build-with-ai
(PROJECT_NARRATIVE.md, PROJECT_STATUS.md, DECISIONS.md are
project-specific — start new ones from scratch).

---

## Starting a new project session

### First session ever (project setup)

1. Read `USER_MANUAL.md` (this file) — once only
2. Fill out `PROJECT_BRIEF_TEMPLATE.md` completely before opening
   Claude Code — the more complete this is, the less the first session
   wastes time on scope clarification
3. Open Claude Code and say:
   > "Read CLAUDE.md, then read my project brief at
   > framework/PROJECT_BRIEF_TEMPLATE.md. Confirm you understand the
   > project and propose the first task."
4. Work one confirmed task at a time from there

### Every subsequent session

Claude Code reads `CLAUDE.md` automatically (it is in the repo root
or framework/ directory depending on your setup). You do not need to
brief it — just open the session. The session start protocol in
`CLAUDE.md` handles the rest.

If the session is starting cold after a long gap:

> "Read CLAUDE.md, PROJECT_STATUS.md, and DECISIONS.md in order, then
> tell me where we are and propose the next task."

That is all that is required.

---

## The core loop

Every session follows the same pattern:

```
Read status files
  → Propose one task
  → User confirms
  → Execute (8-step protocol for any change to working code)
  → Verify
  → Commit
  → Update PROJECT_STATUS.md + DECISIONS.md
  → Repeat
```

**One task at a time** is not a style preference — it is the mechanism
that keeps external memory current. If a session executes three tasks
before updating status files and then the context compacts, the work
is in the conversation, not the repo. The next session starts blind.

---

## The state files

Three files carry the project's state across sessions:

### PROJECT_STATUS.md

What is currently built, what is not built yet, and what the next
task is. Updated at the end of every session — do not wait to be asked.

### DECISIONS.md

Architectural Decision Records (ADRs). Every non-obvious choice that
should not be relitigated later gets an entry here: what was decided,
what was rejected, and why. Saves the cost of rediscovering the same
tradeoffs in a future session.

### PROJECT_NARRATIVE.md (optional)

The "how we thought" story — walls hit, pivots made, key insights.
Not a changelog. Not required for every project, but useful for
portfolio pieces and anything where the reasoning matters as much
as the artifact.

---

## When to delegate to a subagent

The orchestrator/subagent pattern is the single most important
performance lever in this framework. The orchestrator conversation
(your Claude Code session) has a context budget. When that budget
fills up, earlier decisions and constraints get compressed lossily.

**Keep in the orchestrator**: decisions, architecture, status, ADRs.

**Delegate to subagents**: everything executable. Use the capability
matrix in `AI_DELEGATION_POLICY.md` to match task type to agent.

The question before every API call: could a free tool, a cheaper
model, or a different decomposition accomplish this?

---

## The files and what they govern

| File                       | Governs                                          |
|----------------------------|--------------------------------------------------|
| `CLAUDE.md`                | Session protocol — auto-loaded every session     |
| `PROJECT_STATUS.md`        | Current project state — updated every session    |
| `DECISIONS.md`             | ADRs — updated when architectural choices are made |
| `AI_DELEGATION_POLICY.md`  | Which agent handles which task type              |
| `DEVELOPMENT_PROTOCOL.md`  | 8-step safety protocol for code changes          |
| `SECURITY.md`              | Secret handling, pre-deployment checklist        |
| `BUDGET_POLICY.md`         | Spend limits, cost reference, budget_guard       |
| `GIT_POLICY.md`            | Commit rules, branching, .gitignore requirements |
| `CONVENTIONS.md`           | Code style, file organization, .env.example format |
| `ARCHITECTURE.md`          | Component map, data flow, deployment overview    |
| `INFRASTRUCTURE_POLICY.md` | Cloud services, deployment targets, access rules |
| `BACKUP_POLICY.md`         | What gets backed up, how, and how often          |
| `ORCHESTRATION_PROTOCOL.md`| Subagent prompt design, handoff document format  |

---

## The non-negotiables

These rules are not optional regardless of project type or urgency:

1. `.gitignore` is the first commit — before any other file
2. Secrets never appear in committed files — ever
3. Run the pre-deployment security checklist before any public deployment
4. One confirmed task at a time — never bundle without explicit approval
5. Update `PROJECT_STATUS.md` and `DECISIONS.md` before ending the session
6. Any change to working code follows the 8-step protocol

If you skip rule 1 or 2, recovery requires rewriting git history.
If you skip rules 3–6, the next session starts with incomplete context
and the project accretes invisible debt.

---

## Retrofitting an existing project

If you have a project that was not started with this framework, see
`RETROFIT_GUIDE.md`. The short version:

1. Add `.gitignore` immediately — check history for any secrets already
   committed (see `SECURITY.md` for the secrets scan procedure)
2. Copy `framework/` in and fill out `PROJECT_STATUS.md` and
   `DECISIONS.md` based on what already exists
3. Write a smoke test that defines the current working baseline
4. Add `CLAUDE.md` to the repo so the next session starts clean

The gap audit in `RETROFIT_GUIDE.md` identifies which policies are
missing and in what priority order to add them.
