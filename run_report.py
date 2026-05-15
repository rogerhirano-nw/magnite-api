"""
Dimension discovery script — finds which Magnite dimension names are valid.
Tests many candidate names one at a time against the API.
"""

import logging
import os
import sys
from pathlib import Path

from client import MagniteClient, MagniteAPIError

logging.basicConfig(level=logging.WARNING)

env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

client = MagniteClient(
    api_key=os.environ["MAGNITE_KEY"],
    api_secret=os.environ["MAGNITE_SECRET"],
    account_id=os.environ["MAGNITE_PUBLISHER_ID"],
)

CANDIDATES = [
    # DSP / demand
    "partner",
    "partner_name",
    "dsp",
    "dsp_name",
    "buyer",
    "buyer_name",
    "demand_partner",
    "demand_source",
    "channel",
    "demand_channel",
    "market",
    "marketplace",
    "inventory_source",
    "transaction_type",
    # Deal / format
    "deal_type",
    "deal_type_name",
    "deal_name",
    "media_type",
    "ad_type",
    "ad_format",
    "format",
    "size_type",
    "creative_type",
    # Floor / pricing
    "price_floor",
    "floor_price",
    "floor",
    "bid_floor",
    "cpm_floor",
    # Other
    "order",
    "line_item",
    "advertiser",
    "brand",
    "campaign",
    "category",
    "content_type",
    "video_type",
]

print("Testing dimensions against deal report...\n")
working = []
failed  = []

for dim in CANDIDATES:
    try:
        df = client.run_report(
            dimensions=["deal", "deal_id", dim],
            metrics=["impressions", "publisher_gross_revenue"],
            date_range="yesterday",
        )
        working.append(dim)
        sample = df[dim].dropna().unique()[:3].tolist() if dim in df.columns else "—"
        print(f"  ✓  {dim:<30} sample values: {sample}")
    except MagniteAPIError:
        failed.append(dim)
        print(f"  ✗  {dim}")

print(f"\n=== WORKING ({len(working)}): {working}")
print(f"=== FAILED  ({len(failed)}): {failed}")
