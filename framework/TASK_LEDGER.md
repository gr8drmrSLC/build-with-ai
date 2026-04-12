# TASK_LEDGER.md

Running log of significant API calls made during this project.
Updated after any call that costs more than ~$0.01 or uses more
than 5,000 tokens. The goal is to answer "how much does this
project cost to run?" at any point in time.

See `BUDGET_POLICY.md` for spend limits and the model cost reference.

---

## Column definitions

| Column      | What to record                                                      |
|-------------|---------------------------------------------------------------------|
| Date        | YYYY-MM-DD                                                          |
| Session     | Short label for the work session (e.g. "Session 1", "bootstrap")   |
| Task        | One-line description of what the call was for                       |
| Model       | Model used (haiku, sonnet, opus, gemini, codex)                     |
| Input tok   | Approximate input tokens (estimate if exact not available)          |
| Output tok  | Approximate output tokens                                           |
| Cost est.   | Calculated cost in USD                                              |
| Outcome     | Done / Retry / Failed / Cancelled                                   |

---

## Cost formula

```
Cost = (input_tokens / 1,000,000 × input_price)
     + (output_tokens / 1,000,000 × output_price)

Haiku:  $0.25/M input  + $1.25/M output
Sonnet: $3.00/M input  + $15.00/M output
Opus:   $15.00/M input + $75.00/M output
Gemini: $0 (free tier)
Codex:  ~$0 (free tier)
```

---

## Ledger

| Date       | Session   | Task                                        | Model  | Input tok | Output tok | Cost est. | Outcome |
|------------|-----------|---------------------------------------------|--------|-----------|------------|-----------|---------|
| 2026-04-10 | Session 1 | OrchestratorPanel live demo — PBJ run       | Haiku  | ~800      | ~500       | $0.001    | Done    |
| 2026-04-10 | Session 1 | Framework file generation (11 .md files)    | Sonnet | ~8,000    | ~18,000    | $0.294    | Done    |
| 2026-04-10 | Session 1 | Demo component generation (3 TSX + CSS)     | Sonnet | ~6,000    | ~12,000    | $0.198    | Done    |

---

## Session totals

| Session   | Total cost est. | Notes                                          |
|-----------|-----------------|------------------------------------------------|
| Session 1 | ~$0.49          | Bootstrap session — framework + demo built end to end |
| Session 2 | —               | In progress                                    |

---

## Cumulative total

**~$0.49** (through Session 1)

---

*Add a row after any significant API call. Update session totals at
session close. The ledger is a record, not a real-time tracker —
estimate when exact counts are unavailable.*
