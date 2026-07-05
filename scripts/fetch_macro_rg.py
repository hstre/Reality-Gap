#!/usr/bin/env python3
"""
Reality Gap — TE-Corrected Macro RG Fetcher
============================================
The firm-level RG is  RG_N = MC / (TE + N·G).  The CAPE-based macro RG
(CAPE/10) captures only the earnings half of the fundamental base and is
therefore a systematic upper bound. This script adds the missing half via
the index price-to-book ratio, using the identity

    1/RG_N = TE/MC + N·G/MC  =  1/PB + N/PE_smooth
    =>  RG_N = 1 / (1/PB + N/PE_smooth)

Two independent constructions per index, written to
src/data/macro/macro_rg.json:

1. TOP-DOWN ("corrected"):
   - S&P 500:  PE_smooth = Shiller CAPE (from macro/sp500_cape.json),
               PB from multpl.com (current + monthly history to ~2000)
               → corrected historical series.
   - DAX 40 / Nikkei 225 / Hang Seng: trailing portfolio P/E and P/B of a
     replicating index ETF (yfinance funds_data; Yahoo reports these as
     inverse yields → invert). Trailing P/E, not CAPE — labelled.

2. BOTTOM-UP ("aggregate"):  ΣMC / Σ(TE + N·G) over the covered
   constituents in src/data/companies — the exact paper formula including
   tangible equity. Coverage subset only (top caps of each index).

Caveat: index P/B uses BOOK equity (incl. goodwill/intangibles), not
tangible book → the corrected value is a LOWER bound; the earnings-only
value an upper bound. The bottom-up aggregate uses true tangible equity.

Usage:
    python3 scripts/fetch_macro_rg.py

Env (optional): YF_IMPERSONATE, YF_CA_BUNDLE (proxy-restricted envs).
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

import requests as _requests

from fetch_data import make_yf_session

REPO_ROOT  = Path(__file__).resolve().parent.parent
DATA_DIR   = REPO_ROOT / "src" / "data" / "companies"
MACRO_DIR  = REPO_ROOT / "src" / "data" / "macro"
CAPE_FILE  = MACRO_DIR / "sp500_cape.json"
OUT_FILE   = MACRO_DIR / "macro_rg.json"

MULTPL_PB_URL = "https://www.multpl.com/s-p-500-price-to-book/table/by-month"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

# index-field value in company JSONs → output key / ETF proxy ticker
INDEXES = {
    "sp500": {"label": "S&P 500",    "member_index": "S&P 500",    "etf": "SPY"},
    "dax40": {"label": "DAX 40",     "member_index": "DAX 40",     "etf": "EXS1.DE"},
    "n225":  {"label": "Nikkei 225", "member_index": "Nikkei 225", "etf": "1321.T"},
    "hsi":   {"label": "Hang Seng",  "member_index": "Hang Seng",  "etf": "2800.HK"},
}

_MONTHS = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05",
           "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10",
           "Nov": "11", "Dec": "12"}


def corrected_rg(pb: float, pe: float, n: int) -> float:
    return round(1.0 / (1.0 / pb + n / pe), 3)


# ---------------------------------------------------------------------------
# 1. Bottom-up aggregates from local company data
# ---------------------------------------------------------------------------

def bottom_up() -> dict:
    agg: dict = {k: {"n": 0, "mc": 0.0, "fb8": 0.0, "fb10": 0.0, "fb12": 0.0}
                 for k in INDEXES}
    by_index = {v["member_index"]: k for k, v in INDEXES.items()}

    for path in sorted(DATA_DIR.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        key = by_index.get(d.get("index", ""))
        if key is None or not d.get("observations"):
            continue
        obs = max(d["observations"], key=lambda o: o.get("periodKey", ""))
        mc, te, g = obs.get("marketCap"), obs.get("tangibleEquity"), obs.get("smoothedEarnings")
        if mc is None or te is None:
            continue
        e1 = max(g or 0.0, 0.0)
        a = agg[key]
        a["n"]    += 1
        a["mc"]   += mc
        a["fb8"]  += te + 8 * e1
        a["fb10"] += te + 10 * e1
        a["fb12"] += te + 12 * e1

    out: dict = {}
    for key, a in agg.items():
        if a["n"] == 0 or a["fb10"] <= 0:
            continue
        out[key] = {
            "n":    a["n"],
            "rg8":  round(a["mc"] / a["fb8"], 3)  if a["fb8"]  > 0 else None,
            "rg10": round(a["mc"] / a["fb10"], 3),
            "rg12": round(a["mc"] / a["fb12"], 3) if a["fb12"] > 0 else None,
            "note": "Value-weighted aggregate ΣMC / Σ(TE + N·G) over covered "
                    "constituents (latest observation per company). "
                    "Exact RG formula incl. tangible equity; coverage subset only.",
        }
    return out


# ---------------------------------------------------------------------------
# 2. multpl.com S&P 500 price-to-book (current + monthly history)
# ---------------------------------------------------------------------------

def _http_get(url: str) -> str:
    try:
        r = _requests.get(url, headers={"User-Agent": UA}, timeout=45)
        r.raise_for_status()
        return r.text
    except Exception:
        # browser-impersonating fallback for restrictive proxies/CDNs
        from curl_cffi import requests as cr
        import os
        verify = os.environ.get("YF_CA_BUNDLE") or True
        r = cr.get(url, impersonate="chrome110", verify=verify, timeout=45)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code} for {url}")
        return r.text


def fetch_multpl_pb_series() -> list[tuple[str, float]]:
    """[(YYYY-MM, pb), ...] newest-first from multpl's P/B table.

    multpl serves S&P 500 P/B as ANNUAL year-end values (1999–present)
    plus the current reading. Values may carry a '†' estimate marker.
    """
    from bs4 import BeautifulSoup
    html = _http_get(MULTPL_PB_URL)
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id="datatable") or soup.find("table")
    if table is None:
        raise RuntimeError("multpl P/B table not found")
    series: list[tuple[str, float]] = []
    for tr in table.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cells) < 2:
            continue
        m = re.match(r"(\w{3})\s+\d+,\s+(\d{4})", cells[0])
        if not m or m.group(1) not in _MONTHS:
            continue
        num = re.sub(r"[^0-9.]", "", cells[1])
        try:
            val = float(num)
        except ValueError:
            continue
        if 0.5 < val < 20:
            series.append((f"{m.group(2)}-{_MONTHS[m.group(1)]}", val))
    if len(series) < 20:
        raise RuntimeError(f"multpl P/B series too short: {len(series)} rows")
    return series


# ---------------------------------------------------------------------------
# 3. ETF portfolio P/B + P/E via yfinance funds_data
# ---------------------------------------------------------------------------

def fetch_etf_ratios(ticker: str) -> tuple[float, float]:
    """(pb, trailing_pe) of the ETF's equity portfolio. Yahoo serves these
    as inverse yields (book yield / earnings yield) → invert."""
    import yfinance as yf
    t = yf.Ticker(ticker, session=make_yf_session())
    eh = t.funds_data.equity_holdings
    col = eh.columns[0]
    inv_pe = float(eh.loc["Price/Earnings", col])
    inv_pb = float(eh.loc["Price/Book", col])
    if not (0 < inv_pe < 1 and 0 < inv_pb < 2):
        raise RuntimeError(f"{ticker}: implausible fund ratios "
                           f"(1/PE={inv_pe}, 1/PB={inv_pb})")
    return round(1.0 / inv_pb, 3), round(1.0 / inv_pe, 3)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    result: dict = {
        "fetched": date.today().isoformat(),
        "formula": "RG_N = 1 / (1/PB + N/PE_smooth)",
        "note": ("TE-corrected macro RG. Index P/B uses book equity "
                 "(incl. goodwill/intangibles), not tangible book — the "
                 "corrected value is a lower bound, the earnings-only value "
                 "an upper bound. Bottom-up aggregates use true tangible "
                 "equity but cover only the constituents in this dataset."),
        "indices": {},
    }

    bu = bottom_up()
    bu_summary = ", ".join(f"{k}={v['rg10']}" for k, v in bu.items())
    print(f"Bottom-up aggregates: {bu_summary}")

    # --- CAPE (for S&P 500 top-down + series) ------------------------------
    cape_current, cape_series = None, {}
    try:
        with open(CAPE_FILE, encoding="utf-8") as f:
            cape_data = json.load(f)
        cape_current = cape_data["current"]["cape"]
        cape_series = {p["date"]: p["cape"] for p in cape_data.get("series", [])}
    except Exception as exc:
        print(f"  [warn] CAPE data unavailable: {exc}")

    # --- multpl P/B ---------------------------------------------------------
    pb_series: list[tuple[str, float]] = []
    try:
        pb_series = fetch_multpl_pb_series()
        print(f"  [multpl] S&P 500 P/B: {len(pb_series)} monthly rows, "
              f"latest {pb_series[0][0]} = {pb_series[0][1]}")
    except Exception as exc:
        print(f"  [warn] multpl P/B failed: {exc}")

    for key, cfg in INDEXES.items():
        entry: dict = {"label": cfg["label"]}
        if key in bu:
            entry["bottomUp"] = bu[key]

        # earnings-only + top-down corrected
        try:
            if key == "sp500":
                if cape_current is None or not pb_series:
                    raise RuntimeError("missing CAPE or P/B")
                pb = pb_series[0][1]
                pe, pe_basis, pb_source = cape_current, "Shiller CAPE (10y real)", "multpl.com"
            else:
                pb, pe = fetch_etf_ratios(cfg["etf"])
                pe_basis  = f"trailing 12m portfolio P/E ({cfg['etf']})"
                pb_source = f"ETF portfolio ({cfg['etf']}, yfinance funds data)"
            entry["earningsOnly"] = {"rg10": round(pe / 10, 3), "peBasis": pe_basis, "pe": pe}
            entry["topDown"] = {
                "pb": pb, "pe": pe, "peBasis": pe_basis, "pbSource": pb_source,
                "rg8":  corrected_rg(pb, pe, 8),
                "rg10": corrected_rg(pb, pe, 10),
                "rg12": corrected_rg(pb, pe, 12),
            }
            print(f"  [{cfg['label']}] PB={pb} PE={pe} → corrected RG10="
                  f"{entry['topDown']['rg10']} (earnings-only {round(pe/10, 2)})")
        except Exception as exc:
            print(f"  [warn] top-down {cfg['label']} failed: {exc}")

        result["indices"][key] = entry

    # --- S&P 500 corrected historical series (annual year-end + current) ----
    if pb_series and cape_series:
        series = []
        for d, pb in reversed(pb_series):          # oldest-first
            cape = cape_series.get(d)
            if cape is None or pb <= 0 or cape <= 0:
                continue
            series.append({"date": d, "pb": pb, "cape": cape,
                           "rg10": corrected_rg(pb, cape, 10)})
        if series:
            result["indices"]["sp500"]["series"] = series
            result["indices"]["sp500"]["seriesStandard"] = \
                "annual (year-end P/B from multpl.com × same-month CAPE) + current month"
            print(f"  [S&P 500] corrected series: {len(series)} points "
                  f"({series[0]['date']} – {series[-1]['date']})")

    ok = any("topDown" in e or "bottomUp" in e for e in result["indices"].values())
    if not ok:
        print("Nothing fetched — keeping previous file.")
        return 1

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"✓  {OUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
