#!/usr/bin/env bash
set -e
for post in "$@"; do
  python scripts/capture_demo_screenshot.py --post "$post"
done
