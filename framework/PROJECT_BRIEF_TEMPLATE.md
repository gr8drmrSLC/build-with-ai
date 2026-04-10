# PROJECT_BRIEF_TEMPLATE.md

Fill out this document completely before opening the first Claude Code
session. The more complete this is, the less time the first session
spends on scope clarification.

When done, keep this file in the repo as the project's origin document.
Do not delete it — it is the record of what you knew and decided before
any code was written.

---

## Project name

[One line. This becomes the repo name and the name used throughout all
framework files.]

## What this project does

[2–4 sentences. What does it do, for whom, and why does it need to
exist? Avoid implementation details here — just the purpose.]

## What kind of project is this?

Check all that apply:
- [ ] Automated system / bot (runs without active user input)
- [ ] Web application (user-facing UI)
- [ ] API or backend service
- [ ] Data pipeline or ETL
- [ ] CLI tool or script
- [ ] AI agent or multi-agent system
- [ ] Portfolio / demo piece
- [ ] Retrofit of an existing project

## What does success look like?

[Describe the minimum state at which this project is "done enough to
use." Not perfect — just working. One paragraph.]

## What are the hard constraints?

[Things that cannot be changed regardless of what seems easiest.
Examples: must run on AWS, must use Python, must not exceed $X/month,
must be publicly accessible, must integrate with existing system Y.]

---

## Architecture sketch

### What it calls (external dependencies)

| Service / API        | Purpose                        | Auth method           |
|----------------------|--------------------------------|-----------------------|
| [e.g. Anthropic API] | [e.g. LLM inference]           | [e.g. API key in .env]|

### What it stores

| Data type            | Where                          | Retention             |
|----------------------|--------------------------------|-----------------------|
| [e.g. session logs]  | [e.g. SQLite local]            | [e.g. 30 days]        |

### How it runs

- [ ] Long-running process (daemon / service)
- [ ] Scheduled job (cron / systemd timer)
- [ ] On-demand CLI invocation
- [ ] Web server (always-on)
- [ ] Serverless / event-driven

### Deployment target

[Where does this run in production? Examples: local machine only,
EC2 t3.micro, Lambda, GitHub Pages + Cloudflare Worker, Fly.io]

---

## Open questions

[List anything you are not sure about before building. These become
the first agenda items for the opening session. Better to name them
here than to discover them mid-build.]

1.
2.
3.

---

## What already exists

[If this is a retrofit or build-on-top, describe what is already
built and working. If greenfield, write "nothing — starting from
scratch."]

---

## Budget

### Hard cap (monthly, all-in)
$[amount]

### Expected spend breakdown
| Service              | Est. monthly cost | Notes                  |
|----------------------|-------------------|------------------------|
| [e.g. Anthropic API] | $[amount]         | [e.g. ~500 Haiku calls]|

### Behavior when cap is approached
[e.g. alert at 80%, stop all API calls at 100%, notify via email]

---

## Security considerations

### What secrets does this project require?

| Secret               | Where stored           | Who has access        |
|----------------------|------------------------|-----------------------|
| [e.g. API key]       | [e.g. .env, not committed] | [e.g. deployer only] |

### Is any part of this publicly accessible?

- [ ] Yes — public URL or public repo
- [ ] No — internal/local only

If yes: which secrets are in scope of the public surface? Run the
pre-deployment checklist in `SECURITY.md` before the first deployment.

---

## First task

[What is the very first thing that should be built or done in the
first session? Be specific. This prevents the first session from
spending time deciding where to start.]

Example: "Scaffold the repo structure: .gitignore first, then
framework/ directory with CLAUDE.md, PROJECT_STATUS.md, DECISIONS.md."

---

## Decisions already made

[List any architectural decisions that were made before the first
session — things the agent should not relitigate. Each one will
become an ADR in DECISIONS.md.]

| Decision             | Chosen                 | Rejected               | Why                   |
|----------------------|------------------------|------------------------|-----------------------|
| [e.g. language]      | [e.g. Python]          | [e.g. Node.js]         | [e.g. existing infra] |
