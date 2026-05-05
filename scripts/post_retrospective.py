"""
post_retrospective.py — one-off retrospective post about build-with-ai since inception.
Uses the same session and posting machinery as post_linkedin_daily.py.
Run: python scripts/post_retrospective.py
     python scripts/post_retrospective.py --dry-run
"""

import argparse
import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

# Reuse all machinery from the daily poster
from post_linkedin_daily import (
    _build_context,
    _verify_login,
    post_to_linkedin,
    _delay,
    SESSION_PATH,
    log,
)

POST_TEXT = """\
Six weeks ago I built a framework to prevent AI development failure modes. Here's the honest accounting.

The founding problem: five AI projects, same walls every time. No external memory that survived context compaction. No cost controls before a runaway API call. No regression safety. No record of why decisions were made. Every session started from scratch.

The framework was the answer. Six practices, 19 policy files, 7 Python modules, a live demo. Built in a single Saturday session using the methodology it was designed to demonstrate.

Then I used it to build something real.

ARIA — Autonomous Research Intelligence Agent — went live on EC2 on April 23. It monitors arXiv daily, scores papers with Claude, and autonomously decides when the research landscape is worth reporting. No human prompting. Four independent triggers. A newspaper-style dashboard at aria-agent.duckdns.org.

Then I ran the security audit.

What the audit found:
- PostgreSQL exposed to the internet (0.0.0.0:5432)
- Flask dashboard bypassing nginx, directly reachable
- .env files world-readable on a shared server
- API token sitting in plaintext crontab
- Budget guard as a global variable that resets on restart

None of this was caught during build. All of it was caught during audit.

The framework has a pre-deployment checklist. The honest version: we didn't run it on ARIA's deployment. We caught up last week.

That gap — between what the methodology says and what actually happened — is the most useful data point in the project. AI tools build fast. The security questions still have to be asked before shipping, not after.

They're in CLAUDE.md now.

Framework: github.com/gr8drmrSLC/build-with-ai
Demo: gr8drmrslc.github.io/build-with-ai
ARIA: aria-agent.duckdns.org"""

SCREENSHOT = os.path.join(SCRIPTS_DIR, "screenshots", "post_12.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print(POST_TEXT)
        print(f"\nScreenshot: {SCREENSHOT} (exists: {os.path.exists(SCREENSHOT)})")
        return

    if not os.path.exists(SESSION_PATH):
        log.error(f"Session not found: {SESSION_PATH}")
        sys.exit(1)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.error("playwright not installed")
        sys.exit(1)

    with sync_playwright() as p:
        browser, context, page = _build_context(p)
        try:
            if not _verify_login(page):
                sys.exit(1)
            screenshot = SCREENSHOT if os.path.exists(SCREENSHOT) else None
            success = post_to_linkedin(page, POST_TEXT, screenshot)
        finally:
            context.close()
            browser.close()

    if success:
        log.info("Retrospective post sent successfully.")
    else:
        log.error("Post failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
