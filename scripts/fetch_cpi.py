#!/usr/bin/env python3
"""
Reality Gap — US CPI (CPIAUCSL) Updater
========================================
Refreshes src/data/reference/cpi_us_monthly.csv from FRED's public CSV
endpoint (no API key required):

    https://fred.stlouisfed.org/graphs/fredgraph.csv?id=CPIAUCSL

The CSV feeds the Shiller-style inflation adjustment of the 8-quarter
earnings window for US companies in fetch_data.py.

Safety: the existing file is only overwritten when the download parses
cleanly, has at least as many rows as the current file, and its latest
observation is not older than the current one. On any failure the script
exits non-zero and leaves the existing CSV untouched.

Usage:
    python3 scripts/fetch_cpi.py
"""

from __future__ import annotations

import csv
import io
import sys
import time
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
CPI_FILE  = REPO_ROOT / "src" / "data" / "reference" / "cpi_us_monthly.csv"

URL = "https://fred.stlouisfed.org/graphs/fredgraph.csv?id=CPIAUCSL"
UA  = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def download() -> str:
    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            r = requests.get(URL, headers={"User-Agent": UA}, timeout=60)
            r.raise_for_status()
            return r.text
        except Exception as exc:
            last_exc = exc
            time.sleep(5 * (attempt + 1))
    # Fallback: browser-impersonating client (some proxies/CDNs reject
    # plain requests); curl_cffi ships as a yfinance dependency.
    try:
        from curl_cffi import requests as cr
        r = cr.get(URL, impersonate="chrome110", timeout=60)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    raise RuntimeError(f"CPI download failed: {last_exc}")


def parse(text: str) -> list[tuple[str, str]]:
    """Return [(date, value), ...]; raises on malformed content."""
    rows: list[tuple[str, str]] = []
    reader = csv.DictReader(io.StringIO(text))
    fields = reader.fieldnames or []
    if "observation_date" not in fields or "CPIAUCSL" not in fields:
        raise ValueError(f"Unexpected CSV header: {fields}")
    for row in reader:
        d, v = row["observation_date"], row["CPIAUCSL"]
        if not d or v in ("", "."):
            continue
        float(v)                      # must parse
        if len(d) != 10 or d[4] != "-":
            raise ValueError(f"Unexpected date format: {d}")
        rows.append((d, v))
    return rows


def current_state() -> tuple[int, str]:
    """(row_count, latest_date) of the existing CSV; (0, '') if absent."""
    if not CPI_FILE.exists():
        return 0, ""
    with open(CPI_FILE, newline="") as f:
        data = [r for r in csv.DictReader(f) if r.get("observation_date")]
    if not data:
        return 0, ""
    return len(data), max(r["observation_date"] for r in data)


def main() -> int:
    rows = parse(download())
    if len(rows) < 900:               # series starts 1947 → ~950+ rows
        print(f"Refusing to write: only {len(rows)} rows parsed")
        return 1

    old_count, old_latest = current_state()
    new_latest = rows[-1][0]
    if len(rows) < old_count or (old_latest and new_latest < old_latest):
        print(f"Refusing to write: new data is behind existing "
              f"({len(rows)} rows to {new_latest} vs {old_count} rows to {old_latest})")
        return 1

    with open(CPI_FILE, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["observation_date", "CPIAUCSL"])
        w.writerows(rows)

    print(f"✓  CPI updated: {len(rows)} rows, latest {new_latest} "
          f"(was: {old_count} rows, latest {old_latest or 'n/a'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
