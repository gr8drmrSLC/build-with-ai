# ARCHITECTURE.md

System design for build-with-ai. Read this to understand how the
pieces relate before reading any individual file.

---

## System Overview

Two subsystems, one repo, one story:

```
build-with-ai/
├── framework/          ← The methodology (files, policy, src/core/)
└── demo/               ← The proof (React app that demonstrates it)
```

The framework is the product. The demo is the interface to it.
The repo is the artifact that proves both exist and are consistent.

---

## Component Map

### framework/

```
framework/
│
├── PLANNING & CONTEXT
├── CLAUDE.md               ← Auto-loaded by Claude Code; session protocols
├── PROJECT_STATUS.md       ← Current state; read first every session
├── DECISIONS.md            ← ADR log; why things were built this way
├── PROJECT_NARRATIVE.md    ← Living "how we thought" story; fetched by demo
├── ARCHITECTURE.md         ← This file
│
├── POLICY FILES (planned)
├── CONVENTIONS.md          ← Code style, naming, file organization
├── DEVELOPMENT_PROTOCOL.md ← 8-step regression safety with examples
├── AI_DELEGATION_POLICY.md ← Agent capability matrix, Wall Protocol
├── GIT_POLICY.md           ← Commit rules, branching, what never commits
├── SECURITY.md             ← Threat model, secret handling, commit hygiene
├── BUDGET_POLICY.md        ← Spend limits, model selection rules
├── BACKUP_POLICY.md        ← Data survival, recovery tiers
├── INFRASTRUCTURE_POLICY.md← AWS + Cloudflare rules
├── ORCHESTRATION_PROTOCOL.md← Multi-agent delegation framework
├── PROJECT_BRIEF_TEMPLATE.md← PM planning template
├── TASK_LEDGER.md          ← Cost + completion tracker
├── USER_MANUAL.md          ← Operator-facing documentation
│
├── BACKLOG
└── RETROFIT_GUIDE.md       ← Checklist for applying framework to
                               existing projects (job bot, ARIA)
│
└── src/core/ (planned)
    ├── budget_guard.py         ← API spend enforcement
    ├── agent_dispatcher.py     ← Orchestrator/subagent spawner
    ├── task_schema.py          ← AtomicTask contract
    ├── logging_config.py       ← Sanitized logging (no secrets in logs)
    ├── config.py               ← Env-only settings loader
    ├── rate_limiter.py         ← Web-facing protection
    └── aws_config_validator.py ← Pre-deploy infrastructure check
```

### demo/

```
demo/
├── src/
│   ├── App.tsx                 ← Three-panel layout, header, View Source link
│   ├── components/
│   │   ├── MethodologyPanel.tsx← Left: 6-step walkthrough (static content)
│   │   ├── OrchestratorPanel.tsx← Center: live Claude API call
│   │   └── CaseStudyPanel.tsx  ← Right: fetches PROJECT_NARRATIVE.md live
│   └── App.css                 ← Dark theme, responsive grid
├── vite.config.ts              ← base: '/build-with-ai/' for Pages routing
└── package.json
```

---

## How the Demo Fetches Framework Files

CaseStudyPanel fetches `framework/PROJECT_NARRATIVE.md` at runtime
from the GitHub raw content API — no build step, no copy, always
in sync with the repo.

```
GET https://raw.githubusercontent.com/gr8drmrSLC/build-with-ai/master/framework/PROJECT_NARRATIVE.md
```

The response is plain Markdown text, rendered in the panel.
This means the case study is always the authoritative version —
whatever is committed to `master` is what the demo shows.

**Why this matters architecturally**: the demo cannot drift from
the methodology. They share a single source of truth.

---

## Data Flow

```
User opens demo (GitHub Pages)
    │
    ├── MethodologyPanel renders static 6-step content
    │
    ├── OrchestratorPanel waits for user input
    │   └── User enters project idea
    │       └── POST /v1/messages (Claude API, proxied or direct)
    │           └── Response streamed into panel
    │
    └── CaseStudyPanel mounts
        └── GET raw.githubusercontent.com/.../PROJECT_NARRATIVE.md
            └── Markdown rendered in panel
```

---

## Deployment Architecture

```
Local dev          →  npm run dev (Vite HMR, localhost:5173)
Push to master     →  GitHub Actions triggers (demo/** path filter)
                       → npm ci + npm run build (demo/)
                       → Upload demo/dist to GitHub Pages artifact
                       → Deploy to gr8drmrSLC.github.io/build-with-ai/
```

Path filter means changes to `framework/` alone do not trigger
a rebuild. Only `demo/` changes or workflow changes trigger deploy.
Framework files are fetched at runtime, not at build time.

---

## Security Boundary

```
Safe to commit:     framework/*.md, demo/src/**, vite.config.ts
Never commit:       .env, .env.*, *.pem, *.key, any API key
Claude API key:     Loaded from environment only (config.py pattern)
                    In demo: loaded from .env.local (gitignored),
                    or injected via GitHub Actions secret
```

See `SECURITY.md` (planned) for full threat model.

---

## ADR Index

| ADR   | Decision                                    | File            |
|-------|---------------------------------------------|-----------------|
| 001   | Vite + TypeScript over CRA or Next.js       | DECISIONS.md    |
| 002   | Single repo, two subdirectories             | DECISIONS.md    |
| 003   | GitHub Actions over gh-pages npm package    | DECISIONS.md    |
| 004   | .gitignore committed before all other files | DECISIONS.md    |

New ADRs are added to DECISIONS.md and indexed here.

---

## Portability Note

Every file in `framework/` is designed to be copied into any new
project and used immediately. The `src/core/` modules are standalone
— no framework-specific dependencies. The `.md` policy files are
plain text — no tooling required to use them.

This is intentional. A framework that requires its own infrastructure
to install is not a framework — it is a product. This one is a set
of practices you carry.
