# DECISIONS.md — Architecture Decision Records

This file records significant decisions made during development:
what was decided, why, and what was rejected. New decisions are
added at the top. Do not delete old records — they are the
reasoning history of the project.

Format per entry:
- **Decision**: what was chosen
- **Context**: why this decision came up
- **Rejected alternatives**: what else was considered
- **Reason**: why this option won

---

## ADR-010 — Public Endpoint Security Gate added to CLAUDE.md
**Date**: 2026-05-05
**Decision**: Three mandatory questions added to `CLAUDE.md` as a required pre-production gate for any public route that touches a paid external API: (1) Can a bot hit this in a loop? (2) Does each hit trigger a paid API call? (3) What is the worst-case cost at 100,000 hits?
**Context**: A real incident on a separate project resulted in 148,277 SMS messages ($1,235) over three days from a runaway webhook feedback loop (initially misdiagnosed as bot abuse). Investigation revealed neither the developer nor the AI considered the failure path. The three questions are now applied at Sprint 1, not after go-live.
**Rejected alternatives**: Adding as a SECURITY.md checklist item only (easily skipped); relying on budget guards alone (guards stop overspend but don't prevent the root failure).
**Reason**: CLAUDE.md is loaded every session and enforced as mandatory. A gate in CLAUDE.md is unconditional. A gate in a checklist is aspirational.

---

## ADR-009 — LinkedIn session self-contained per project
**Date**: 2026-05-05
**Decision**: Each project stores its own `scripts/linkedin_session.json` and `scripts/save_linkedin_session.py`. No shared dependency on the job-search repo.
**Context**: Both `post_linkedin_daily.py` (build-with-ai) and `update_linkedin.py` (ARIA) originally pointed to `../job-search/data/sessions/linkedin_session.json` as the session source. This created a hidden cross-repo dependency — if the job-search directory structure changed or the project was cloned fresh, LinkedIn posting silently broke.
**Rejected alternatives**: Shared session file in a common `~/shared/` directory; keeping the job-search dependency.
**Reason**: Each project should be runnable in isolation from a fresh clone. LinkedIn sessions are short-lived credentials — each project manages its own independently. `save_linkedin_session.py` in each project makes the setup reproducible with one command.

---

## ADR-008 — Agent Teams lead model: Sonnet, not Opus
**Date**: 2026-04-12
**Decision**: In the Agent Teams pattern, the orchestration/lead role uses Sonnet, not Opus.
**Context**: An Agent Teams configuration was proposed with Opus 4.6 as lead. Orchestration tasks (planning, routing, synthesis) are the highest-token workload in any session — the lead reads full project context repeatedly. Opus at $15/M input + $75/M output makes this significantly expensive as a default.
**Rejected alternatives**: Opus as permanent lead.
**Reason**: Sonnet handles orchestration well at $3/M input + $15/M output — 5× cheaper. Opus is reserved for a single hard architectural decision where the cost is justified by irreversibility. It is not justified as a session-level default. The Opus reservation rule is already in AI_DELEGATION_POLICY.md; this ADR applies it explicitly to the teams pattern.

---

## ADR-007 — src/core/ as reference implementations, not just stubs
**Date**: 2026-04-12
**Decision**: The `src/core/` modules in this repo are working reference implementations, not placeholder stubs.
**Context**: `bootstrap.sh` creates stubs in target projects. The question was whether this repo should also contain only stubs (simpler) or full implementations (more useful as a reference).
**Rejected alternatives**: Stubs only in this repo, pointing users to documentation.
**Reason**: A framework that documents patterns but does not demonstrate them is weaker than one that does both. The reference implementations are also the test subjects for `smoke_test.py`. Keeping them working and tested means the framework itself stays honest — if a module is broken, the smoke test says so.

---

## ADR-006 — Cloudflare Worker proxy for OrchestratorPanel API calls
**Date**: 2026-04-10
**Decision**: OrchestratorPanel calls a Cloudflare Worker proxy, not the Anthropic API directly. The API key is stored as a Cloudflare Worker secret — never in the JS bundle, never in the repo.
**Context**: Three approaches were evaluated after the initial direct-browser approach was found to combine badly with public deployment. See PROJECT_NARRATIVE Entry 006 for the full decision progression. The two rejected approaches were: (1) build-time env var — key ends up in public JS bundle; (2) user-supplied key field — creates friction and looks like credential harvesting.
**Rejected alternatives**: Build-time VITE_ANTHROPIC_API_KEY (ADR-005, superseded); user-supplied key input in UI.
**Reason**: Key never leaves the server. Visitor experience is seamless. Cloudflare Worker free tier handles portfolio demo traffic with no cost. Rate limiting (10 req/IP/hour via KV) and a hard Anthropic Console spend cap ($20/month) prevent abuse.
**Supersedes**: ADR-005.

---

## ADR-005 — Claude API called directly from browser (dangerouslyAllowBrowser)
**Date**: 2026-04-10
**Decision**: OrchestratorPanel calls the Anthropic API directly from the browser using `dangerouslyAllowBrowser: true`.
**Context**: See ADR-006 — this decision was reversed.
**Superseded by**: ADR-006.

---

## ADR-004 — .gitignore committed before all other files
**Date**: 2026-04-10
**Decision**: The `.gitignore` is always the first commit in any repo using this framework.
**Context**: Secrets are the most catastrophic thing to accidentally commit. Once in git history, rotation alone is insufficient.
**Reason**: Sequencing it first makes the protection unconditional.

---

## ADR-003 — GitHub Actions for Pages deployment, not gh-pages npm package
**Date**: 2026-04-10
**Decision**: GitHub Actions workflow deploys `demo/dist` to GitHub Pages.
**Reason**: Path filtering means framework file changes don't trigger unnecessary builds. No extra branch. Native to GitHub.

---

## ADR-002 — Single repo, two subdirectories
**Date**: 2026-04-10
**Decision**: `framework/` and `demo/` live in the same repo.
**Reason**: The React app fetches and renders `framework/*.md` files live. Separate repos would introduce sync drift and split the story across two URLs.

---

## ADR-001 — Vite + TypeScript over Create React App
**Date**: 2026-04-10
**Decision**: React demo scaffolded with Vite + TypeScript.
**Reason**: CRA is deprecated. Vite is fast, actively maintained, pairs cleanly with GitHub Pages static hosting.
