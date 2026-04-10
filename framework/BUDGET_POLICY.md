# BUDGET_POLICY.md

Spend controls, model cost reference, and the rule that governs
every API call in this framework. Cost surprises are a process
failure, not a model failure.

---

## The Core Rule

No API call is made without knowing its approximate cost first.

This is not about being cheap. It is about maintaining the habit
that prevents a runaway loop, a misconfigured prompt, or an
accidental large-context call from producing a bill that dwarfs
the value of the work.

---

## Model Cost Reference

Prices as of early 2026. Verify current pricing before any
production workload: https://www.anthropic.com/pricing

### Claude (Anthropic)

| Model           | Input ($/M tokens) | Output ($/M tokens) | Best for                        |
|-----------------|--------------------|---------------------|---------------------------------|
| Claude Haiku    | $0.25              | $1.25               | Atomic tasks, classification    |
| Claude Sonnet   | $3.00              | $15.00              | Reasoning, planning, analysis   |
| Claude Opus     | $15.00             | $75.00              | High-stakes architecture        |

### Free / Near-Free Alternatives

| Tool         | Cost    | Constraint                        | Best for                     |
|--------------|---------|-----------------------------------|------------------------------|
| Gemini CLI   | Free    | Rate limits, sequential only      | Large context reading        |
| Codex CLI    | ~Free   | Scoped to code generation         | File-level code tasks        |
| Local tools  | $0      | Must be installed                 | Anything they handle well    |

**Default**: exhaust free options before spending tokens.
**Haiku** is the default paid model for any task it can handle.
**Sonnet** requires justification. **Opus** requires explicit approval.

---

## Spend Limits

### Per-call limits
- Any single API call estimated above **$0.10**: pause and confirm
- Any call processing more than **50,000 tokens**: pause and confirm
- Any loop making more than **5 iterations**: add a hard cap before starting

### Per-session limits
- Default session budget: **$5.00**
- Exceeding $5 in a session requires noting it in PROJECT_STATUS.md
- Any session over **$20**: flag for review before the next session

### Per-project limits
- No hard monthly cap by default — but track cumulative spend in TASK_LEDGER.md
- If a project exceeds **$50/month**: schedule a model selection review

These are guardrails, not ceilings. The goal is awareness, not restriction.

---

## Token Estimation Rules

Before a significant API call, estimate token count:

```
~750 words ≈ 1,000 tokens (rough rule of thumb)

A typical framework .md file: 1,000–3,000 tokens
A typical source file (100–300 lines): 2,000–5,000 tokens
A full repo context: 50,000–200,000 tokens (use Gemini, not Claude)
A single user message + system prompt: 500–2,000 tokens
```

For streaming calls (OrchestratorPanel), estimate based on
typical response length. Budget for worst-case, not average.

---

## The Budget Guard Pattern

`src/core/budget_guard.py` enforces spend limits in code.
Before any API call, it checks:

1. Estimated token count against per-call limit
2. Session spend to date against session limit
3. Whether a cheaper model could handle the task

If a limit would be exceeded, it raises `BudgetExceeded` before
the call is made — not after.

```python
# Usage pattern
from core.budget_guard import BudgetGuard

guard = BudgetGuard(session_limit_usd=5.00)
guard.check(model="claude-haiku-4-5", estimated_tokens=2000)
# Raises BudgetExceeded if limit would be exceeded
response = client.messages.create(...)
guard.record(model="claude-haiku-4-5", input_tokens=1800, output_tokens=400)
```

The guard records actual usage after each call so session totals
are accurate, not estimated.

---

## Model Selection at Decision Points

When choosing a model for a task, work through this in order:

```
1. Can a free CLI tool do this?          → Use it
2. Is the task atomic and well-defined?  → Haiku
3. Does it require reasoning/judgment?   → Sonnet
4. Is it a one-time architectural call?  → Opus (explicit approval)
5. Does it require reading a large file? → Gemini CLI (free)
```

The question is not "what is the best model for this?" —
it is "what is the cheapest model that handles this correctly?"

---

## Prompt Efficiency Rules

1. **System prompts are reused, not regenerated.** Cache-friendly
   prompts (stable prefix, variable suffix) reduce input token cost
   significantly at scale.

2. **Do not pass context the model does not need.** Every token in
   the prompt is a token billed. Subagent prompts should contain
   exactly what is required for the task.

3. **Streaming is preferred for user-facing calls.** It does not
   reduce cost, but it surfaces runaway responses early so they
   can be cancelled.

4. **Log token usage after every call.** Surprises compound. A call
   that costs $0.03 when expected to cost $0.003 is a signal —
   either the estimation was wrong or the prompt is inefficient.

---

## TASK_LEDGER.md — Cost Tracking

Every significant API call is logged in TASK_LEDGER.md:

```markdown
| Date       | Task                        | Model   | Input tok | Output tok | Cost est. | Outcome |
|------------|-----------------------------|---------|-----------|------------|-----------|---------|
| 2026-04-10 | Orchestrator decomposition  | Sonnet  | 1,200     | 800        | $0.016    | Done    |
```

This is not bureaucracy. It is the data that lets you answer
"how much does this project cost to run?" — a question every
technical stakeholder will eventually ask.
