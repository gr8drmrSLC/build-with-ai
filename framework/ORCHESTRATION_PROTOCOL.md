# ORCHESTRATION_PROTOCOL.md

How to structure AI sessions, hand off work between contexts, and
design subagent prompts. This is the operational core of the framework.

---

## The Core Model

Every AI-assisted project runs on a two-layer structure:

```
Orchestrator (you + Claude Code session)
    ├── Holds: decisions, architecture, open questions, task queue
    ├── Does NOT hold: executable work, large file contents, output
    └── Delegates to: subagents born with exactly what they need

Subagent (fresh Claude session, Codex, Haiku call, Gemini read)
    ├── Receives: one precise task + only the context it requires
    ├── Executes: the task
    └── Closes: carries nothing forward
```

The orchestrator is not an agent — it is a decision layer. The human
is the orchestrator. Claude Code is the orchestrator's instrument.

**The failure mode this prevents**: a single long session that accumulates
context until earlier decisions and constraints are compressed lossily.
The orchestrator stays lean by delegating everything executable.

---

## Session Pattern

Each Claude Code session is a subagent. It is born from a handoff
document, executes a bounded scope of work, commits it, and closes.

### Opening a session

The minimal opening for any session:

> "Read CLAUDE.md, PROJECT_STATUS.md, and DECISIONS.md in order.
> Confirm you have read all three, then propose the next task."

That is all. The files carry the context. No verbal briefing required.

For a task you already know you want to run:

> "Read CLAUDE.md and PROJECT_STATUS.md. Then: [one atomic task description]."

Do not paste full file contents, full conversation history, or
background that the agent can retrieve itself. That is orchestrator
context. The subagent doesn't need it.

### During a session

- One task at a time. Confirm before executing. Commit before moving on.
- If the agent proposes bundling tasks, decline. Bundled tasks produce
  bundled commits, which produce untraceable regressions.
- If the agent hits a wall, the Wall Protocol applies (see `CLAUDE.md`).
  It must exhaust options before escalating — escalation includes findings,
  not just a report of being stuck.

### Closing a session

Before closing:
1. `PROJECT_STATUS.md` — updated to reflect what was built and what is next
2. `DECISIONS.md` — any new ADRs from decisions made this session
3. `CHANGELOG.md` — what changed and why
4. All changes committed and pushed

A session that ends without updating the state files has burned context
without producing durable memory. The next session starts blind.

---

## Handoff Document Format

A handoff document is what a subagent receives instead of conversation
history. It must be self-contained — the subagent has no access to
anything outside it.

### Minimum viable handoff

```
## Project
[One sentence: what this project is and what it does.]

## Current state
[What is working now. What the last session built. Where the repo is.]

## Task
[Exactly one atomic task. Specific enough that "done" is unambiguous.]

## Constraints
[Things that must not change. Dependencies. Non-negotiables.]

## Deliverable
[What the output looks like. File path, format, test to run, etc.]
```

### What not to include

- Conversation history — the subagent doesn't need to know how you
  arrived at the decision. It needs to know what the decision is.
- Open questions — those belong to the orchestrator. The subagent
  executes a decided task, not an ambiguous one. If the task is not
  decided, resolve it before delegating.
- Background that doesn't constrain the task — context that doesn't
  change what the agent should do is noise that consumes token budget.

### The test for a good handoff

Read it cold. Could you execute the task correctly from this document
alone, with no other information? If the answer is no, what is missing?
Add only that. Nothing else.

---

## The PROJECT_BRIEF as Session Zero Handoff

`PROJECT_BRIEF_TEMPLATE.md` is the handoff document for the very first
session of a new project. It follows the same principles:

- Self-contained: the agent reads it and knows where to start
- Decided: open questions are listed, but the first task is unambiguous
- Scoped: the first session has a clear end state

The difference from a mid-project handoff: the brief includes more
background, because there is no `PROJECT_STATUS.md` to read yet.
Once the framework files exist, the brief's role is taken over by
`PROJECT_STATUS.md` + `DECISIONS.md`.

---

## Context Budget Rules

Context is finite and compresses lossily. These rules preserve it.

### What stays in the orchestrator session

| Keep                          | Reason                                      |
|-------------------------------|---------------------------------------------|
| Architectural decisions        | Inform every subsequent task                |
| Open questions                 | The orchestrator resolves them              |
| Task queue (next 2–3 tasks)    | Ordering matters; context carries it        |
| ADR summaries                  | "Why we can't do X" prevents relitigating   |

### What gets delegated

| Delegate                      | To                    |
|-------------------------------|-----------------------|
| File generation, code writing | Codex CLI             |
| Large file reading, research  | Gemini CLI (free)     |
| Classification, extraction    | Haiku via API         |
| Reasoning, planning           | Sonnet via API        |
| Anything that produces output | Any subagent          |

The output of a subagent call goes into a file — never pasted back into
the orchestrator session wholesale. If the result is significant, a
one-sentence summary goes into the orchestrator. The file is the record.

### Compaction signals

Watch for these — they indicate the session context is growing too large:

- The agent starts re-asking questions that were already answered
- The agent proposes something that contradicts an earlier decision
- Responses get slower or less precise on nuanced questions

When compaction occurs, the session is effectively a new subagent
reading compressed context. The antidote: end the session, update the
state files, and open a fresh session from the handoff documents.

---

## Multi-Agent Task Design

For tasks that span more than one agent type, design the sequence
explicitly before starting. Example:

```
Task: Generate and validate a new src/core/ module

Step 1 — Codex: write the module stub to src/core/budget_guard.py
Step 2 — Claude Code: review output, check against CONVENTIONS.md
Step 3 — Claude Code: run tests, confirm smoke_test.py passes
Step 4 — Claude Code: commit if clean, log to TASK_LEDGER.md
```

Each step is a separate agent invocation with its own handoff.
Step 2's handoff includes the output of Step 1 and the review criteria.
Step 3's handoff includes what "passing" looks like.

The orchestrator holds the sequence. The subagents hold nothing
across steps.

---

## The Handoff Document Is the Interface

In software, an interface defines the contract between two components.
In this framework, the handoff document is the interface between the
orchestrator and the subagent.

A bad interface creates bugs. A bad handoff creates misexecuted tasks,
wrong assumptions, and outputs that don't fit the project.

The quality of your handoff documents is the quality of your delegation.
An agent that produces unexpected output usually received an ambiguous
prompt — not a failure of the model, a failure of the interface.

Write handoff documents like you are writing a function signature:
precise, unambiguous, with explicit inputs and expected outputs.
The agent's job is to implement the function. Your job is to define it.
