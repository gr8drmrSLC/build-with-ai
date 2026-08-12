# CHANGELOG.md

All significant changes to this project are documented here.
Format: date, what changed, and why it mattered.

---

## 2026-08-12 — Session 5 — Tracking Documents convention + Gemini CLI removal

### Tracking Documents convention added

**Added** `framework/CONVENTIONS.md`: a "Duplicate tracking lists" anti-pattern
and a new "Tracking Documents" rule (one tracker, everything else points to
it, enforced by an automated check, not just a written reminder). Prompted by
real, repeated documentation drift found and fixed in a downstream project
(V2R Enterprise Knowledge) built on this framework. See `DECISIONS.md`
ADR-012.

### Gemini CLI removed

**Removed** every Gemini CLI reference across the framework: `CLAUDE.md`,
`AI_DELEGATION_POLICY.md` (including its dedicated "Gemini CLI — Specific
Rules" section), `BUDGET_POLICY.md`, `ORCHESTRATION_PROTOCOL.md`,
`TASK_LEDGER.md`, and the live demo's orchestrator system prompt
(`demo/src/components/OrchestratorPanel.tsx`), folding "large context
reading" into Sonnet everywhere it appeared. Prompted by the same downstream
project confirming Google discontinued the free tier this framework's
guidance depended on. Verified the demo edit with `npx tsc -b --noEmit`,
0 errors. See `DECISIONS.md` ADR-013.

---

## 2026-06-11 — Session 4 — LinkedIn series completion + framework validation

### LinkedIn series complete (12/12)

**Added** `framework/PROJECT_NARRATIVE.md` Entry 007 — "The Feedback Loop: What
the Bot Attack Was Not", a post-incident case study revisiting the Session 3
incident with corrected analysis.

**Fixed** `scripts/capture_demo_screenshot.py` — resize LinkedIn screenshots to
1080x1350 (LinkedIn's correct image aspect ratio, superseding the Session 3
900px height cap); added a recapture helper script for re-generating existing
screenshots.

**Added** `worker/package-lock.json` — pins Worker dependency versions for
reproducible installs.

**Marked** the LinkedIn 12-post series complete — all posts sent 2026-04-13
through 2026-05-22 (confirmed via `scripts/linkedin_post_state.json` and
`scripts/linkedin_post.log`). The daily Task Scheduler job now runs as a no-op
("All posts have been sent. Nothing to do.").

### Framework validation: finances-2025 retrofit

**Applied** `framework/RETROFIT_GUIDE.md` end-to-end to `finances-2025`
(private repo, real personal/business tax recordkeeping) — Priority 1 (safety
+ smoke test, 2026-06-11) and Priority 3 plus relevant Priority 4 items
(cost/quality + governance docs: ruff, `budget_guard.py`, `BUDGET_POLICY.md`,
`GIT_POLICY.md`, `CONVENTIONS.md`, `DEVELOPMENT_PROTOCOL.md`,
`BACKUP_POLICY.md`, `TASK_LEDGER.md`, 2026-06-12). This is the first full
real-world application of the guide's priority ordering, and it caught a real
gitignore/PII gap (source-document folders were untracked-but-not-ignored)
during the Priority 1 pass. See `finances-2025/PROJECT_STATUS.md` and
`DECISIONS.md` for the full record.

---

## 2026-05-05 — Session 3 — Security hardening

**Added** ADR-010 (Public Endpoint Security Gate) and ADR-009 (LinkedIn
session self-contained per project) to DECISIONS.md.

**Added** Public Endpoint Security Gate to `framework/CLAUDE.md` — three
mandatory questions before any public route goes live: can a bot hit it in a
loop, does each hit trigger a paid API call, and what is the worst-case cost
at 100,000 hits. Motivated by a real incident on a separate project: 148,277
SMS messages ($1,235) over three days from a runaway webhook feedback loop,
initially misdiagnosed as bot abuse.

**Fixed** `worker/src/index.ts` — rate limiting is now fail-closed, returning
503 if `RATE_LIMIT_KV` is not bound instead of silently skipping the check.

**Updated** `framework/SECURITY.md` — threat model expanded to cover bot abuse
and the notification feedback-loop failure mode; pre-deployment checklist
updated accordingly.

**Fixed** LinkedIn posting pipeline — `build-with-ai` and ARIA each now store
their own `scripts/linkedin_session.json` and `scripts/save_linkedin_session.py`,
removing a hidden cross-repo dependency on the job-search repo's session file.

**Fixed** `scripts/capture_demo_screenshot.py` — capped screenshot height at
900px for correct LinkedIn aspect ratio (later superseded by the Session 4
1080x1350 resize).

**Added** EC2 deployment vars to `.env.example`.

---

## 2026-04-12

### Session 2 — Framework completion + src/core/ executable layer

**Added** `framework/ORCHESTRATION_PROTOCOL.md` — session pattern, handoff
document format, context budget rules, multi-agent sequencing, and Agent
Teams pattern with file ownership rules and spawn prompt template.

**Added** `framework/INFRASTRUCTURE_POLICY.md` — deployment target decision
tree, environment separation, Cloudflare Worker setup and CORS rules, AWS
baseline (EC2, IAM, systemd), GitHub Actions deploy rules.

**Added** `framework/BACKUP_POLICY.md` — what needs backup vs. what git handles,
secrets backup via password manager, S3 encrypted backup pattern, recovery
runbook requirements, verification protocol.

**Added** `framework/TASK_LEDGER.md` — cost tracking log template with column
definitions, cost formula, and first real Session 1 entries (~$0.49 total).

**Added** `framework/RETROFIT_GUIDE.md` — secrets scan procedure, gap audit
checklist, priority-ordered additions (safety → continuity → cost → full
coverage), retrofit checklist template, known targets (job bot + ARIA).

**Added** `src/core/` — seven reference implementation modules:
`config.py` (typed settings + startup validation),
`budget_guard.py` (per-call and session spend enforcement),
`logging_config.py` (structured JSON/text logging),
`rate_limiter.py` (token bucket, sync + async),
`task_schema.py` (Task, TaskResult, ComplexityTier Pydantic models),
`agent_dispatcher.py` (model selection, budget/rate check, API dispatch),
`aws_config_validator.py` (credential check, identity log, service probes).

**Added** `tests/smoke_test.py` — 14-test baseline covering all src/core/
modules. Live API call auto-skips on placeholder key. 14/14 passing.

**Added** `pyproject.toml` — dependencies declared, ruff configured (E, F, B,
S, T20, I rule sets), pytest path set.

**Added** `.env.example` — all required environment variables documented.

**Added** ADR-007 (src/core/ as reference implementations) and ADR-008
(Agent Teams lead model: Sonnet not Opus) to DECISIONS.md.

**Updated** `framework/PROJECT_STATUS.md` — all items complete.

---

## 2026-04-10 — Session 1 (bootstrap)

### Bootstrap layer

**Added** `bootstrap.sh` — one-command install of the framework into any new
project directory. Copies policy files, creates `src/core/` stubs, creates
`.env.example`, prints next-step instructions.

**Added** `framework/USER_MANUAL.md` — full workflow documentation: how to
install, how to run a first session, the core loop, what each file governs,
the non-negotiables. Closes the gap between reference library and reusable tool.

**Added** `framework/PROJECT_BRIEF_TEMPLATE.md` — pre-session planning template.
Architecture sketch, budget, secrets, open questions, decisions already made,
and a mandatory "first task" field. Prevents the first session from spending
time on scope clarification.

### Demo

**Fixed** `OrchestratorPanel` — replaced Anthropic SDK with direct `fetch()` +
manual SSE parsing. The SDK validates the API key format before making any
request and rejects `apiKey: 'proxied'`. Direct fetch has no such gate.

**Fixed** CORS — added `x-api-key` and `anthropic-beta` to `Access-Control-Allow-Headers`
in the Cloudflare Worker. The preflight was failing silently.

**Fixed** GitHub Actions trigger — workflow had `branches: [main]` but the repo
uses `master`. Changed to `branches: [main, master]`.

**Fixed** contrast — comprehensive pass across all three panels:
body text raised from #666→#999+, textarea background lightened to #222,
button colors raised to #e8e8e8 text on #333 background.

**Redesigned** `CaseStudyPanel` — replaced full-text markdown wall with entry
cards: title, phase tag, date, 3-line preview collapsed, inline Read more /
Show less toggle.

**Added** live demo URL to README.

### Security

**Deployed** Cloudflare Worker proxy (`build-with-ai-proxy.vision2reality.workers.dev`).
API key stored as Worker secret — never in the JS bundle, never client-side.
Rate limited to 10 requests/IP/hour via KV namespace.

**Superseded** ADR-005 (direct browser API call) with ADR-006 (Worker proxy).
The original approach combined with public GitHub Pages deployment to create
a latent key exposure. Key was rotated as precaution. See PROJECT_NARRATIVE
Entries 004–006 for the full account.

**Added** pre-deployment security checklist to `SECURITY.md` — four questions,
with question 4 ("is any secret one natural-next-step away from being in scope?")
being the one the original architecture missed.

### Framework files

11 policy files written and committed in Session 1:

| File | What it governs |
|------|----------------|
| `CLAUDE.md` | Session protocol, 8-step safety, Wall Protocol, delegation |
| `DECISIONS.md` | ADR-001 through ADR-006 |
| `PROJECT_STATUS.md` | Current project state |
| `PROJECT_NARRATIVE.md` | How we thought — 8 entries |
| `ARCHITECTURE.md` | Component map, data flow, deployment |
| `AI_DELEGATION_POLICY.md` | Capability matrix, model selection |
| `SECURITY.md` | Threat model, secret handling, incident response |
| `BUDGET_POLICY.md` | Spend limits, cost reference, budget_guard pattern |
| `GIT_POLICY.md` | Commit rules, branching, .gitignore requirements |
| `DEVELOPMENT_PROTOCOL.md` | 8-step safety protocol with examples |
| `CONVENTIONS.md` | Python + TypeScript style, file organization |

### Git

**Added** `.gitignore` as the first commit — before any other file.
The `!.env.example` negation required its comment on a separate line;
inline comments break gitignore negation parsing.

---

*Earlier entries will not be backfilled — git log is the authoritative
record for changes before this file existed.*
