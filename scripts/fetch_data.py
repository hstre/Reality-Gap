#!/usr/bin/env python3
"""
Reality Gap (RG) Data Fetcher  —  with historical annual chart data
=====================================================================
Fetches via yfinance and calculates RG8/10/12 for S&P 500, Nikkei 225, DAX 40.

Two layers of observations per company
---------------------------------------
1. RECENT (quarterly)  — last 4 quarters, from quarterly_income_stmt
2. HISTORICAL (annual) — per fiscal year using annual_income + historical price

Historical market cap  =  closing price at FY-end  x  current shares outstanding
(approximation; share count changes are not reflected)

Usage:
    python3 scripts/fetch_data.py               # full run
    python3 scripts/fetch_data.py --index SP500
    python3 scripts/fetch_data.py --limit 5
    python3 scripts/fetch_data.py --ticker AAPL
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT    = Path(__file__).resolve().parent.parent
DATA_DIR     = REPO_ROOT / "src" / "data" / "companies"
INDEX_FILE   = REPO_ROOT / "src" / "data" / "companies.index.json"
SECTORS_FILE = REPO_ROOT / "src" / "data" / "sectors.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Index member definitions  (ticker, name, sector, index, country, currency)
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
    ("7203.T",  "Toyota Motor",         "Automotive",                       "Nikkei 225", "JP", "JPY"),
    ("6758.T",  "Sony Group",           "Technology / Consumer Electronics","Nikkei 225", "JP", "JPY"),
    ("9984.T",  "SoftBank Group",       "Technology",                       "Nikkei 225", "JP", "JPY"),
    ("9983.T",  "Fast Retailing",       "Consumer Discretionary",           "Nikkei 225", "JP", "JPY"),
    ("6861.T",  "Keyence",              "Industrials",                      "Nikkei 225", "JP", "JPY"),
    ("6367.T",  "Daikin Industries",    "Industrials",                      "Nikkei 225", "JP", "JPY"),
    ("6954.T",  "Fanuc",                "Industrials",                      "Nikkei 225", "JP", "JPY"),
    ("4063.T",  "Shin-Etsu Chemical",   "Materials",                        "Nikkei 225", "JP", "JPY"),
    ("6098.T",  "Recruit Holdings",     "Industrials",                      "Nikkei 225", "JP", "JPY"),
    ("7974.T",  "Nintendo",             "Technology / Consumer Electronics","Nikkei 225", "JP", "JPY"),
    ("8306.T",  "Mitsubishi UFJ",       "Financials",                       "Nikkei 225", "JP", "JPY"),
    ("9432.T",  "NTT",                  "Telecommunications",               "Nikkei 225", "JP", "JPY"),
    ("6501.T",  "Hitachi",              "Industrials",                      "Nikkei 225", "JP", "JPY"),
    ("7267.T",  "Honda Motor",          "Automotive",                       "Nikkei 225", "JP", "JPY"),
    ("8035.T",  "Tokyo Electron",       "Semiconductors",                   "Nikkei 225", "JP", "JPY"),
    ("4519.T",  "Chugai Pharmaceutical","Healthcare",                       "Nikkei 225", "JP", "JPY"),
    ("4568.T",  "Daiichi Sankyo",       "Healthcare",                       "Nikkei 225", "JP", "JPY"),
    ("7751.T",  "Canon",                "Technology",                       "Nikkei 225", "JP", "JPY"),
    ("9022.T",  "Central Japan Railway","Industrials",                      "Nikkei 225", "JP", "JPY"),
]

DAX_MEMBERS: list[tuple] = [
    ("SAP.DE",  "SAP",                 "Technology",              "DAX 40", "DE", "EUR"),
    ("SIE.DE",  "Siemens",             "Industrials",             "DAX 40", "DE", "EUR"),
    ("ALV.DE",  "Allianz",             "Financials",              "DAX 40", "DE", "EUR"),
    ("DTE.DE",  "Deutsche Telekom",    "Telecommunications",      "DAX 40", "DE", "EUR"),
    ("MUV2.DE", "Munich Re",           "Financials",              "DAX 40", "DE", "EUR"),
    ("MBG.DE",  "Mercedes-Benz",       "Automotive",              "DAX 40", "DE", "EUR"),
    ("BMW.DE",  "BMW",                 "Automotive",              "DAX 40", "DE", "EUR"),
    ("EOAN.DE", "E.ON",                "Utilities",               "DAX 40", "DE", "EUR"),
    ("BAS.DE",  "BASF",                "Materials",               "DAX 40", "DE", "EUR"),
    ("DBK.DE",  "Deutsche Bank",       "Financials",              "DAX 40", "DE", "EUR"),
    ("RWE.DE",  "RWE",                 "Utilities",               "DAX 40", "DE", "EUR"),
    ("HEN3.DE", "Henkel",              "Consumer Staples",        "DAX 40", "DE", "EUR"),
    ("IFX.DE",  "Infineon",            "Semiconductors",          "DAX 40", "DE", "EUR"),
    ("BAYN.DE", "Bayer",               "Healthcare",              "DAX 40", "DE", "EUR"),
    ("ADS.DE",  "Adidas",              "Consumer Discretionary",  "DAX 40", "DE", "EUR"),
    ("AIR.DE",  "Airbus",              "Industrials",             "DAX 40", "DE", "EUR"),
    ("VOW3.DE", "Volkswagen",          "Automotive",              "DAX 40", "DE", "EUR"),
    ("DHL.DE",  "DHL Group",           "Industrials",             "DAX 40", "DE", "EUR"),
    ("DB1.DE",  "Deutsche Boerse",     "Financials",              "DAX 40", "DE", "EUR"),
    ("CON.DE",  "Continental",         "Automotive",              "DAX 40", "DE", "EUR"),
    ("MRK.DE",  "Merck KGaA",          "Healthcare",              "DAX 40", "DE", "EUR"),
    ("BNR.DE",  "Brenntag",            "Materials",               "DAX 40", "DE", "EUR"),
    ("SHL.DE",  "Siemens Healthineers","Healthcare",              "DAX 40", "DE", "EUR"),
    ("HEI.DE",  "HeidelbergMaterials", "Materials",               "DAX 40", "DE", "EUR"),
    ("P911.DE", "Porsche AG",          "Automotive",              "DAX 40", "DE", "EUR"),
    ("FRE.DE",  "Fresenius",           "Healthcare",              "DAX 40", "DE", "EUR"),
    ("QIA.DE",  "Qiagen",              "Healthcare",              "DAX 40", "DE", "EUR"),
    ("SY1.DE",  "Symrise",             "Materials",               "DAX 40", "DE", "EUR"),
    ("PAH3.DE", "Porsche SE",          "Financials",              "DAX 40", "DE", "EUR"),
    ("SRT.DE",  "Sartorius",           "Healthcare",              "DAX 40", "DE", "EUR"),
]

INDEX_MAP = {
    "SP500": SP500_MEMBERS,
    "N225":  NIKKEI_MEMBERS,
    "DAX":   DAX_MEMBERS,
}

NI_LABELS = [
    "Net Income",
    "Net Income Common Stockholders",
    "Net Income From Continuing Operation Net Minority Interest",
    "Net Income Including Noncontrolling Interests",
    "Net Income From Continuing And Discontinued Operation",
    "Net Income Continuous Operations",
    "Normalized Income",
]

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
    if delta > 10:   return "++"
    if delta > 3:    return "+"
    if delta >= -3:  return "="
    if delta >= -10: return "-"
    return "--"


def calc_rg(market_cap_b: float, smoothed_annual_b: float,
            tangible_eq_b: float) -> Optional[float]:
    """RG = marketCap / (max(tangibleEquity,0) + smoothedAnnualEarnings*10)"""
    fb = max(tangible_eq_b, 0.0) + smoothed_annual_b * 10
    if fb <= 0:
        return None
    return round(market_cap_b / fb, 2)


def build_ni_series(quarterly_ni: list[float], annual_ni: list[float],
                    n_needed: int) -> tuple[list[float], bool]:
    """Extend quarterly series with annual/4 fallback (newest-first)."""
    result = list(quarterly_ni)
    supplemented = False
    if len(result) >= n_needed:
        return result[:n_needed], supplemented
    for ann_val in reversed(annual_ni):
        per_q = ann_val / 4.0
        for _ in range(4):
            if len(result) >= n_needed:
                break
            result.append(per_q)
            supplemented = True
        if len(result) >= n_needed:
            break
    return result, supplemented


def price_at_date(history_df: pd.DataFrame,
                  target: pd.Timestamp) -> Optional[float]:
    """Return the closing price closest to target date."""
    if history_df is None or history_df.empty:
        return None
    try:
        # history index may be tz-aware; normalise
        idx = history_df.index
        if hasattr(idx, "tz") and idx.tz is not None:
            idx_naive = idx.tz_localize(None)
        else:
            idx_naive = idx
        target_naive = target.tz_localize(None) if target.tzinfo else target
        pos = idx_naive.searchsorted(target_naive)
        pos = min(pos, len(history_df) - 1)
        return float(history_df["Close"].iloc[pos])
    except Exception:
        return None


def build_historical_annual_obs(
    annual_ni_series: pd.Series,      # annual NI oldest-first
    price_history: pd.DataFrame,       # daily/quarterly price history
    shares: float,                     # current shares outstanding
    tangible_eq_b: float,
    current_mc_b: float,
) -> list[dict]:
    """
    Build one RG observation per available fiscal-year-end using:
      - Annual NI rolling window (oldest data extends backwards)
      - Historical market cap = price at FY-end × current shares (approx)

    Returns observations oldest-first.
    """
    if annual_ni_series is None or len(annual_ni_series) < 2:
        return []

    annual_values_b = [to_billions(float(v)) for v in annual_ni_series.values]  # oldest-first
    dates            = list(annual_ni_series.index)  # oldest-first Timestamps

    observations: list[dict] = []

    for i, date in enumerate(dates):
        # NI series available UP TO this year (index 0..i), convert to quarterly equiv
        avail_annual  = annual_values_b[: i + 1]   # oldest to this year
        # Build per-quarter synthetic values (each annual = 4 quarters)
        q_synthetic   = [v / 4.0 for v in avail_annual for _ in range(4)]
        n_q = len(q_synthetic)

        # Need at least 8 synthetic quarters for any RG variant
        if n_q < 8:
            continue

        # Historical market cap
        hist_price = price_at_date(price_history, date)
        if hist_price and shares > 0:
            hist_mc_b = to_billions(hist_price * shares)
        else:
            hist_mc_b = current_mc_b  # fallback

        # Smoothed earnings (annualised mean over window)
        def se(n: int) -> Optional[float]:
            if n_q < n:
                return None
            window = q_synthetic[-n:]   # most-recent n synthetic quarters
            return round(sum(window) / n * 4, 4)

        se8  = se(8)
        se10 = se(10)
        se12 = se(12)

        rg8  = calc_rg(hist_mc_b, se8  or 0, tangible_eq_b) if se8  else None
        rg10 = calc_rg(hist_mc_b, se10 or 0, tangible_eq_b) if se10 else None
        rg12 = calc_rg(hist_mc_b, se12 or 0, tangible_eq_b) if se12 else None

        # Skip only if we can't compute even RG8
        if rg8 is None:
            continue

        fb = round(max(tangible_eq_b, 0) + (se10 or 0) * 10, 2)

        obs: dict = {
            "periodKey":             period_key(date),
            "periodLabel":           period_label(date),
            "rg8":   rg8,
            "rg10":  rg10,
            "rg12":  rg12,
            "trend": None,
            "marketCap":             round(hist_mc_b, 1),
            "bookEquity":            round(tangible_eq_b, 1),
            "netIncome":             round(avail_annual[-1] if avail_annual else 0, 1),
            "fundamentalBaseApprox": fb,
            "dataType":              "annual",
            "note": (
                "Annual historical observation. Market cap approximated from "
                "historical close price × current shares outstanding. "
                "Earnings smoothed from available annual data. Approximation."
            ),
        }
        observations.append(obs)

    return observations  # oldest-first


# ---------------------------------------------------------------------------
# Core fetching logic
# ---------------------------------------------------------------------------

def fetch_company(ticker: str, display_name: str, sector: str,
                  index_name: str, country: str, currency: str,
                  slug_override: Optional[str] = None) -> Optional[dict]:
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
        shares = float(info.get("sharesOutstanding") or 0)

        # --- Price history (for historical market cap) -------------------------
        try:
            price_hist = stock.history(period="15y", interval="1mo")
        except Exception:
            price_hist = pd.DataFrame()

        # --- Quarterly income -------------------------------------------------
        try:
            q_stmt = stock.quarterly_income_stmt
        except Exception:
            q_stmt = pd.DataFrame()

        if q_stmt is None or q_stmt.empty:
            print("SKIP (no quarterly income)")
            return None

        ni_label = next((l for l in NI_LABELS if l in q_stmt.index), None)

        # --- Annual income (supplement + historical chart) --------------------
        a_series_sorted: Optional[pd.Series] = None
        a_values: list[float] = []
        annual_latest_date: Optional[pd.Timestamp] = None
        try:
            a_stmt = stock.income_stmt
            if a_stmt is not None and not a_stmt.empty:
                a_ni_label = next((l for l in NI_LABELS if l in a_stmt.index), None)
                if a_ni_label:
                    raw = a_stmt.loc[a_ni_label].dropna().sort_index()  # oldest-first
                    a_series_sorted = raw
                    a_values = [to_billions(float(v)) for v in reversed(raw.values)]
                    if len(raw) > 0:
                        annual_latest_date = raw.index[-1]
        except Exception:
            pass

        # --- Tangible equity --------------------------------------------------
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
                intan = bs(["Other Intangible Assets",
                             "Net Intangible Assets Including Goodwill",
                             "Intangible Assets"])
                tangible_eq_b = to_billions(eq - gw - intan)
        except Exception:
            pass

        # --- Recent quarterly observations (newest-first) --------------------
        if ni_label is None:
            if not a_values:
                print("SKIP (no income data)")
                return None
            q_ni_series = None
            latest_q_date = annual_latest_date
            q_values: list[float] = []
        else:
            raw_q = q_stmt.loc[ni_label].dropna().sort_index()
            if len(raw_q) < 1:
                if not a_values:
                    print("SKIP (no data)")
                    return None
                q_ni_series = None
                latest_q_date = annual_latest_date
                q_values = []
            else:
                q_ni_series   = raw_q
                latest_q_date = raw_q.index[-1]
                q_values = [to_billions(float(v)) for v in reversed(raw_q.values)]

        recent_obs: list[dict] = []
        n_obs = min(4, max(1, len(q_values))) if q_values else 1

        for obs_idx in range(n_obs):
            if q_ni_series is not None and obs_idx >= len(q_ni_series):
                break
            date = q_ni_series.index[-(obs_idx + 1)] if q_ni_series is not None else latest_q_date
            pk   = period_key(date)
            pl   = period_label(date)

            avail_q = q_values[obs_idx:]
            s8,  sup8  = build_ni_series(avail_q, a_values, 8)
            s10, sup10 = build_ni_series(avail_q, a_values, 10)
            s12, sup12 = build_ni_series(avail_q, a_values, 12)

            def sa(series: list[float]) -> Optional[float]:
                return round(sum(series) / len(series) * 4, 4) if series else None

            rg8  = calc_rg(market_cap_b, sa(s8)  or 0, tangible_eq_b) if len(s8)  >= 8  else None
            rg10 = calc_rg(market_cap_b, sa(s10) or 0, tangible_eq_b) if len(s10) >= 10 else None
            rg12 = calc_rg(market_cap_b, sa(s12) or 0, tangible_eq_b) if len(s12) >= 12 else None

            used_annual = any([sup8, sup10, sup12])
            fb = round(max(tangible_eq_b, 0) + (sa(s10) or 0) * 10, 2)

            note = "Computed via yfinance."
            if used_annual:
                note += (" Older quarters estimated from annual NI / 4."
                         " Historical market cap not adjusted.")
            note += " Approximation."

            recent_obs.append({
                "periodKey":             pk,
                "periodLabel":           pl,
                "rg8":  rg8,
                "rg10": rg10,
                "rg12": rg12,
                "trend": None,
                "marketCap":             round(market_cap_b, 1),
                "bookEquity":            round(tangible_eq_b, 1),
                "netIncome":             round((avail_q[0] if avail_q else 0) * 4, 1),
                "fundamentalBaseApprox": fb,
                "dataType":              "quarterly",
                "note": note,
            })

        # Trend codes for recent obs
        for i in range(len(recent_obs)):
            curr = recent_obs[i]["rg10"]
            prev = recent_obs[i + 1]["rg10"] if i + 1 < len(recent_obs) else None
            recent_obs[i]["trend"] = trend_code(curr, prev)

        recent_obs = [o for o in recent_obs if o.get("rg10") is not None]

        if not recent_obs:
            print("SKIP (no valid RG10)")
            return None

        # --- Historical annual observations (for chart) ----------------------
        hist_obs: list[dict] = []
        if a_series_sorted is not None and shares > 0:
            hist_obs = build_historical_annual_obs(
                a_series_sorted, price_hist, shares,
                tangible_eq_b, market_cap_b)

        # --- Merge: combine recent quarterly + historical annual -------------
        # Deduplicate by periodKey; quarterly takes priority over annual
        recent_keys = {o["periodKey"] for o in recent_obs}
        extra_hist  = [o for o in hist_obs if o["periodKey"] not in recent_keys]

        # Assign trend codes to historical obs
        all_obs_by_key: dict[str, dict] = {}
        for o in hist_obs:
            all_obs_by_key[o["periodKey"]] = o
        for o in recent_obs:
            all_obs_by_key[o["periodKey"]] = o  # quarterly overrides

        # Sort all observations newest-first
        all_sorted = sorted(all_obs_by_key.values(),
                            key=lambda o: o["periodKey"], reverse=True)

        # Recompute trend across entire merged series (newest-first)
        for i, obs in enumerate(all_sorted):
            next_obs = all_sorted[i + 1] if i + 1 < len(all_sorted) else None
            obs["trend"] = trend_code(obs.get("rg10"), next_obs.get("rg10") if next_obs else None)

        slug = slug_override or slugify(display_name)
        company = {
            "company":      display_name,
            "ticker":       ticker,
            "slug":         slug,
            "sector":       sector,
            "currency":     currency,
            "country":      country,
            "index":        index_name,
            "description":  "Data sourced via yfinance / Yahoo Finance. Approximation.",
            "observations": all_sorted,
        }

        n_hist = len(extra_hist)
        rg10_val = all_sorted[0].get("rg10")
        print(f"OK  ({len(all_sorted)} obs [{n_hist} hist], RG10={rg10_val})")
        return company

    except Exception as exc:
        print(f"ERROR: {exc}")
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch RG data via yfinance")
    parser.add_argument("--index",  choices=["SP500", "N225", "DAX", "ALL"], default="ALL")
    parser.add_argument("--limit",  type=int, default=0)
    parser.add_argument("--ticker", default="")
    parser.add_argument("--delay",  type=float, default=1.0)
    args = parser.parse_args()

    if args.ticker:
        result = fetch_company(args.ticker, args.ticker, "Unknown", "Debug", "XX", "USD")
        if result:
            print(json.dumps(result, indent=2, default=str))
        return

    to_run = list(INDEX_MAP.keys()) if args.index == "ALL" else [args.index]

    all_slugs: list[str] = []
    all_sectors: set[str] = set()

    if INDEX_FILE.exists():
        with open(INDEX_FILE) as f:
            all_slugs = json.load(f)
    if SECTORS_FILE.exists():
        with open(SECTORS_FILE) as f:
            all_sectors = set(json.load(f))

    for index_key in to_run:
        members = INDEX_MAP[index_key]
        if args.limit > 0:
            members = members[: args.limit]

        print(f"\n{'='*60}")
        print(f"Index: {index_key}  ({len(members)} companies)")
        print(f"{'='*60}")

        seen: set[str] = set()
        for ticker, name, sector, index_name, country, currency in members:
            slug = slugify(name)
            if slug in seen:
                continue
            seen.add(slug)

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

    with open(INDEX_FILE, "w") as f:
        json.dump(all_slugs, f, indent=2)
    with open(SECTORS_FILE, "w") as f:
        json.dump(sorted(all_sectors), f, indent=2)

    print(f"\n✓  {len(all_slugs)} companies  →  {DATA_DIR}")


if __name__ == "__main__":
    main()
