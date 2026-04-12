"""
scripts/update_linkedin.py
Add or update the build-with-ai project entry on LinkedIn.

Uses the saved LinkedIn session from the job-search bot — no login,
no password. Loads stored cookies and picks up the session.

Tasks:
  --project     Add build-with-ai as a project in the Projects section
  --dry-run     Print what would be filled without actually submitting

Usage:
  python scripts/update_linkedin.py --project
  python scripts/update_linkedin.py --project --dry-run

Requires: playwright, playwright-stealth
Session file: ../job-search/data/sessions/linkedin_session.json
"""

import argparse
import logging
import os
import random
import sys
import time

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
except ImportError:
    pass

_DEFAULT_SESSION = os.path.normpath(os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "..", "job-search", "data", "sessions", "linkedin_session.json"
))
SESSION_PATH = os.environ.get("LINKEDIN_SESSION_PATH", _DEFAULT_SESSION)

PROFILE_URL = "https://www.linkedin.com/in/stephenthoemmes/"
HEADLESS = os.environ.get("LINKEDIN_HEADLESS", "false").lower() == "true"

# ── Content ───────────────────────────────────────────────────────────────────

PROJECT_NAME = "build-with-ai — AI-Native Project Development Framework"

PROJECT_DESCRIPTION = (
    "A personal framework for AI-native project development — and a live demo that shows it working.\n\n"
    "Most AI project failures are not model failures. They are architecture failures: "
    "no cost controls, no regression safety, no delegation policy, no external memory "
    "that survives context compaction. This framework codifies the practices that prevent "
    "those failures.\n\n"
    "The framework consists of 19 policy files that govern how Claude Code sessions are run — "
    "session protocols, architectural decision records, security checklists, budget controls, "
    "agent delegation rules, and a bootstrap script that installs all of it into any new project "
    "with a single command. Seven Python modules (config, budget_guard, agent_dispatcher, "
    "rate_limiter, task_schema, logging_config, aws_config_validator) provide the executable layer.\n\n"
    "The demo is a live React app powered by the Claude API via a Cloudflare Worker proxy. "
    "Describe any project idea and it decomposes it into phases, risks, agent assignments, "
    "and a first atomic task — applying the framework's own methodology in real time.\n\n"
    "The best proof that a methodology works is that the tool demonstrating it was built using it. "
    "The entire framework was built in two Claude Code sessions using the protocols it defines.\n\n"
    "Live demo: https://gr8drmrslc.github.io/build-with-ai/\n"
    "Source code: https://github.com/gr8drmrSLC/build-with-ai"
)

PROJECT_URL = "https://gr8drmrslc.github.io/build-with-ai/"
GITHUB_URL = "https://github.com/gr8drmrSLC/build-with-ai"

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Helpers (shared pattern from ARIA update_linkedin.py) ────────────────────

def _delay(min_ms: int = 1000, max_ms: int = 2500):
    time.sleep(random.randint(min_ms, max_ms) / 1000)


def _screenshot(page, label: str):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"screenshot_{label}.png")
    page.screenshot(path=path)
    log.info(f"Screenshot: {path}")


def _check_session(session_path: str):
    if not os.path.exists(session_path):
        log.error(f"LinkedIn session not found at: {session_path}")
        log.error("Run: cd job-search && python scripts/save_session.py  (choose LinkedIn)")
        sys.exit(1)
    log.info(f"Session: {session_path}")


def _build_context(playwright, session_path: str):
    browser = playwright.chromium.launch(
        headless=HEADLESS,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    context = browser.new_context(
        storage_state=session_path,
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1280, "height": 900},
    )
    page = context.new_page()
    try:
        from playwright_stealth import Stealth
        Stealth().apply_stealth_sync(page)
        log.info("Stealth patches applied")
    except ImportError:
        log.warning("playwright-stealth not installed — continuing without stealth")
    return browser, context, page


def _verify_login(page) -> bool:
    log.info("Verifying session...")
    page.goto("https://www.linkedin.com/feed/", timeout=20000)
    _delay(2000, 3500)
    url = page.url
    on_auth = any(s in url for s in ("login", "signup", "authwall", "checkpoint"))
    logged_in = "linkedin.com" in url and not on_auth
    if not logged_in:
        log.error("Session expired. Re-run: python job-search/scripts/save_session.py")
    return logged_in


def _save_modal(page) -> bool:
    save_selectors = [
        "button[aria-label='Save']",
        "div[role='dialog'] button:has-text('Save')",
        "div.artdeco-modal button:has-text('Save')",
        "button.artdeco-button--primary:has-text('Save')",
    ]
    for sel in save_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=5000, state="visible")
            if el:
                el.scroll_into_view_if_needed()
                el.click()
                log.info(f"  Saved via: {sel}")
                return True
        except Exception:
            continue
    log.error("  Save button not found")
    return False


def _close_modal(page):
    for sel in ["button[aria-label='Dismiss']", "button:has-text('Cancel')"]:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.click()
                _delay(500, 1000)
                return
        except Exception:
            continue


# ── Task: Add project ─────────────────────────────────────────────────────────

def add_project(page, dry_run: bool = False) -> bool:
    log.info("=== Adding build-with-ai project ===")

    page.goto(PROFILE_URL, timeout=20000)
    _delay(2500, 4000)

    page.evaluate("window.scrollBy(0, 1200)")
    _delay(1000, 1800)
    _screenshot(page, "10_profile_scrolled")

    if not _click_link(page, "add-edit/PROJECT/", "Add project link"):
        _screenshot(page, "10_project_link_not_found")
        log.error("Cannot find Add project link")
        return False

    _delay(1500, 2500)
    _screenshot(page, "11_project_modal")

    if dry_run:
        log.info("[DRY RUN] Would fill:")
        log.info(f"  Name: {PROJECT_NAME}")
        log.info(f"  Desc: {PROJECT_DESCRIPTION[:120]}...")
        _close_modal(page)
        return True

    name_sel = "input[id*='PROJECT'][id*='single-line']"
    fallback_name_sel = "input[id*='PROJECT']:not([placeholder*='looking'])"
    try:
        name_el = page.wait_for_selector(name_sel, timeout=6000, state="visible")
        if not name_el:
            name_el = page.wait_for_selector(fallback_name_sel, timeout=4000, state="visible")
        name_el.fill(PROJECT_NAME)
        _delay(400, 700)
        log.info("  Project name filled")
    except Exception as e:
        log.error(f"  Project name field not found: {e}")
        _screenshot(page, "11_project_name_not_found")
        return False

    desc_sel = "textarea[id*='PROJECT']"
    try:
        desc_el = page.wait_for_selector(desc_sel, timeout=5000, state="visible")
        desc_el.fill(PROJECT_DESCRIPTION)
        _delay(500, 900)
        log.info("  Description filled")
    except Exception as e:
        log.warning(f"  Description field not found: {e}")

    # Set start date — April 2026
    try:
        month_sels = page.query_selector_all("select[name='month']")
        year_sels = page.query_selector_all("select[name='year']")
        visible_month = [s for s in month_sels if s.is_visible()]
        visible_year = [s for s in year_sels if s.is_visible()]
        if visible_month:
            visible_month[0].select_option(label="April")
            _delay(300, 500)
            log.info("  Start month: April")
        if visible_year:
            visible_year[0].select_option(label="2026")
            _delay(300, 500)
            log.info("  Start year: 2026")
    except Exception as e:
        log.warning(f"  Date fields: {e}")

    _screenshot(page, "12_project_filled")

    if not _save_modal(page):
        return False

    _delay(2500, 4000)
    _screenshot(page, "13_project_saved")
    log.info("  build-with-ai project added")
    return True


def _click_link(page, href_fragment: str, label: str, timeout: int = 8000) -> bool:
    sel = f"a[href*='{href_fragment}']"
    try:
        el = page.wait_for_selector(sel, timeout=timeout, state="visible")
        if el:
            el.scroll_into_view_if_needed()
            _delay(400, 700)
            el.click()
            log.info(f"  Clicked {label}")
            return True
    except Exception as e:
        log.warning(f"  Link not found ({label}): {e}")
    return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Update LinkedIn with build-with-ai project")
    parser.add_argument("--project", action="store_true", help="Add project to LinkedIn")
    parser.add_argument("--dry-run", action="store_true", help="Print content without submitting")
    args = parser.parse_args()

    if not args.project:
        parser.print_help()
        sys.exit(0)

    if args.dry_run:
        log.info("[DRY RUN] Content preview:")
        log.info(f"  Project name: {PROJECT_NAME}")
        log.info(f"  Description:\n{PROJECT_DESCRIPTION}")
        return

    _check_session(SESSION_PATH)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.error("playwright not installed. Run: pip install playwright && playwright install chromium")
        sys.exit(1)

    with sync_playwright() as p:
        browser, context, page = _build_context(p, SESSION_PATH)
        try:
            if not _verify_login(page):
                sys.exit(1)
            if args.project:
                ok = add_project(page, dry_run=args.dry_run)
                if not ok:
                    log.error("Project add failed")
                    sys.exit(1)
        finally:
            context.close()
            browser.close()

    log.info("Done.")


if __name__ == "__main__":
    main()
