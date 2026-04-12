# BACKUP_POLICY.md

What gets backed up, how, and how often. Backup policy exists to
answer one question: if this machine or service disappeared right
now, what work would be unrecoverable?

Anything with an answer of "significant work" needs a backup.
Anything where the answer is "nothing — it's in git" does not.

---

## What Needs Backup

### Code and configuration

**Does not need backup**: any file committed to a remote git repository.
GitHub is the backup. If the local machine disappears, `git clone` recovers it.

**Does need backup**:
- `.env` files — never committed, never in git, contain the secrets
  that make everything work
- SSH private keys (`~/.ssh/*.pem`, `~/.ssh/id_*`) — if lost, you lose
  access to every server they unlock
- Any local-only database file (`.db`, `.sqlite`) not synced elsewhere
- API key values not stored in a secrets manager

### Data and state

| Data type                  | Backup needed? | Why                                     |
|----------------------------|----------------|-----------------------------------------|
| Source code                | No             | Git + GitHub                            |
| `.env` files               | Yes            | Not in git; losing them = re-rotation   |
| SSH keys                   | Yes            | Not in git; losing them = server lockout|
| SQLite databases           | Yes, if prod   | Local file, no inherent redundancy      |
| Cloudflare Worker secrets  | No             | Re-run `wrangler secret put` to restore |
| GitHub Actions secrets     | No             | Re-enter via repo settings              |
| Framework `.md` files      | No             | In git                                  |

---

## Backup Methods

### Secrets — manual encrypted backup

`.env` files and SSH keys should be stored in a password manager
(1Password, Bitwarden) or an encrypted note. Not in a cloud drive
folder without encryption.

**Minimum**: export each `.env` file to a secure note in your password
manager. Label it with the project name and date. Update it when
secrets are rotated.

**For SSH keys**: back up the private key file content as a secure note.
Label with the key name, the servers it unlocks, and the date created.

### Databases — S3 encrypted backup (for production workloads)

If a project has a SQLite or PostgreSQL database with production data:

```bash
# Example: daily backup of SQLite to S3 with server-side encryption
aws s3 cp /path/to/db.sqlite \
  s3://{bucket}/{project}/db-$(date +%Y%m%d).sqlite \
  --sse AES256
```

Add this as a systemd timer or cron job on the server. Retain at least
7 daily backups before pruning.

S3 bucket requirements:
- Versioning enabled
- Public access blocked
- Server-side encryption (SSE-S3 minimum; SSE-KMS for sensitive data)
- Lifecycle rule to expire backups older than 30 days (adjust per project)

### Git remote — already handled

Every project uses GitHub as the remote. Pushing after every committed
task (as required by `GIT_POLICY.md`) means the remote is always
current. No additional git backup is needed.

---

## Recovery Runbook

Document recovery steps in `docs/DEPLOYMENT_RUNBOOK.md` for any
project with a non-trivial recovery path. At minimum, the runbook answers:

1. Where are the `.env` values stored? (password manager entry name)
2. Where are the SSH keys? (password manager entry name)
3. How do you redeploy from scratch if the server is gone?
4. How do you restore the database if the file is lost?

A runbook that requires you to remember things is not a runbook.
It should be followable by someone who has never seen the project.

---

## Backup Verification

A backup that has never been restored is a backup you cannot trust.

For each project at least once:
- [ ] Confirm `.env` backup is readable in the password manager
- [ ] Confirm SSH key backup is complete (not just the public key)
- [ ] If database backups exist: restore one to a temp location and verify it opens

Add this as a quarterly reminder. Discovering a corrupt backup during
an incident is worse than having no backup — it costs the same time
and produces false confidence until the moment it fails.

---

## What This Policy Does Not Cover

This policy covers project-level backup. It does not cover:
- OS-level machine backup (Time Machine, Windows Backup) — use one
- Password manager backup — your password manager has its own export/backup flow; use it
- GitHub account access recovery — set up recovery codes and a second auth method

If your password manager is the single point of failure for all secrets,
back up the password manager itself.
