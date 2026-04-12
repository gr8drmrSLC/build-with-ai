# RETROFIT_GUIDE.md

How to apply this framework to a project that was already started
without it. A retrofit is not a rewrite — it is an audit followed
by targeted additions in priority order.

The goal is not to achieve perfect coverage immediately. It is to
close the highest-risk gaps first and establish the session protocol
so that future work on the project accretes structure rather than debt.

---

## Step 0 — Secrets scan (do this before anything else)

If the project has a git history, scan it for committed secrets before
adding any framework files. A pre-commit hook and `.gitignore` are
useless after the fact — the damage is already in the history.

### Manual scan

```bash
# Search entire git history for common secret patterns
git log --all --full-history -p | grep -E \
  "sk-ant-|AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9]{48}|password\s*=|api_key\s*=" \
  | head -50
```

### Automated scan (recommended)

```bash
# truffleHog — scans git history for high-entropy strings and known patterns
pip install trufflehog
trufflehog git file://. --only-verified

# gitleaks — alternative, fast, configurable
# https://github.com/gitleaks/gitleaks
gitleaks detect --source . -v
```

### If a secret is found in history

1. Rotate the secret immediately — assume it is compromised
2. Rewrite history to remove it:
   ```bash
   # Install git-filter-repo (preferred over BFG for modern git)
   pip install git-filter-repo

   # Remove all occurrences of the secret value
   git filter-repo --replace-text <(echo "sk-ant-ACTUAL_KEY==>REDACTED")
   ```
3. Force-push to remote — coordinate with any collaborators first
4. Add the secret to `.gitignore` and document the incident in `SECURITY.md`

If no secrets are found: document that the scan was run and when,
in `SECURITY.md` under a "Secrets Scan History" section.

---

## Step 1 — Add .gitignore (if missing or incomplete)

Check whether `.gitignore` exists and covers the minimum set:

```bash
cat .gitignore 2>/dev/null || echo "MISSING"
```

If missing or incomplete, add or extend it. Minimum content:

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
*.pyo

# Data and output (never commit these)
/logs/
/data/
/output/
*.db
*.sqlite

# Node
node_modules/

# Keep this — allows .env.example to be committed
!.env.example
```

Commit `.gitignore` changes before any other retrofit work.

---

## Step 2 — Gap audit

Run through this checklist against the existing project. Check what
exists, what is absent, and what is present but not enforced.

### Existence checks

```bash
ls framework/           # framework files present?
ls .env.example         # env contract documented?
ls tests/smoke_test.py  # working baseline defined?
ls pyproject.toml       # dependencies declared?
cat .pre-commit-config.yaml 2>/dev/null || echo "no pre-commit"
```

### Quality checks

| Check                                    | Command / Method                              |
|------------------------------------------|-----------------------------------------------|
| Are secrets in `.gitignore`?             | `cat .gitignore`                              |
| Is there a smoke test?                   | `python tests/smoke_test.py`                  |
| Do all modules import cleanly?           | `python -c "import src.<module>"`             |
| Is spend tracked anywhere?               | Look for TASK_LEDGER.md or equivalent         |
| Are API keys loaded from env only?       | `grep -r "sk-ant-\|api_key" src/ --include="*.py"` |
| Is there a CLAUDE.md or equivalent?      | `ls framework/CLAUDE.md`                      |
| Is there a PROJECT_STATUS.md?            | `ls framework/PROJECT_STATUS.md`              |

---

## Step 3 — Priority order for additions

Not all framework files are equally urgent. Add in this order:

### Priority 1 — Safety (add before any further work)

These prevent the most costly failures. Nothing else should be
worked on until these exist.

1. `.gitignore` with secrets coverage (Step 1 above)
2. `framework/SECURITY.md` — pre-deployment checklist + secret handling rules
3. `.env.example` — documents every required env var
4. `framework/CLAUDE.md` — session protocol so the next session starts correctly

### Priority 2 — Continuity (add before the next session)

These prevent the "starting from scratch" problem on every session.

5. `framework/PROJECT_STATUS.md` — current state, what works, what is next
6. `framework/DECISIONS.md` — backfill any non-obvious decisions already made
7. `tests/smoke_test.py` — define the current working baseline

### Priority 3 — Cost and quality (add when the project reaches regular use)

8. `src/core/config.py` — centralize env loading, eliminate magic strings
9. `src/core/budget_guard.py` — add spend tracking before API usage grows
10. `framework/BUDGET_POLICY.md` — document limits and model selection rules
11. `framework/DEVELOPMENT_PROTOCOL.md` — introduce the 8-step protocol

### Priority 4 — Full coverage (add over time)

Remaining framework files in whatever order fits the project's needs.
See `USER_MANUAL.md` for the full file list.

---

## Step 4 — Writing PROJECT_STATUS.md for an existing project

For a new project, `PROJECT_STATUS.md` starts blank. For a retrofit,
it starts as a snapshot of current reality. Answer these:

```markdown
## Current State
[What is working right now. Be specific — "the API client calls /v1/messages
and returns a parsed response" is better than "mostly working".]

## What Is Built
[Bullet list of the major components that exist and are functional.]

## What Is Not Built Yet
[Honest list of gaps, todos, known broken things.]

## Open Questions
[Decisions that haven't been made yet. Ambiguities.]

## Next Task
[The one specific thing the next session should do first.]
```

The value of this document is precision. Vague status files produce
vague sessions. "Get the API working" is not a next task.
"Add retry logic with exponential backoff to `src/api_client.py`
for 429 responses" is.

---

## Step 5 — Introducing the 8-step protocol

You do not need to go back and retroactively apply the 8-step protocol
to every past change. You apply it from now on, to every change that
touches working code.

The first time you apply it to a new project, do it explicitly:

1. Run `smoke_test.py` (or equivalent) and record the passing output
   in `PROJECT_STATUS.md` as the "current working baseline"
2. Make the first change under the protocol
3. Run `smoke_test.py` again and confirm it still passes
4. Commit

After two or three cycles it becomes automatic. The protocol is most
useful on the first change after a long gap — the moment when you are
most likely to have forgotten what was working and most likely to
introduce a silent regression.

---

## Retrofit checklist template

Copy this into the project you are retrofitting and work through it.
Check each item off as it is completed and committed.

```markdown
# Retrofit Checklist — [Project Name]

Started: [date]

## Step 0 — Secrets scan
- [ ] Scan run: `trufflehog git file://.` or `gitleaks detect`
- [ ] Result: [CLEAN / FOUND — describe and link to remediation]
- [ ] Scan date and tool version recorded in SECURITY.md

## Step 1 — .gitignore
- [ ] .gitignore exists and covers: .env, .env.*, *.pem, *.key
- [ ] .gitignore committed (or confirmed already committed)
- [ ] !.env.example negation present (on its own line)

## Priority 1 — Safety
- [ ] framework/SECURITY.md added
- [ ] .env.example added and covers all required vars
- [ ] framework/CLAUDE.md added

## Priority 2 — Continuity
- [ ] framework/PROJECT_STATUS.md written (current state snapshot)
- [ ] framework/DECISIONS.md written (backfill non-obvious decisions)
- [ ] tests/smoke_test.py added and passing

## Priority 3 — Cost and quality
- [ ] src/core/config.py added (or env loading centralized)
- [ ] src/core/budget_guard.py added (or spend limit enforced)
- [ ] framework/BUDGET_POLICY.md added
- [ ] framework/DEVELOPMENT_PROTOCOL.md added

## Priority 4 — Full coverage
- [ ] Remaining framework files added (see USER_MANUAL.md)
- [ ] bootstrap.sh run to fill any gaps

## Done
- [ ] All checks committed
- [ ] PROJECT_STATUS.md updated with retrofit completion
- [ ] DECISIONS.md updated with any decisions made during retrofit
```

---

## Known retrofit targets

### Job Search Bot (`C:\Users\V2Rst\`)

Primary gaps to audit: secrets scan on commit history, smoke test
existence, budget guard on API calls, CLAUDE.md for session continuity.
See `job_search_next_steps.md` in workspace memory for open items.

### ARIA (`C:\Users\V2Rst\aria\`)

Phase 1 pipeline built, not yet deployed to EC2. Good time to retrofit
before deployment — adding the framework before production reduces the
cost of the security and infrastructure work. Priority: SECURITY.md
and pre-deployment checklist before any EC2 deployment step.

---

## What a completed retrofit looks like

A project that has been fully retrofitted:

1. Has no secrets in git history (scan confirmed clean)
2. Has a `.gitignore` that would have caught any secret before it was committed
3. Has a `CLAUDE.md` so any session starts from a defined state
4. Has a `PROJECT_STATUS.md` that accurately describes current reality
5. Has a `tests/smoke_test.py` that defines and verifies the working baseline
6. Has `.env.example` that documents every required environment variable
7. Has `budget_guard.py` or equivalent protecting every paid API call

A project that has all seven has the same session hygiene as a
project built with this framework from the start. The retrofit is
complete when a fresh Claude Code session can read the framework
files, run the smoke test, and know exactly where to start —
without any verbal briefing.
