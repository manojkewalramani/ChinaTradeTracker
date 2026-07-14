#!/usr/bin/env python3
"""Extract report URLs from a yearly index page.

Reports of interest:
  (2)  Imports and Exports by Country (Region) of Origin/Destination
  (13) Major Export Commodities in Quantity and Value
  (14) Major Import Commodities in Quantity and Value
  (15) Exports by Selected Countries (Regions) and by HS Divisions
  (16) Imports by Selected Countries (Regions) and by HS Divisions
"""
import json
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"

REPORT_KEYS = {
    "country": "（2）Imports and Exports by Country",
    "export_commodities": "（13）Major Export Commodities",
    "import_commodities": "（14）Major Import Commodities",
    "exports_by_country_hs": "（15）Exports by Selected Countries",
    "imports_by_country_hs": "（16）Imports by Selected Countries",
}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def parse_index(html_path: Path) -> dict:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    out = {k: {} for k in REPORT_KEYS}
    for row in soup.select("table tr"):
        cells = row.find_all("td")
        if len(cells) != 2:
            continue
        title = cells[0].get_text(strip=True)
        for key, prefix in REPORT_KEYS.items():
            if title.startswith(prefix):
                for a in cells[1].find_all("a"):
                    href = a.get("href", "").strip()
                    label = a.get_text(strip=True).rstrip(".")
                    if href and label in MONTHS:
                        out[key][label] = href
                break
    return out


def main():
    result = {}
    for year, fname in [("2024", "index_2024.html"),
                        ("2025", "index_2025.html"),
                        ("2026", "index_2026.html")]:
        path = RAW / fname
        result[year] = parse_index(path)
    out_path = ROOT / "urls.json"
    out_path.write_text(json.dumps(result, indent=2))
    print(f"Wrote {out_path}")
    for year, reports in result.items():
        for key, months in reports.items():
            print(f"  {year} {key}: {len(months)} months")


if __name__ == "__main__":
    main()
