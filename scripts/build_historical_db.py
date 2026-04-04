#!/usr/bin/env python3
"""
Reality Gap — Historical Fundamentals Database Builder
=======================================================
Fetches structured financial statement data from the SEC XBRL API
(data.sec.gov/api/xbrl/companyfacts) and stores it in a local SQLite
database for use in historical RG calculations.

Coverage
--------
- US companies (S&P 500 members): 2007–present via SEC XBRL
  (XBRL adoption by large accelerated filers started 2007–2009)
- Non-US companies (Nikkei 225, DAX 40): not available via SEC;
  yfinance remains the source for those companies.

Data stored per observation
---------------------------
  ticker, cik, period_end, form_type, fiscal_year, fiscal_quarter,
  net_income, stockholders_equity, goodwill, intangibles,
  source ('sec_xbrl'), filed_date

Fields map to SEC US-GAAP XBRL concepts:
  net_income          ← NetIncomeLoss
  stockholders_equity ← StockholdersEquity (fallback: CommonStockEquity)
  goodwill            ← Goodwill
  intangibles         ← IntangibleAssetsNetExcludingGoodwill
                         (fallback: OtherIntangibleAssetsNet)

CPI inflation adjustment
------------------------
The database also imports the FRED CPI monthly series from
src/data/reference/cpi_us_monthly.csv so that callers can easily
compute real earnings:
    real_NI_t = nominal_NI_t × (CPI_latest / CPI_at_period_end)

Usage
-----
    python3 scripts/build_historical_db.py               # all US tickers
    python3 scripts/build_historical_db.py --ticker AAPL # single ticker
    python3 scripts/build_historical_db.py --cpi-only    # refresh CPI only
    python3 scripts/build_historical_db.py --force       # re-fetch all
"""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import time
import urllib.request
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT  = Path(__file__).resolve().parent.parent
DB_PATH    = REPO_ROOT / "src" / "data" / "reference" / "fundamentals.db"
CPI_CSV    = REPO_ROOT / "src" / "data" / "reference" / "cpi_us_monthly.csv"
INDEX_FILE = REPO_ROOT / "src" / "data" / "companies.index.json"

SEC_HEADERS = {"User-Agent": "reality-gap-research rentschler@lbsmail.de"}
SEC_DELAY   = 0.12   # 8–10 req/s → well within SEC's fair-use limit

# ---------------------------------------------------------------------------
# US tickers we want (S&P 500 subset tracked by the website)
# ---------------------------------------------------------------------------
US_TICKERS = [
    "AAPL","NVDA","MSFT","AMZN","GOOGL","META","TSLA","BRK-B","LLY","JPM",
    "V","WMT","XOM","UNH","MA","AVGO","COST","PG","JNJ","HD","ABBV","BAC",
    "MRK","ORCL","CRM","CVX","NFLX","AMD","KO","PEP",
]

# XBRL concept → column name (ordered list = priority fallback chain)
CONCEPT_MAP: dict[str, list[str]] = {
    "net_income": [
        "NetIncomeLoss",
        "NetIncomeLossAvailableToCommonStockholdersBasic",
        "NetIncomeLossFromContinuingOperationsAvailableToCommonShareholdersBasic",
    ],
    "stockholders_equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        "CommonStockEquity",
    ],
    "goodwill": [
        "Goodwill",
    ],
    "intangibles": [
        "IntangibleAssetsNetExcludingGoodwill",
        "OtherIntangibleAssetsNet",
        "FiniteLivedIntangibleAssetsNet",
    ],
}


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

def open_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS fundamentals (
            id                   INTEGER PRIMARY KEY,
            ticker               TEXT NOT NULL,
            cik                  TEXT NOT NULL,
            period_end           TEXT NOT NULL,   -- YYYY-MM-DD
            form_type            TEXT,            -- 10-K, 10-Q
            fiscal_year          INTEGER,
            fiscal_quarter       INTEGER,         -- 1-4 or NULL for annual
            net_income           REAL,            -- USD, raw (not billions)
            stockholders_equity  REAL,
            goodwill             REAL,
            intangibles          REAL,
            source               TEXT DEFAULT 'sec_xbrl',
            filed_date           TEXT,
            UNIQUE(ticker, period_end, form_type)
        );

        CREATE TABLE IF NOT EXISTS cpi_monthly (
            date   TEXT PRIMARY KEY,  -- YYYY-MM-DD (first of month)
            cpi    REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS fetch_log (
            ticker     TEXT PRIMARY KEY,
            cik        TEXT,
            fetched_at TEXT,
            n_rows     INTEGER,
            status     TEXT
        );
    """)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# CPI import
# ---------------------------------------------------------------------------

def import_cpi(conn: sqlite3.Connection, csv_path: Path) -> int:
    rows = []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            if row["CPIAUCSL"].strip():
                rows.append((row["observation_date"], float(row["CPIAUCSL"])))
    conn.executemany(
        "INSERT OR REPLACE INTO cpi_monthly (date, cpi) VALUES (?, ?)", rows)
    conn.commit()
    return len(rows)


def latest_cpi(conn: sqlite3.Connection) -> Optional[float]:
    """Return the most recent CPI value available."""
    row = conn.execute(
        "SELECT cpi FROM cpi_monthly ORDER BY date DESC LIMIT 1").fetchone()
    return row["cpi"] if row else None


def cpi_at(conn: sqlite3.Connection, yyyy_mm: str) -> Optional[float]:
    """CPI for a given YYYY-MM month string."""
    date = yyyy_mm + "-01"
    row = conn.execute(
        "SELECT cpi FROM cpi_monthly WHERE date <= ? ORDER BY date DESC LIMIT 1",
        (date,)).fetchone()
    return row["cpi"] if row else None


# ---------------------------------------------------------------------------
# SEC API helpers
# ---------------------------------------------------------------------------

def sec_get(url: str) -> Optional[dict]:
    req = urllib.request.Request(url, headers=SEC_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception as e:
        print(f"    SEC API error: {e}")
        return None


def get_cik_map() -> dict[str, str]:
    """Return {ticker: zero-padded 10-digit CIK}."""
    data = sec_get("https://www.sec.gov/files/company_tickers.json")
    if not data:
        return {}
    return {v["ticker"]: str(v["cik_str"]).zfill(10) for v in data.values()}


def extract_concept(facts_usgaap: dict, concepts: list[str],
                    unit: str = "USD") -> dict[str, float]:
    """
    Try concepts in priority order; return {period_end: value} dict
    using 10-K and 10-Q filings only, keeping the most recent filing
    per period (deduplicated).
    """
    for concept in concepts:
        if concept not in facts_usgaap:
            continue
        vals = facts_usgaap[concept].get("units", {}).get(unit, [])
        if not vals:
            continue
        # keep 10-K / 10-Q only; deduplicate by (end, form), latest filed wins
        best: dict[tuple, dict] = {}
        for v in vals:
            if v.get("form") not in ("10-K", "10-Q"):
                continue
            key = (v["end"], v["form"])
            if key not in best or v.get("filed", "") > best[key].get("filed", ""):
                best[key] = v
        return {k: v for k, v in {
            (vv["end"], vv["form"]): vv for vv in best.values()
        }.items()}
    return {}


# ---------------------------------------------------------------------------
# Fetch one company
# ---------------------------------------------------------------------------

def fetch_company(ticker: str, cik: str, conn: sqlite3.Connection,
                  force: bool = False) -> int:
    """Fetch companyfacts from SEC and upsert into DB. Returns rows added."""

    if not force:
        row = conn.execute(
            "SELECT status FROM fetch_log WHERE ticker=?", (ticker,)).fetchone()
        if row and row["status"] == "ok":
            return 0  # already fetched

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    data = sec_get(url)
    if not data:
        conn.execute(
            "INSERT OR REPLACE INTO fetch_log VALUES (?,?,datetime('now'),0,'error')",
            (ticker, cik))
        conn.commit()
        return 0

    usgaap = data.get("facts", {}).get("us-gaap", {})

    # Extract each field using priority fallback
    ni_map    = extract_concept(usgaap, CONCEPT_MAP["net_income"])
    eq_map    = extract_concept(usgaap, CONCEPT_MAP["stockholders_equity"])
    gw_map    = extract_concept(usgaap, CONCEPT_MAP["goodwill"])
    intan_map = extract_concept(usgaap, CONCEPT_MAP["intangibles"])

    # Collect all (period_end, form_type) combinations that have any data
    all_keys: set[tuple] = (set(ni_map) | set(eq_map) |
                             set(gw_map) | set(intan_map))

    rows_added = 0
    for (period_end, form_type) in all_keys:
        ni   = ni_map.get((period_end, form_type))
        eq   = eq_map.get((period_end, form_type))
        gw   = gw_map.get((period_end, form_type))
        intn = intan_map.get((period_end, form_type))

        # Need at least NI and equity to be useful
        if ni is None and eq is None:
            continue

        ni_val  = ni["val"]   if ni   else None
        eq_val  = eq["val"]   if eq   else None
        gw_val  = gw["val"]   if gw   else None
        in_val  = intn["val"] if intn else None
        filed   = (ni or eq or gw or intn or {}).get("filed")

        # Derive fiscal year / quarter from period_end
        from datetime import date as dt
        try:
            d = dt.fromisoformat(period_end)
            fy = d.year
            fq = (d.month - 1) // 3 + 1
        except Exception:
            fy, fq = None, None

        conn.execute("""
            INSERT OR REPLACE INTO fundamentals
              (ticker, cik, period_end, form_type, fiscal_year, fiscal_quarter,
               net_income, stockholders_equity, goodwill, intangibles,
               source, filed_date)
            VALUES (?,?,?,?,?,?,?,?,?,?,'sec_xbrl',?)
        """, (ticker, cik, period_end, form_type, fy, fq,
              ni_val, eq_val, gw_val, in_val, filed))
        rows_added += 1

    conn.commit()
    conn.execute(
        "INSERT OR REPLACE INTO fetch_log VALUES (?,?,datetime('now'),?,'ok')",
        (ticker, cik, rows_added))
    conn.commit()
    return rows_added


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build historical fundamentals SQLite DB from SEC XBRL API")
    parser.add_argument("--ticker", default="",
                        help="Fetch a single ticker (for testing)")
    parser.add_argument("--cpi-only", action="store_true",
                        help="Only import/refresh CPI data, skip SEC fetch")
    parser.add_argument("--force", action="store_true",
                        help="Re-fetch even if already in fetch_log")
    args = parser.parse_args()

    conn = open_db(DB_PATH)

    # Always import CPI
    if CPI_CSV.exists():
        n = import_cpi(conn, CPI_CSV)
        ref_cpi = latest_cpi(conn)
        print(f"CPI: {n} months imported. Latest = {ref_cpi:.3f}")
    else:
        print(f"WARNING: CPI file not found at {CPI_CSV}")

    if args.cpi_only:
        return

    # CIK lookup
    print("Fetching SEC ticker→CIK map …")
    cik_map = get_cik_map()
    if not cik_map:
        print("ERROR: Could not fetch CIK map from SEC.")
        return
    print(f"  {len(cik_map):,} tickers mapped.")

    tickers = [args.ticker.upper()] if args.ticker else US_TICKERS

    total_rows = 0
    for i, ticker in enumerate(tickers):
        cik = cik_map.get(ticker)
        if not cik:
            print(f"  {ticker:<8} CIK not found — skipping")
            continue

        print(f"  {ticker:<8} CIK {cik} … ", end="", flush=True)
        n = fetch_company(ticker, cik, conn, force=args.force)
        if n == 0:
            row = conn.execute(
                "SELECT n_rows FROM fetch_log WHERE ticker=?", (ticker,)).fetchone()
            cached = row["n_rows"] if row else "?"
            print(f"cached ({cached} rows)")
        else:
            print(f"{n} rows")
            total_rows += n

        time.sleep(SEC_DELAY)

    # Summary
    total_in_db = conn.execute("SELECT COUNT(*) FROM fundamentals").fetchone()[0]
    earliest = conn.execute(
        "SELECT MIN(period_end) FROM fundamentals").fetchone()[0]
    latest_q = conn.execute(
        "SELECT MAX(period_end) FROM fundamentals WHERE form_type='10-Q'").fetchone()[0]
    print()
    print(f"Database: {DB_PATH}")
    print(f"  Total rows   : {total_in_db:,}")
    print(f"  Earliest obs : {earliest}")
    print(f"  Latest 10-Q  : {latest_q}")
    print(f"  CPI ref value: {latest_cpi(conn):.3f}")


if __name__ == "__main__":
    main()
