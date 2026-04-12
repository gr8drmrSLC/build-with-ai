# INFRASTRUCTURE_POLICY.md

Rules for infrastructure choices, deployment targets, and access
management across projects using this framework. Infrastructure
decisions made without a policy become undocumented dependencies —
the kind that cause incidents when someone assumes something that
was never written down.

---

## Deployment Target Selection

Choose the simplest option that meets the requirements. Infrastructure
complexity is a maintenance cost. Avoid it unless it buys something specific.

### Decision tree

```
Is this a static frontend only (HTML/CSS/JS, no server)?
  → GitHub Pages (free, zero ops, deploy via GitHub Actions)

Does it need server-side logic but must be cheap and stateless?
  → Cloudflare Worker (free tier: 100K req/day, globally distributed)

Does it need persistent compute — long-running process, daemon, scheduler?
  → EC2 t3.micro or t3.small (cheapest persistent compute on AWS)

Does it need to scale automatically and tolerate cold starts?
  → AWS Lambda (pay-per-invocation, no idle cost)

Does it need a managed container runtime?
  → Fly.io or Railway before ECS — lower ops overhead for small services
```

**Default for demos and portfolio pieces**: GitHub Pages + Cloudflare Worker.
Zero idle cost, globally available, no infrastructure to maintain.

**Default for bots and scheduled jobs**: EC2 t3.micro + systemd timer.
Predictable, cheap, easy to SSH into when something breaks.

---

## Environment Separation

Every project has at minimum two environments:

| Environment | Purpose                              | Where it runs           |
|-------------|--------------------------------------|-------------------------|
| Local       | Active development, testing changes  | Developer machine       |
| Production  | Live, committed, user-accessible     | Deployed target         |

Staging (a third environment matching production) is only added when:
- The production environment is business-critical (real users, real money)
- Or deploys have caused production incidents more than once

Do not add staging infrastructure speculatively. Add it when the cost
of a bad production deploy exceeds the cost of maintaining a third environment.

### Environment variables

Each environment gets its own `.env` file. None are committed.

```
.env.local      — local development (your machine)
.env.production — production values (never on developer machine)
.env.example    — committed template with no real values
```

The `.env.example` is the contract. It documents every variable the
application needs, with placeholder values and a comment explaining
each. It is the first thing a new contributor reads.

See `CONVENTIONS.md` for `.env.example` format rules.

---

## Cloudflare Workers

Workers are the preferred pattern for thin server-side logic that
fronts a public-facing frontend.

### When to use a Worker

- The frontend needs to make an API call whose key must not be client-side
- Rate limiting is required before requests hit a downstream service
- CORS needs to be enforced at the edge
- A simple transform or cache is needed between client and API

### Worker setup checklist

- [ ] Secret stored via `wrangler secret put SECRET_NAME` — never in `wrangler.toml`
- [ ] `ALLOWED_ORIGIN` set to the exact production URL — no wildcards in production
- [ ] CORS preflight (`OPTIONS`) handled explicitly — list every header the client sends
- [ ] Rate limiting bound to a KV namespace if abuse is plausible
- [ ] Worker name follows `{project-name}-proxy` convention
- [ ] `wrangler.toml` committed (it contains no secrets)

### CORS configuration

The most common Worker failure is a missing header in
`Access-Control-Allow-Headers`. The client sends a header the preflight
doesn't allow, the browser blocks the request, and the error message
is "connection error" — not "CORS error." Check headers first.

Every header the fetch call sends must appear in `Access-Control-Allow-Headers`.
If using the Anthropic API directly, include: `Content-Type, anthropic-version,
anthropic-beta` at minimum.

---

## AWS

AWS is used for persistent compute (EC2), object storage (S3), and
scheduled jobs. Use it when Cloudflare or GitHub Pages cannot do the job.

### Access rules

- **Root account**: MFA enabled, no programmatic access, used only for
  billing and IAM management
- **IAM users**: one per project, minimum permissions for that project only
- **Access keys**: stored in `.env` locally, never committed, rotated on
  any suspected exposure
- **SSH keys**: stored in `~/.ssh/`, named `{project}-key.pem`,
  referenced by path in runbooks — never copied elsewhere

### EC2 baseline

| Setting          | Value                                         |
|------------------|-----------------------------------------------|
| Default instance | t3.micro (free tier eligible; t3.small if memory constrained) |
| Region           | us-east-1 unless latency or compliance requires otherwise |
| Security group   | SSH from known IPs only; no 0.0.0.0/0 on port 22 |
| Storage          | 20GB gp3 (sufficient for most bots and services) |
| Key pair         | Project-specific; stored in `~/.ssh/` |

### Systemd for persistent services

Long-running processes on EC2 are managed by systemd — not screen,
not nohup, not a cron job that checks if the process is running.

```ini
# /etc/systemd/system/{project}.service (minimum viable unit)
[Unit]
Description={Project} service
After=network.target

[Service]
Type=simple
User={deploy-user}
WorkingDirectory=/home/{deploy-user}/{project}
ExecStart=/home/{deploy-user}/{project}/.venv/bin/python main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Systemd provides restart-on-failure, logging to journald, and
startup-on-boot. Screen provides none of these.

---

## GitHub Actions

GitHub Actions is used exclusively for CI/CD — build, test, and deploy.
It is not used for scheduled jobs or triggered automations (use
systemd timers or Lambda for those).

### Deploy workflow rules

- Path filter every workflow. A change to `framework/` should not
  trigger a demo rebuild. A change to `worker/` should not trigger
  a Pages deploy. Use `paths:` to be explicit.
- Inject secrets at build time via `${{ secrets.SECRET_NAME }}`.
  Secrets are set in repo Settings → Secrets and variables → Actions.
  They are never hardcoded in `.yml` files.
- Always specify both `main` and `master` in `branches:` unless you
  are certain which the repo uses. Branch name mismatches are the most
  common reason a workflow never triggers.

---

## Pre-Deployment Checklist

Run this before any deployment that makes something publicly accessible.
The full checklist is in `SECURITY.md`. The four questions that matter most:

1. Does this deployment make anything public that was not public before?
2. If yes — what secrets are now in scope of the public surface?
3. Are any secrets baked into build artifacts (JS bundles, config files)?
4. Is any secret one natural-next-step away from being in scope?

Question 4 is the one that gets missed. "One step away" is treated as
already exposed. Fix the architecture before deploying, not after.

---

## Infrastructure as Documentation

Every infrastructure component must be documented in `ARCHITECTURE.md`:
what it is, why it exists, and how to access or redeploy it.

Infrastructure that is not documented is infrastructure that is invisible
to future sessions. An agent asked to fix a production issue with no
record of what production looks like will either hallucinate the
architecture or ask questions that burn session context.

The deployment runbook lives in `docs/DEPLOYMENT_RUNBOOK.md` (create if
the project has a non-trivial deployment). It documents every manual step
that is not automated — the steps you would need to run from scratch if
the deployment environment were destroyed.
