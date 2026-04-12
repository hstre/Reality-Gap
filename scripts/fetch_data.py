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
import csv
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
CPI_FILE     = REPO_ROOT / "src" / "data" / "reference" / "cpi_us_monthly.csv"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# CPI data (US CPIAUCSL from FRED, 1947–present)
# Used to inflation-adjust the 8-quarter smoothing window for US companies.
# ---------------------------------------------------------------------------

def _load_cpi() -> dict:
    """Return {(year, month): cpi_value} from the local FRED CSV."""
    data: dict = {}
    try:
        with open(CPI_FILE, newline="") as f:
            for row in csv.DictReader(f):
                try:
                    # Support both "date" and "observation_date" column names
                    date_str = row.get("date") or row.get("observation_date", "")
                    val_str  = row.get("value") or row.get("CPIAUCSL", "")
                    y = int(date_str[:4])
                    m = int(date_str[5:7])
                    data[(y, m)] = float(val_str)
                except (ValueError, KeyError):
                    pass
    except (FileNotFoundError, OSError):
        pass
    return data

_CPI: dict = _load_cpi()
_CPI_CURRENT: Optional[float] = _CPI[max(_CPI)] if _CPI else None

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

FTSE_MEMBERS: list[tuple] = [
    ("AZN.L",  "AstraZeneca",    "Healthcare",              "FTSE 100", "GB", "GBP"),
    ("SHEL.L", "Shell",          "Energy",                  "FTSE 100", "GB", "GBP"),
    ("HSBA.L", "HSBC",           "Financials",              "FTSE 100", "GB", "GBP"),
    ("ULVR.L", "Unilever",       "Consumer Staples",        "FTSE 100", "GB", "GBP"),
    ("BP.L",   "BP",             "Energy",                  "FTSE 100", "GB", "GBP"),
    ("GSK.L",  "GSK",            "Healthcare",              "FTSE 100", "GB", "GBP"),
    ("RIO.L",  "Rio Tinto",      "Materials",               "FTSE 100", "GB", "GBP"),
    ("DGE.L",  "Diageo",         "Consumer Staples",        "FTSE 100", "GB", "GBP"),
    ("BA.L",   "BAE Systems",    "Industrials",             "FTSE 100", "GB", "GBP"),
    ("RR.L",   "Rolls-Royce",    "Industrials",             "FTSE 100", "GB", "GBP"),
    ("REL.L",  "RELX",           "Technology",              "FTSE 100", "GB", "GBP"),
    ("LLOY.L", "Lloyds Banking", "Financials",              "FTSE 100", "GB", "GBP"),
    ("BARC.L", "Barclays",       "Financials",              "FTSE 100", "GB", "GBP"),
    ("NG.L",   "National Grid",  "Utilities",               "FTSE 100", "GB", "GBP"),
    ("CPG.L",  "Compass Group",  "Consumer Discretionary",  "FTSE 100", "GB", "GBP"),
]

CAC_MEMBERS: list[tuple] = [
    ("MC.PA",  "LVMH",              "Consumer Discretionary", "CAC 40", "FR", "EUR"),
    ("TTE.PA", "TotalEnergies",     "Energy",                 "CAC 40", "FR", "EUR"),
    ("OR.PA",  "L'Oreal",           "Consumer Staples",       "CAC 40", "FR", "EUR"),
    ("SAN.PA", "Sanofi",            "Healthcare",             "CAC 40", "FR", "EUR"),
    ("AI.PA",  "Air Liquide",       "Materials",              "CAC 40", "FR", "EUR"),
    ("RMS.PA", "Hermes",            "Consumer Discretionary", "CAC 40", "FR", "EUR"),
    ("BNP.PA", "BNP Paribas",       "Financials",             "CAC 40", "FR", "EUR"),
    ("SU.PA",  "Schneider Electric","Industrials",            "CAC 40", "FR", "EUR"),
    ("SAF.PA", "Safran",            "Industrials",            "CAC 40", "FR", "EUR"),
    ("DSY.PA", "Dassault Systemes", "Technology",             "CAC 40", "FR", "EUR"),
    ("CS.PA",  "AXA",               "Financials",             "CAC 40", "FR", "EUR"),
    ("RI.PA",  "Pernod Ricard",     "Consumer Staples",       "CAC 40", "FR", "EUR"),
    ("DG.PA",  "Vinci",             "Industrials",            "CAC 40", "FR", "EUR"),
    ("KER.PA", "Kering",            "Consumer Discretionary", "CAC 40", "FR", "EUR"),
    ("CAP.PA", "Capgemini",         "Technology",             "CAC 40", "FR", "EUR"),
]

SMI_MEMBERS: list[tuple] = [
    ("NESN.SW", "Nestle",          "Consumer Staples",       "SMI", "CH", "CHF"),
    ("NOVN.SW", "Novartis",        "Healthcare",             "SMI", "CH", "CHF"),
    ("ROG.SW",  "Roche",           "Healthcare",             "SMI", "CH", "CHF"),
    ("ABBN.SW", "ABB",             "Industrials",            "SMI", "CH", "CHF"),
    ("ZURN.SW", "Zurich Insurance","Financials",             "SMI", "CH", "CHF"),
    ("SREN.SW", "Swiss Re",        "Financials",             "SMI", "CH", "CHF"),
    ("CFR.SW",  "Richemont",       "Consumer Discretionary", "SMI", "CH", "CHF"),
    ("LONN.SW", "Lonza",           "Healthcare",             "SMI", "CH", "CHF"),
    ("PGHN.SW", "Partners Group",  "Financials",             "SMI", "CH", "CHF"),
    ("SIKA.SW", "Sika",            "Materials",              "SMI", "CH", "CHF"),
]

INDEX_MAP = {
    "SP500": SP500_MEMBERS,
    "N225":  NIKKEI_MEMBERS,
    "DAX":   DAX_MEMBERS,
    "FTSE":  FTSE_MEMBERS,
    "CAC":   CAC_MEMBERS,
    "SMI":   SMI_MEMBERS,
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


def cpi_at(date: pd.Timestamp) -> Optional[float]:
    """Return CPI for the month of *date*, searching up to ±3 months if needed."""
    if not _CPI:
        return None
    for delta in [0, -1, 1, -2, 2, -3, 3]:
        m = date.month + delta
        y = date.year
        while m < 1:
            m += 12
            y -= 1
        while m > 12:
            m -= 12
            y += 1
        if (y, m) in _CPI:
            return _CPI[(y, m)]
    return None


def build_dated_ni_series(
    q_dates: list,           # pd.Timestamp list, newest-first
    q_values_b: list[float], # NI in billions, newest-first (same length as q_dates)
    annual_oldest_first: Optional[pd.Series],  # annual income stmt, oldest-first
    n_needed: int,
) -> list[tuple]:
    """
    Build a newest-first list of (ni_value_b, date) tuples for n_needed quarters.

    Fills actual quarterly observations first; supplements with annual/4 estimates
    (using FY-end dates staggered by 3 months per sub-quarter) if needed.
    """
    result: list[tuple] = list(zip(q_values_b, q_dates))
    if len(result) >= n_needed or annual_oldest_first is None:
        return result[:n_needed]

    ann_vals_newest  = list(reversed(annual_oldest_first.values))
    ann_dates_newest = list(reversed(annual_oldest_first.index))
    for ann_val, fy_date in zip(ann_vals_newest, ann_dates_newest):
        per_q = to_billions(float(ann_val)) / 4.0
        for q_off in range(4):
            if len(result) >= n_needed:
                break
            approx_date = fy_date - pd.DateOffset(months=3 * q_off)
            result.append((per_q, approx_date))
        if len(result) >= n_needed:
            break
    return result[:n_needed]


def compute_g(
    dated_quarters: list[tuple],  # [(ni_b, date), ...] newest-first, already length-8
    apply_cpi: bool = False,
) -> Optional[float]:
    """
    Compute smoothed annual earnings G = mean(window) × 4.

    When apply_cpi=True and CPI data is available, each quarter is scaled to
    current-dollar terms before averaging (Shiller-CAPE style).
    """
    n = len(dated_quarters)
    if n == 0:
        return None
    if apply_cpi and _CPI_CURRENT is not None:
        total = 0.0
        for v, date in dated_quarters:
            c = cpi_at(date)
            total += v * (_CPI_CURRENT / c) if (c and c > 0) else v
    else:
        total = sum(v for v, _ in dated_quarters)
    return round(total / n * 4, 4)


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
            tangible_eq_b: float, multiplier: int) -> Optional[float]:
    """RG_N = MC / FB_N  (paper definition)

    FB_N = TE + E_N
    E_N  = N * G  if G > 0,  else  0   (negative earnings do NOT reduce FB)
    TE   = tangible equity (enters as-is; not floored to zero)

    Returns None ("not fundamentally covered") when FB_N <= 0.
    """
    if smoothed_annual_b is None:
        return None
    E  = max(smoothed_annual_b, 0.0) * multiplier   # E = N*G if G>0 else 0
    FB = tangible_eq_b + E                           # TE is not floored
    if FB <= 0:
        return None
    return round(market_cap_b / FB, 2)


def fundamental_base(smoothed_annual_b: Optional[float],
                     tangible_eq_b: float, multiplier: int) -> Optional[float]:
    """Return FB_N = TE + E_N, or None when FB_N <= 0."""
    if smoothed_annual_b is None:
        return None
    E  = max(smoothed_annual_b, 0.0) * multiplier
    FB = tangible_eq_b + E
    return round(FB, 4) if FB > 0 else None


NEAR_BOUNDARY_THRESHOLD = 0.10

def is_near_boundary(G: Optional[float], tangible_eq_b: float) -> bool:
    """True when any FB_N (N∈{8,10,12}) is positive but < 10% of G×N.

    Catches near-singular denominators across all three RG variants.
    Example: a company where FB8 < 0 (RG8 null) but FB10 ≈ 0 (RG10 extreme).
    """
    if G is None or G <= 0 or tangible_eq_b >= 0:
        return False
    for N in [8, 10, 12]:
        E  = G * N
        FB = tangible_eq_b + E
        if 0.0 < FB < E * NEAR_BOUNDARY_THRESHOLD:
            return True
    return False


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
    te_is_approx: bool = True,        # historical obs always use current TE
    use_cpi: bool = False,            # inflation-adjust earnings (US only)
) -> list[dict]:
    """
    Build one RG observation per available fiscal-year-end using:
      - Annual NI rolling window (oldest data extends backwards)
      - Historical market cap = price at FY-end × current shares (approx)
      - TE is the current tangible equity (not historical — always approximate)
      - use_cpi: if True, each quarter's earnings are scaled to current dollars
        via CPIAUCSL before computing the 8-quarter smoothed G

    Returns observations oldest-first.
    """
    if annual_ni_series is None or len(annual_ni_series) < 2:
        return []

    annual_values_b = [to_billions(float(v)) for v in annual_ni_series.values]  # oldest-first
    dates            = list(annual_ni_series.index)  # oldest-first Timestamps

    observations: list[dict] = []

    for i, date in enumerate(dates):
        avail_annual  = annual_values_b[: i + 1]   # oldest to this year
        avail_dates   = dates[: i + 1]

        # Build dated synthetic quarters: newest-first, 4 quarters per FY
        dated_synthetic: list[tuple] = []
        for fy_b, fy_date in zip(reversed(avail_annual), reversed(avail_dates)):
            per_q = fy_b / 4.0
            for q_off in range(4):
                approx_date = fy_date - pd.DateOffset(months=3 * q_off)
                dated_synthetic.append((per_q, approx_date))

        if len(dated_synthetic) < 8:
            continue

        # Historical market cap (approx: historical price × current shares)
        hist_price = price_at_date(price_history, date)
        if hist_price and shares > 0:
            hist_mc_b = to_billions(hist_price * shares)
        else:
            hist_mc_b = current_mc_b

        # G = smoothed long-run earnings: mean of last 8 synthetic quarters × 4
        # CPI adjustment: scale each quarter to current dollars if use_cpi=True
        window8_dated = dated_synthetic[:8]
        G = compute_g(window8_dated, apply_cpi=use_cpi)

        # FB_N = TE + E_N  where E_N = N*G if G>0 else 0  (paper §4)
        fb8  = fundamental_base(G, tangible_eq_b, 8)
        fb10 = fundamental_base(G, tangible_eq_b, 10)
        fb12 = fundamental_base(G, tangible_eq_b, 12)

        rg8  = calc_rg(hist_mc_b, G, tangible_eq_b, multiplier=8)
        rg10 = calc_rg(hist_mc_b, G, tangible_eq_b, multiplier=10)
        rg12 = calc_rg(hist_mc_b, G, tangible_eq_b, multiplier=12)

        # Skip historical obs where even RG8 is not computable (FB ≤ 0)
        if rg8 is None and rg10 is None and rg12 is None:
            continue

        cpi_note = " Earnings inflation-adjusted to current USD (CPIAUCSL)." if use_cpi else ""
        obs: dict = {
            "periodKey":            period_key(date),
            "periodLabel":          period_label(date),
            "rg8":                  rg8,
            "rg10":                 rg10,
            "rg12":                 rg12,
            "trend":                None,
            "marketCap":            round(hist_mc_b, 1),
            "tangibleEquity":       round(tangible_eq_b, 1),
            "smoothedEarnings":     G,
            "fundamentalBaseRG8":   round(fb8, 2) if fb8 is not None else None,
            "fundamentalBaseRG10":  round(fb10, 2) if fb10 is not None else None,
            "fundamentalBaseRG12":  round(fb12, 2) if fb12 is not None else None,
            "netIncome":            round(avail_annual[-1] if avail_annual else 0, 1),
            "dataType":             "annual",
            "teIsApprox":           True,  # historical TE is always current snapshot
            "nearBoundary":         is_near_boundary(G, tangible_eq_b),
            "note": (
                "Annual historical observation. Market cap approximated from "
                "historical close price × current shares outstanding. "
                "TE uses current balance sheet (not historical)." +
                cpi_note +
                " Approximation."
            ),
        }
        observations.append(obs)

    return observations  # oldest-first


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_and_annotate_observations(observations: list[dict]) -> list[dict]:
    """
    Validate each observation per paper specification and add a 'dataQuality' field.

    Paper rules checked:
      1. RG ordering: with G > 0, RG8 >= RG10 >= RG12 must hold.
      2. FB–RG round-trip: RG10 ≈ MC / fundamentalBaseRG10.
      3. Not-covered consistency: if all RG are null, no FB should be positive.

    Values:
      "ok"                    – all checks pass
      "ordering_violation"    – RG8 < RG10 or RG10 < RG12 when G > 0 (formula error)
      "fb_rg_inconsistency"   – RG10 × fundamentalBaseRG10 ≠ marketCap by >5% AND >0.10
      "not_covered_fb_leak"   – all RG null but a positive FB was stored (shouldn't happen)
    Multiple issues are joined with "|".
    """
    for obs in observations:
        rg8  = obs.get("rg8")
        rg10 = obs.get("rg10")
        rg12 = obs.get("rg12")
        mc   = obs.get("marketCap")
        fb10 = obs.get("fundamentalBaseRG10")
        G    = obs.get("smoothedEarnings")

        issues: list[str] = []

        # 1. RG ordering: must be RG8 >= RG10 >= RG12 when G > 0
        #    (paper guarantee; G <= 0 means E=0 so all three denominators equal → all equal)
        if G is not None and G > 0 and rg8 is not None and rg10 is not None:
            if rg8 < rg10 - 0.005:
                issues.append("ordering_violation")
        if G is not None and G > 0 and rg10 is not None and rg12 is not None:
            if rg10 < rg12 - 0.005:
                issues.append("ordering_violation")

        # 2. FB–RG10 round-trip (tolerance: >5% AND >0.10 to absorb 2-decimal rounding)
        if rg10 is not None and mc is not None and fb10 is not None and fb10 > 0:
            implied = mc / fb10
            rel_err = abs(implied - rg10) / max(abs(rg10), 1e-9)
            abs_err = abs(implied - rg10)
            if rel_err > 0.05 and abs_err > 0.10:
                issues.append("fb_rg_inconsistency")

        # 3. Not-covered leak check
        all_null = rg8 is None and rg10 is None and rg12 is None
        if all_null and fb10 is not None and fb10 > 0:
            issues.append("not_covered_fb_leak")

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
        shares = float(info.get("sharesOutstanding") or 0)

        # --- Price history (for historical market cap) -------------------------
        try:
            price_hist = stock.history(period="15y", interval="1mo")
        except Exception:
            price_hist = pd.DataFrame()

        # --- Currency normalisation ------------------------------------------
        # yfinance returns prices (and price_hist) in the trading currency, but
        # financial statements in financialCurrency (often USD for non-US stocks).
        # We convert price_hist and mc so that price × shares gives a value in the
        # same currency as the income/balance-sheet data (financialCurrency).
        price_currency_raw = info.get("currency", "USD")
        financial_currency  = info.get("financialCurrency", price_currency_raw)

        # Step 1 – GBp (pence) → GBP (pounds)
        # For LSE stocks (.L), price_hist is ALWAYS in GBp (pence) regardless of
        # what info.get('currency') reports — yfinance inconsistently returns
        # 'GBp', 'GBP', or even 'USD' for different .L tickers while history()
        # always returns raw pence prices. Always divide price_hist by 100.
        price_currency = price_currency_raw
        is_lse = ticker.upper().endswith(".L")
        if price_currency_raw == "GBp" or is_lse:
            price_currency = "GBP"
            if not price_hist.empty and "Close" in price_hist.columns:
                price_hist = price_hist.copy()
                price_hist["Close"] = price_hist["Close"] / 100.0
            # info.marketCap for .L tickers is usually in GBP already (yfinance
            # converts pence → pounds for the snapshot value). Leave mc as-is;
            # it is only used as a fallback when price_hist has no data.

        # Step 2 – Convert normalized price currency → financialCurrency
        # (e.g. GBP → USD for London-listed stocks that report in USD)
        if price_currency != financial_currency:
            fx_pair = f"{price_currency}{financial_currency}=X"
            try:
                fx_df = yf.Ticker(fx_pair).history(period="15y", interval="1mo")
                if not fx_df.empty and "Close" in fx_df.columns:
                    current_fx = float(fx_df["Close"].iloc[-1])
                    # Convert current market cap
                    mc = float(mc) * current_fx
                    # Convert price_hist using historical FX at each date
                    if not price_hist.empty:
                        price_hist = price_hist.copy()
                        fx_vals = [price_at_date(fx_df, ts) or current_fx
                                   for ts in price_hist.index]
                        price_hist["Close"] = (
                            price_hist["Close"].values * fx_vals
                        )
            except Exception as _fx_exc:
                pass  # leave mc and price_hist in non-converted state

        market_cap_b = to_billions(float(mc))

        # --- Quarterly income -------------------------------------------------
        try:
            q_stmt = stock.quarterly_income_stmt
        except Exception:
            q_stmt = pd.DataFrame()

        # Many non-US companies report semi-annually or annually; allow fallback.
        q_stmt_available = q_stmt is not None and not q_stmt.empty
        ni_label = (
            next((l for l in NI_LABELS if l in q_stmt.index), None)
            if q_stmt_available else None
        )

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
        # TE = EQ - GW - IA  (paper definition)
        # If GW or IA are unavailable from yfinance, TE falls back to EQ
        # and te_is_approx is set to True to label the observation.
        tangible_eq_b = 0.0
        te_is_approx  = True   # assume approximation until proven otherwise
        try:
            q_bs = stock.quarterly_balance_sheet
            if q_bs is not None and not q_bs.empty:
                col = sorted(q_bs.columns)[-1]

                def bs_val(keys: list[str]) -> tuple[float, bool]:
                    """Return (value, found_in_data)."""
                    for k in keys:
                        if k in q_bs.index:
                            v = q_bs.loc[k, col]
                            if pd.notna(v):
                                return float(v), True
                    return 0.0, False

                eq,    _        = bs_val(["Stockholders Equity",
                                          "Total Stockholders Equity",
                                          "Common Stock Equity"])
                gw,    gw_found = bs_val(["Goodwill"])
                intan, ia_found = bs_val(["Other Intangible Assets",
                                          "Net Intangible Assets Including Goodwill",
                                          "Intangible Assets"])
                tangible_eq_b = to_billions(eq - gw - intan)
                # TE is exact when at least one intangible item was explicitly
                # deducted (even if zero); it is approximate when both were
                # missing from the balance sheet.
                te_is_approx = not (gw_found or ia_found)
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
        # Dates for actual quarterly observations (newest-first list of Timestamps)
        q_dates_newest: list = (
            list(reversed(q_ni_series.index)) if q_ni_series is not None else []
        )
        use_cpi = (country == "US") and bool(_CPI_CURRENT)

        for obs_idx in range(n_obs):
            if q_ni_series is not None and obs_idx >= len(q_ni_series):
                break
            date = q_ni_series.index[-(obs_idx + 1)] if q_ni_series is not None else latest_q_date
            pk   = period_key(date)
            pl   = period_label(date)

            avail_q       = q_values[obs_idx:]
            avail_q_dates = q_dates_newest[obs_idx:]

            # G = smoothed long-run earnings (paper §4)
            # Fixed 8-quarter window; N in RG_N is the capitalization factor.
            # For US companies: each quarter scaled to current dollars (CPIAUCSL)
            # before averaging → Shiller-CAPE style real smoothed earnings.
            dated_s8 = build_dated_ni_series(avail_q_dates, avail_q, a_series_sorted, 8)
            used_annual = len(dated_s8) > len(avail_q_dates) or (
                len(dated_s8) == 8 and len(avail_q) < 8
            )
            G: Optional[float] = compute_g(dated_s8, apply_cpi=use_cpi) if len(dated_s8) >= 8 else None

            # E_N = N * G if G > 0, else 0  (paper §4: negative earnings → E = 0)
            # FB_N = TE + E_N  (TE enters as-is, not floored)
            fb8  = fundamental_base(G, tangible_eq_b, 8)
            fb10 = fundamental_base(G, tangible_eq_b, 10)
            fb12 = fundamental_base(G, tangible_eq_b, 12)

            # Use historical end-of-quarter closing price × current shares
            # (historical shares not available; current shares are an approximation)
            q_hist_price = price_at_date(price_hist, date) if not price_hist.empty else None
            if q_hist_price and shares > 0:
                q_mc_b = to_billions(q_hist_price * shares)
                hist_price_used = True
            else:
                q_mc_b = market_cap_b  # fallback: current market cap
                hist_price_used = False

            rg8  = calc_rg(q_mc_b, G, tangible_eq_b, multiplier=8)
            rg10 = calc_rg(q_mc_b, G, tangible_eq_b, multiplier=10)
            rg12 = calc_rg(q_mc_b, G, tangible_eq_b, multiplier=12)

            note = "Computed via yfinance."
            if hist_price_used:
                note += " Historical end-of-quarter closing price × current shares outstanding."
            else:
                note += " Current market cap used (historical price unavailable)."
            if used_annual:
                note += " Older quarters estimated from annual NI / 4."
            if use_cpi:
                note += " Earnings inflation-adjusted to current USD (CPIAUCSL)."
            if te_is_approx:
                note += " TE approximated as book equity (GW/IA not separately available)."
            note += " Approximation."

            not_covered = rg8 is None and rg10 is None and rg12 is None
            if not_covered:
                note = (
                    "Not fundamentally covered: fundamental base FB_N = TE + E_N ≤ 0 "
                    "for all capitalization factors. "
                    "TE is negative and smoothed earnings G ≤ 0 (or G × N < |TE|)."
                )

            recent_obs.append({
                "periodKey":            pk,
                "periodLabel":          pl,
                "rg8":                  rg8,
                "rg10":                 rg10,
                "rg12":                 rg12,
                "trend":                None,
                "marketCap":            round(q_mc_b, 1),
                "tangibleEquity":       round(tangible_eq_b, 1),
                "smoothedEarnings":     G,
                "fundamentalBaseRG8":   round(fb8, 2) if fb8 is not None else None,
                "fundamentalBaseRG10":  round(fb10, 2) if fb10 is not None else None,
                "fundamentalBaseRG12":  round(fb12, 2) if fb12 is not None else None,
                "netIncome":            round((avail_q[0] if avail_q else 0) * 4, 1),
                "dataType":             "quarterly",
                "teIsApprox":           te_is_approx,
                "nearBoundary":         is_near_boundary(G, tangible_eq_b),
                "note":                 note,
            })

        # Trend codes across all recent obs (rg10-based; null → null)
        for i in range(len(recent_obs)):
            curr = recent_obs[i]["rg10"]
            prev = recent_obs[i + 1]["rg10"] if i + 1 < len(recent_obs) else None
            recent_obs[i]["trend"] = trend_code(curr, prev)

        # --- Historical annual observations (for chart) ----------------------
        hist_obs: list[dict] = []
        if a_series_sorted is not None and shares > 0:
            hist_obs = build_historical_annual_obs(
                a_series_sorted, price_hist, shares,
                tangible_eq_b, market_cap_b, use_cpi=use_cpi)

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
    parser.add_argument("--index",  choices=["SP500", "N225", "DAX", "FTSE", "CAC", "SMI", "ALL"], default="ALL")
    parser.add_argument("--limit",  type=int, default=0)
    parser.add_argument("--ticker", default="")
    parser.add_argument("--delay",  type=float, default=1.0)
    args = parser.parse_args()

    if args.ticker:
        # Look up full metadata from member lists before fetching
        all_members = [m for members in INDEX_MAP.values() for m in members]
        member_meta = next(
            (m for m in all_members if m[0].upper() == args.ticker.upper()), None
        )
        if member_meta:
            t, name, sector, idx, country, currency = member_meta
        else:
            t, name, sector, idx, country, currency = (
                args.ticker, args.ticker, "Unknown", "Debug", "XX", "USD"
            )
        result = fetch_company(t, name, sector, idx, country, currency)
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
