#!/usr/bin/env python3
"""
Reality Gap — Pre-2009 Fundamentals Backfill via EDGAR HTML 10-K Parsing
=========================================================================
Fills the dot-com (1995–2002) and early-GFC (2003–2008) gap in
fundamentals.db by parsing annual 10-K filings directly from
SEC EDGAR's HTML archives.

Strategy
--------
Each 10-K contains a "Selected Financial Data" table showing 5 years
of summary data (net income, equity, total assets).  By fetching two
10-K filings per company (≈ FY2007/08 and ≈ FY2002/03) we cover
approximately FY1998–FY2008 with full net income + equity data.

Goodwill and intangibles are parsed from the balance sheet in the same
HTML document.

The script only inserts rows that are genuinely missing from the DB
(no duplicate writes).  All pre-2009 rows are flagged source='edgar_html'.

Usage
-----
    python3 scripts/backfill_pre2009.py                 # all tickers
    python3 scripts/backfill_pre2009.py --ticker AAPL   # single ticker
    python3 scripts/backfill_pre2009.py --dry-run       # print only

Dependencies: requests (pip install requests)
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import time
import sys
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    sys.exit("requests not installed: pip install requests")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH   = REPO_ROOT / "src" / "data" / "reference" / "fundamentals.db"

HEADERS = {
    "User-Agent": "reality-gap-research rentschler@lbsmail.de",
    "Accept": "text/html,*/*",
}
DELAY = 0.5   # seconds between EDGAR requests (respect rate limit)

# CIK mapping for our 30 US tickers
CIK_MAP: dict[str, str] = {
    "AAPL":  "0000320193",
    "ABBV":  "0001551152",   # founded 2013 — no pre-2009 data
    "AMD":   "0000002488",
    "AMZN":  "0001018724",
    "AVGO":  "0001730168",   # founded 2018 (spun out) — no pre-2009
    "BAC":   "0000070858",
    "BRK-B": "0001067983",
    "COST":  "0000909832",
    "CRM":   "0001108524",   # IPO 2004
    "CVX":   "0000093410",
    "GOOGL": "0001652044",   # IPO 2004 (Alphabet CIK)
    "HD":    "0000354950",
    "JNJ":   "0000200406",
    "JPM":   "0000019617",
    "KO":    "0000021344",
    "LLY":   "0000059478",
    "MA":    "0001141391",   # IPO 2006
    "META":  "0001326801",   # IPO 2012
    "MRK":   "0000310158",
    "MSFT":  "0000789019",
    "NFLX":  "0001065280",   # IPO 2002
    "NVDA":  "0001045810",   # IPO 1999
    "ORCL":  "0001341439",
    "PEP":   "0000077476",
    "PG":    "0000080424",
    "TSLA":  "0001318605",   # IPO 2010 — no pre-2009
    "UNH":   "0000731766",
    "V":     "0001403161",   # IPO 2008 — very limited pre-2009
    "WMT":   "0000104169",
    "XOM":   "0000034088",
}

# Target fiscal years to fetch 10-Ks for per company.
# Each 10-K has a 5-year selected-financial-data table, so FY2007 gives
# FY2003–2007, and FY2002 gives FY1998–2002.
TARGET_FY = [2008, 2003]   # will try both; skip gracefully if not found


# ---------------------------------------------------------------------------
# EDGAR helpers
# ---------------------------------------------------------------------------

def get_submissions(cik: str) -> dict:
    """Fetch the submissions JSON for a CIK (both recent + archive files)."""
    cik_padded = cik.lstrip("0").zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()
    time.sleep(DELAY)
    return data


def find_10k_accessions(cik: str, target_fys: list[int]) -> dict[int, str]:
    """
    Return {target_fy: accession_number} for the requested target fiscal years.

    Strategy: for target_fy N, we want the LATEST 10-K filing whose date is
    before {N+1}-07-01.  This correctly handles:
      - Dec 31 FY end (filed Feb/Mar of N+1)
      - Sep 30 FY end (filed Nov/Dec of N)
      - Jan 31 FY end (filed Mar/Apr of N+1)
    """
    sub = get_submissions(cik)

    # Collect all 10-K filings as (date, accn) across recent + archive files
    all_filings: list[tuple[str, str]] = []

    def collect(filing_data: dict) -> None:
        forms = filing_data.get("form", [])
        dates = filing_data.get("filingDate", [])
        accns = filing_data.get("accessionNumber", [])
        for form, date, accn in zip(forms, dates, accns):
            if form in ("10-K", "10-K/A"):
                all_filings.append((date, accn))

    collect(sub["filings"]["recent"])
    for archive_file in sub["filings"].get("files", []):
        url = f"https://data.sec.gov/submissions/{archive_file['name']}"
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            collect(r.json())
        time.sleep(DELAY)

    # Sort filings newest → oldest
    all_filings.sort(key=lambda x: x[0], reverse=True)

    result: dict[int, str] = {}
    for fy in target_fys:
        cutoff = f"{fy + 1}-07-01"  # latest acceptable filing date for this FY
        earliest = f"{fy - 1}-01-01"  # don't go too far back
        for date, accn in all_filings:
            if date <= cutoff and date >= earliest:
                result[fy] = accn
                break

    return result


def get_filing_html_url(cik: str, accn: str) -> Optional[str]:
    """
    Return the URL of the primary 10-K HTML document from a filing index.
    """
    cik_num = cik.lstrip("0")
    accn_clean = accn.replace("-", "")
    idx_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik_num}&type=10-K&dateb=&owner=include&count=1&search_text=&output=atom"

    # Use the filing index page directly
    idx_page = f"https://www.sec.gov/Archives/edgar/data/{cik_num}/{accn_clean}/{accn}-index.htm"
    r = requests.get(idx_page, headers=HEADERS, timeout=15)
    time.sleep(DELAY)
    if r.status_code != 200:
        return None

    # Find the main HTM document link (not exhibit)
    matches = re.findall(
        r'href="(/Archives/edgar/data/[^"]+\.htm[l]?)"',
        r.text, re.IGNORECASE
    )
    # Filter: exclude exhibits (ex-), prefer the longest/first substantive file
    main_docs = [m for m in matches if not re.search(r'ex[-_]', m, re.IGNORECASE)]
    if not main_docs:
        main_docs = matches  # fallback: take any htm

    # Also check via submissions primaryDocument field
    sub_url = f"https://data.sec.gov/submissions/CIK{cik.lstrip('0').zfill(10)}.json"

    if main_docs:
        return f"https://www.sec.gov{main_docs[0]}"
    return None


def fetch_10k_html(url: str) -> Optional[str]:
    """Fetch a 10-K HTML document and return cleaned plain text."""
    r = requests.get(url, headers=HEADERS, timeout=30)
    time.sleep(DELAY)
    if r.status_code != 200:
        return None
    text = r.text
    # Decode HTML entities
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&#\d+;', ' ', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Collapse whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    return text


# ---------------------------------------------------------------------------
# Financial data parsing
# ---------------------------------------------------------------------------

def detect_unit_multiplier(text: str) -> int:
    """
    Return the multiplier to convert reported numbers to raw USD.
    E.g. 'in millions' → 1_000_000.
    """
    lower = text[:5000].lower()
    if 'in billions' in lower:
        return 1_000_000_000
    if 'in millions' in lower or 'millions of dollars' in lower:
        return 1_000_000
    if 'in thousands' in lower or 'thousands of dollars' in lower:
        return 1_000
    return 1_000_000  # default assumption for large US companies


def parse_number(s: str) -> Optional[float]:
    """Parse a formatted number string like '3,496' or '( 1,234 )' to float."""
    if not s:
        return None
    s = s.strip()
    negative = (s.startswith('(') and ')' in s) or s.startswith('-')
    s = s.replace(',', '').replace('$', '').replace('(', '').replace(')', '').replace('-', '').strip()
    try:
        v = float(s)
        return -v if negative else v
    except ValueError:
        return None


def extract_selected_financial_data(text: str) -> dict[int, dict]:
    """
    Parse the 'Selected Financial Data' / 'Selected Consolidated Financial Data'
    table from a 10-K plain-text body.

    Returns {year: {'net_income': float_raw, 'equity': float_raw, ...}}
    where values are already multiplied by the unit multiplier.
    """
    mult = detect_unit_multiplier(text)

    # Find the Selected Financial Data section
    idx = -1
    for pattern in [
        r'selected financial data',
        r'selected consolidated financial data',
        r'selected combined financial data',
        r'five.year selected financial',
    ]:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            idx = m.start()
            break

    if idx < 0:
        return {}

    section = text[idx: idx + 5000]

    # Extract year headers — look for 4-digit years in a row
    years_match = re.findall(r'\b(20[0-9]{2}|199[0-9])\b', section[:1500])
    years = [int(y) for y in years_match]
    if len(years) < 2:
        return {}
    # Remove duplicates preserving order
    seen = set()
    years_unique = []
    for y in years:
        if y not in seen:
            seen.add(y)
            years_unique.append(y)
    years = years_unique[:6]  # at most 6 years

    result: dict[int, dict] = {y: {} for y in years}

    def extract_row(label_pattern: str, key: str) -> None:
        """Find a labelled row and extract its numeric values into result."""
        m = re.search(label_pattern, section, re.IGNORECASE)
        if not m:
            return
        after = section[m.end(): m.end() + 500]
        # Match numbers: plain integers, with commas, or negative in parens
        # Pattern: optional $, optional space, optional (, digits with commas, optional )
        nums_raw = re.findall(
            r'[\$]?\s*(\(?\s*\d[\d,]*\s*\)?)',
            after
        )
        nums_clean = []
        for n in nums_raw:
            v = parse_number(n)
            if v is not None and (abs(v) >= 1 or ',' in n):
                nums_clean.append(v)
            if len(nums_clean) >= len(years):
                break
        for i, yr in enumerate(years):
            if i < len(nums_clean) and key not in result[yr]:
                result[yr][key] = nums_clean[i] * mult

    extract_row(r'Net income\b(?:\s*\(loss\))?', 'net_income')
    extract_row(r'Net earnings\b(?:\s*\(loss\))?', 'net_income')
    extract_row(r"(?:Total )?[Ss]hareholders['\u2019\s]*equity\b", 'equity')
    extract_row(r"(?:Total )?[Ss]tockholders['\u2019\s]*equity\b", 'equity')
    extract_row(r'Total assets\b', 'total_assets')

    return result


def extract_balance_sheet(text: str, mult: int) -> dict:
    """
    Parse goodwill and intangible assets from the balance sheet section.
    Returns values for the most recent fiscal year only.

    Strategy: first locate the CONSOLIDATED BALANCE SHEET heading, then
    search only within the next ~4000 chars of that section.  This prevents
    prose footnotes (which often mention 'goodwill' alongside year numbers)
    from contaminating the result.
    """
    result: dict = {}

    # ---- 1. Locate the balance sheet section --------------------------------
    bs_start = -1
    for pat in [
        r'CONSOLIDATED BALANCE SHEET',
        r'CONSOLIDATED STATEMENTS? OF FINANCIAL POSITION',
        r'BALANCE SHEETS?',
    ]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            bs_start = m.start()
            break

    if bs_start < 0:
        # Fallback: search entire text (may be less accurate)
        section = text
    else:
        # Use up to 5000 chars after the heading (covers most balance sheets)
        section = text[bs_start: bs_start + 5000]

    # ---- 2. Sanity-check helper: reject raw values that look like years -----
    def is_year_like(raw_val: float) -> bool:
        """True if the parsed value (before multiplier) looks like a 4-digit year."""
        return 1_990 <= raw_val <= 2_035

    def find_value(patterns: list[str]) -> Optional[float]:
        for pat in patterns:
            for m in re.finditer(pat, section, re.IGNORECASE):
                # Only look at a short window immediately after the label
                after = section[m.end(): m.end() + 120]
                nums = re.findall(r'\$?\s*(\d[\d,]*)', after)
                for n in nums:
                    v = parse_number(n)
                    if v is not None and v > 0 and not is_year_like(v):
                        return v * mult
        return None

    result['goodwill'] = find_value([
        r'\bGoodwill\b(?!\s+and\s+intangible)',
    ])

    result['intangibles'] = find_value([
        r'(?:Acquired |Net )?[Ii]ntangible assets,?\s*net',
        r'[Ii]ntangible assets\b',
        r'Other intangible assets\b',
    ])

    return result


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_existing_periods(conn: sqlite3.Connection, ticker: str) -> set[str]:
    """Return set of period_end strings already in DB for this ticker."""
    cur = conn.execute(
        "SELECT period_end FROM fundamentals WHERE ticker=?", (ticker,)
    )
    return {row[0] for row in cur.fetchall()}


def insert_row(conn: sqlite3.Connection, row: dict, dry_run: bool) -> bool:
    def fmt(v): return f"{v/1e9:.2f}B" if v is not None else "—"
    if dry_run:
        print(f"  [DRY] {row['ticker']} {row['period_end']}: "
              f"NI={fmt(row['net_income'])}  "
              f"EQ={fmt(row['stockholders_equity'])}  "
              f"GW={fmt(row['goodwill'])}  "
              f"IA={fmt(row['intangibles'])}")
        return True
    try:
        conn.execute("""
            INSERT OR IGNORE INTO fundamentals
              (ticker, cik, period_end, form_type, fiscal_year, fiscal_quarter,
               net_income, stockholders_equity, goodwill, intangibles,
               source, filed_date)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            row['ticker'], row['cik'], row['period_end'], '10-K',
            row['fiscal_year'], None,
            row['net_income'], row['stockholders_equity'],
            row['goodwill'], row['intangibles'],
            'edgar_html', None,
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"  DB error: {e}")
        return False


# ---------------------------------------------------------------------------
# Main per-ticker logic
# ---------------------------------------------------------------------------

def process_ticker(ticker: str, cik: str, conn: sqlite3.Connection,
                   dry_run: bool, target_fy: list[int] | None = None) -> int:
    if target_fy is None:
        target_fy = TARGET_FY
    print(f"\n{'='*60}")
    print(f"  {ticker}  (CIK {cik})")
    print(f"{'='*60}")

    existing = get_existing_periods(conn, ticker)
    inserted = 0

    # Find 10-K accessions for our target fiscal years
    print(f"  Looking up 10-K filings on EDGAR...")
    try:
        accessions = find_10k_accessions(cik, target_fy)
    except Exception as e:
        print(f"  FAILED to get submissions: {e}")
        return 0

    if not accessions:
        print(f"  No 10-K filings found for target years {TARGET_FY}")
        return 0

    print(f"  Found filings: {accessions}")

    for target_fy, accn in sorted(accessions.items()):
        print(f"\n  -- FY{target_fy} filing: {accn} --")

        # Get HTML URL
        html_url = get_filing_html_url(cik.lstrip("0"), accn)
        if not html_url:
            print(f"  Could not locate HTML document")
            continue
        print(f"  URL: {html_url}")

        # Fetch and parse
        text = fetch_10k_html(html_url)
        if not text:
            print(f"  Failed to fetch HTML")
            continue
        print(f"  Fetched {len(text):,} chars")

        mult = detect_unit_multiplier(text)
        print(f"  Unit multiplier: {mult:,} (reports in {'billions' if mult==1e9 else 'millions' if mult==1e6 else 'thousands'})")

        sfd = extract_selected_financial_data(text)
        bs  = extract_balance_sheet(text, mult)

        print(f"  Selected Financial Data years: {sorted(sfd.keys())}")
        print(f"  Balance sheet: goodwill={bs.get('goodwill')}, intangibles={bs.get('intangibles')}")

        if not sfd:
            print(f"  WARNING: No Selected Financial Data found")
            continue

        # The most recent year in SFD corresponds to the 10-K filing year → use BS values
        most_recent_yr = max(sfd.keys())

        for yr, fields in sorted(sfd.items()):
            ni  = fields.get('net_income')
            eq  = fields.get('equity')
            # Goodwill/intangibles only reliably available for most recent yr
            gw  = bs.get('goodwill') if yr == most_recent_yr else None
            ia  = bs.get('intangibles') if yr == most_recent_yr else None

            if ni is None and eq is None:
                continue

            # Construct approximate period_end date (fiscal year end)
            # Use Sep 30 for Apple, Dec 31 for most, Jan 31 for retail, etc.
            # We'll use a simple heuristic: if existing DB has entries for this
            # ticker, use the same month pattern
            period_end = f"{yr}-12-31"  # default
            # Try to infer from existing records
            for existing_period in sorted(existing):
                if existing_period.startswith(str(yr)):
                    period_end = existing_period
                    break
                # Infer month from a recent year's period
                if existing_period[:4] > str(yr):
                    month_day = existing_period[4:]  # e.g. "-09-30"
                    period_end = f"{yr}{month_day}"
                    break

            if period_end in existing:
                print(f"  SKIP {yr}: already in DB ({period_end})")
                continue

            row = {
                'ticker': ticker,
                'cik': cik,
                'period_end': period_end,
                'fiscal_year': yr,
                'net_income': ni,
                'stockholders_equity': eq,
                'goodwill': gw,
                'intangibles': ia,
            }

            ok = insert_row(conn, row, dry_run)
            if ok:
                inserted += 1
                def _f(v): return f"{v/1e9:.2f}B" if v is not None else "—"
            print(f"  + {yr} ({period_end}): NI={_f(ni)}  EQ={_f(eq)}  GW={_f(gw)}  IA={_f(ia)}")

    print(f"\n  Total inserted for {ticker}: {inserted}")
    return inserted


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill pre-2009 fundamentals from EDGAR HTML 10-Ks")
    parser.add_argument("--ticker", help="Process single ticker only")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing to DB")
    parser.add_argument("--fy", type=int, nargs="+", default=TARGET_FY,
                        help=f"Target fiscal years (default: {TARGET_FY})")
    args = parser.parse_args()

    target_fy = args.fy

    conn = sqlite3.connect(DB_PATH)

    tickers_to_run = {args.ticker: CIK_MAP[args.ticker]} if args.ticker else CIK_MAP
    skipped = [t for t in tickers_to_run if t not in CIK_MAP]
    if skipped:
        print(f"Unknown tickers: {skipped}")

    total = 0
    for ticker, cik in tickers_to_run.items():
        try:
            n = process_ticker(ticker, cik, conn, args.dry_run, target_fy)
            total += n
        except KeyboardInterrupt:
            print("\nInterrupted.")
            break
        except Exception as e:
            print(f"  ERROR processing {ticker}: {e}")
            import traceback; traceback.print_exc()

    conn.close()
    print(f"\n{'='*60}")
    print(f"Total rows {'would be ' if args.dry_run else ''}inserted: {total}")


if __name__ == "__main__":
    main()
