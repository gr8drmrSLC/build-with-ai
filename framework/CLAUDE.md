# CLAUDE.md — build-with-ai

This file is auto-loaded by Claude Code at session start.
Follow every instruction in this file exactly.

---

## Session Start Protocol (mandatory, in order)

1. Read `framework/PROJECT_STATUS.md` — current state, open questions, next work
2. Read `framework/DECISIONS.md` — why things were built the way they were
3. Confirm you have read both before taking any action
4. State the next proposed task based on what you read

Do not skip this protocol. Do not begin work before completing it.

---

## Core Principles

### One task at a time
Propose one atomic task. Wait for confirmation. Execute. Repeat.
Never bundle multiple tasks without explicit approval.

### Explain decisions, don't just execute
This project is a PM/strategist portfolio piece. When you make an
architectural or structural choice, name the tradeoff. One sentence
is enough. The user is not a software engineer — build the mental model.

### External memory over conversation memory
`PROJECT_STATUS.md` and `DECISIONS.md` are the source of truth.
Conversation context compresses and degrades. Files do not.
Update them before ending any session. Do not wait to be asked.

---

## The 8-Step Regression Safety Protocol

Before making any change to existing, working code or files:

1. State what is currently working and must not break
2. Identify the smallest change that achieves the goal
3. Check whether the change affects any other file or system
4. Make the change
5. Verify the change works (build, lint, or manual test as appropriate)
6. Verify nothing that was working before is now broken
7. Commit with a message that explains *why*, not just *what*
8. Update PROJECT_STATUS.md and DECISIONS.md if the change was significant

Do not skip steps. Do not batch steps across tasks.

---

## The Wall Protocol

When you hit a blocker, before escalating to the user:

1. List ALL approaches to the problem (minimum 3)
2. Identify tools already in the ecosystem that could solve it
3. Ask: what is the simplest solution?
4. Ask: what would a senior engineer try before writing code?
5. Ask: can the problem be decomposed differently to avoid the wall entirely?

Only escalate after completing all five steps. When you do escalate,
present your findings — not just "I'm stuck."

---

## Agent Delegation Policy

| Task type                        | Agent             |
|----------------------------------|-------------------|
| Architecture, planning, ADRs     | Claude Code (this)|
| Targeted code generation         | Codex CLI         |
| Large context reading / research | Claude Sonnet     |
| Atomic tasks, classification     | Claude Haiku      |
| Reasoning + planning             | Claude Sonnet     |

### Orchestrator context rule
Keep only decisions, architecture, project narrative, and task ledger
in the orchestrator conversation. Everything executable gets delegated.
Subagents are born with exactly what they need, complete the task, and close.

---

## Model Selection Rule

```
Tool/CLI available?        → Use it (no tokens spent)
Atomic, well-scoped?       → Haiku
Code generation?           → Codex
Large context reading?     → Sonnet
Reasoning + planning?      → Sonnet
Architecture judgment?     → Claude Code (sparingly)
```

---

## Public Endpoint Security Gate

Before any public route goes to production, answer these three questions.
This is mandatory — apply at Sprint 1, not after go-live.

**1. Can a bot hit this endpoint in a loop?**
If yes: add rate limiting at both the CDN/edge layer (Cloudflare rule) and
in application code. Rate limiting must fail-closed — if the limiter is
misconfigured, reject the request, do not proceed unprotected.

**2. Does each hit trigger a paid external API call?**
If yes: add CAPTCHA (hCaptcha or Cloudflare Turnstile) so bots that do not
execute JavaScript cannot submit. Rate limiting alone is not sufficient.

**3. What is the worst-case cost at 100,000 hits?**
Calculate it. If non-trivial (> $10): set a hard spend cap in the provider
console *before* enabling the feature. Document the cap in DECISIONS.md.

If all three answers are "no risk": document that conclusion in DECISIONS.md
and proceed. The goal is a conscious decision, not a checkbox.

---

## Budget Guard

Never call a paid API without knowing the approximate cost.
If a task would make more than 5 API calls or process more than
50,000 tokens, pause and confirm with the user first.

---

## Git Rules

- `.gitignore` is committed before any other file — always
- Never commit `.env`, `.env.*`, `*.pem`, `*.key`
- Commit messages explain *why*, not just *what*
- One logical change per commit
- Update CHANGELOG.md before committing any significant change

---

## Session End Protocol (mandatory)

Before ending any session:

1. Update `framework/PROJECT_STATUS.md` — current state, what was completed, open questions, next task
2. Update `framework/DECISIONS.md` — any architectural or structural decisions made this session
3. Update `CHANGELOG.md` — what changed and why
4. Confirm all changes are committed

Do not skip this protocol. The next session depends on it.
