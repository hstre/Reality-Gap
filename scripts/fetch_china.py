#!/usr/bin/env python3
"""
Reality Gap — China (Hang Seng / HK-listed) Data Fetcher
=========================================================
Fetches HK-listed Chinese companies via yfinance and calculates RG8/10/12
on an ANNUAL basis, writing one JSON per company plus the China index file
(src/data/companies.china.index.json).

Why a separate script (and not fetch_data.py)
----------------------------------------------
Many HK-listed companies report semi-annually. fetch_data.py's 8-quarter
smoothing window would misread 6-month periods as quarters and roughly
double smoothed earnings G for those companies. This script therefore
smooths over ANNUAL net income with a 4-year window:

    G_t = mean(NI_{t-3} ... NI_t)          (>= 2 fiscal years required)
    RG_N = MC / (TE + N x G)   with  E_N = N x G  if G > 0, else 0

matching the methodology of the original China pilot dataset.

Market cap
----------
- Latest fiscal year:  current market cap from yfinance
- Older fiscal years:  FY-end close x current shares outstanding
  (approximation; share count changes are not reflected)

Selection rule (see src/pages/china/research.astro)
----------------------------------------------------
Only companies whose HK line represents (approximately) the full equity:
primary HK listings, WVR / red-chip structures, or HK secondary listings
of the same share class (Alibaba, Baidu, JD.com, ...).
A-share-dominant dual-listed SOEs (ICBC, China Construction Bank,
PetroChina, ...) remain excluded: market cap for their H-share ticker
cannot be reconstructed consistently.

Usage:
    python3 scripts/fetch_china.py               # full run
    python3 scripts/fetch_china.py --limit 3
    python3 scripts/fetch_china.py --ticker 0700.HK
    python3 scripts/fetch_china.py --delay 2.0

Env (optional, for proxy-restricted environments):
    YF_IMPERSONATE  e.g. "chrome110"
    YF_CA_BUNDLE    path to a CA bundle
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf

# Shared helpers / definitions from the main fetcher (same directory)
from fetch_data import (
    NI_LABELS,
    calc_rg,
    fundamental_base,
    is_near_boundary,
    make_yf_session,
    price_at_date,
    to_billions,
    trend_code,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT        = Path(__file__).resolve().parent.parent
DATA_DIR         = REPO_ROOT / "src" / "data" / "companies"
CHINA_INDEX_FILE = REPO_ROOT / "src" / "data" / "companies.china.index.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

_YF_SESSION = make_yf_session()

# ---------------------------------------------------------------------------
# Members: (ticker, name, sector, slug)
# Slugs are explicit to stay stable against display-name changes and to
# match the pre-existing files (alibaba-hk, byd-hk, ...).
# ---------------------------------------------------------------------------
CHINA_MEMBERS: list[tuple] = [
    # --- original pilot set (keep slugs/sectors unchanged) -----------------
    ("0700.HK", "Tencent",       "Technology",               "tencent"),
    ("9988.HK", "Alibaba",       "Consumer Discretionary",   "alibaba-hk"),
    ("0941.HK", "China Mobile",  "Telecommunications",       "chinamobile"),
    ("3690.HK", "Meituan",       "Technology",               "meituan"),
    ("9618.HK", "JD.com",        "Consumer Discretionary",   "jdcom"),
    ("0883.HK", "CNOOC",         "Energy",                   "cnooc"),
    ("1211.HK", "BYD",           "Consumer Discretionary",   "byd-hk"),
    # --- expansion: primary/secondary HK listings, full-equity basis -------
    ("1810.HK", "Xiaomi",        "Technology / Consumer Electronics", "xiaomi"),
    ("9888.HK", "Baidu",         "Technology",               "baidu"),
    ("9999.HK", "NetEase",       "Technology",               "netease"),
    ("1024.HK", "Kuaishou",      "Technology",               "kuaishou"),
    ("0175.HK", "Geely Automobile", "Automotive",            "geelyautomobile"),
    ("2015.HK", "Li Auto",       "Automotive",               "liauto"),
    ("9868.HK", "XPeng",         "Automotive",               "xpeng"),
    ("0992.HK", "Lenovo",        "Technology",               "lenovo"),
    ("2020.HK", "Anta Sports",   "Consumer Discretionary",   "antasports"),
    ("9961.HK", "Trip.com",      "Consumer Discretionary",   "tripcom"),
    ("9992.HK", "Pop Mart",      "Consumer Discretionary",   "popmart"),
    ("2382.HK", "Sunny Optical", "Technology",               "sunnyoptical"),
    ("2269.HK", "WuXi Biologics","Healthcare",               "wuxibiologics"),
    ("9633.HK", "Nongfu Spring", "Consumer Staples",         "nongfuspring"),
]

INDEX_NAME = "Hang Seng"
COUNTRY    = "CN"
CURRENCY   = "HKD"
WINDOW_YEARS = 4
MIN_WINDOW   = 2

OBS_NOTE = (
    "HK-listed (Hang Seng). yfinance / Yahoo Finance. "
    "MC: current market cap (latest) or shares × year-end close (historical). "
    "4-year window. All values in HKD billions. Approximation."
)

DESCRIPTION = (
    "Data sourced via yfinance / Yahoo Finance. HK-listed. "
    "Values in HKD billions. Approximation."
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fy_period_key(date: pd.Timestamp) -> str:
    q = (date.month - 1) // 3 + 1
    return f"{date.year}_q{q}"


def fy_period_label(date: pd.Timestamp) -> str:
    """FY2024 for Dec fiscal years, FY2025 (Mar) otherwise."""
    if date.month == 12:
        return f"FY{date.year}"
    return f"FY{date.year} ({date.strftime('%b')})"


def bs_value(bs: Optional[pd.DataFrame], col, keys: list[str]) -> tuple[float, bool]:
    """Return (value_raw, found) for the first matching row label."""
    if bs is None or bs.empty or col is None:
        return 0.0, False
    for k in keys:
        if k in bs.index:
            v = bs.loc[k, col]
            if pd.notna(v):
                return float(v), True
    return 0.0, False


def nearest_bs_column(bs: Optional[pd.DataFrame], target: pd.Timestamp):
    """Balance-sheet column closest to target FY-end (max 370 days off)."""
    if bs is None or bs.empty:
        return None
    best, best_delta = None, None
    for col in bs.columns:
        try:
            delta = abs((pd.Timestamp(col) - target).days)
        except Exception:
            continue
        if best_delta is None or delta < best_delta:
            best, best_delta = col, delta
    if best is not None and best_delta is not None and best_delta <= 370:
        return best
    return None


# ---------------------------------------------------------------------------
# Core fetching logic
# ---------------------------------------------------------------------------

def fetch_china_company(ticker: str, display_name: str, sector: str,
                        slug: str) -> Optional[dict]:
    print(f"  {ticker:<10} {display_name:<22}", end=" ", flush=True)
    try:
        stock = yf.Ticker(ticker, session=_YF_SESSION)
        info  = stock.info

        mc = info.get("marketCap")
        if not mc or mc <= 0:
            print("SKIP (no market cap)")
            return None
        current_mc_b = to_billions(float(mc))
        shares = float(info.get("sharesOutstanding") or 0)

        # --- Annual net income (oldest-first) --------------------------------
        a_stmt = stock.income_stmt
        if a_stmt is None or a_stmt.empty:
            print("SKIP (no annual income)")
            return None
        ni_label = next((l for l in NI_LABELS if l in a_stmt.index), None)
        if ni_label is None:
            print("SKIP (no NI row)")
            return None
        ni_series = a_stmt.loc[ni_label].dropna().sort_index()  # oldest-first
        if len(ni_series) < MIN_WINDOW:
            print("SKIP (too little history)")
            return None
        ni_b   = [to_billions(float(v)) for v in ni_series.values]
        fyends = [pd.Timestamp(d) for d in ni_series.index]

        # --- Annual balance sheet (per-FY TE) ---------------------------------
        try:
            a_bs = stock.balance_sheet
        except Exception:
            a_bs = None

        # --- Price history for historical market cap --------------------------
        try:
            price_hist = stock.history(period="15y", interval="1mo")
        except Exception:
            price_hist = pd.DataFrame()

        # --- Build one observation per fiscal year (oldest-first loop) --------
        observations: list[dict] = []
        latest_i = len(fyends) - 1
        for i, fy_end in enumerate(fyends):
            window = ni_b[max(0, i - (WINDOW_YEARS - 1)): i + 1]
            if len(window) < MIN_WINDOW:
                continue
            G = round(sum(window) / len(window), 4)

            if i == latest_i:
                mc_b, data_type = current_mc_b, "current"
            else:
                px = price_at_date(price_hist, fy_end)
                if px is None or shares <= 0:
                    continue
                mc_b, data_type = to_billions(px * shares), "annual"

            col = nearest_bs_column(a_bs, fy_end)
            eq,    eq_found = bs_value(a_bs, col, ["Stockholders Equity",
                                                   "Total Stockholders Equity",
                                                   "Common Stock Equity"])
            gw,    gw_found = bs_value(a_bs, col, ["Goodwill"])
            intan, ia_found = bs_value(a_bs, col, ["Other Intangible Assets",
                                                   "Net Intangible Assets Including Goodwill",
                                                   "Intangible Assets"])
            if not eq_found:
                continue
            te_b = to_billions(eq - gw - intan)
            te_is_approx = not (gw_found or ia_found)

            note = OBS_NOTE
            if len(window) < WINDOW_YEARS:
                note += f" Smoothing window: {len(window)}y."
            if te_is_approx:
                note += " TE approximated as book equity (GW/IA not separately available)."

            observations.append({
                "periodKey":        fy_period_key(fy_end),
                "periodLabel":      fy_period_label(fy_end),
                "rg8":              calc_rg(mc_b, G, te_b, multiplier=8),
                "rg10":             calc_rg(mc_b, G, te_b, multiplier=10),
                "rg12":             calc_rg(mc_b, G, te_b, multiplier=12),
                "trend":            None,
                "marketCap":        round(mc_b, 2),
                "tangibleEquity":   round(te_b, 2),
                "smoothedEarnings": round(G, 2),
                "fundamentalBaseRG10": fundamental_base(G, te_b, 10),
                "netIncome":        round(ni_b[i], 2),
                "goodwill":         round(to_billions(gw), 2),
                "intangibles":      round(to_billions(intan), 2),
                "bookEquity":       round(to_billions(eq), 2),
                "dataType":         data_type,
                "teIsApprox":       te_is_approx,
                "nearBoundary":     is_near_boundary(G, te_b),
                "note":             note,
            })

        if not observations:
            print("SKIP (no usable observations)")
            return None

        # Newest-first + trend codes (rg10-based)
        observations.sort(key=lambda o: o["periodKey"], reverse=True)
        for i, obs in enumerate(observations):
            prev = observations[i + 1]["rg10"] if i + 1 < len(observations) else None
            obs["trend"] = trend_code(obs["rg10"], prev)

        company = {
            "company":      display_name,
            "ticker":       ticker,
            "slug":         slug,
            "sector":       sector,
            "currency":     CURRENCY,
            "country":      COUNTRY,
            "index":        INDEX_NAME,
            "description":  DESCRIPTION,
            "observations": observations,
        }
        rg10_val = observations[0]["rg10"]
        status = "OK " if rg10_val is not None else "RG=∅"
        print(f"{status} ({len(observations)} obs, RG10={rg10_val})")
        return company

    except Exception as exc:
        print(f"ERROR: {exc}")
        return None


def merge_legacy_observations(company: dict, out_path: Path) -> None:
    """Keep observations from the existing file for fiscal years that
    yfinance no longer serves (its statement window rolls forward), so the
    historical chart does not shrink on refresh. Fresh data wins per period.
    """
    if not out_path.exists():
        return
    try:
        with open(out_path, encoding="utf-8") as f:
            old = json.load(f)
        new_keys = {o["periodKey"] for o in company["observations"]}
        legacy = [o for o in old.get("observations", [])
                  if o.get("periodKey") and o["periodKey"] not in new_keys]
        if not legacy:
            return
        merged = company["observations"] + legacy
        merged.sort(key=lambda o: o["periodKey"], reverse=True)
        for i, obs in enumerate(merged):
            prev = merged[i + 1].get("rg10") if i + 1 < len(merged) else None
            obs["trend"] = trend_code(obs.get("rg10"), prev)
        company["observations"] = merged
    except Exception as exc:
        print(f"    (legacy merge skipped: {exc})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch China RG data via yfinance")
    parser.add_argument("--limit",  type=int, default=0)
    parser.add_argument("--ticker", default="")
    parser.add_argument("--delay",  type=float, default=1.0)
    args = parser.parse_args()

    members = CHINA_MEMBERS
    if args.ticker:
        members = [m for m in CHINA_MEMBERS if m[0].upper() == args.ticker.upper()]
        if not members:
            print(f"Ticker {args.ticker} not in CHINA_MEMBERS")
            return
    elif args.limit > 0:
        members = members[: args.limit]

    china_slugs: list[str] = []
    if CHINA_INDEX_FILE.exists():
        with open(CHINA_INDEX_FILE) as f:
            china_slugs = json.load(f)

    print(f"\n{'='*60}")
    print(f"Index: CHINA / Hang Seng  ({len(members)} companies)")
    print(f"{'='*60}")

    ok = 0
    for ticker, name, sector, slug in members:
        company = fetch_china_company(ticker, name, sector, slug)
        if company is None:
            continue
        out_path = DATA_DIR / f"{slug}.json"
        merge_legacy_observations(company, out_path)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(company, f, indent=2, ensure_ascii=False)
        if slug not in china_slugs:
            china_slugs.append(slug)
        ok += 1
        time.sleep(args.delay)

    # Only rewrite the index on a full successful-ish run (not --ticker/--limit)
    if not args.ticker and args.limit == 0:
        with open(CHINA_INDEX_FILE, "w") as f:
            json.dump(china_slugs, f, indent=2)

    print(f"\n✓  {ok}/{len(members)} companies  →  {DATA_DIR}")


if __name__ == "__main__":
    main()
