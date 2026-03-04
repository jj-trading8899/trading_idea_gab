#!/usr/bin/env python3
"""
update_index.py — Scans the reports directory and builds index.json
with a sorted list of available report dates (newest first).
Called by GitHub Actions after each report is generated.
"""

import json
import re
import argparse
from pathlib import Path


def update_index(reports_dir: str):
    rdir = Path(reports_dir)
    rdir.mkdir(parents=True, exist_ok=True)

    # Find all trading-ideas-YYYY-MM-DD.md files
    pattern = re.compile(r"trading-ideas-(\d{4}-\d{2}-\d{2})\.md")
    dates = []

    for f in rdir.iterdir():
        m = pattern.match(f.name)
        if m:
            dates.append(m.group(1))

    # Sort newest first
    dates.sort(reverse=True)

    # Write index
    index_path = rdir / "index.json"
    index_path.write_text(json.dumps(dates, indent=2), encoding="utf-8")
    print(f"Updated {index_path} with {len(dates)} reports")
    for d in dates[:5]:
        print(f"  {d}")
    if len(dates) > 5:
        print(f"  ... and {len(dates) - 5} more")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-dir", required=True, help="Path to reports directory")
    args = parser.parse_args()
    update_index(args.reports_dir)
