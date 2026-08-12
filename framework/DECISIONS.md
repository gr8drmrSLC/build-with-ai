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

## ADR-013 — Gemini CLI removed from the framework
**Date**: 2026-08-12
**Decision**: Removed Gemini CLI from every reference across the framework (`CLAUDE.md`'s Agent Delegation Policy and Model Selection Rule, `AI_DELEGATION_POLICY.md`'s Agent Capability Matrix, Model Selection Rule, and its dedicated "Gemini CLI — Specific Rules" section, `BUDGET_POLICY.md`'s tool cost table and decision tree, `ORCHESTRATION_PROTOCOL.md`'s subagent list and delegate table, `TASK_LEDGER.md`'s cost reference) and the live demo's orchestrator system prompt (`demo/src/components/OrchestratorPanel.tsx`), folding "large context reading" into Sonnet everywhere it appeared.
**Context**: A downstream project (V2R Enterprise Knowledge) found and fixed this same staleness in its own adapted copy of `AI_DELEGATION_POLICY.md` after Google discontinued the free "Gemini Code Assist for individuals" tier this framework's guidance depended on, confirmed directly (`gemini -p "..."` → `IneligibleTierError`, a full client discontinuation, not a paid-tier gate). This framework, the actual source document, still referenced it everywhere, including a live, functional reference in the demo's system prompt that could assign a real user's project phase to a tool that no longer runs.
**Rejected alternatives**: Fixing only the most visible reference (`CLAUDE.md`) and assuming the rest was clean (rejected: a full-repo search found five more files still referencing it after the first fix, not assumed clean without checking). Leaving the demo component unfixed since it is UI code, not documentation (rejected: `ARCHITECTURE.md` already states the demo must not drift from the framework's own methodology; leaving it stale here would violate that on the first real check).
**Reason**: A documented-but-broken tool costs the same trust and time the Wall Protocol and senior-engineer heuristic exist to prevent. Verified the `.tsx` edit did not break anything: `npx tsc -b --noEmit` passes clean, 0 errors.

---

## ADR-012 — Tracking Documents convention added to CONVENTIONS.md
**Date**: 2026-08-12
**Decision**: Added a "Duplicate tracking lists" anti-pattern and a new "Tracking Documents" rule to `CONVENTIONS.md`: when a repository needs a single view of many items' status, exactly one file is that tracker, and every other document that would restate the same fact links to it instead. States that a written rule alone does not hold this in practice; it needs an automated check that fails when a tracker and its source disagree.
**Context**: A downstream project built on this framework (V2R Enterprise Knowledge) experienced real, repeated drift: its own single-source-of-truth tracker fell out of sync with the documents it tracked three times in one session, and a separate bootstrap reading-order document went stale for over a week without anyone noticing, both because two documents independently recorded the same fact with no automated check that they still agreed. The fix that actually worked there was collapsing the duplicate into a single pointer plus a validator check and pre-commit hook, not a written reminder.
**Rejected alternatives**: Leaving this as project-specific knowledge in V2R's own repository (rejected: this framework is the template other projects, including a planned accounting repository, will bootstrap from; each one re-deriving this lesson after its own first drift incident does not scale). Writing only the anti-pattern without the prescriptive rule (rejected: naming a failure mode is not the same as telling the next project what to do instead).
**Reason**: This framework already names "single source of truth" as a value (`ARCHITECTURE.md`'s demo/methodology relationship, `CONVENTIONS.md`'s magic-strings anti-pattern) but had never stated it as a rule for documentation and tracking specifically, the exact gap that caused real drift downstream.

---

## ADR-011 — RETROFIT_GUIDE.md validated end-to-end on finances-2025
**Date**: 2026-06-12
**Decision**: Treat the `finances-2025` retrofit (Priority 1 on 2026-06-11, Priority 3 + relevant Priority 4 on 2026-06-12) as the framework's first full end-to-end validation of `RETROFIT_GUIDE.md`'s priority ordering on a real, non-framework project.
**Context**: `RETROFIT_GUIDE.md` (added Session 2) listed "job bot + ARIA" as known retrofit targets, but both are already part of this ecosystem and share conventions. `finances-2025` is a single-developer Python/SQLite project handling real personal/business PII, with no prior framework adoption beyond an initial Priority-1 pass — a colder, more realistic test of whether "safety first, cost/quality second" actually surfaces the right issues in the right order.
**Rejected alternatives**: Treating the retrofit as routine project work with no framework-level record; waiting for a larger/more complex target project before calling the guide "validated."
**Reason**: The Priority-1 pass on finances-2025 caught a genuine, previously-unnoticed gap — source-document folders (`personal/`, `great-self-llc/`, `rental-pueblo/*`) that real W-2s/1099s/bank exports get dropped into were not gitignored, risking real PII landing in a (private) GitHub repo on the next `git add`. That is exactly the class of issue Priority 1 ("Safety") is meant to catch before anything else. Recording this as an ADR closes the loop: the guide was written, then independently exercised against a real project, and it worked as designed.

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
