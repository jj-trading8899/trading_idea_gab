#!/usr/bin/env python3
"""
generate_report.py — Called by GitHub Actions to generate the daily trading ideas report.
Uses the Anthropic API with web search enabled.
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

import anthropic

SYSTEM_PROMPT = """You are a senior stock analyst at an absolute return hedge fund 
focused on Hong Kong-listed equities. You produce daily trading idea reports that are 
concise, actionable, and backed by specific catalysts. You always cite current prices 
and provide precise entry, stop-loss, and target levels. Format your output as clean markdown."""

USER_PROMPT = """Today is {date}.

## Your Task

1. Search aastocks.com and other financial news sources for today's top news affecting Hong Kong stocks
2. Search for the latest broker research reports, upgrades/downgrades, and macro headlines
3. Identify **three actionable trading ideas** from today's news flow

## Report Structure

Start with:
# Daily Trading Ideas — {date}

## Macro Backdrop
HSI close/level, key overnight moves, major risk events, market turnover

---

Then for each of the 3 ideas:

## Idea [N]: [TICKER] — [COMPANY NAME] — [LONG/SHORT]

**Conviction:** High / Medium / Low | **Theme:** [2-3 words] | **Sizing:** [X]% of NAV

### Catalyst
What specific news is driving this idea today and why timing matters

### Fundamental Summary
Company overview, key financials (PE, market cap, margins), competitive positioning

### Game Plan

| Level | Price | % from Entry |
|-------|-------|-------------|
| Entry Zone | HK$xx–xx | — |
| Cut Loss | HK$xx | –x% |
| Target 1 | HK$xx | +x% |
| Target 2 | HK$xx | +x% |

**Risk/Reward:** x.x:1 | **Timeframe:** x–x weeks

### Sizing Rationale
Why this position size given the conviction and risk profile

### Key Risks
- Risk 1
- Risk 2
- Risk 3

---

## Guidelines
- Focus on liquid Hong Kong main board stocks
- Mix of idea types: catalyst-driven, thematic, event-driven, or contrarian
- Include at least one long and consider shorts if compelling
- Be specific on price levels using current market data from your web searches
- Include risk/reward ratios for each trade
"""


def generate(date_str: str, output_path: str):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print(f"Generating report for {date_str}...")
    print(f"Model: claude-sonnet-4-5-20250929 with web search")

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search",
            }
        ],
        messages=[
            {
                "role": "user",
                "content": USER_PROMPT.format(date=date_str),
            }
        ],
    )

    # Extract text blocks from response
    parts = []
    for block in response.content:
        if hasattr(block, "text"):
            parts.append(block.text)

    report = "\n".join(parts)

    if not report.strip():
        print("WARNING: Empty report generated")
        report = f"# Daily Trading Ideas — {date_str}\n\n*Report generation failed. Please check logs.*\n"

    # Ensure output directory exists
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")

    print(f"Report saved to {output_path} ({len(report)} chars)")
    print(f"Tokens: {response.usage.input_tokens} in / {response.usage.output_tokens} out")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Report date (YYYY-MM-DD)")
    parser.add_argument("--output", required=True, help="Output markdown file path")
    args = parser.parse_args()
    generate(args.date, args.output)
