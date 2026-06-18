#!/usr/bin/env python3
"""
Reality Gap — merge-based full refresh across all indices.

Unlike fetch_data.py (which is keyed on hard-coded S&P 500 / Nikkei / DAX
member lists), this driver is *file-driven*: it iterates the company JSON
files that already exist in src/data/companies/, reads each company's own
ticker / index / currency metadata, re-fetches fresh data via the tested
fetch_data.fetch_company() logic, and MERGES the result into the existing
file by periodKey.

Merge rules (non-destructive):
  - top-level metadata (company, ticker, slug, sector, currency, country,
    index, description) is preserved from the existing file
  - observations are merged by periodKey:
      * a freshly fetched period overwrites the existing one (recompute)
      * existing periods not returned by the fetch are KEPT (curated history)
  - observations are re-sorted newest-first

This covers all seven indices (S&P 500, DAX 40, Nikkei 225, Hang Seng,
FTSE 100, CAC 40, SMI) because the ticker comes from each file itself.

Usage:
    python3 scripts/refresh_all.py                 # all files
    python3 scripts/refresh_all.py --only AAPL,SAP.DE   # by ticker
    python3 scripts/refresh_all.py --limit 5
    python3 scripts/refresh_all.py --dry-run       # fetch + report, no write
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "src" / "data" / "companies"

# Import the tested fetch logic from the sibling script.
_spec = importlib.util.spec_from_file_location("fetch_data", Path(__file__).with_name("fetch_data.py"))
fd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fd)

META_KEYS = ["company", "ticker", "dataTicker", "slug", "sector", "currency", "country", "index", "description"]


def period_sort_key(pk: str) -> tuple[int, int]:
    """'2026_q1' -> (2026, 1) for newest-first sorting."""
    try:
        year, q = pk.split("_q")
        return (int(year), int(q))
    except Exception:
        return (0, 0)


def merge_observations(existing: list[dict], fresh: list[dict]) -> tuple[list[dict], int, int]:
    """Merge fresh observations into existing by periodKey. Returns (merged, updated, added)."""
    by_key: dict[str, dict] = {o["periodKey"]: o for o in existing if "periodKey" in o}
    before = set(by_key)
    updated = added = 0
    for o in fresh:
        pk = o.get("periodKey")
        if not pk:
            continue
        if pk in before:
            updated += 1
        else:
            added += 1
        by_key[pk] = o
    merged = sorted(by_key.values(), key=lambda o: period_sort_key(o["periodKey"]), reverse=True)
    return merged, updated, added


def fetch_with_retry(meta: dict, retries: int = 3, base_delay: float = 4.0):
    last = None
    # dataTicker overrides the display ticker for fetching only (e.g. a delisted
    # local symbol mapped to a live ADR so market cap is still retrievable).
    fetch_ticker = meta.get("dataTicker") or meta["ticker"]
    for attempt in range(retries):
        try:
            return fd.fetch_company(
                fetch_ticker, meta.get("company", meta["ticker"]),
                meta.get("sector", ""), meta.get("index", ""),
                meta.get("country", ""), meta.get("currency", "USD"),
                slug_override=meta.get("slug"),
            )
        except Exception as e:  # noqa: BLE001
            last = e
            wait = base_delay * (2 ** attempt)
            print(f"    retry {attempt + 1}/{retries} after error: {e!r} (wait {wait:.0f}s)")
            time.sleep(wait)
    print(f"    GAVE UP: {last!r}")
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma-separated tickers to refresh")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--delay", type=float, default=1.5, help="seconds between companies")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    only = {t.strip().upper() for t in args.only.split(",") if t.strip()}

    files = sorted(DATA_DIR.glob("*.json"))
    if args.limit:
        files = files[: args.limit]

    total = changed = failed = 0
    for fp in files:
        existing = json.loads(fp.read_text(encoding="utf-8"))
        meta = {k: existing.get(k) for k in META_KEYS if k in existing}
        ticker = meta.get("ticker")
        if not ticker:
            print(f"SKIP {fp.name}: no ticker")
            continue
        if only and ticker.upper() not in only:
            continue
        total += 1

        fresh = fetch_with_retry(meta)
        if not fresh or not fresh.get("observations"):
            failed += 1
            continue

        merged, upd, add = merge_observations(existing.get("observations", []), fresh["observations"])
        latest = merged[0] if merged else {}
        print(f"    {meta.get('slug'):28} {len(merged):2} obs  (+{add} new, ~{upd} upd)  "
              f"latest={latest.get('periodKey')} rg10={latest.get('rg10')}")

        if not args.dry_run:
            out = dict(existing)          # preserve curated top-level metadata
            out["observations"] = merged  # only observations refreshed/merged
            fp.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            changed += 1

        time.sleep(args.delay)

    print(f"\n{'DRY-RUN ' if args.dry_run else ''}done: {total} processed, "
          f"{changed} written, {failed} failed.")


if __name__ == "__main__":
    main()
