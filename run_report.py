"""
Exploration script — run locally to discover available Magnite dimensions.

Usage:
    python run_report.py

Tries to pull the deal report with additional candidate dimensions.
Check the output to confirm which fields actually come back from the API.
"""

import logging
import os
import sys
from pathlib import Path

import pandas as pd

from client import MagniteClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

key       = os.environ["MAGNITE_KEY"]
secret    = os.environ["MAGNITE_SECRET"]
publisher = os.environ["MAGNITE_PUBLISHER_ID"]

client = MagniteClient(api_key=key, api_secret=secret, account_id=publisher)

# ── Test 1: add deal_type and partner (DSP) to the deal report ────────────────
print("\n=== Test 1: deal_type + partner at deal level ===", file=sys.stderr)
try:
    df1 = client.run_report(
        dimensions=["date", "deal", "deal_id", "deal_type", "partner"],
        metrics=["bid_requests", "bid_responses", "impressions",
                 "paid_impression", "publisher_gross_revenue",
                 "seller_net_revenue", "ecpm"],
        date_range="yesterday",
    )
    print(f"Rows: {len(df1)}  Columns: {list(df1.columns)}", file=sys.stderr)
    with pd.option_context("display.max_columns", None, "display.width", 300):
        print(df1.head(5).to_string(index=False))
    df1.to_csv("test1_deal_type_partner.csv", index=False)
    print("Saved test1_deal_type_partner.csv", file=sys.stderr)
except Exception as e:
    print(f"Test 1 FAILED: {e}", file=sys.stderr)

# ── Test 2: look for a demand_channel / channel dimension ─────────────────────
print("\n=== Test 2: demand_channel ===", file=sys.stderr)
try:
    df2 = client.run_report(
        dimensions=["date", "deal", "deal_id", "demand_channel"],
        metrics=["impressions", "publisher_gross_revenue"],
        date_range="yesterday",
    )
    print(f"Rows: {len(df2)}  Columns: {list(df2.columns)}", file=sys.stderr)
    with pd.option_context("display.max_columns", None, "display.width", 300):
        print(df2.head(5).to_string(index=False))
except Exception as e:
    print(f"Test 2 FAILED: {e}", file=sys.stderr)

# ── Test 3: look for format / ad_format dimension ─────────────────────────────
print("\n=== Test 3: format ===", file=sys.stderr)
try:
    df3 = client.run_report(
        dimensions=["date", "deal", "deal_id", "format"],
        metrics=["impressions", "publisher_gross_revenue"],
        date_range="yesterday",
    )
    print(f"Rows: {len(df3)}  Columns: {list(df3.columns)}", file=sys.stderr)
    with pd.option_context("display.max_columns", None, "display.width", 300):
        print(df3.head(5).to_string(index=False))
except Exception as e:
    print(f"Test 3 FAILED (try 'ad_format'): {e}", file=sys.stderr)

# ── Test 4: floor_price or price_floor ────────────────────────────────────────
print("\n=== Test 4: price_floor ===", file=sys.stderr)
try:
    df4 = client.run_report(
        dimensions=["date", "deal", "deal_id", "price_floor"],
        metrics=["impressions", "publisher_gross_revenue"],
        date_range="yesterday",
    )
    print(f"Rows: {len(df4)}  Columns: {list(df4.columns)}", file=sys.stderr)
    with pd.option_context("display.max_columns", None, "display.width", 300):
        print(df4.head(5).to_string(index=False))
except Exception as e:
    print(f"Test 4 FAILED: {e}", file=sys.stderr)
