# AI_DELEGATION_POLICY.md

How work gets assigned to agents in this framework.
The goal is not to use AI everywhere — it is to use the right
tool for each task, preserve context budget, and maintain a
clear human decision point at the orchestration layer.

---

## The Core Principle

Every AI project has a context budget. Conversation context
compresses and degrades as it grows — earlier decisions, subtle
reasoning, and edge-case constraints get flattened lossily.
The orchestrator/subagent pattern protects against this.

```
Orchestrator (this conversation)
    ├── Stays lean: decisions, architecture, narrative, task ledger only
    ├── Delegates everything executable to subagents
    └── Subagents are born with exactly what they need,
        complete one task, and close — no accumulated state
```

A subagent that closes carries nothing forward. A subagent prompt
that contains exactly the right context — no more, no less — is
the craft of this role.

---

## Agent Capability Matrix

| Agent            | Best for                                              | Avoid for                          |
|------------------|-------------------------------------------------------|------------------------------------|
| Claude Code      | Architecture, planning, ADRs, session orchestration   | Large code generation (burns context) |
| Codex CLI        | Targeted code generation, well-scoped file edits      | Open-ended design decisions        |
| Claude Haiku     | Atomic subagent tasks, classification, structured output | Ambiguous or multi-step problems |
| Claude Sonnet    | Reasoning, planning, nuanced judgment                 | Tasks a cheaper model handles fine |
| Claude Opus      | Highest-stakes architectural judgment                 | Routine tasks (cost not justified) |

---

## Model Selection Rule

Work through this decision tree in order. Stop at the first match.

```
1. Is there a CLI tool available that does this without an API call?
   → Use it. (No tokens, no cost, no context consumption.)

2. Is the task atomic and well-scoped with a clear correct answer?
   → Haiku. ($0.25/M input — use it freely for classification,
     extraction, formatting, structured output.)

3. Is the task primarily code generation for a known, bounded problem?
   → Codex CLI. (Targeted, fast, doesn't consume orchestrator context.)

4. Does the task require reading a large file, repo, or document, or
   multi-step reasoning and nuanced judgment?
   → Sonnet. (Default for planning, analysis, and large-context reading.)

5. Is this a founding architectural decision with long-term consequences?
   → Claude Code / Opus. (Use sparingly — cost is justified only when
     the decision is hard to reverse.)
```

**The question to ask before every API call**: could a free tool,
a cheaper model, or a different decomposition accomplish this?

---

## The Wall Protocol

When an agent hits a blocker, escalating immediately is the wrong
move. Blockers are usually decomposition failures — the task was
framed in a way that created a wall that a different framing
would route around.

Before escalating, the agent must complete all five steps:

**Step 1 — List all approaches (minimum 3)**
Do not anchor on the first approach that failed. Force a search
for alternatives before concluding the wall is real.

**Step 2 — Identify ecosystem tools**
What already exists — in the repo, in the language stdlib, in
the platform — that could solve this without writing new code?
The best solution is often already present.

**Step 3 — Find the simplest solution**
Complexity is usually optional. Ask: what is the minimum change
that achieves the goal? Is there a version of this task that
takes ten lines instead of a hundred?

**Step 4 — Apply the senior engineer heuristic**
What would a senior engineer try before writing code?
- Read the error message carefully
- Check the docs for the specific version in use
- Search for the exact error string
- Look at what changed most recently
- Ask whether the problem is in the code or the environment

**Step 5 — Decompose differently**
Can the task be split so that the blocking part is isolated and
smaller? Can the goal be achieved via a different path that avoids
the wall entirely?

**Only after completing all five steps**: escalate with findings —
not just "I'm stuck." The escalation message should contain:
- What was tried (the three approaches)
- What tools exist that were considered
- The simplest version of the problem that remains unsolved
- A recommendation for how the human should proceed

---

## Subagent Prompt Design

A subagent prompt that is too broad produces generic output.
A subagent prompt that is too narrow misses context and makes
wrong assumptions. The right level is: exactly what the agent
needs to complete the task correctly, and nothing it doesn't need.

**Required elements in every subagent prompt**:
1. What you are trying to accomplish and why
2. What you have already tried or ruled out
3. The specific deliverable — what does "done" look like?
4. Any constraints the agent must not violate
5. The format expected back (code, JSON, prose, file path, etc.)

**What not to include**:
- Full conversation history (that's the orchestrator's context,
  not the subagent's problem)
- Background that doesn't affect the task
- Open-ended questions (subagents answer one thing well)

---

## Orchestrator Hygiene Rules

1. **Keep only what survives compaction in the orchestrator**: decisions,
   architecture, project narrative, task ledger. Executable work gets
   delegated.

2. **One task at a time**: propose, confirm, execute, update status.
   Never bundle tasks without explicit user approval.

3. **Update external memory before the session ends**: PROJECT_STATUS.md
   and DECISIONS.md live in files, not conversation. They survive
   context compaction. The conversation does not.

4. **The task ledger tracks cost**: log model used, approximate tokens,
   and outcome for every significant API call. Surprises on the bill
   are a process failure, not a model failure.

---

## What This Policy Is Not

This policy does not claim that AI agents are reliable, autonomous,
or production-safe without human review. Every agent output that
affects a committed file, a deployed system, or a user-facing
surface requires human confirmation before it takes effect.

The orchestrator is the human decision point. Delegation is not
abdication.
