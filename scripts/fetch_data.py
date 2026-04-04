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

# Samsung Electronics is not part of the three covered indices but was
# included in the initial dataset. Fetched separately as KOSPI company.
KOSPI_MEMBERS: list[tuple] = [
    ("005930.KS", "Samsung", "Technology / Consumer Electronics", "KOSPI", "KR", "KRW"),
]

INDEX_MAP = {
    "SP500":  SP500_MEMBERS,
    "N225":   NIKKEI_MEMBERS,
    "DAX":    DAX_MEMBERS,
    "KOSPI":  KOSPI_MEMBERS,
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


def calc_rg(market_cap_b: float, smoothed_annual_b: Optional[float],
            tangible_eq_b: float, multiplier: int = 10) -> Optional[float]:
    """RG_N = marketCap / (max(tangibleEquity,0) + smoothedAnnualEarnings * N)

    The subscript N (8, 10, 12) is the capitalization factor — how many years
    of smoothed earnings are assumed to represent 'fair value' of the earnings
    component.  A larger N implies a more generous valuation assumption, so
    RG8 >= RG10 >= RG12 for any company with positive smoothed earnings.

    Smoothed earnings are always derived from the same fixed 8-quarter window;
    only the capitalization multiple varies across RG8/10/12.

    Returns None when smoothed earnings are None or when the fundamental
    base is zero or negative.
    """
    if smoothed_annual_b is None:
        return None
    fb = max(tangible_eq_b, 0.0) + smoothed_annual_b * multiplier
    if fb <= 0:
        return None
    return round(market_cap_b / fb, 2)


def build_ni_series(quarterly_ni: list[float], annual_ni: list[float],
                    n_needed: int) -> tuple[list[float], bool]:
    """
    Extend a newest-first quarterly NI series with annual/4 estimates.

    annual_ni must be newest-first (most recent fiscal year first).
    Iteration proceeds newest → oldest so that the most recent annual
    data fills the positions immediately after the known quarters.
    This preserves chronological order in the smoothing window.

    Previously used reversed(annual_ni) which incorrectly placed the
    oldest annual year (highest for turnaround companies) into the
    most-recent unobserved positions, inflating smoothed earnings for
    companies with deteriorating earnings history.
    """
    result = list(quarterly_ni)
    supplemented = False
    if len(result) >= n_needed:
        return result[:n_needed], supplemented
    for ann_val in annual_ni:          # newest-first (no reversed)
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

        # Need at least 8 synthetic quarters for smoothed earnings
        if n_q < 8:
            continue

        # Historical market cap
        hist_price = price_at_date(price_history, date)
        if hist_price and shares > 0:
            hist_mc_b = to_billions(hist_price * shares)
        else:
            hist_mc_b = current_mc_b  # fallback

        # Single smoothed earnings: mean of the 8 most-recent synthetic quarters × 4
        # N in RG_N is the capitalization factor, not the smoothing window.
        window8 = q_synthetic[-8:]
        se = round(sum(window8) / 8 * 4, 4)

        rg8  = calc_rg(hist_mc_b, se, tangible_eq_b, multiplier=8)
        rg10 = calc_rg(hist_mc_b, se, tangible_eq_b, multiplier=10)
        rg12 = calc_rg(hist_mc_b, se, tangible_eq_b, multiplier=12)

        # Skip annual historical obs where RG8 is not computable (fundamental base ≤ 0)
        if rg8 is None:
            continue

        _fb_raw = max(tangible_eq_b, 0) + se * 10
        fb: Optional[float] = round(_fb_raw, 2) if _fb_raw > 0 else None

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
# Validation
# ---------------------------------------------------------------------------

def validate_and_annotate_observations(observations: list[dict]) -> list[dict]:
    """
    Validate each observation for internal consistency and add a 'dataQuality' field.

    Convention (post-fix): RG_N = mc / (max(TE,0) + se × N) where se is fixed
    (mean of last 8 quarters × 4) and N ∈ {8,10,12} is the capitalization factor.
    With se > 0 this guarantees RG8 >= RG10 >= RG12 mathematically.

    Values:
      "ok"                        – all checks pass
      "negative_earnings_ordering"– se < 0 so the RG ordering inverts (RG8 ≤ RG10 ≤ RG12);
                                     the company had negative smoothed earnings at this
                                     observation but a large enough tangible equity to keep
                                     all three fundamental bases positive. Mathematically
                                     correct; not a formula error.
      "fb_rg_inconsistency"       – RG10 × fundamentalBaseApprox ≠ marketCap by more than
                                     5% AND 0.10 absolute (indicates stale/placeholder data)
      "positive_rg_no_fb"         – RG is positive but fundamentalBase is null or ≤ 0
                                     (can occur at boundary observations where se is not
                                     storable via the N=10 base; informational only)
    Multiple issues are joined with "|".
    """
    for obs in observations:
        rg8  = obs.get("rg8")
        rg10 = obs.get("rg10")
        rg12 = obs.get("rg12")
        mc   = obs.get("marketCap")
        fb   = obs.get("fundamentalBaseApprox")

        issues: list[str] = []

        # 1. Detect negative-earnings ordering inversion
        #    With positive se: RG8 >= RG10 >= RG12 (normal)
        #    With negative se: RG8 <= RG10 <= RG12 (inverted, but mathematically correct)
        if rg8 is not None and rg10 is not None:
            if rg8 < rg10 - 0.005:          # strictly inverted (beyond rounding)
                issues.append("negative_earnings_ordering")

        # 2. FB–RG10 round-trip: rg10 ≈ marketCap / fundamentalBaseApprox
        #    Require BOTH >5% relative AND >0.10 absolute to avoid rounding false positives.
        if rg10 is not None and mc is not None and fb is not None and fb > 0:
            implied = mc / fb
            rel_err = abs(implied - rg10) / max(abs(rg10), 1e-9)
            abs_err = abs(implied - rg10)
            if rel_err > 0.05 and abs_err > 0.10:
                issues.append("fb_rg_inconsistency")

        # 3. Positive RG values with no positive fundamental base stored
        has_positive_rg = any(v is not None and v > 0 for v in [rg8, rg10, rg12])
        if has_positive_rg and (fb is None or fb <= 0):
            issues.append("positive_rg_no_fb")

        obs["dataQuality"] = "|".join(issues) if issues else "ok"

    return observations


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

            # Single smoothed earnings from a fixed 8-quarter window.
            # N in RG_N is the capitalization factor (not the smoothing window),
            # ensuring RG8 >= RG10 >= RG12 for any company with positive earnings.
            s8, used_annual = build_ni_series(avail_q, a_values, 8)
            se = round(sum(s8) / len(s8) * 4, 4) if len(s8) >= 8 else None

            # Three RG variants: same smoothed earnings, different multipliers
            rg8  = calc_rg(market_cap_b, se, tangible_eq_b, multiplier=8)
            rg10 = calc_rg(market_cap_b, se, tangible_eq_b, multiplier=10)
            rg12 = calc_rg(market_cap_b, se, tangible_eq_b, multiplier=12)

            # fundamentalBaseApprox stores the N=10 base for reference
            _fb_raw = max(tangible_eq_b, 0) + (se or 0) * 10
            fb: Optional[float] = round(_fb_raw, 2) if _fb_raw > 0 else None

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

        # Trend codes for recent obs (computed from rg10; null-rg obs get null trend)
        for i in range(len(recent_obs)):
            curr = recent_obs[i]["rg10"]
            prev = recent_obs[i + 1]["rg10"] if i + 1 < len(recent_obs) else None
            recent_obs[i]["trend"] = trend_code(curr, prev)

        # Keep observations even when RG is None (negative fundamental base).
        # Filtering them out would leave stale data on disk. Instead, include
        # them with a clear note so the detail page can explain the situation.
        has_any_rg = any(o.get("rg10") is not None for o in recent_obs)
        if not has_any_rg:
            # Add explicit explanation to each null-RG observation
            for o in recent_obs:
                o["note"] = (
                    "RG values not computable: fundamental base is zero or negative "
                    "(tangible equity negative and smoothed earnings negative across "
                    "all window sizes). The company's earnings do not provide a "
                    "positive fundamental base at any smoothing horizon."
                )

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

        # --- Validate and annotate each observation --------------------------
        all_sorted = validate_and_annotate_observations(all_sorted)

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
        status = "OK " if rg10_val is not None else "RG=∅"
        print(f"{status} ({len(all_sorted)} obs [{n_hist} hist], RG10={rg10_val})")
        return company

    except Exception as exc:
        print(f"ERROR: {exc}")
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch RG data via yfinance")
    parser.add_argument("--index",  choices=["SP500", "N225", "DAX", "KOSPI", "ALL"], default="ALL")
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
