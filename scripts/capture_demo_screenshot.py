"""
scripts/capture_demo_screenshot.py
Take a screenshot of the live demo with a specific prompt entered and
the output visible. Used to generate post_01.png through post_12.png.

Usage:
  python scripts/capture_demo_screenshot.py --post 1
  python scripts/capture_demo_screenshot.py --all
  python scripts/capture_demo_screenshot.py --post 1 --dry-run

Output: scripts/screenshots/post_NN.png
Requires: playwright  (pip install playwright && playwright install chromium)
"""

import argparse
import json
import logging
import os
import sys
import time

DEMO_URL = "https://gr8drmrslc.github.io/build-with-ai/"
SCHEDULE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "linkedin_schedule.json")
SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def load_schedule():
    with open(SCHEDULE_PATH, encoding="utf-8") as f:
        return json.load(f)


def capture_post(post: dict, dry_run: bool = False):
    post_id = post["id"]
    prompt = post["demo_prompt"]
    out_path = os.path.join(SCREENSHOTS_DIR, f"post_{post_id:02d}.png")

    log.info(f"Post {post_id}: {post['theme']}")
    log.info(f"  Prompt : {prompt[:80]}...")
    log.info(f"  Output : {out_path}")

    if dry_run:
        log.info("  [DRY RUN] skipping browser")
        return True

    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.error("playwright not installed. Run: pip install playwright && playwright install chromium")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        log.info("  Loading demo...")
        page.goto(DEMO_URL, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=15000)
        time.sleep(2)

        # Type the prompt into the orchestrator textarea
        textarea = page.query_selector("textarea.orchestrator-input")
        if not textarea:
            log.error("  Could not find orchestrator textarea — demo may not be loaded")
            page.screenshot(path=out_path)
            browser.close()
            return False

        textarea.fill(prompt)
        time.sleep(0.5)

        # Click Decompose
        decompose_btn = page.query_selector("button.btn-primary")
        if decompose_btn:
            decompose_btn.click()
            log.info("  Waiting for output...")
            # Wait up to 30s for output or error
            try:
                page.wait_for_selector(
                    ".orchestrator-output, .orchestrator-error",
                    timeout=30000,
                )
                time.sleep(3)  # let streaming finish
                # Check for rate limit error
                error_el = page.query_selector(".orchestrator-error")
                if error_el:
                    error_text = error_el.inner_text()
                    if "Rate limit" in error_text or "429" in error_text:
                        log.error(f"  RATE LIMITED: {error_text}")
                        log.error("  Wait ~60 min then re-run: python scripts/capture_demo_screenshot.py --post " + str(post_id))
                        page.screenshot(path=out_path)
                        browser.close()
                        return False
            except Exception:
                log.warning("  Output did not appear in time — screenshotting anyway")
        else:
            log.warning("  Decompose button not found")

        page.screenshot(path=out_path, full_page=False)
        log.info(f"  Saved: {out_path}")
        browser.close()
    return True


def main():
    parser = argparse.ArgumentParser(description="Capture demo screenshots for LinkedIn posts")
    parser.add_argument("--post", type=int, help="Post ID to capture (1-12)")
    parser.add_argument("--all", action="store_true", help="Capture all posts")
    parser.add_argument("--dry-run", action="store_true", help="Show what would run without browser")
    args = parser.parse_args()

    if not args.post and not args.all:
        parser.print_help()
        sys.exit(0)

    schedule = load_schedule()

    if args.all:
        posts = schedule
    else:
        posts = [p for p in schedule if p["id"] == args.post]
        if not posts:
            log.error(f"Post {args.post} not found in schedule")
            sys.exit(1)

    for post in posts:
        ok = capture_post(post, dry_run=args.dry_run)
        if not ok:
            log.warning(f"  Post {post['id']} screenshot failed — continuing")
        time.sleep(2)

    log.info("Done.")


if __name__ == "__main__":
    main()
