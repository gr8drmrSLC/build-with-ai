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

Subagent (fresh Claude session, Codex, Haiku call)
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
| Large file reading, research  | Sonnet via API        |
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

## Agent Teams Pattern

For tasks that are genuinely parallelizable — research + implementation +
validation running simultaneously — Claude Code supports spawning multiple
subagents that work in parallel and report back to the orchestrator.

### When to use a team vs. a sequence

Use a team when:
- Three or more independent workstreams can run simultaneously
- Each stream has a clearly bounded file scope with no overlap
- The combined time saving justifies the coordination overhead

Use sequential subagents (the default) when:
- Tasks depend on each other's output
- The codebase is small enough that parallelism adds complexity without speed
- You are not sure — sequential is always safe, teams are sometimes faster

### Team structure

```
Orchestrator (you + Claude Code session)
    ├── Defines the team, assigns scopes, synthesizes results
    ├── research-agent  — data gathering, reading, web search
    ├── impl-agent      — code writing, file editing
    └── qa-agent        — testing, validation, error checking
```

**Lead model**: Sonnet. Orchestration is a high-token workload (repeated
reads of project state, routing decisions, synthesis). Sonnet handles
this well at a fraction of Opus cost. Reserve Opus for a single
hard architectural decision — not as the session lead.

**Teammate model**: Sonnet for complex reasoning tasks, Haiku for
atomic/well-scoped tasks. Match the model to the task, not the role.

### File ownership rules

Parallel agents writing to the same file produce non-deterministic
results. Assign exclusive ownership before spawning:

| Agent            | Owns                        | Cannot touch               |
|------------------|-----------------------------|----------------------------|
| research-agent   | `/data/`, `/research/`      | `/src/`, `/tests/`         |
| impl-agent       | `/src/`, `/services/`       | `/data/`, `/tests/`        |
| qa-agent         | `/tests/`                   | `/src/`, `/data/`          |

These boundaries are enforced by prompt — include them explicitly in
each agent's spawn prompt. An agent that is not told what it owns
will touch whatever seems relevant.

### Spawn prompt template

```
Create an agent team for [TASK DESCRIPTION].

Spawn three agents with the following scopes:

research-agent:
  Goal: [specific research objective]
  Files it may read: [list]
  Files it may write: /data/, /research/ only
  Deliverable: [specific output — file path, format, what "done" looks like]

impl-agent:
  Goal: [specific implementation objective]
  Files it may read: [list, including research-agent output once ready]
  Files it may write: /src/, /services/ only
  Deliverable: [specific output]
  Dependency: [any output from research-agent it needs before starting]

qa-agent:
  Goal: [specific validation objective]
  Files it may read: [list, including impl-agent output once ready]
  Files it may write: /tests/ only
  Deliverable: [specific output — test results, pass/fail, issues found]
  Dependency: impl-agent must complete before qa-agent starts

Synthesize when all agents report idle: [what the synthesis should produce]
```

### Coordination rules

1. **Dependencies are explicit**: if qa-agent needs impl-agent's output,
   state the dependency in the spawn prompt. Do not assume agents will
   coordinate implicitly — they will not.

2. **Each agent closes when done**: a subagent that stays open after
   completing its task consumes context. Include "report results and close"
   in every spawn prompt.

3. **The orchestrator synthesizes, not the agents**: agents produce
   bounded outputs. The orchestrator reads all outputs and synthesizes
   the final result. Agents that try to synthesize exceed their scope.

4. **Commit after synthesis**: the team's work is not committed until
   the orchestrator has reviewed all outputs and confirmed they are
   coherent together. Individual agent outputs are intermediate artifacts.

---

## Worktree Isolation for True Parallel Execution

The Agent Teams pattern uses file ownership enforced by prompt. That is
soft enforcement. Git worktrees make it hard enforcement: each agent gets
its own directory on its own branch. Two agents cannot conflict because
they are not in the same filesystem location.

### When to use worktrees

Use worktrees when:
- Two or more agents will be running simultaneously (not just sequentially)
- You cannot guarantee agents will respect file ownership rules by prompt alone
- A merge conflict would be costly to resolve and easy to prevent

Use prompt-only ownership (the default) when:
- Agents are time-shifted, not truly simultaneous
- The task scope is narrow enough that overlap is unlikely
- You need results fast and the coordination overhead is not worth it

### The worktree lifecycle

**1. Orchestrator creates isolated checkouts before spawning**

```bash
git worktree add ../project-agent-research -b feat/research-task
git worktree add ../project-agent-impl      -b feat/impl-task
git worktree add ../project-agent-qa        -b feat/qa-task
```

Each worktree is a fully independent working directory. Agents write
to their own directory. No locks, no coordination at the filesystem level.

**2. Spawn each agent pointed at its worktree**

Each Claude Code terminal opens the worktree path as its project root,
not the main repo. The agent reads CLAUDE.md, does its work, commits
to its branch, and closes.

**3. Orchestrator merges after all agents close**

```bash
# From the main repo
git merge feat/research-task
git merge feat/impl-task
git merge feat/qa-task
```

Resolve any conflicts here. Run the smoke test. If clean, the merge
is the commit that represents the team's combined output.

**4. Clean up worktrees**

```bash
git worktree remove ../project-agent-research
git worktree remove ../project-agent-impl
git worktree remove ../project-agent-qa
git branch -d feat/research-task feat/impl-task feat/qa-task
```

### Updated spawn prompt template with worktrees

```
Orchestrator creates worktrees first:
  git worktree add ../[project]-research -b feat/[task]-research
  git worktree add ../[project]-impl     -b feat/[task]-impl
  git worktree add ../[project]-qa       -b feat/[task]-qa

research-agent (working directory: ../[project]-research):
  Goal: [specific research objective]
  Deliverable: write findings to /research/[output-file].md
  When done: commit, close terminal

impl-agent (working directory: ../[project]-impl):
  Goal: [specific implementation objective]
  Dependency: wait for research-agent to commit before starting
  Deliverable: [file paths], smoke_test.py passes
  When done: commit, close terminal

qa-agent (working directory: ../[project]-qa):
  Goal: [validation objective]
  Dependency: impl-agent must complete first
  Deliverable: test results written to /tests/[report].md
  When done: commit, close terminal

Orchestrator merges all three branches, resolves conflicts, runs final
smoke test, commits the synthesis, removes worktrees.
```

### What this enables

For a project with four independent pending tasks, the orchestrator
assigns each track to its own worktree and spawns four Claude Code
terminals simultaneously. The constraint is no longer the filesystem.
The only remaining constraint is logical dependency: tasks that depend
on each other's output must still be sequenced. Tasks that do not
can run in parallel without any coordination.

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
