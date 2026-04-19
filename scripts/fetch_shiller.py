#!/usr/bin/env python3
"""
Reality Gap — Shiller CAPE + S&P 500 P/B Fetcher
==================================================
Primary CAPE source:  Robert Shiller ie_data.xls (Yale University).
CAPE supplement:      multpl.com monthly CAPE table (months after Yale cutoff).
P/B source:           multpl.com S&P 500 Price-to-Book monthly table (~1960–present).

Full RG formula (where P/B available):
    M(S&P500)RG10_full = 1 / (1/PB + 10/CAPE)
                       = (PB × CAPE) / (CAPE + 10 × PB)
  Derivation:
    RG10 = Price / (BookValue + 10 × SmoothedEarnings)
         = Price / (Price/PB + 10 × Price/CAPE)
         = 1 / (1/PB + 10/CAPE)

Approximation (no P/B data, pre-1960):
    M(S&P500)RG10 = CAPE / 10  (tangible equity omitted)

Usage:
    python3 scripts/fetch_shiller.py

Dependencies: requests, pandas, xlrd, beautifulsoup4
    pip install requests pandas xlrd beautifulsoup4
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

SHILLER_URL  = "http://www.econ.yale.edu/~shiller/data/ie_data.xls"
MULTPL_URL   = "https://www.multpl.com/shiller-pe/table/by-month"
MULTPL_PB_URL = "https://www.multpl.com/s-and-p-500-price-to-book-value/table/by-month"

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
    print(f"  [Yale] Fetching {SHILLER_URL} ...")
    r = requests.get(SHILLER_URL, headers=HEADERS_YALE, timeout=60)
    r.raise_for_status()
    print(f"  [Yale] Downloaded {len(r.content):,} bytes")

    buf = io.BytesIO(r.content)
    # col 0=Date, col 6=GS10 (10-yr Treasury), col 12=CAPE
    df = pd.read_excel(buf, sheet_name="Data", header=None,
                       engine="xlrd", skiprows=8, usecols=[0, 6, 12])
    df.columns = ["date_raw", "gs10", "cape"]

    df["date_raw"] = pd.to_numeric(df["date_raw"], errors="coerce")
    df = df.dropna(subset=["date_raw"]).copy()
    df["year"]     = df["date_raw"].astype(int)
    df["month"]    = ((df["date_raw"] - df["year"]) * 100).round().astype(int).clip(1, 12)
    df["date_str"] = (df["year"].map(lambda y: f"{y:04d}") + "-" +
                      df["month"].map(lambda m: f"{m:02d}"))

    df["cape"] = pd.to_numeric(df["cape"], errors="coerce")
    df["gs10"] = pd.to_numeric(df["gs10"], errors="coerce")
    df = df[df["cape"].notna() & (df["cape"] > 0) & (df["year"] >= 1871)].copy()
    df = df[["date_str", "cape", "gs10"]].sort_values("date_str").reset_index(drop=True)

    print(f"  [Yale] Parsed {len(df)} monthly observations "
          f"({df['date_str'].iloc[0]} – {df['date_str'].iloc[-1]})")
    return df


# ---------------------------------------------------------------------------
# 2. multpl.com helpers
# ---------------------------------------------------------------------------

def parse_multpl_date(raw: str) -> str | None:
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


def fetch_multpl_table(url: str, label: str, value_min: float, value_max: float,
                       after: str | None = None) -> pd.DataFrame:
    """
    Generic multpl.com table scraper.
    `after`: if set, only return rows with date_str > after.
    """
    print(f"  [multpl/{label}] Fetching {url} ...")
    try:
        r = requests.get(url, headers=HEADERS_MULTPL, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"  [multpl/{label}] WARNING: fetch failed ({e}). Returning empty.")
        return pd.DataFrame(columns=["date_str", "value"])

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", id="datatable")
    if not table:
        print(f"  [multpl/{label}] WARNING: datatable not found.")
        return pd.DataFrame(columns=["date_str", "value"])

    rows_out = []
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all("td")
        if len(cells) < 2:
            continue
        date_str = parse_multpl_date(cells[0].text.strip())
        if date_str is None:
            continue
        if after and date_str <= after:
            continue
        val_text = cells[1].text.strip().replace(",", "")
        try:
            val = float(val_text)
        except ValueError:
            continue
        if value_min < val < value_max:
            rows_out.append({"date_str": date_str, "value": val})

    df = pd.DataFrame(rows_out).sort_values("date_str").reset_index(drop=True)
    if not df.empty:
        print(f"  [multpl/{label}] {len(df)} rows "
              f"({df['date_str'].iloc[0]} – {df['date_str'].iloc[-1]})")
    else:
        print(f"  [multpl/{label}] No rows found.")
    return df


# ---------------------------------------------------------------------------
# 3. Trend
# ---------------------------------------------------------------------------

def compute_trend(series: list[dict]) -> str:
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
    print("  Shiller CAPE + S&P500 P/B → M(S&P500)RG10 Fetcher")
    print("=" * 60)

    # -- CAPE: Yale + multpl supplement ------------------------------------
    yale_df      = fetch_yale()
    yale_cutoff  = yale_df["date_str"].iloc[-1]

    supp_df = fetch_multpl_table(
        MULTPL_URL, label="CAPE", value_min=5, value_max=200, after=yale_cutoff
    )
    supp_df = supp_df.rename(columns={"value": "cape"})

    cape_df = pd.concat([yale_df, supp_df[["date_str", "cape"]]], ignore_index=True)
    cape_df = cape_df.drop_duplicates(subset="date_str").sort_values("date_str").reset_index(drop=True)
    # gs10 comes only from Yale; fill NaN for supplement months
    if "gs10" not in cape_df.columns:
        cape_df["gs10"] = None

    sources = ["yale_xls"]
    if not supp_df.empty:
        sources.append("multpl_supplement")

    # -- P/B: multpl.com (no cutoff — take full table) ---------------------
    pb_raw = fetch_multpl_table(
        MULTPL_PB_URL, label="P/B", value_min=0.3, value_max=30.0
    )
    pb_map: dict[str, float] = {}
    if not pb_raw.empty:
        pb_map = dict(zip(pb_raw["date_str"], pb_raw["value"]))
        sources.append("multpl_pb")
        pb_series_start = pb_raw["date_str"].iloc[0]
    else:
        pb_series_start = None

    print(f"\n  CAPE series:  {len(cape_df)} months "
          f"({cape_df['date_str'].iloc[0]} – {cape_df['date_str'].iloc[-1]})")
    print(f"  P/B map:      {len(pb_map)} months")

    # -- Build output series ----------------------------------------------
    series = []
    for _, row in cape_df.iterrows():
        ds   = row["date_str"]
        cape = round(float(row["cape"]), 2)
        rg10 = round(cape / 10, 3)
        pb   = pb_map.get(ds)

        gs10_val = row.get("gs10")
        gs10 = round(float(gs10_val), 2) if gs10_val is not None and not pd.isna(gs10_val) else None

        if pb is not None and pb > 0 and cape > 0:
            rg10_full = round(1.0 / (1.0 / pb + 10.0 / cape), 3)
        else:
            rg10_full = None

        point: dict = {"date": ds, "cape": cape, "rg10": rg10}
        if gs10 is not None:
            point["gs10"] = gs10
        if pb is not None:
            point["pb"]        = round(pb, 2)
            point["rg10_full"] = rg10_full
        series.append(point)

    trend   = compute_trend(series)
    current = series[-1]

    # -- Long-run stats ---------------------------------------------------
    all_rg10      = [s["rg10"]      for s in series]
    all_rg10_full = [s["rg10_full"] for s in series if s.get("rg10_full") is not None]

    avg_rg10 = sum(all_rg10) / len(all_rg10)
    max_rg10 = max(all_rg10)
    min_rg10 = min(all_rg10)

    avg_rg10_full = (sum(all_rg10_full) / len(all_rg10_full)) if all_rg10_full else None
    max_rg10_full = max(all_rg10_full) if all_rg10_full else None
    min_rg10_full = min(all_rg10_full) if all_rg10_full else None

    # -- Annotate peaks ---------------------------------------------------
    by_date = {s["date"]: s for s in series}
    peaks = []
    for dt, note in PEAK_DATES.items():
        match = by_date.get(dt)
        if match:
            entry = {"date": dt, "note": note,
                     "cape": match["cape"], "rg10": match["rg10"]}
            if match.get("rg10_full") is not None:
                entry["rg10_full"] = match["rg10_full"]
            if match.get("pb") is not None:
                entry["pb"] = match["pb"]
            peaks.append(entry)
        else:
            peaks.append({"date": dt, "note": note})

    # -- Write output -----------------------------------------------------
    out = {
        "source": "Robert Shiller, Yale University — Irrational Exuberance dataset",
        "sources": sources,
        "yale_cutoff": yale_cutoff,
        "url": SHILLER_URL,
        "supplement_url": MULTPL_URL if "multpl_supplement" in sources else None,
        "pb_url": MULTPL_PB_URL if "multpl_pb" in sources else None,
        "pb_series_start": pb_series_start,
        "fetched": date.today().isoformat(),
        "series_standard": "monthly",
        "note": (
            "M(S&P500)RG10 = CAPE/10 (pre-1960, no P/B available). "
            "M(S&P500)RG10_full = 1/(1/PB + 10/CAPE) (1960+, includes book value). "
            f"Primary CAPE source: Yale (up to {yale_cutoff}). "
            + (f"Supplemented with multpl.com for {supp_df['date_str'].iloc[0]}–{supp_df['date_str'].iloc[-1]}."
               if not supp_df.empty else "No CAPE supplement applied.")
        ),
        "long_run_avg_rg10":       round(avg_rg10, 4),
        "long_run_max_rg10":       round(max_rg10, 3),
        "long_run_min_rg10":       round(min_rg10, 3),
        "long_run_avg_rg10_full":  round(avg_rg10_full, 4) if avg_rg10_full else None,
        "long_run_max_rg10_full":  round(max_rg10_full, 3) if max_rg10_full else None,
        "long_run_min_rg10_full":  round(min_rg10_full, 3) if min_rg10_full else None,
        "current": {
            "date":      current["date"],
            "cape":      current["cape"],
            "rg10":      current["rg10"],
            "gs10":      current.get("gs10"),
            "pb":        current.get("pb"),
            "rg10_full": current.get("rg10_full"),
            "trend":     trend,
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
          f"M(S&P500)RG10={current['rg10']}  "
          f"P/B={current.get('pb')}  "
          f"RG10_full={current.get('rg10_full')}  trend={trend}")
    if avg_rg10_full:
        print(f"  Full RG: avg={avg_rg10_full:.3f}  max={max_rg10_full:.3f}  min={min_rg10_full:.3f}")
    print(f"  Sources: {sources}")


if __name__ == "__main__":
    main()
