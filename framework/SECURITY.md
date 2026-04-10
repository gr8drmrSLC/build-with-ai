# SECURITY.md

Threat model, secret handling rules, and commit hygiene for
projects using this framework. Security is not a feature added
at the end — it is a precondition established at repo creation.

---

## Threat Model

The realistic threats for AI-native personal projects are not
sophisticated. They are mundane and almost entirely preventable.

| Threat                        | Likelihood | Impact   | Prevention                          |
|-------------------------------|------------|----------|-------------------------------------|
| API key committed to git      | High       | Critical | .gitignore first; pre-commit hook   |
| API key in log output         | Medium     | High     | Sanitized logging (logging_config)  |
| Overspend on API calls        | Medium     | High     | budget_guard.py; spend limits       |
| .env file pushed to GitHub    | Medium     | Critical | .gitignore + git secret scan        |
| Credentials in error messages | Medium     | High     | Never format secrets into strings   |
| Shared AWS root account       | Low        | Critical | IAM user per project, MFA on root   |
| Unencrypted local data        | Low        | Medium   | BitLocker; never store in /output/  |
| Dependency with CVE           | Low        | Medium   | Dependabot; pin major versions      |

Threats not modeled here: nation-state actors, supply chain attacks,
physical access. These are out of scope for this threat model.

---

## The .gitignore-First Rule

The `.gitignore` is always the first commit in any repo using this
framework — before README, before source files, before anything.

```bash
git init
# Write .gitignore
git add .gitignore
git commit -m "Add .gitignore before any other files"
# Now add everything else
```

**Why sequencing matters**: if a secret file is created before
`.gitignore` exists and is accidentally staged, `git add .` will
include it. Once committed, the secret is in history. Rotation
alone is insufficient — history must be rewritten with
`git filter-repo` or BFG Repo Cleaner, which rewrites all
commit hashes and requires force-push. Prevention costs nothing.
Recovery costs hours and breaks collaborator forks.

### Minimum .gitignore for every project

```gitignore
# Secrets
.env
.env.*
*.pem
*.key

# Python
__pycache__/
.venv/
*.pyc

# Data / output
*.db
*.sqlite
/logs/
/data/
/output/

# Node
node_modules/
```

---

## Secret Handling Rules

**Rule 1 — Secrets live in environment variables only.**
Never in source code. Never in config files. Never in comments.
Load via `os.environ` or a dedicated config loader (see `config.py`).

**Rule 2 — `.env` is local only.**
Commit `.env.example` with placeholder values. Never commit `.env`.
Document every required variable in `.env.example`.

**Rule 3 — Never format secrets into strings.**
```python
# Wrong — secret appears in logs and tracebacks
raise ValueError(f"Auth failed for key: {api_key}")

# Right — reference the variable name, not its value
raise ValueError("Auth failed — check ANTHROPIC_API_KEY in .env")
```

**Rule 4 — Sanitize before logging.**
The `logging_config.py` module scrubs known secret patterns from
log output. Never log request headers, full API responses, or
environment variables directly.

**Rule 5 — Rotate immediately if exposed.**
If a secret is committed, pushed, or logged:
1. Revoke and rotate the key immediately — assume it is compromised
2. Rewrite history with `git filter-repo` (not `git filter-branch`)
3. Force-push and notify any collaborators to re-clone
4. Audit usage logs for the exposed key before rotation

---

## One-Time Secrets Scan

Run this before making any repo public, or when retrofitting the
framework onto an existing project.

### Option 1 — truffleHog (recommended)
```bash
pip install truffleHog
trufflehog git file://. --only-verified
```

### Option 2 — gitleaks
```bash
# Install: https://github.com/gitleaks/gitleaks
gitleaks detect --source . -v
```

### Option 3 — git log manual scan (no install required)
```bash
# Search all commits for common secret patterns
git log -p | grep -iE "(api_key|secret|password|token|bearer)" | head -50
```

If any scan returns results, treat them as live exposures and
follow Rule 5 above before proceeding.

---

## Pre-Commit Hook

The `.pre-commit-config.yaml` in this framework includes a secrets
detection hook that runs on every commit attempt. It blocks commits
containing patterns that match common API key formats.

```yaml
# .pre-commit-config.yaml (excerpt)
- repo: https://github.com/gitleaks/gitleaks
  rev: v8.18.0
  hooks:
    - id: gitleaks
```

Install hooks after cloning:
```bash
pip install pre-commit
pre-commit install
```

A commit blocked by this hook is not an error — it is the system
working correctly.

---

## AWS Security Rules

1. **Never use root account credentials in code or .env**
   Create an IAM user with least-privilege permissions per project.

2. **MFA on root account** — no exceptions.

3. **No access keys for root account.**
   Root access keys should not exist. If they do, delete them.

4. **Rotate IAM access keys every 90 days.**

5. **S3 buckets are private by default.**
   Explicit public access requires a documented reason in DECISIONS.md.

6. **Enable AWS CloudTrail** on any account running production workloads.

---

## Dependency Security

- Pin major versions in `pyproject.toml` and `package.json`
- Enable Dependabot alerts on GitHub (Settings → Security)
- Run `pip audit` and `npm audit` before any production deployment
- Never install packages from untrusted sources or with `--ignore-errors`

---

## Incident Response

If a security incident occurs:

1. **Contain**: revoke the exposed credential immediately
2. **Assess**: determine what was accessible with that credential
3. **Rotate**: issue new credentials for all affected services
4. **Audit**: review access logs for the exposure window
5. **Document**: add an entry to DECISIONS.md with the incident date,
   what happened, and what changed — even if embarrassing
6. **Harden**: add the failure mode to this file if it is not already here

Incidents that are not documented are incidents that will recur.
