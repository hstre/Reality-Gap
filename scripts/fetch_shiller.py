#!/usr/bin/env python3
"""
Reality Gap — Shiller CAPE Data Fetcher
========================================
Fetches Robert Shiller's ie_data.xls from Yale and writes
src/data/macro/sp500_cape.json with the full CAPE / M(S&P500)RG10 series.

Usage:
    python3 scripts/fetch_shiller.py

Dependencies: requests, pandas, xlrd  (pip install requests pandas xlrd)

Output JSON schema:
  {
    "source": "...",
    "fetched": "YYYY-MM-DD",
    "note": "...",
    "current": {
      "date": "YYYY-MM",
      "cape": 30.8,
      "rg10": 3.08,
      "trend": "+"
    },
    "series": [
      {"date": "1881-01", "cape": 18.5, "rg10": 1.85},
      ...
    ],
    "peaks": [...]
  }
"""

from __future__ import annotations

import io
import json
import sys
from datetime import date
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    sys.exit("requests not installed: pip install requests")

try:
    import pandas as pd
    import numpy as np
except ImportError:
    sys.exit("pandas not installed: pip install pandas xlrd")

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH  = REPO_ROOT / "src" / "data" / "macro" / "sp500_cape.json"

SHILLER_URL = "http://www.econ.yale.edu/~shiller/data/ie_data.xls"
HEADERS = {"User-Agent": "reality-gap-research rentschler@lbsmail.de"}

# Known peaks for annotation
PEAK_DATES = {
    "1929-09": "Great Crash — post-peak",
    "2000-01": "Dot-com bubble peak",
    "2007-10": "Pre-GFC peak",
    "2021-11": "Post-COVID peak",
}


def fetch_shiller() -> pd.DataFrame:
    """Download Shiller Excel and return a clean DataFrame with date_str and cape."""
    print(f"  Fetching {SHILLER_URL} ...")
    r = requests.get(SHILLER_URL, headers=HEADERS, timeout=60)
    r.raise_for_status()
    print(f"  Downloaded {len(r.content):,} bytes")

    buf = io.BytesIO(r.content)
    # skiprows=8: skip the 8 intro/header rows (rows 0-7); row 8 is first data row
    df = pd.read_excel(buf, sheet_name="Data", header=None, engine="xlrd", skiprows=8)

    # Column layout (from inspecting header rows 5-7):
    # 0=Date, 1=P, 2=D, 3=E, 4=CPI, 5=Fraction,
    # 6=Rate GS10, 7=Real Price, 8=Real Dividend, 9=Real TR Price,
    # 10=Real Earnings, 11=Real Scaled Earnings, 12=CAPE(P/E10),
    # 13=?, 14=TR CAPE, 15=?, 16=CAPE Yield, ...
    CAPE_COL = 12

    df = df[[0, CAPE_COL]].copy()
    df.columns = ["date_raw", "cape"]

    # Parse dates: Shiller format is float YYYY.MM (e.g. 1881.01, 2023.09)
    df["date_raw"] = pd.to_numeric(df["date_raw"], errors="coerce")
    df = df.dropna(subset=["date_raw"])
    df["year"]  = df["date_raw"].astype(int)
    df["month"] = ((df["date_raw"] - df["year"]) * 100).round().astype(int).clip(1, 12)
    df["date_str"] = (
        df["year"].map(lambda y: f"{y:04d}") + "-" +
        df["month"].map(lambda m: f"{m:02d}")
    )

    # Parse CAPE
    df["cape"] = pd.to_numeric(df["cape"], errors="coerce")
    df = df[df["cape"].notna() & (df["cape"] > 0) & (df["year"] >= 1871)].copy()
    df = df.sort_values("date_str").reset_index(drop=True)

    print(f"  Parsed {len(df)} monthly observations")
    print(f"  CAPE range: {df['date_str'].iloc[0]} – {df['date_str'].iloc[-1]}")
    return df


def compute_trend(series: list[dict]) -> str:
    """12-month % change in CAPE → trend symbol."""
    if len(series) < 13:
        return "="
    current  = series[-1]["cape"]
    year_ago = series[-13]["cape"]
    if year_ago == 0:
        return "="
    pct = (current - year_ago) / year_ago * 100
    if   pct >  20: return "++"
    elif pct >   5: return "+"
    elif pct < -20: return "--"
    elif pct <  -5: return "-"
    else:            return "="


def main() -> None:
    print("=" * 60)
    print("  Shiller CAPE → M(S&P500)RG10 Fetcher")
    print("=" * 60)

    df = fetch_shiller()

    series = [
        {
            "date": row["date_str"],
            "cape": round(float(row["cape"]), 2),
            "rg10": round(float(row["cape"]) / 10, 3),
        }
        for _, row in df.iterrows()
    ]

    trend   = compute_trend(series)
    current = series[-1]

    # Annotate peaks
    series_by_date = {s["date"]: s for s in series}
    peaks = []
    for dt, note in PEAK_DATES.items():
        match = series_by_date.get(dt)
        if match:
            peaks.append({"date": dt, "note": note,
                          "cape": match["cape"], "rg10": match["rg10"]})
        else:
            peaks.append({"date": dt, "note": note})

    out = {
        "source": "Robert Shiller, Yale University — Irrational Exuberance dataset",
        "url": SHILLER_URL,
        "fetched": date.today().isoformat(),
        "note": (
            "M(S&P500)RG10 = CAPE / 10. "
            "Macro approximation only — tangible equity not included. "
            "CAPE = cyclically adjusted P/E ratio (10-year real earnings average)."
        ),
        "current": {
            "date":  current["date"],
            "cape":  current["cape"],
            "rg10":  current["rg10"],
            "trend": trend,
        },
        "series":  series,
        "peaks":   peaks,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, separators=(",", ":"))

    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"\n  Written: {OUT_PATH}  ({size_kb:.0f} KB)")
    print(f"  Current: {current['date']}  CAPE={current['cape']}  "
          f"M(S&P500)RG10={current['rg10']}  trend={trend}")
    print()
    print("  Key peaks:")
    for p in peaks:
        if "cape" in p:
            print(f"    {p['date']}  CAPE={p['cape']:.2f}  RG10={p['rg10']:.2f}  ({p['note']})")


if __name__ == "__main__":
    main()
