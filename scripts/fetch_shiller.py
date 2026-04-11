#!/usr/bin/env python3
"""
Reality Gap — Shiller CAPE Data Fetcher
========================================
Primary source: Robert Shiller's ie_data.xls (Yale University).
Supplement:     multpl.com monthly CAPE table for months after the Yale cutoff.

The Yale file updates sporadically; multpl.com tracks the same Shiller CAPE
series on a monthly basis and is used to fill the gap to the present.

All data uses a single consistent standard: monthly observations.
- "current" field = the most recent monthly observation available
- "series"  field = all monthly observations 1881-present
- The page chart uses the same monthly series; no annual downsampling

Usage:
    python3 scripts/fetch_shiller.py

Dependencies: requests, pandas, xlrd, beautifulsoup4
    pip install requests pandas xlrd beautifulsoup4

Output JSON schema:
  {
    "source": "...",
    "sources": ["yale_xls", "multpl_supplement"],
    "yale_cutoff": "YYYY-MM",
    "fetched": "YYYY-MM-DD",
    "series_standard": "monthly",
    "note": "...",
    "current": {
      "date": "YYYY-MM",
      "cape": 39.35,
      "rg10": 3.935,
      "trend": "+"
    },
    "series": [{"date": "1881-01", "cape": 18.5, "rg10": 1.85}, ...],
    "peaks": [...]
  }
"""

from __future__ import annotations

import io
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("requests not installed: pip install requests")

try:
    import pandas as pd
except ImportError:
    sys.exit("pandas not installed: pip install pandas xlrd")

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("beautifulsoup4 not installed: pip install beautifulsoup4")

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH  = REPO_ROOT / "src" / "data" / "macro" / "sp500_cape.json"

SHILLER_URL = "http://www.econ.yale.edu/~shiller/data/ie_data.xls"
MULTPL_URL  = "https://www.multpl.com/shiller-pe/table/by-month"

HEADERS_YALE   = {"User-Agent": "reality-gap-research rentschler@lbsmail.de"}
HEADERS_MULTPL = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

PEAK_DATES = {
    "1929-09": "Great Crash — post-peak",
    "2000-01": "Dot-com bubble peak",
    "2007-10": "Pre-GFC peak",
    "2021-11": "Post-COVID peak",
}


# ---------------------------------------------------------------------------
# 1. Yale Shiller data
# ---------------------------------------------------------------------------

def fetch_yale() -> pd.DataFrame:
    """
    Download and parse Shiller ie_data.xls.
    Returns a DataFrame with columns: date_str (YYYY-MM), cape (float).
    Series standard: monthly.
    """
    print(f"  [Yale] Fetching {SHILLER_URL} ...")
    r = requests.get(SHILLER_URL, headers=HEADERS_YALE, timeout=60)
    r.raise_for_status()
    print(f"  [Yale] Downloaded {len(r.content):,} bytes")

    buf = io.BytesIO(r.content)
    # skiprows=8: 8 intro/header rows; col 0=Date, col 12=CAPE
    df = pd.read_excel(buf, sheet_name="Data", header=None,
                       engine="xlrd", skiprows=8, usecols=[0, 12])
    df.columns = ["date_raw", "cape"]

    df["date_raw"] = pd.to_numeric(df["date_raw"], errors="coerce")
    df = df.dropna(subset=["date_raw"]).copy()
    df["year"]     = df["date_raw"].astype(int)
    df["month"]    = ((df["date_raw"] - df["year"]) * 100).round().astype(int).clip(1, 12)
    df["date_str"] = (df["year"].map(lambda y: f"{y:04d}") + "-" +
                      df["month"].map(lambda m: f"{m:02d}"))

    df["cape"] = pd.to_numeric(df["cape"], errors="coerce")
    df = df[df["cape"].notna() & (df["cape"] > 0) & (df["year"] >= 1871)].copy()
    df = df[["date_str", "cape"]].sort_values("date_str").reset_index(drop=True)

    print(f"  [Yale] Parsed {len(df)} monthly observations "
          f"({df['date_str'].iloc[0]} – {df['date_str'].iloc[-1]})")
    return df


# ---------------------------------------------------------------------------
# 2. multpl.com supplement
# ---------------------------------------------------------------------------

def parse_multpl_date(raw: str) -> str | None:
    """
    Parse 'Apr 10, 2026', 'Mar 1, 2026', 'Jan 1, 2025' → 'YYYY-MM'.
    multpl.com uses 'Mon DD, YYYY' or 'Mon D, YYYY' format.
    """
    months = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
    }
    m = re.match(r'(\w{3})\s+\d+,\s+(\d{4})', raw.strip())
    if m:
        mon, yr = m.group(1), m.group(2)
        if mon in months:
            return f"{yr}-{months[mon]}"
    return None


def fetch_multpl_supplement(after: str) -> pd.DataFrame:
    """
    Scrape monthly CAPE values from multpl.com for months strictly after `after` (YYYY-MM).
    Returns DataFrame with columns: date_str, cape.
    Falls back to empty DataFrame on any error.
    """
    print(f"  [multpl] Fetching supplement for months after {after} ...")
    try:
        r = requests.get(MULTPL_URL, headers=HEADERS_MULTPL, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"  [multpl] WARNING: fetch failed ({e}). Continuing without supplement.")
        return pd.DataFrame(columns=["date_str", "cape"])

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", id="datatable")
    if not table:
        print("  [multpl] WARNING: datatable not found. Continuing without supplement.")
        return pd.DataFrame(columns=["date_str", "cape"])

    rows_out = []
    for tr in table.find_all("tr")[1:]:  # skip header
        cells = tr.find_all("td")
        if len(cells) < 2:
            continue
        date_str = parse_multpl_date(cells[0].text.strip())
        if date_str is None:
            continue
        # Only keep months strictly after the Yale cutoff
        if date_str <= after:
            continue
        cape_text = cells[1].text.strip().replace(",", "")
        try:
            cape = float(cape_text)
        except ValueError:
            continue
        if 5 < cape < 200:
            rows_out.append({"date_str": date_str, "cape": cape})

    df = pd.DataFrame(rows_out).sort_values("date_str").reset_index(drop=True)
    if not df.empty:
        print(f"  [multpl] Supplement: {len(df)} months "
              f"({df['date_str'].iloc[0]} – {df['date_str'].iloc[-1]})")
    else:
        print("  [multpl] No supplement months found after cutoff.")
    return df


# ---------------------------------------------------------------------------
# 3. Trend
# ---------------------------------------------------------------------------

def compute_trend(series: list[dict]) -> str:
    """
    12-month % change in CAPE (most recent vs 12 monthly observations ago).
    ++ >+20%  + >+5%  = ±5%  - >-5%  -- >-20%
    """
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


# ---------------------------------------------------------------------------
# 4. Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("  Shiller CAPE → M(S&P500)RG10 Fetcher  [monthly standard]")
    print("=" * 60)

    # -- Fetch Yale data --------------------------------------------------
    yale_df      = fetch_yale()
    yale_cutoff  = yale_df["date_str"].iloc[-1]

    # -- Fetch multpl supplement ------------------------------------------
    supp_df      = fetch_multpl_supplement(after=yale_cutoff)

    # -- Merge and deduplicate --------------------------------------------
    combined     = pd.concat([yale_df, supp_df], ignore_index=True)
    combined     = combined.drop_duplicates(subset="date_str").sort_values("date_str")
    combined     = combined.reset_index(drop=True)

    sources = ["yale_xls"]
    if not supp_df.empty:
        sources.append("multpl_supplement")

    print(f"\n  Combined: {len(combined)} monthly observations "
          f"({combined['date_str'].iloc[0]} – {combined['date_str'].iloc[-1]})")

    # -- Build output series ----------------------------------------------
    series = [
        {
            "date": row["date_str"],
            "cape": round(float(row["cape"]), 2),
            "rg10": round(float(row["cape"]) / 10, 3),
        }
        for _, row in combined.iterrows()
    ]

    trend   = compute_trend(series)
    current = series[-1]

    # -- Long-run stats ---------------------------------------------------
    all_rg10 = [s["rg10"] for s in series]
    avg_rg10 = sum(all_rg10) / len(all_rg10)
    max_rg10 = max(all_rg10)
    min_rg10 = min(all_rg10)

    # -- Annotate peaks ---------------------------------------------------
    by_date = {s["date"]: s for s in series}
    peaks = []
    for dt, note in PEAK_DATES.items():
        match = by_date.get(dt)
        if match:
            peaks.append({"date": dt, "note": note,
                          "cape": match["cape"], "rg10": match["rg10"]})
        else:
            peaks.append({"date": dt, "note": note})

    # -- Write output -----------------------------------------------------
    out = {
        "source": "Robert Shiller, Yale University — Irrational Exuberance dataset",
        "sources": sources,
        "yale_cutoff": yale_cutoff,
        "url": SHILLER_URL,
        "supplement_url": MULTPL_URL if "multpl_supplement" in sources else None,
        "fetched": date.today().isoformat(),
        "series_standard": "monthly",
        "note": (
            "M(S&P500)RG10 = CAPE / 10. Macro approximation — tangible equity not included. "
            f"Primary source: Yale (up to {yale_cutoff}). "
            + (f"Supplemented with multpl.com for {supp_df['date_str'].iloc[0]}–{supp_df['date_str'].iloc[-1]}."
               if not supp_df.empty else "No supplement applied.")
        ),
        "long_run_avg_rg10": round(avg_rg10, 4),
        "long_run_max_rg10": round(max_rg10, 3),
        "long_run_min_rg10": round(min_rg10, 3),
        "current": {
            "date":  current["date"],
            "cape":  current["cape"],
            "rg10":  current["rg10"],
            "trend": trend,
        },
        "series": series,
        "peaks":  peaks,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, separators=(",", ":"))

    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"\n  Written: {OUT_PATH}  ({size_kb:.0f} KB)")
    print(f"  Current: {current['date']}  CAPE={current['cape']}  "
          f"M(S&P500)RG10={current['rg10']}  trend={trend}")
    print(f"  Long-run avg RG10: {avg_rg10:.3f}  "
          f"max={max_rg10:.3f}  min={min_rg10:.3f}")
    print(f"  Sources: {sources}")


if __name__ == "__main__":
    main()
