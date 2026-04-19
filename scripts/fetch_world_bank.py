#!/usr/bin/env python3
"""
Reality Gap — World Bank Buffett Indicator Fetcher
===================================================
Fetches Stock Market Capitalization / GDP (%) for major markets.
World Bank indicator: CM.MKT.LCAP.GD.ZS
Source: World Bank Open Data API v2 — no API key required.

Usage:
    python3 scripts/fetch_world_bank.py

Output: src/data/macro/buffett_global.json

Countries covered:
    US (USA), Germany (DEU), Japan (JPN), China (CHN),
    UK (GBR), France (FRA), Switzerland (CHE)
"""

from __future__ import annotations

import json
import sys
import time
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("requests not installed: pip install requests")

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH  = REPO_ROOT / "src" / "data" / "macro" / "buffett_global.json"

WB_BASE = "https://api.worldbank.org/v2"
INDICATOR = "CM.MKT.LCAP.GD.ZS"

COUNTRIES = [
    ("USA", "US", "United States"),
    ("DEU", "DE", "Germany"),
    ("JPN", "JP", "Japan"),
    ("CHN", "CN", "China"),
    ("GBR", "GB", "United Kingdom"),
    ("FRA", "FR", "France"),
    ("CHE", "CH", "Switzerland"),
]

HEADERS = {"User-Agent": "reality-gap-research rentschler@lbsmail.de"}


def fetch_indicator(iso3: str, indicator: str, date_range: str = "1975:2024") -> list[dict]:
    url = (f"{WB_BASE}/country/{iso3}/indicator/{indicator}"
           f"?format=json&per_page=100&date={date_range}")
    print(f"  [{iso3}] {url}")
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=40)
            r.raise_for_status()
            break
        except Exception as e:
            last_err = e
            wait = 2 ** attempt
            print(f"  [{iso3}] attempt {attempt+1} failed ({e}), retry in {wait}s")
            time.sleep(wait)
    else:
        print(f"  [{iso3}] ERROR after 3 attempts: {last_err}")
        return []

    payload = r.json()
    if not isinstance(payload, list) or len(payload) < 2:
        print(f"  [{iso3}] Unexpected response format")
        return []

    data_points = payload[1]
    if not data_points:
        print(f"  [{iso3}] No data returned")
        return []

    series = []
    for pt in data_points:
        if pt.get("value") is None:
            continue
        try:
            year  = int(pt["date"])
            value = round(float(pt["value"]), 1)
        except (ValueError, TypeError):
            continue
        series.append({"year": year, "value": value})

    series.sort(key=lambda x: x["year"])
    if series:
        print(f"  [{iso3}] {len(series)} annual observations "
              f"({series[0]['year']}–{series[-1]['year']})")
    return series


def main() -> None:
    print("=" * 60)
    print("  World Bank Buffett Indicator Fetcher")
    print(f"  Indicator: {INDICATOR} — Market Cap / GDP (%)")
    print("=" * 60)

    countries_out: dict[str, dict] = {}

    for iso3, iso2, name in COUNTRIES:
        series = fetch_indicator(iso3, INDICATOR)
        countries_out[iso2] = {
            "name": name,
            "iso3": iso3,
            "series": series,
            "latest": series[-1] if series else None,
        }
        time.sleep(0.3)  # polite rate limiting

    out = {
        "indicator":   INDICATOR,
        "description": "Stock market capitalization to GDP (%)",
        "source":      "World Bank Open Data — World Development Indicators",
        "url":         f"https://data.worldbank.org/indicator/{INDICATOR}",
        "fetched":     date.today().isoformat(),
        "note": (
            "Annual data. Values above 100% indicate market cap exceeds GDP. "
            "Often called the 'Buffett Indicator' after Warren Buffett's reference "
            "to this ratio as a valuation gauge. Not adjusted for differences in "
            "listing practices, foreign company listings, or corporate structure."
        ),
        "countries": countries_out,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, separators=(",", ":"), indent=2)

    print(f"\n  Written: {OUT_PATH}")
    print("\n  Latest readings:")
    for iso2, data in countries_out.items():
        latest = data["latest"]
        if latest:
            print(f"    {iso2} ({data['name']:20s})  {latest['year']}:  {latest['value']:.1f}%")
        else:
            print(f"    {iso2} ({data['name']:20s})  no data")


if __name__ == "__main__":
    main()
