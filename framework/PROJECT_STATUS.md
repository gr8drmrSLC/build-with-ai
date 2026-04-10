# PROJECT_STATUS.md

Last updated: 2026-04-10
Updated by: Claude Sonnet 4.6 (session: CORE FILES)

---

## Current State

The demo is functionally complete. All three panels have real content.
Framework core files are written. The repo is self-bootstrapping.

**GitHub**: https://github.com/gr8drmrSLC/build-with-ai
**Live demo**: Deploy wired — pending one manual step:
  repo Settings → Pages → Source → GitHub Actions
  (The push that added MethodologyPanel qualifies as the trigger —
  set Pages source and the deploy will run immediately.)

---

## What Is Built

### Infrastructure
- [x] `.gitignore` — committed first; `!.env.example` negation confirmed working
- [x] Repo skeleton — `framework/`, `demo/`, `README.md`
- [x] GitHub repo live: `gr8drmrSLC/build-with-ai`
- [x] GitHub Actions deploy workflow — path-filtered to `demo/**`

### Framework files (11 of ~18)
- [x] `CLAUDE.md` — session protocol, 8-step safety, Wall Protocol, delegation
- [x] `DECISIONS.md` — ADR-001 through ADR-005
- [x] `PROJECT_STATUS.md` — this file
- [x] `PROJECT_NARRATIVE.md` — Entry 001 (founding session) + Entry 002 (Wall Protocol)
- [x] `ARCHITECTURE.md` — component map, data flow, deployment, ADR index
- [x] `AI_DELEGATION_POLICY.md` — capability matrix, model selection, Wall Protocol detail
- [x] `SECURITY.md` — threat model, secret handling, secrets scan, incident response
- [x] `BUDGET_POLICY.md` — cost reference, spend limits, budget_guard pattern, TASK_LEDGER format
- [x] `GIT_POLICY.md` — non-negotiables, commit message rules, branching, .gitattributes
- [x] `DEVELOPMENT_PROTOCOL.md` — 8-step protocol with examples, scope creep rule, smoke test
- [x] `CONVENTIONS.md` — Python + TypeScript style, file organization, .env.example format

### Demo app (`demo/`)
- [x] Vite + TypeScript, dark theme, responsive three-panel layout
- [x] `MethodologyPanel` — 6-step walkthrough with principle lines
- [x] `OrchestratorPanel` — live Claude API streaming (Haiku); KNOWN TRADEOFF comment + ADR-005
- [x] `CaseStudyPanel` — fetches `PROJECT_NARRATIVE.md` live from GitHub raw API
- [x] Build verified clean (tsc + vite, 0 errors)
- [x] `demo/.env.example` — documents `VITE_ANTHROPIC_API_KEY`

---

## What Is Not Built Yet

### Framework files (remaining)
- [ ] `BACKUP_POLICY.md`
- [ ] `INFRASTRUCTURE_POLICY.md`
- [ ] `ORCHESTRATION_PROTOCOL.md`
- [ ] `PROJECT_BRIEF_TEMPLATE.md`
- [ ] `TASK_LEDGER.md`
- [ ] `USER_MANUAL.md`
- [ ] `RETROFIT_GUIDE.md` — **backlog** — retrofit checklist for job bot + ARIA

### `src/core/` Python modules
- [ ] `budget_guard.py`, `agent_dispatcher.py`, `task_schema.py`
- [ ] `logging_config.py`, `config.py`, `rate_limiter.py`, `aws_config_validator.py`
- [ ] Bootstrap: `pyproject.toml`, `.pre-commit-config.yaml`, `bootstrap.sh`, `.env.example`

### Repo hygiene
- [ ] Root `CHANGELOG.md`
- [ ] `demo/` — remove Vite boilerplate assets (hero.png, react.svg, vite.svg) and `index.css` reset conflicts

---

## Open Questions

None blocking.

**Pending manual action**: GitHub Pages source → "GitHub Actions"

---

## Next Task

Write root `CHANGELOG.md` to capture this session's work, then move to
`src/core/` Python modules — starting with `config.py` and `budget_guard.py`
as the two that the remaining modules depend on.

Alternatively: pivot to LinkedIn posts and PDF summary (Saturday deliverable 3 + 4)
now that the demo is demonstrable. User to direct.

---

## Backlog

- `RETROFIT_GUIDE.md` — gap audit, priority order, secrets scan on commit history,
  8-step protocol introduction, `retrofit_checklist.md` template.
  Real targets: job search bot, ARIA.
