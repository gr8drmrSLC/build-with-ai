# CHANGELOG.md

All significant changes to this project are documented here.
Format: date, what changed, and why it mattered.

---

## 2026-04-12

### Session 2 — Status sync + bootstrap layer completion

**Updated** `framework/PROJECT_STATUS.md` — reflected current state accurately;
prior version was stale from Session 1 end.

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
