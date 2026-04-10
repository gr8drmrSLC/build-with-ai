# GIT_POLICY.md

What commits, what doesn't, how commits are written, and how
branches are managed. Git history is a design artifact — it
should be readable, trustworthy, and safe.

---

## The Non-Negotiables

These rules have no exceptions:

1. **`.gitignore` is the first commit** — before README, before source,
   before anything. See `SECURITY.md` for why sequencing matters.

2. **Secrets never commit** — `.env`, `.env.*`, `*.pem`, `*.key`,
   API keys, passwords, tokens. If one slips through, treat it as
   a live exposure and follow the incident response protocol in
   `SECURITY.md` immediately.

3. **`--no-verify` is never used** — pre-commit hooks exist to catch
   problems before they enter history. Bypassing them to save time
   always costs more time later.

4. **Force-push to `main`/`master` requires explicit justification** —
   it rewrites shared history and breaks collaborator clones. The only
   acceptable reason is removing a committed secret, and even then,
   notify all collaborators before pushing.

---

## What Commits

**Yes:**
- Source code, tests, configuration
- `.md` documentation files
- `.env.example` (placeholder values only — never real values)
- `pyproject.toml`, `package.json`, lock files
- `.gitignore`, `.gitattributes`, `.pre-commit-config.yaml`
- GitHub Actions workflows
- `bootstrap.sh`

**No:**
- `.env` or any file containing real credentials
- `/logs/`, `/data/`, `/output/` directories
- `__pycache__/`, `.venv/`, `node_modules/`
- `*.db`, `*.sqlite` — local state, not source
- Editor config files (`.vscode/`, `.idea/`) unless the team agreed to share them
- Build artifacts (`dist/`, `build/`, `*.pyc`)
- Any file over 10MB without a documented reason

---

## Commit Message Rules

### Format
```
<short summary — 50 characters or less>

<optional body — explain WHY, not what. The diff shows what.>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

### The why-not-what rule
The diff already shows what changed. The commit message should
answer: why was this change necessary? What problem does it solve?
What would break if this commit were reverted?

```
# Wrong — describes the diff, not the reason
Add error handling to api_client.py

# Right — explains the reason
Prevent silent failures when Anthropic API returns 529

Without this, a rate-limit response was swallowed and the
task appeared to complete successfully when it had not.
```

### Verb conventions
- `Add` — new file or feature that did not exist
- `Update` — change to something that already existed
- `Fix` — corrects a bug or broken behavior
- `Remove` — deletes something
- `Refactor` — restructures without changing behavior
- `Docs` — documentation only, no code change

### One logical change per commit
Don't bundle a bug fix, a refactor, and a new feature in one commit.
If `git revert` on that commit would cause confusion about what to
keep, it should have been multiple commits.

---

## Branching Strategy

This framework uses a simple trunk-based model appropriate for
solo or small-team AI projects:

```
master / main       ← always deployable; protected
feature/<name>      ← one task or feature; short-lived
fix/<name>          ← bug fix; merge and delete
```

### Rules
- `master`/`main` is always in a state that could be deployed
- Feature branches are created from `master`, merged back to `master`
- Branch names are lowercase with hyphens: `feature/orchestrator-panel`
- Delete branches after merging — they are not archives
- No long-lived branches except `master`

### When to branch
- Any change that could break the current working state
- Any experiment that may be discarded
- Any change being reviewed by a collaborator

For solo work on a task that is clearly additive and low-risk,
committing directly to `master` is acceptable.

---

## Protected Files — .gitattributes Merge Strategy

When a file should never be overwritten by a merge — a collaborator's
local settings, an environment-specific config — use `.gitattributes`
to set the merge strategy to `ours`:

```
# .gitattributes
settings.py merge=ours
.env.local merge=ours
```

This means: when merging, always keep the local version of this file
regardless of what the incoming branch contains. The collaborator's
local config survives every pull and merge without conflict.

**When to use this**: for files that are committed (so they exist in
the repo) but are intentionally different per deployment — not for
secrets (those should not be committed at all).

---

## CHANGELOG.md

Every significant change is recorded in `CHANGELOG.md` before the
commit that contains it. Format:

```markdown
## [Unreleased]

### Added
- framework/SECURITY.md — threat model and secret handling rules

### Changed
- README.md — added proof-of-methodology line

### Fixed
- vite.config.ts — set base path for GitHub Pages routing
```

Update CHANGELOG.md in the same commit as the change it describes.
Do not batch CHANGELOG updates at the end of a session.

---

## Pre-Commit Hooks

Installed via `pre-commit`. Run on every `git commit` attempt:

- **gitleaks** — scans staged files for secret patterns
- **ruff** — Python linting and formatting (if Python files are staged)
- **tsc** — TypeScript type check (if `.ts`/`.tsx` files are staged, optional)

A blocked commit is the hook working correctly. Fix the issue,
re-stage, and commit again. Never use `--no-verify`.

Install after cloning:
```bash
pip install pre-commit
pre-commit install
```

---

## Commit History Is a Design Artifact

The commit history of a well-run project tells the story of how
it was built — what problems were solved, in what order, and why.
A history of "WIP", "fix", "fix2", "final", "final2" tells a
different story.

Write commits as if a new collaborator will read them six months
from now to understand what happened and why. Because they will —
and that collaborator might be you.
