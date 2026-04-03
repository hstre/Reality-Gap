#!/usr/bin/env python3
"""
Reality Gap (RG) Data Fetcher
==============================
Fetches financial data via yfinance and calculates RG8, RG10, RG12
for companies in the S&P 500 (US), Nikkei 225 (JP) and DAX 40 (DE).

Usage:
    python3 scripts/fetch_data.py                     # full run (all indices)
    python3 scripts/fetch_data.py --index SP500        # only S&P 500
    python3 scripts/fetch_data.py --index N225         # only Nikkei 225
    python3 scripts/fetch_data.py --index DAX          # only DAX 40
    python3 scripts/fetch_data.py --limit 10           # max 10 companies per index
    python3 scripts/fetch_data.py --ticker AAPL        # single ticker (debug)

Output:
    src/data/companies/<slug>.json   one file per company
    src/data/companies.index.json    list of all slugs
    src/data/sectors.json            collected sector labels

Data source limitation:
    yfinance (free) typically returns only 4-5 recent quarters of income data.
    To extend to 8-12 quarters, this script supplements with annual income data
    (divided by 4 per quarter as a first-order approximation). This is clearly
    approximate; quarters reconstructed from annual data are flagged in the note.

RG formula (heuristic approximation):
    smoothedEarnings_N = mean(last N "quarterly" net incomes) * 4  [annualised]
    tangibleEquity     = totalEquity - goodwill - intangibles
    fundamentalBase    = max(tangibleEquity, 0) + smoothedEarnings_N * 10
    RG_N               = marketCap / fundamentalBase                [ratio]

    All monetary values in billions of the company's native currency.
    The factor 10 represents a simplified normalisation (10× capitalised
    earnings). See the working paper for the full derivation.

Trend thresholds (quarter-over-quarter change in RG10):
    ∆ > +10%  →  ++
    ∆ >  +3%  →  +
    |∆| ≤ 3%  →  =
    ∆ <  -3%  →  -
    ∆ < -10%  →  --
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR  = REPO_ROOT / "src" / "data" / "companies"
INDEX_FILE   = REPO_ROOT / "src" / "data" / "companies.index.json"
SECTORS_FILE = REPO_ROOT / "src" / "data" / "sectors.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Index member definitions
# Each entry: (ticker, display_name, sector, index_name, country, currency)
# ---------------------------------------------------------------------------

SP500_MEMBERS: list[tuple] = [
    ("AAPL",  "Apple",              "Technology",               "S&P 500", "US", "USD"),
    ("NVDA",  "Nvidia",             "Semiconductors",           "S&P 500", "US", "USD"),
    ("MSFT",  "Microsoft",          "Technology",               "S&P 500", "US", "USD"),
    ("AMZN",  "Amazon",             "Consumer Discretionary",   "S&P 500", "US", "USD"),
    ("GOOGL", "Alphabet",           "Technology",               "S&P 500", "US", "USD"),
    ("META",  "Meta Platforms",     "Technology",               "S&P 500", "US", "USD"),
    ("TSLA",  "Tesla",              "Automotive / Technology",  "S&P 500", "US", "USD"),
    ("BRK-B", "Berkshire Hathaway", "Financials",               "S&P 500", "US", "USD"),
    ("LLY",   "Eli Lilly",          "Healthcare",               "S&P 500", "US", "USD"),
    ("JPM",   "JPMorgan Chase",     "Financials",               "S&P 500", "US", "USD"),
    ("V",     "Visa",               "Financials",               "S&P 500", "US", "USD"),
    ("WMT",   "Walmart",            "Consumer Staples",         "S&P 500", "US", "USD"),
    ("XOM",   "ExxonMobil",         "Energy",                   "S&P 500", "US", "USD"),
    ("UNH",   "UnitedHealth",       "Healthcare",               "S&P 500", "US", "USD"),
    ("MA",    "Mastercard",         "Financials",               "S&P 500", "US", "USD"),
    ("AVGO",  "Broadcom",           "Semiconductors",           "S&P 500", "US", "USD"),
    ("COST",  "Costco",             "Consumer Staples",         "S&P 500", "US", "USD"),
    ("PG",    "Procter & Gamble",   "Consumer Staples",         "S&P 500", "US", "USD"),
    ("JNJ",   "Johnson & Johnson",  "Healthcare",               "S&P 500", "US", "USD"),
    ("HD",    "Home Depot",         "Consumer Discretionary",   "S&P 500", "US", "USD"),
    ("ABBV",  "AbbVie",             "Healthcare",               "S&P 500", "US", "USD"),
    ("BAC",   "Bank of America",    "Financials",               "S&P 500", "US", "USD"),
    ("MRK",   "Merck & Co.",        "Healthcare",               "S&P 500", "US", "USD"),
    ("ORCL",  "Oracle",             "Technology",               "S&P 500", "US", "USD"),
    ("CRM",   "Salesforce",         "Technology",               "S&P 500", "US", "USD"),
    ("CVX",   "Chevron",            "Energy",                   "S&P 500", "US", "USD"),
    ("NFLX",  "Netflix",            "Consumer Discretionary",   "S&P 500", "US", "USD"),
    ("AMD",   "AMD",                "Semiconductors",           "S&P 500", "US", "USD"),
    ("KO",    "Coca-Cola",          "Consumer Staples",         "S&P 500", "US", "USD"),
    ("PEP",   "PepsiCo",            "Consumer Staples",         "S&P 500", "US", "USD"),
]

NIKKEI_MEMBERS: list[tuple] = [
    ("7203.T",  "Toyota Motor",        "Automotive",                      "Nikkei 225", "JP", "JPY"),
    ("6758.T",  "Sony Group",          "Technology / Consumer Electronics","Nikkei 225", "JP", "JPY"),
    ("9984.T",  "SoftBank Group",      "Technology",                      "Nikkei 225", "JP", "JPY"),
    ("9983.T",  "Fast Retailing",      "Consumer Discretionary",          "Nikkei 225", "JP", "JPY"),
    ("6861.T",  "Keyence",             "Industrials",                     "Nikkei 225", "JP", "JPY"),
    ("6367.T",  "Daikin Industries",   "Industrials",                     "Nikkei 225", "JP", "JPY"),
    ("6954.T",  "Fanuc",               "Industrials",                     "Nikkei 225", "JP", "JPY"),
    ("4063.T",  "Shin-Etsu Chemical",  "Materials",                       "Nikkei 225", "JP", "JPY"),
    ("6098.T",  "Recruit Holdings",    "Industrials",                     "Nikkei 225", "JP", "JPY"),
    ("7974.T",  "Nintendo",            "Technology / Consumer Electronics","Nikkei 225", "JP", "JPY"),
    ("8306.T",  "Mitsubishi UFJ",      "Financials",                      "Nikkei 225", "JP", "JPY"),
    ("9432.T",  "NTT",                 "Telecommunications",              "Nikkei 225", "JP", "JPY"),
    ("6501.T",  "Hitachi",             "Industrials",                     "Nikkei 225", "JP", "JPY"),
    ("7267.T",  "Honda Motor",         "Automotive",                      "Nikkei 225", "JP", "JPY"),
    ("8035.T",  "Tokyo Electron",      "Semiconductors",                  "Nikkei 225", "JP", "JPY"),
    ("4519.T",  "Chugai Pharmaceutical","Healthcare",                     "Nikkei 225", "JP", "JPY"),
    ("4568.T",  "Daiichi Sankyo",      "Healthcare",                      "Nikkei 225", "JP", "JPY"),
    ("7751.T",  "Canon",               "Technology",                      "Nikkei 225", "JP", "JPY"),
    ("7267.T",  "Honda Motor",         "Automotive",                      "Nikkei 225", "JP", "JPY"),
    ("9022.T",  "Central Japan Railway","Industrials",                    "Nikkei 225", "JP", "JPY"),
]

DAX_MEMBERS: list[tuple] = [
    ("SAP.DE",  "SAP",                "Technology",              "DAX 40", "DE", "EUR"),
    ("SIE.DE",  "Siemens",            "Industrials",             "DAX 40", "DE", "EUR"),
    ("ALV.DE",  "Allianz",            "Financials",              "DAX 40", "DE", "EUR"),
    ("DTE.DE",  "Deutsche Telekom",   "Telecommunications",      "DAX 40", "DE", "EUR"),
    ("MUV2.DE", "Munich Re",          "Financials",              "DAX 40", "DE", "EUR"),
    ("MBG.DE",  "Mercedes-Benz",      "Automotive",              "DAX 40", "DE", "EUR"),
    ("BMW.DE",  "BMW",                "Automotive",              "DAX 40", "DE", "EUR"),
    ("EOAN.DE", "E.ON",               "Utilities",               "DAX 40", "DE", "EUR"),
    ("BAS.DE",  "BASF",               "Materials",               "DAX 40", "DE", "EUR"),
    ("DBK.DE",  "Deutsche Bank",      "Financials",              "DAX 40", "DE", "EUR"),
    ("RWE.DE",  "RWE",                "Utilities",               "DAX 40", "DE", "EUR"),
    ("HEN3.DE", "Henkel",             "Consumer Staples",        "DAX 40", "DE", "EUR"),
    ("IFX.DE",  "Infineon",           "Semiconductors",          "DAX 40", "DE", "EUR"),
    ("BAYN.DE", "Bayer",              "Healthcare",              "DAX 40", "DE", "EUR"),
    ("ADS.DE",  "Adidas",             "Consumer Discretionary",  "DAX 40", "DE", "EUR"),
    ("AIR.DE",  "Airbus",             "Industrials",             "DAX 40", "DE", "EUR"),
    ("VOW3.DE", "Volkswagen",         "Automotive",              "DAX 40", "DE", "EUR"),
    ("DHL.DE",  "DHL Group",          "Industrials",             "DAX 40", "DE", "EUR"),
    ("DB1.DE",  "Deutsche Boerse",    "Financials",              "DAX 40", "DE", "EUR"),
    ("CON.DE",  "Continental",        "Automotive",              "DAX 40", "DE", "EUR"),
    ("MRK.DE",  "Merck KGaA",         "Healthcare",              "DAX 40", "DE", "EUR"),
    ("BNR.DE",  "Brenntag",           "Materials",               "DAX 40", "DE", "EUR"),
    ("SHL.DE",  "Siemens Healthineers","Healthcare",             "DAX 40", "DE", "EUR"),
    ("HEI.DE",  "HeidelbergMaterials","Materials",               "DAX 40", "DE", "EUR"),
    ("P911.DE", "Porsche AG",         "Automotive",              "DAX 40", "DE", "EUR"),
    ("FRE.DE",  "Fresenius",          "Healthcare",              "DAX 40", "DE", "EUR"),
    ("QIA.DE",  "Qiagen",             "Healthcare",              "DAX 40", "DE", "EUR"),
    ("SY1.DE",  "Symrise",            "Materials",               "DAX 40", "DE", "EUR"),
    ("PAH3.DE", "Porsche SE",         "Financials",              "DAX 40", "DE", "EUR"),
    ("SRT.DE",  "Sartorius",          "Healthcare",              "DAX 40", "DE", "EUR"),
]

INDEX_MAP = {
    "SP500": SP500_MEMBERS,
    "N225":  NIKKEI_MEMBERS,
    "DAX":   DAX_MEMBERS,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[&/]", "-", s)
    s = re.sub(r"[^a-z0-9\-]", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def period_key(date: pd.Timestamp) -> str:
    q = (date.month - 1) // 3 + 1
    return f"{date.year}_q{q}"


def period_label(date: pd.Timestamp) -> str:
    q = (date.month - 1) // 3 + 1
    return f"Q{q} {date.year}"


def to_billions(value: float) -> float:
    return round(value / 1e9, 4)


def trend_code(current: Optional[float], previous: Optional[float]) -> Optional[str]:
    if current is None or previous is None or previous == 0:
        return None
    delta = (current - previous) / abs(previous) * 100
    if delta > 10:  return "++"
    if delta > 3:   return "+"
    if delta >= -3: return "="
    if delta >= -10:return "-"
    return "--"


def calc_rg(market_cap_b: float, smoothed_annual_earnings_b: float,
            tangible_equity_b: float) -> Optional[float]:
    """
    RG = marketCap / fundamentalBase
    fundamentalBase = max(tangibleEquity, 0) + smoothedAnnualEarnings * 10
    """
    fb = max(tangible_equity_b, 0.0) + smoothed_annual_earnings_b * 10
    if fb <= 0:
        return None
    return round(market_cap_b / fb, 2)


def build_ni_series(quarterly_ni: list[float], annual_ni: list[float],
                    n_needed: int) -> tuple[list[float], bool]:
    """
    Build a combined quarterly NI series (newest-first) of length n_needed.

    Strategy:
    - Take as many actual quarterly values as possible (newest first).
    - Fill remaining slots by dividing each annual NI value by 4 (per-quarter
      approximation), oldest annual first.
    - Annual and quarterly periods may overlap slightly; this is acceptable
      for a heuristic indicator.

    Returns (series, is_supplemented) where is_supplemented=True if annual
    data was used.
    """
    result = list(quarterly_ni)
    supplemented = False

    if len(result) >= n_needed:
        return result[:n_needed], supplemented

    # Fill with annual / 4 (oldest annuals fill the gap)
    for ann_val in reversed(annual_ni):        # oldest annual first
        per_q = ann_val / 4.0
        for _ in range(4):
            if len(result) >= n_needed:
                break
            result.append(per_q)
            supplemented = True
        if len(result) >= n_needed:
            break

    return result, supplemented


# ---------------------------------------------------------------------------
# Core fetching logic
# ---------------------------------------------------------------------------

def fetch_company(ticker: str, display_name: str, sector: str,
                  index_name: str, country: str, currency: str,
                  slug_override: Optional[str] = None) -> Optional[dict]:
    """
    Fetch and compute RG data for one company.
    Returns a company dict or None on failure.
    """
    print(f"  {ticker:<12} {display_name:<30}", end=" ", flush=True)
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info

        # --- Market cap -------------------------------------------------------
        mc = info.get("marketCap")
        if not mc or mc <= 0:
            print("SKIP (no market cap)")
            return None
        market_cap_b = to_billions(float(mc))

        # --- Quarterly net income (newest first after sorting) ----------------
        try:
            q_stmt = stock.quarterly_income_stmt
        except Exception:
            q_stmt = pd.DataFrame()

        if q_stmt is None or q_stmt.empty:
            print("SKIP (no quarterly income)")
            return None

        NI_LABELS = [
            "Net Income",
            "Net Income Common Stockholders",
            "Net Income From Continuing Operation Net Minority Interest",
            "Net Income Including Noncontrolling Interests",
            "Net Income From Continuing And Discontinued Operation",
            "Net Income Continuous Operations",
            "Normalized Income",
        ]
        ni_label = next((l for l in NI_LABELS if l in q_stmt.index), None)

        # --- Annual net income (always try, used as fallback or supplement) --
        a_values: list[float] = []
        annual_latest_date: Optional[pd.Timestamp] = None
        try:
            a_stmt = stock.income_stmt
            if a_stmt is not None and not a_stmt.empty:
                a_ni_label = next((l for l in NI_LABELS if l in a_stmt.index), None)
                if a_ni_label:
                    a_series = a_stmt.loc[a_ni_label].dropna().sort_index()
                    a_values = [to_billions(float(v)) for v in reversed(a_series.values)]
                    if len(a_series) > 0:
                        annual_latest_date = a_series.index[-1]
        except Exception:
            pass

        # If quarterly NI label not found, try to use annual data only
        if ni_label is None:
            if not a_values:
                print("SKIP (no income data at all)")
                return None
            # Use annual data as synthetic quarterly series
            q_ni_series = None
            latest_q_date = annual_latest_date  # approximate period from last annual
            q_values = []  # no real quarterly values
        else:
            q_ni_series = q_stmt.loc[ni_label].dropna().sort_index()  # oldest first
            if len(q_ni_series) < 1:
                if not a_values:
                    print("SKIP (no data)")
                    return None
                # No quarterly data but have annual
                q_ni_series = None
                latest_q_date = annual_latest_date
                q_values = []
            else:
                latest_q_date = q_ni_series.index[-1]
                q_values = [to_billions(float(v)) for v in reversed(q_ni_series.values)]

        # --- Tangible equity (from latest balance sheet) --------------------
        tangible_eq_b = 0.0
        try:
            q_bs = stock.quarterly_balance_sheet
            if q_bs is not None and not q_bs.empty:
                col = sorted(q_bs.columns)[-1]

                def bs(keys: list[str]) -> float:
                    for k in keys:
                        if k in q_bs.index:
                            v = q_bs.loc[k, col]
                            if pd.notna(v):
                                return float(v)
                    return 0.0

                eq    = bs(["Stockholders Equity", "Total Stockholders Equity",
                             "Common Stock Equity"])
                gw    = bs(["Goodwill"])
                intan = bs(["Other Intangible Assets", "Net Intangible Assets Including Goodwill",
                             "Intangible Assets"])
                tangible_eq_b = to_billions(eq - gw - intan)
        except Exception:
            pass

        # --- Build one observation (latest quarter) using hybrid NI series ---
        # We create a single observation for the most recent available quarter.
        # Trend will be based on a second observation built from the prior quarter.

        observations: list[dict] = []

        n_obs = min(4, max(1, len(q_values))) if q_values else 1
        for obs_idx in range(n_obs):
            # For observation obs_idx, shift NI series back by obs_idx quarters.
            if q_ni_series is not None and obs_idx >= len(q_ni_series):
                break

            if q_ni_series is not None:
                date = q_ni_series.index[-(obs_idx + 1)]
            else:
                # Annual-only fallback: approximate date from last annual report
                date = latest_q_date
            pk   = period_key(date)
            pl   = period_label(date)

            # Slice quarterly values starting from obs_idx (skip most-recent obs_idx)
            avail_q = q_values[obs_idx:]

            series8,  sup8  = build_ni_series(avail_q, a_values, 8)
            series10, sup10 = build_ni_series(avail_q, a_values, 10)
            series12, sup12 = build_ni_series(avail_q, a_values, 12)

            def smoothed_annual(series: list[float]) -> Optional[float]:
                if len(series) == 0:
                    return None
                return round(sum(series) / len(series) * 4, 4)

            rg8  = calc_rg(market_cap_b, smoothed_annual(series8)  or 0, tangible_eq_b) if len(series8)  >= 8  else None
            rg10 = calc_rg(market_cap_b, smoothed_annual(series10) or 0, tangible_eq_b) if len(series10) >= 10 else None
            rg12 = calc_rg(market_cap_b, smoothed_annual(series12) or 0, tangible_eq_b) if len(series12) >= 12 else None

            # Build note
            used_annual = any([sup8, sup10, sup12])
            note_parts = ["Computed via yfinance."]
            if used_annual:
                note_parts.append(
                    "Insufficient quarterly history; older quarters estimated from "
                    "annual net income / 4. Historical market cap not adjusted.")
            note_parts.append("Approximation — not fully adjusted.")

            fb_approx = round(max(tangible_eq_b, 0) + (smoothed_annual(series10) or 0) * 10, 2)

            obs: dict = {
                "periodKey":   pk,
                "periodLabel": pl,
                "rg8":  rg8,
                "rg10": rg10,
                "rg12": rg12,
                "trend": None,
                "marketCap":             round(market_cap_b, 1),
                "bookEquity":            round(tangible_eq_b, 1),
                "netIncome":             round((avail_q[0] if avail_q else 0) * 4, 1),
                "fundamentalBaseApprox": fb_approx,
                "note": " ".join(note_parts),
            }
            observations.append(obs)

        # Sort newest-first and fill trend codes
        # observations are already newest-first (obs_idx 0 = newest)
        for i in range(len(observations)):
            curr = observations[i]["rg10"]
            prev = observations[i + 1]["rg10"] if i + 1 < len(observations) else None
            observations[i]["trend"] = trend_code(curr, prev)

        # Keep only observations with at least rg10
        observations = [o for o in observations if o.get("rg10") is not None]

        if not observations:
            print("SKIP (no valid RG10)")
            return None

        slug = slug_override or slugify(display_name)

        company = {
            "company":     display_name,
            "ticker":      ticker,
            "slug":        slug,
            "sector":      sector,
            "currency":    currency,
            "country":     country,
            "index":       index_name,
            "description": "Data sourced via yfinance / Yahoo Finance. Illustrative approximation.",
            "observations": observations,
        }

        rg10_val = observations[0].get("rg10")
        print(f"OK  ({len(observations)} obs, RG10={rg10_val})")
        return company

    except Exception as exc:
        print(f"ERROR: {exc}")
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch RG data via yfinance")
    parser.add_argument("--index",  choices=["SP500", "N225", "DAX", "ALL"],
                        default="ALL")
    parser.add_argument("--limit",  type=int, default=0,
                        help="Max companies per index (0 = no limit)")
    parser.add_argument("--ticker", default="",
                        help="Single ticker debug mode")
    parser.add_argument("--delay",  type=float, default=0.8,
                        help="Seconds between requests (default 0.8)")
    args = parser.parse_args()

    # ---- Single ticker debug ------------------------------------------------
    if args.ticker:
        result = fetch_company(
            args.ticker, args.ticker, "Unknown", "Debug", "XX", "USD")
        if result:
            print(json.dumps(result, indent=2, default=str))
        return

    # ---- Select indices to run  ---------------------------------------------
    to_run = list(INDEX_MAP.keys()) if args.index == "ALL" else [args.index]

    all_slugs: list[str] = []
    all_sectors: set[str] = set()

    # Preserve existing manually created entries
    if INDEX_FILE.exists():
        with open(INDEX_FILE) as f:
            all_slugs = json.load(f)
    if SECTORS_FILE.exists():
        with open(SECTORS_FILE) as f:
            all_sectors = set(json.load(f))

    # ---- Fetch  -------------------------------------------------------------
    for index_key in to_run:
        members = INDEX_MAP[index_key]
        if args.limit > 0:
            members = members[: args.limit]

        print(f"\n{'='*60}")
        print(f"Index: {index_key}  ({len(members)} companies)")
        print(f"{'='*60}")

        seen_slugs_this_run: set[str] = set()

        for ticker, name, sector, index_name, country, currency in members:
            slug = slugify(name)
            if slug in seen_slugs_this_run:
                continue  # skip duplicate names
            seen_slugs_this_run.add(slug)

            company = fetch_company(ticker, name, sector, index_name,
                                    country, currency, slug_override=slug)
            if company is None:
                continue

            out_path = DATA_DIR / f"{slug}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(company, f, indent=2, ensure_ascii=False)

            if slug not in all_slugs:
                all_slugs.append(slug)
            all_sectors.add(sector)

            time.sleep(args.delay)

    # ---- Write index + sectors  ---------------------------------------------
    with open(INDEX_FILE, "w") as f:
        json.dump(all_slugs, f, indent=2)

    sorted_sectors = sorted(all_sectors)
    with open(SECTORS_FILE, "w") as f:
        json.dump(sorted_sectors, f, indent=2)

    print(f"\n✓  {len(all_slugs)} companies  →  {DATA_DIR}")
    print(f"✓  {len(sorted_sectors)} sectors  →  {SECTORS_FILE}")
    print(f"✓  Index  →  {INDEX_FILE}")


if __name__ == "__main__":
    main()
