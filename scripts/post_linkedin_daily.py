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
HEADLESS = os.environ.get("LINKEDIN_HEADLESS", "true").lower() == "true"

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

def post_to_linkedin(page, text: str, screenshot_path: str | None) -> bool:
    log.info("Opening post composer...")

    # Click the Start a post button
    start_selectors = [
        "button.share-box-feed-entry__trigger",
        "button[aria-label*='Start a post']",
        "div.share-box-feed-entry__top-bar button",
        "button:has-text('Start a post')",
    ]
    clicked = False
    for sel in start_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=5000, state="visible")
            if el:
                el.click()
                clicked = True
                log.info(f"  Opened via: {sel}")
                break
        except Exception:
            continue

    if not clicked:
        log.error("  Could not find 'Start a post' button")
        return False

    _delay(1500, 2500)

    # Type post content
    editor_selectors = [
        "div.ql-editor",
        "div[contenteditable='true'][role='textbox']",
        "div[data-placeholder]",
    ]
    typed = False
    for sel in editor_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=5000, state="visible")
            if el:
                el.click()
                _delay(400, 700)
                # Use keyboard to type (more natural, avoids paste detection)
                page.keyboard.type(text, delay=10)
                typed = True
                log.info(f"  Text entered via: {sel}")
                break
        except Exception:
            continue

    if not typed:
        log.error("  Could not find post editor")
        return False

    _delay(800, 1200)

    # Attach image if available
    if screenshot_path and os.path.exists(screenshot_path):
        log.info(f"  Attaching image: {screenshot_path}")
        image_btn_selectors = [
            "button[aria-label*='Add a photo']",
            "button[aria-label*='photo']",
            "label[for*='image']",
            "button.share-creation-state__media-button",
        ]
        for sel in image_btn_selectors:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    el.click()
                    _delay(1000, 1500)
                    # Handle file chooser
                    with page.expect_file_chooser(timeout=5000) as fc_info:
                        el.click()
                    file_chooser = fc_info.value
                    file_chooser.set_files(screenshot_path)
                    log.info("  Image attached")
                    _delay(2000, 3000)
                    break
            except Exception as e:
                log.warning(f"  Image attach via {sel}: {e}")
                continue
    elif screenshot_path:
        log.warning(f"  Screenshot not found: {screenshot_path} — posting text only")

    _delay(1000, 1500)

    # Click Post button
    post_btn_selectors = [
        "button.share-actions__primary-action",
        "button[aria-label='Post']",
        "button:has-text('Post'):not(:has-text('Start'))",
        "div[role='dialog'] button.artdeco-button--primary",
    ]
    for sel in post_btn_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=5000, state="visible")
            if el and el.is_visible() and el.is_enabled():
                el.click()
                log.info(f"  Posted via: {sel}")
                _delay(3000, 5000)
                return True
        except Exception:
            continue

    log.error("  Post button not found")
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
