# PROJECT_STATUS.md

Last updated: 2026-04-12
Updated by: Claude Sonnet 4.6 (session: CORE FILES)

---

## Current State

The repo skeleton is live and self-bootstrapping. A fresh Claude Code
session pointed at this repo can read this file and DECISIONS.md and
know exactly where to pick up — no verbal context required.

**GitHub**: https://github.com/gr8drmrSLC/build-with-ai
**Live demo**: Not yet deployed (GitHub Pages source must be set to
"GitHub Actions" in repo Settings → Pages — one manual step pending)

---

## What Is Built

### Infrastructure
- [x] `.gitignore` — committed first, before all other files
- [x] Repo skeleton — `framework/`, `demo/`, `README.md`
- [x] GitHub repo created and pushed (`gr8drmrSLC/build-with-ai`)
- [x] GitHub Actions deploy workflow (`.github/workflows/deploy.yml`)
  - Triggers on push to `main`/`master` when `demo/` changes
  - Builds `demo/dist`, uploads to GitHub Pages
  - **Pending**: Pages source must be set to "GitHub Actions" in repo settings

### Framework files
- [x] `framework/CLAUDE.md` — session protocol, 8-step safety, Wall Protocol, delegation policy
- [x] `framework/DECISIONS.md` — ADR-001 through ADR-004
- [x] `framework/PROJECT_STATUS.md` — this file

### Demo app (`demo/`)
- [x] Vite + TypeScript scaffolded
- [x] Three-panel layout skeleton — MethodologyPanel, OrchestratorPanel, CaseStudyPanel
- [x] Dark theme, responsive (collapses below 900px)
- [x] `base: '/build-with-ai/'` set in vite.config.ts for Pages routing
- [x] Build verified clean (tsc + vite, 0 errors)
- [ ] Panel content — all three panels show placeholders

---

## What Is Not Built Yet

### Framework files (priority order)
1. `framework/PROJECT_NARRATIVE.md` — the "how we thought" story; includes the
   self-referential insight: *"The brainstorming session that designed this
   framework was itself an example of the framework."*
2. `framework/ARCHITECTURE.md` — system design, component map, ADR index
3. `framework/CONVENTIONS.md` — code style, naming, file organization rules
4. `framework/DEVELOPMENT_PROTOCOL.md` — 8-step protocol expanded with examples
5. `framework/AI_DELEGATION_POLICY.md` — agent capability matrix, Wall Protocol detail
6. `framework/SECURITY.md` — threat model, secret handling, commit hygiene
7. `framework/BUDGET_POLICY.md` — spend limits, model selection rules
8. `framework/RETROFIT_GUIDE.md` — **backlog** — checklist for applying framework
   to existing projects (job bot, ARIA); see backlog section below
9. Remaining policy files from the brief (GIT_POLICY, BACKUP_POLICY, etc.)

### `src/core/` Python modules
- `budget_guard.py`, `agent_dispatcher.py`, `task_schema.py`,
  `logging_config.py`, `config.py`, `rate_limiter.py`,
  `aws_config_validator.py`
- Bootstrap files: `pyproject.toml`, `.pre-commit-config.yaml`,
  `bootstrap.sh`, `.env.example`

### Demo app — real content
- MethodologyPanel: 6-step methodology walkthrough
- OrchestratorPanel: live Claude API call (project idea → decomposition)
- CaseStudyPanel: fetches `framework/PROJECT_NARRATIVE.md` from GitHub raw API
- CHANGELOG.md (root level)

---

## Open Questions

None blocking. One pending manual action:
- Enable GitHub Pages: repo Settings → Pages → Source → GitHub Actions

---

## Next Task

Write `framework/PROJECT_NARRATIVE.md` — the living "how we thought" story.
First entry covers this founding session: problem identified, framework designed,
repo bootstrapped. Include the self-referential proof-of-methodology line.

---

## Backlog

- `framework/RETROFIT_GUIDE.md` — checklist for retrofitting this framework onto
  existing projects built without it. Real targets: job search bot, ARIA.
  Covers: gap audit, priority order (security first), one-time secrets scan on
  commit history, 8-step protocol introduction, `retrofit_checklist.md` template.
