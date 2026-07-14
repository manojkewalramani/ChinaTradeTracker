#!/usr/bin/env python3
"""Download reports we need into raw/."""
import json
import os
import sys
import time
import urllib.request
import ssl
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
RAW.mkdir(exist_ok=True)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


PLAN = {
    "2024": {
        "country": ["Dec"],
        "export_commodities": ["Dec"],
        "import_commodities": ["Dec"],
        "exports_by_country_hs": ["Dec"],
        "imports_by_country_hs": ["Dec"],
    },
    "2025": {
        "country": ["Dec"],
        "export_commodities": ["Dec"],
        "import_commodities": ["Dec"],
        "exports_by_country_hs": ["Dec"],
        "imports_by_country_hs": ["Dec"],
    },
    "2026": {
        "country": ["Jan", "Feb", "Mar", "Apr", "May"],
        "export_commodities": ["Jan", "Feb", "Mar", "Apr", "May"],
        "import_commodities": ["Jan", "Feb", "Mar", "Apr", "May"],
        "exports_by_country_hs": ["May"],
        "imports_by_country_hs": ["May"],
    },
}


def fetch(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 1000:
        return True
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=30) as resp:
            data = resp.read()
        dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"  FAILED {url}: {e}", file=sys.stderr)
        return False


def main():
    urls = json.load(open(ROOT / "urls.json"))
    total = 0
    ok = 0
    for year, reports in PLAN.items():
        for report, months in reports.items():
            for month in months:
                url = urls[year][report].get(month)
                if not url:
                    print(f"  No URL: {year} {report} {month}")
                    continue
                dest = RAW / f"{year}_{report}_{month}.html"
                total += 1
                print(f"[{total}] {year} {report} {month} -> {dest.name}")
                if fetch(url, dest):
                    ok += 1
                time.sleep(0.5)
    print(f"Done: {ok}/{total}")


if __name__ == "__main__":
    main()
