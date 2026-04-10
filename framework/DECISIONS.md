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

## ADR-006 — Cloudflare Worker proxy for OrchestratorPanel API calls
**Date**: 2026-04-12
**Decision**: OrchestratorPanel calls a Cloudflare Worker proxy, not the Anthropic API directly. The API key is stored as a Cloudflare Worker secret — never in the JS bundle, never in the repo.
**Context**: Three approaches were evaluated after the initial direct-browser approach was found to combine badly with public deployment. See PROJECT_NARRATIVE Entry 006 for the full decision progression. The two rejected approaches were: (1) build-time env var — key ends up in public JS bundle; (2) user-supplied key field — creates friction and looks like credential harvesting.
**Rejected alternatives**: Build-time VITE_ANTHROPIC_API_KEY (ADR-005, superseded); user-supplied key input in UI.
**Reason**: Key never leaves the server. Visitor experience is seamless. Cloudflare Worker free tier handles portfolio demo traffic with no cost. Rate limiting (10 req/IP/hour via KV) and a hard Anthropic Console spend cap ($20/month) prevent abuse. This is also the architecture documented in INFRASTRUCTURE_POLICY.md — the demo runs on its own framework.
**Cost analysis**: Haiku at $0.25/M input + $1.25/M output. Typical decomposition: ~800 input + ~500 output tokens = ~$0.001 per run. 1,000 demo runs/month = $1.00. Hard cap at $20/month provides 20× headroom. Cloudflare Worker free tier: 100K requests/day — not a constraint.
**Supersedes**: ADR-005 (direct browser call — that decision is now reversed and documented as a failure mode in PROJECT_NARRATIVE Entries 004–006).

---

## ADR-005 — Claude API called directly from browser (dangerouslyAllowBrowser)
**Date**: 2026-04-12
**Decision**: OrchestratorPanel calls the Anthropic API directly from the browser using `dangerouslyAllowBrowser: true`. The API key is injected at build time via `VITE_ANTHROPIC_API_KEY` in `.env.local`.
**Context**: Browser → API directly exposes the key to anyone who opens DevTools on the deployed page. The production-correct approach is a thin server-side proxy (Cloudflare Worker, Vercel Edge Function) that holds the key and forwards requests. At the decision point, two options were surfaced: (1) direct browser call with documented tradeoff, (2) Cloudflare Worker proxy. Option 1 was recommended and confirmed.
**Rejected alternatives**: Cloudflare Worker proxy; Vercel Edge Function proxy. Both are correct production approaches — rejected here because infrastructure complexity (second deployment, secrets in a second service, CORS config) is not justified for a personal portfolio demo where the deployer controls access.
**Reason**: This is a portfolio demo, not a user-facing product. The tradeoff is flagged in the source code directly above the API call and documented here. The component is structured so the client initialization is a single swap if a proxy is added later.
**Trigger for revisiting**: If this demo becomes publicly accessible with open access (e.g., shared on social media with no auth), add the proxy. The key in a build artifact is readable by anyone with DevTools. For a controlled demo (shared directly with interviewers), the risk is acceptable.

---

## ADR-004 — .gitignore committed before all other files
**Date**: 2026-04-12
**Decision**: The `.gitignore` is always the first commit in any repo using this framework.
**Context**: Secrets (`.env`, API keys, PEM files) are the most catastrophic thing to accidentally commit. Once in git history, rotation alone is insufficient — the history must be rewritten. Prevention is cheaper than recovery.
**Rejected alternatives**: Adding `.gitignore` as part of an initial scaffold commit alongside other files.
**Reason**: Sequencing it first makes the protection unconditional. It cannot be forgotten if it is the precondition for everything else.

---

## ADR-003 — GitHub Actions for Pages deployment, not gh-pages npm package
**Date**: 2026-04-12
**Decision**: GitHub Actions workflow (`deploy.yml`) deploys `demo/dist` to GitHub Pages.
**Context**: Two common approaches: `gh-pages` npm package (pushes to a `gh-pages` branch) or GitHub Actions (uploads artifact directly). Chosen for a monorepo where only `demo/` should trigger deploys.
**Rejected alternatives**: `gh-pages` npm package run manually or via a deploy script.
**Reason**: GitHub Actions allows path filtering (`paths: demo/**`) so framework file changes don't trigger unnecessary builds. No extra branch to manage. Native to GitHub — no extra package dependency.

---

## ADR-002 — Single repo, two subdirectories
**Date**: 2026-04-12
**Decision**: `framework/` and `demo/` live in the same repo (`build-with-ai`).
**Context**: Initial question was whether to separate the framework files and the React demo into two repos.
**Rejected alternatives**: Separate repos — `ai-project-framework` for the methodology files, `build-with-ai-demo` for the React app.
**Reason**: The React app fetches and renders `framework/*.md` files live via the GitHub raw content API. Separate repos would require cross-repo URL coupling, introduce sync drift, and split the story across two URLs. Single repo means one link to share, and the demo is always in sync with the files it demonstrates.

---

## ADR-001 — Vite + TypeScript over Create React App
**Date**: 2026-04-12
**Decision**: React demo scaffolded with Vite + TypeScript (`react-ts` template).
**Context**: CRA is officially deprecated. Vite is the current standard for React scaffolding.
**Rejected alternatives**: Create React App; Next.js.
**Reason**: Vite is fast, actively maintained, and pairs cleanly with GitHub Pages static hosting. Next.js adds SSR complexity that a static demo doesn't need — and would complicate the GitHub Pages deploy (Pages serves static files; Next.js requires a Node server or adapter).
