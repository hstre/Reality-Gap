#!/usr/bin/env python3
"""
Reality Gap — DAX 40 Trailing P/E Fetcher
==========================================
Computes M(DAX40)RG10 = trailing P/E / 10 for the DAX 40 index.

IMPORTANT METHODOLOGICAL NOTE
-------------------------------
For the S&P 500, M(S&P500)RG10 = Shiller CAPE / 10, where CAPE is the
cyclically-adjusted (10-year real earnings average) price-to-earnings ratio.
CAPE data is freely available from Robert Shiller / Yale going back to 1881.

For the DAX 40, no equivalent free monthly CAPE time series exists.
All checked sources returned errors or were inaccessible:
  - multpl.com/dax: 404
  - Deutsche Bundesbank API: 503
  - OECD MEI_FIN (Germany): does not include P/E series
  - macrotrends.net: 403
  - stooq.com: requires captcha API key
  - StarCapital (archived): 403
  - JST macrohistory: 404

This script therefore uses the TRAILING 12-month P/E ratio from the
iShares Core DAX UCITS ETF (EXS1.DE) as a proxy, cross-checked against
Xtrackers DAX UCITS ETF (DBXD.DE). Both ETFs replicate the full DAX 40
total-return index and track the same underlying earnings pool.

Trailing P/E is more volatile than CAPE (sensitive to single-year earnings
swings). The resulting M(DAX40)RG10 is labelled as a trailing-PE-based
approximation throughout the page.

Formula:
  M(DAX40)RG10_approx = trailingPE / 10

This mirrors M(S&P500)RG10 = CAPE / 10 in structure but uses a different
earnings denominator (12-month trailing vs. 10-year real average).

Output JSON schema:
  {
    "source": "...",
    "method": "trailing_pe",
    "cape_note": "...",
    "fetched": "YYYY-MM-DD",
    "current": {
      "date": "YYYY-MM",
      "trailing_pe": 18.11,
      "rg10": 1.811,
      "dax_price": 23807.0,
      "ytd_pct": 13.6,
      "sources_used": ["EXS1.DE", "DBXD.DE"]
    }
  }
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    sys.exit("yfinance not installed: pip install yfinance")

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH  = REPO_ROOT / "src" / "data" / "macro" / "dax40_pe.json"

# ETFs that replicate DAX 40 — used to read trailing P/E
ETF_TICKERS = ["EXS1.DE", "DBXD.DE"]
DAX_TICKER  = "^GDAXI"

CAPE_NOTE = (
    "No free automated source for historical DAX CAPE data exists. "
    "Checked sources include multpl.com (404), Deutsche Bundesbank API (503), "
    "OECD MEI_FIN Germany series (no P/E series available), macrotrends.net (403), "
    "stooq.com (captcha required), StarCapital archive (403). "
    "Trailing P/E from iShares Core DAX ETF (EXS1.DE) is used as the best "
    "available free proxy. Unlike CAPE, trailing P/E is sensitive to single-year "
    "earnings swings (e.g. pandemic year 2020: DAX earnings collapsed, P/E spiked)."
)


def fetch_trailing_pe() -> tuple[float, list[str]]:
    """
    Fetch trailing P/E from ETF proxies.
    Returns (pe, sources_used).
    """
    pe_values: list[float] = []
    sources: list[str] = []

    for ticker in ETF_TICKERS:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            pe = info.get("trailingPE")
            if pe and 5 < pe < 200:
                pe_values.append(float(pe))
                sources.append(ticker)
                print(f"  [{ticker}] trailing P/E = {pe:.2f}")
        except Exception as e:
            print(f"  [{ticker}] WARNING: {e}")

    if not pe_values:
        sys.exit("ERROR: Could not fetch any trailing P/E from ETF proxies.")

    avg_pe = sum(pe_values) / len(pe_values)
    print(f"  Average trailing P/E ({', '.join(sources)}): {avg_pe:.2f}")
    return avg_pe, sources


def fetch_dax_price() -> tuple[float, float]:
    """
    Fetch current DAX price and 52-week change percent from yfinance.
    Returns (price, ytd_pct).
    """
    try:
        t = yf.Ticker(DAX_TICKER)
        info = t.info
        price = info.get("regularMarketPrice") or info.get("previousClose", 0.0)
        ytd   = info.get("fiftyTwoWeekChangePercent") or 0.0  # already in % form
        print(f"  [^GDAXI] price = {price:.0f}, 52-week chg = {ytd:.1f}%")
        return float(price), float(ytd)
    except Exception as e:
        print(f"  [^GDAXI] WARNING: {e}")
        return 0.0, 0.0


def main() -> None:
    print("=" * 60)
    print("  DAX 40 Trailing P/E → M(DAX40)RG10 Fetcher")
    print("  Method: trailing P/E / 10  (NOT CAPE-based)")
    print("=" * 60)

    pe, sources = fetch_trailing_pe()
    price, ytd  = fetch_dax_price()

    rg10 = round(pe / 10, 3)
    today = date.today()
    date_str = today.strftime("%Y-%m")

    out = {
        "source":   "yfinance / Yahoo Finance — iShares Core DAX UCITS ETF (EXS1.DE), "
                    "Xtrackers DAX UCITS ETF (DBXD.DE)",
        "method":   "trailing_pe",
        "method_note": (
            "M(DAX40)RG10 = trailing 12-month P/E / 10. "
            "For comparison: M(S&P500)RG10 = Shiller CAPE / 10 (10-year real earnings average). "
            "Trailing P/E and CAPE are not directly comparable: trailing P/E is sensitive to "
            "single-year earnings swings; CAPE smooths over a full business cycle. "
            "In a normal earnings environment they tend to be of similar magnitude, "
            "but can diverge significantly in recession or recovery years."
        ),
        "cape_note": CAPE_NOTE,
        "fetched":  today.isoformat(),
        "current": {
            "date":        date_str,
            "trailing_pe": round(pe, 2),
            "rg10":        rg10,
            "dax_price":   round(price, 0) if price else None,
            "ytd_52w_pct": round(ytd, 1) if ytd else None,
            "sources_used": sources,
        },
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, separators=(",", ":"), indent=2)

    print(f"\n  Written: {OUT_PATH}")
    print(f"  Current: {date_str}  trailing P/E={pe:.2f}  M(DAX40)RG10={rg10}")
    print(f"  DAX price: {price:.0f}  52w change: {ytd:.1f}%")
    print(f"  Sources: {sources}")


if __name__ == "__main__":
    main()
