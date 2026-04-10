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

## ADR-005 — Claude API called directly from browser (dangerouslyAllowBrowser)
**Date**: 2026-04-12
**Decision**: OrchestratorPanel calls the Anthropic API directly from the browser using `dangerouslyAllowBrowser: true`. The API key is injected at build time via `VITE_ANTHROPIC_API_KEY` in `.env.local`.
**Context**: Browser → API directly exposes the key to anyone who opens DevTools on the deployed page. The production-correct approach is a thin server-side proxy (Cloudflare Worker, Vercel Edge Function) that holds the key and forwards requests.
**Rejected alternatives**: Cloudflare Worker proxy; Vercel Edge Function proxy.
**Reason**: This is a personal portfolio demo, not a user-facing product. The deployer controls who accesses it. Adding a proxy introduces infrastructure complexity (a second deployment, secrets in a second service, CORS config) that isn't justified for the current use case. The tradeoff is documented here and flagged in the source code. If this demo ever becomes publicly accessible at scale, add the proxy — the component is already structured to swap the client initialization.

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
