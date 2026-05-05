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

_DEFAULT_SESSION = os.path.join(SCRIPTS_DIR, "linkedin_session.json")
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
        log.error("Run: python scripts/save_linkedin_session.py")
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
    # Warmup on homepage first — lets Cloudflare issue a fresh __cf_bm token
    # before we navigate to an authenticated page. Without this, an expired
    # __cf_bm in the session file causes a checkpoint redirect even when li_at is valid.
    page.goto("https://www.linkedin.com/", timeout=20000)
    _delay(2500, 4000)
    page.goto("https://www.linkedin.com/feed/", timeout=20000)
    _delay(2000, 3500)
    url = page.url
    on_auth = any(s in url for s in ("login", "signup", "authwall", "checkpoint"))
    logged_in = "linkedin.com" in url and not on_auth
    if not logged_in:
        log.error("Session expired. Re-run: python scripts/save_linkedin_session.py")
    return logged_in

# ── Post ──────────────────────────────────────────────────────────────────────

def _focus_shadow_editor(page) -> bool:
    """Walk all shadow roots to find and focus the Quill editor."""
    return bool(page.evaluate("""
        () => {
            function find(root) {
                const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT);
                let node;
                while (node = walker.nextNode()) {
                    if (node.contentEditable === 'true' &&
                        node.getAttribute('aria-label') === 'Text editor for creating content') {
                        node.focus(); node.click(); return true;
                    }
                    if (node.shadowRoot && find(node.shadowRoot)) return true;
                }
                return false;
            }
            return find(document);
        }
    """))


def _click_post_button(page) -> bool:
    """Click the Post button — shadow DOM walk first, then direct selectors."""
    # Shadow DOM walk: match by innerText or aria-label
    clicked = bool(page.evaluate("""
        () => {
            function find(root) {
                const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT);
                let node;
                while (node = walker.nextNode()) {
                    const tag = node.tagName;
                    const text = (node.innerText || '').trim();
                    const label = node.getAttribute('aria-label') || '';
                    if (tag === 'BUTTON' && (text === 'Post' || label === 'Post') && !node.disabled) {
                        node.click(); return true;
                    }
                    if (node.shadowRoot && find(node.shadowRoot)) return true;
                }
                return false;
            }
            return find(document);
        }
    """))
    if clicked:
        return True
    # Direct selectors — more specific, less likely to match wrong buttons
    for sel in [
        "button.share-actions__primary-action",
        "button[aria-label='Post']",
        "button:has-text('Post')",
    ]:
        try:
            el = page.wait_for_selector(sel, timeout=4000, state="visible")
            if el:
                el.click()
                log.info(f"  Post button clicked via: {sel}")
                return True
        except Exception:
            continue
    return False


def _open_and_fill(page, text: str, screenshot_path: str | None) -> bool:
    """
    Open the LinkedIn post composer and fill it with text and optional image.

    Photo-first flow (when image present):
      Feed "Photo" button → media editor → set_input_files → Next → text composer

    Text-only flow (no image):
      Feed "Start a post" → text composer directly

    The feed-bar Photo button is a native button outside shadow DOM and directly
    accessible. The file input in the media editor accepts set_input_files() without
    needing a file chooser dialog. This is the correct approach — learned from ARIA's
    update_linkedin.py which posts two screenshots per post successfully.
    """
    has_image = bool(screenshot_path and os.path.exists(screenshot_path))

    if has_image:
        # Photo-first flow
        try:
            photo_btn = page.get_by_role("button", name="Photo")
            photo_btn.wait_for(state="visible", timeout=8000)
            photo_btn.click()
            log.info("  Photo button clicked (feed bar)")
        except Exception as e:
            log.warning(f"  Feed Photo button not found ({e}) — falling back to text-only")
            has_image = False

    if has_image:
        _delay(1500, 2500)
        file_input = page.query_selector("input[type='file']")
        if file_input:
            file_input.set_input_files(screenshot_path)
            log.info(f"  Image set: {os.path.basename(screenshot_path)}")
            _delay(3000, 5000)

            # Click Next to advance from media editor to text composer
            # Use test-id to avoid matching the carousel's Next button
            try:
                next_btn = page.get_by_test_id("interop-shadowdom").get_by_role("button", name="Next")
                next_btn.wait_for(state="visible", timeout=8000)
                next_btn.click()
                log.info("  Clicked Next — in text composer")
                _delay(2000, 3000)
            except Exception as e:
                log.error(f"  Next button not found: {e}")
                return False
        else:
            log.warning("  File input not found — falling back to text-only")
            has_image = False

    if not has_image:
        # Text-only flow
        try:
            page.get_by_text("Start a post", exact=True).first.click()
            log.info("  Opened text-only composer")
            _delay(2500, 3500)
        except Exception as e:
            log.error(f"  Could not open composer: {e}")
            return False

    # Type text — editor lives in shadow DOM; walk to find and focus it
    focused = False
    for attempt in range(5):
        if _focus_shadow_editor(page):
            focused = True
            log.info("  Editor focused")
            break
        _delay(600, 1000)

    if not focused:
        # Fallback: Playwright locator pierces shadow DOM for fill
        try:
            editor = page.locator("div.ql-editor")
            editor.wait_for(state="visible", timeout=6000)
            editor.click()
            _delay(300, 500)
            editor.fill(text)
            log.info("  Text filled via locator fallback")
            _delay(800, 1200)
            return True
        except Exception as e:
            log.error(f"  Could not focus editor: {e}")
            return False

    _delay(300, 600)
    page.keyboard.type(text, delay=random.randint(15, 35))
    log.info("  Text typed")
    _delay(1000, 1500)
    return True


def post_to_linkedin(page, text: str, screenshot_path: str | None) -> bool:
    log.info("Opening post composer...")

    if not _open_and_fill(page, text, screenshot_path):
        return False

    # Post button is inside shadow DOM — walk to find it
    if _click_post_button(page):
        log.info("  Posted")
        _delay(3000, 5000)
        return True

    # Fallback: Playwright locator
    try:
        page.locator("button").filter(has_text="Post").last.click(timeout=8000)
        log.info("  Posted via locator fallback")
        _delay(3000, 5000)
        return True
    except Exception as e:
        log.error(f"  Post button error: {e}")

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
