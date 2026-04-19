"""
scripts/post_linkedin_daily.py
Post the next scheduled LinkedIn entry in order.

Reads linkedin_schedule.json to get post content.
Reads/writes linkedin_post_state.json to track progress.
Attaches scripts/screenshots/post_NN.png if the file exists.

Usage:
  python scripts/post_linkedin_daily.py
  python scripts/post_linkedin_daily.py --dry-run
  python scripts/post_linkedin_daily.py --status

State file: scripts/linkedin_post_state.json  (gitignored)
Session:    ../job-search/data/sessions/linkedin_session.json
"""

import argparse
import json
import logging
import os
import random
import sys
import time
from datetime import date

# ── Paths ─────────────────────────────────────────────────────────────────────

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEDULE_PATH = os.path.join(SCRIPTS_DIR, "linkedin_schedule.json")
STATE_PATH = os.path.join(SCRIPTS_DIR, "linkedin_post_state.json")
SCREENSHOTS_DIR = os.path.join(SCRIPTS_DIR, "screenshots")

_DEFAULT_SESSION = os.path.normpath(os.path.join(
    SCRIPTS_DIR, "..", "..", "job-search", "data", "sessions", "linkedin_session.json"
))
SESSION_PATH = os.environ.get("LINKEDIN_SESSION_PATH", _DEFAULT_SESSION)
HEADLESS = os.environ.get("LINKEDIN_HEADLESS", "false").lower() == "true"

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── State ─────────────────────────────────────────────────────────────────────

def load_state() -> dict:
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"next_index": 0, "posts_sent": [], "last_sent": None}


def save_state(state: dict):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def load_schedule() -> list:
    with open(SCHEDULE_PATH, encoding="utf-8") as f:
        return json.load(f)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _delay(min_ms: int = 1000, max_ms: int = 2500):
    time.sleep(random.randint(min_ms, max_ms) / 1000)


def _check_session():
    if not os.path.exists(SESSION_PATH):
        log.error(f"LinkedIn session not found: {SESSION_PATH}")
        log.error("Run: cd job-search && python scripts/save_session.py")
        sys.exit(1)
    log.info(f"Session: {SESSION_PATH}")


def _build_context(playwright):
    browser = playwright.chromium.launch(
        headless=HEADLESS,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    context = browser.new_context(
        storage_state=SESSION_PATH,
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

# ── Post ──────────────────────────────────────────────────────────────────────

def _open_and_fill(page, text: str, screenshot_path: str | None) -> bool:
    """Open the LinkedIn post composer and fill it. Returns True if ready to post."""

    # LinkedIn uses obfuscated CSS classes — use text/role selectors only.
    # Headless mode prevents the modal from rendering; browser must run headed.
    try:
        page.get_by_text("Start a post", exact=True).first.click()
        log.info("  Clicked Start a post")
    except Exception as e:
        log.error(f"  Could not find 'Start a post' button: {e}")
        return False

    _delay(2500, 3500)

    # Playwright locators pierce shadow DOM automatically.
    editor = page.locator("div.ql-editor")
    try:
        editor.wait_for(state="visible", timeout=8000)
    except Exception:
        log.error("  Post composer did not open (ql-editor not found)")
        return False

    editor.click()
    _delay(300, 500)
    editor.fill(text)
    log.info("  Text filled into editor")
    _delay(800, 1200)

    # Image attachment via file chooser
    if screenshot_path and os.path.exists(screenshot_path):
        log.info(f"  Attaching image: {screenshot_path}")
        try:
            # The photo icon is inside the shadow DOM — force=True bypasses pointer interception
            with page.expect_file_chooser(timeout=6000) as fc_info:
                page.get_by_text("Photo", exact=True).first.click(force=True)
            fc_info.value.set_files(screenshot_path)
            log.info("  Image attached")
            _delay(2000, 3000)
        except Exception as exc:
            log.warning(f"  Image attach failed: {exc} — posting text only")
    elif screenshot_path:
        log.warning(f"  Screenshot not found: {screenshot_path} — posting text only")

    _delay(1000, 1500)
    return True


def post_to_linkedin(page, text: str, screenshot_path: str | None) -> bool:
    log.info("Opening post composer...")

    if not _open_and_fill(page, text, screenshot_path):
        return False

    # Playwright locator finds the Post button even inside shadow DOM.
    # Use .last — the modal's Post button is the final one on the page.
    try:
        post_btn = page.locator("button").filter(has_text="Post").last
        post_btn.click(timeout=10000)
        log.info("  Posted")
        _delay(3000, 5000)
        return True
    except Exception as e:
        log.error(f"  Post button error: {e}")

    log.error("  Post button not found or not enabled")
    return False

# ── Main ──────────────────────────────────────────────────────────────────────

def show_status():
    schedule = load_schedule()
    state = load_state()
    idx = state.get("next_index", 0)
    print(f"\nSchedule: {len(schedule)} posts total")
    print(f"Sent:     {len(state.get('posts_sent', []))} posts")
    print(f"Last:     {state.get('last_sent', 'never')}")
    print()
    for i, post in enumerate(schedule):
        sent = post["id"] in state.get("posts_sent", [])
        next_marker = " <-- NEXT" if i == idx and not sent else ""
        status = "SENT" if sent else "pending"
        print(f"  [{status:7s}] Post {post['id']:02d}: {post['theme']}{next_marker}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Post next scheduled LinkedIn entry")
    parser.add_argument("--dry-run", action="store_true", help="Show content without posting")
    parser.add_argument("--test", action="store_true", help="Open browser, fill composer, take screenshot, then close WITHOUT posting")
    parser.add_argument("--status", action="store_true", help="Show schedule status and exit")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    schedule = load_schedule()
    state = load_state()
    idx = state.get("next_index", 0)

    if idx >= len(schedule):
        log.info("All posts have been sent. Nothing to do.")
        return

    post = schedule[idx]
    screenshot_path = os.path.join(SCRIPTS_DIR, post.get("screenshot_file", ""))

    log.info(f"Next post: {post['id']} of {len(schedule)} — {post['theme']}")
    log.info(f"Demo prompt: {post['demo_prompt'][:80]}...")

    if args.dry_run:
        log.info("\n--- POST CONTENT ---")
        print(post["text"])
        log.info(f"\nScreenshot: {screenshot_path}")
        log.info(f"  Exists: {os.path.exists(screenshot_path)}")
        return

    _check_session()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.error("playwright not installed. Run: pip install playwright && playwright install chromium")
        sys.exit(1)

    if args.test:
        log.info("TEST MODE — will open composer, fill content, screenshot, then close without posting")
        with sync_playwright() as p:
            browser, context, page = _build_context(p)
            try:
                if not _verify_login(page):
                    sys.exit(1)
                _open_and_fill(page, post["text"], screenshot_path)
                test_shot = os.path.join(SCRIPTS_DIR, "test_composer_preview.png")
                page.screenshot(path=test_shot)
                log.info(f"  Screenshot saved: {test_shot}")
                # Close the modal
                try:
                    page.keyboard.press("Escape")
                except Exception:
                    pass
                _delay(1000, 1500)
            finally:
                context.close()
                browser.close()
        log.info("TEST MODE complete. No post was sent.")
        return

    success = False
    with sync_playwright() as p:
        browser, context, page = _build_context(p)
        try:
            if not _verify_login(page):
                sys.exit(1)
            success = post_to_linkedin(page, post["text"], screenshot_path)
        finally:
            context.close()
            browser.close()

    if success:
        state["posts_sent"] = state.get("posts_sent", []) + [post["id"]]
        state["next_index"] = idx + 1
        state["last_sent"] = str(date.today())
        save_state(state)
        log.info(f"Post {post['id']} sent. Next: {idx + 2 if idx + 1 < len(schedule) else 'none (series complete)'}")
    else:
        log.error(f"Post {post['id']} failed. State not updated — will retry on next run.")
        sys.exit(1)


if __name__ == "__main__":
    main()
