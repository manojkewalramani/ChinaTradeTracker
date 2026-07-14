#!/usr/bin/env python3
"""Parse all raw HTML reports into a single JSON file the website can consume."""
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"

MONTH_NUM = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
             "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


def num(text):
    """Convert '19,203,861' or '-' or '10.4' into float or None."""
    if text is None:
        return None
    s = text.strip().replace(",", "").replace("\xa0", "")
    if not s or s == "-":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def parse_country_report(path: Path):
    """Report (2): country/region totals.

    Columns:
      Country | Total mo | Total YTD | Exports mo | Exports YTD |
      Imports mo | Imports YTD | %chg Total | %chg Exp | %chg Imp
    All money values are US$1,000 (so multiply by 1,000 for USD).
    """
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    rows = soup.select("table tr")
    out = []
    for r in rows:
        cells = r.find_all("td")
        first = clean(cells[0].get_text()) if cells else ""
        if not first or first.endswith(":"):
            continue
        if len(cells) == 10:
            # Standard format: month + YTD pair for each of total/exp/imp
            vals = [num(c.get_text()) for c in cells[1:]]
            if all(v is None for v in vals):
                continue
            out.append({
                "name": first.rstrip(":").rstrip(),
                "total_month": vals[0],
                "total_ytd": vals[1],
                "exports_month": vals[2],
                "exports_ytd": vals[3],
                "imports_month": vals[4],
                "imports_ytd": vals[5],
                "pct_total_yoy": vals[6],
                "pct_exports_yoy": vals[7],
                "pct_imports_yoy": vals[8],
            })
        elif len(cells) == 7:
            # Jan format: only month values (== YTD for the first month)
            vals = [num(c.get_text()) for c in cells[1:]]
            if all(v is None for v in vals):
                continue
            out.append({
                "name": first.rstrip(":").rstrip(),
                "total_month": vals[0],
                "total_ytd": vals[0],
                "exports_month": vals[1],
                "exports_ytd": vals[1],
                "imports_month": vals[2],
                "imports_ytd": vals[2],
                "pct_total_yoy": vals[3],
                "pct_exports_yoy": vals[4],
                "pct_imports_yoy": vals[5],
            })
    return out


def parse_commodity_report(path: Path):
    """Reports (13)/(14): Major commodities.

    Columns:
      Commodity | Qty unit | Qty mo | Value mo | Qty YTD | Value YTD |
      %chg Qty | %chg Value (YoY on YTD).
    """
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    rows = soup.select("table tr")
    out = []
    for r in rows:
        cells = r.find_all("td")
        if len(cells) not in (8, 6):
            continue
        raw_name = cells[0].get_text()
        name = clean(raw_name)
        if not name or name.lower() in {"commodity"}:
            continue
        unit = clean(cells[1].get_text())
        is_category = not raw_name.lstrip(" \t\r\n").startswith("\xa0")
        if len(cells) == 8:
            vals = [num(c.get_text()) for c in cells[2:]]
            if vals[3] is None:
                continue
            row = {
                "qty_month": vals[0],
                "value_month": vals[1],
                "qty_ytd": vals[2],
                "value_ytd": vals[3],
                "pct_qty_yoy": vals[4],
                "pct_value_yoy": vals[5],
            }
        else:  # 6 cells — January layout (only month value, no YTD)
            vals = [num(c.get_text()) for c in cells[2:]]
            if vals[1] is None:
                continue
            row = {
                "qty_month": vals[0],
                "value_month": vals[1],
                "qty_ytd": vals[0],
                "value_ytd": vals[1],
                "pct_qty_yoy": vals[2],
                "pct_value_yoy": vals[3],
            }
        row.update({"name": name, "unit": unit, "is_category": is_category})
        out.append(row)
    return out


# HS Section descriptions (China customs uses Roman numerals).
HS_SECTIONS = {
    "Ⅰ": "Live Animals & Animal Products",
    "Ⅱ": "Vegetable Products",
    "Ⅲ": "Animal & Vegetable Fats",
    "Ⅳ": "Prepared Foodstuffs, Beverages, Tobacco",
    "Ⅴ": "Mineral Products",
    "Ⅵ": "Chemicals & Pharmaceuticals",
    "Ⅶ": "Plastics & Rubber",
    "Ⅷ": "Leather & Furskins",
    "Ⅸ": "Wood Products",
    "Ⅹ": "Pulp, Paper & Paperboard",
    "Ⅺ": "Textiles & Apparel",
    "Ⅻ": "Footwear & Headgear",
    "ⅩⅢ": "Stone, Cement, Ceramics, Glass",
    "ⅩⅣ": "Pearls, Precious Stones & Metals",
    "ⅩⅤ": "Base Metals & Articles Thereof",
    "ⅩⅥ": "Machinery & Electrical Equipment",
    "ⅩⅦ": "Vehicles, Aircraft, Vessels",
    "ⅩⅧ": "Optical, Medical, Photographic Instruments",
    "ⅩⅨ": "Arms & Ammunition",
    "ⅩⅩ": "Miscellaneous Manufactured Articles",
    "ⅩⅪ": "Works of Art & Antiques",
    "ⅩⅫ": "Special Transactions",
}


def parse_country_hs_report(path: Path):
    """Reports (15)/(16): HS Sections/Divisions × countries.

    The header has the country list (one entry per pair of columns: month + YTD).
    Each data row starts with the HS code/identifier; remaining cells are pairs
    of values per country.
    """
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    rows = soup.select("table tr")
    # Find header row with country names (the one with the most <b> entries
    # that aren't single Roman/digit codes).
    country_row = None
    for r in rows:
        cells = r.find_all("td")
        if len(cells) < 30:
            continue
        bolds = [clean(c.get_text()) for c in cells if c.find("b")]
        named = [b for b in bolds if len(b) > 2 and not b.isdigit()]
        if len(named) > 30:
            country_row = r
            countries = [clean(c.get_text()) for c in cells if c.find("b")]
            countries = [c for c in countries if c and c != "Sec. & Div."]
            break
    if country_row is None:
        raise RuntimeError(f"could not find country header row in {path.name}")

    # Now extract data rows: first cell is HS code (Roman numeral section
    # or two-digit chapter); 88 numeric cells follow (44 countries × 2 cols).
    data = {country: {"sections": {}} for country in countries}
    for r in rows:
        cells = r.find_all("td")
        if len(cells) != 89:
            continue
        code_raw = clean(cells[0].get_text())
        if not code_raw or code_raw in {"5", "1to5", "12", "1to12"}:
            continue
        # We only care about section-level rows (Roman numerals) for our UI;
        # division rows are two-digit numbers, which we skip for the country
        # pages because there are too many.
        # But we want TOTAL row too.
        is_section = code_raw == "TOTAL" or any(ch in code_raw for ch in "ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ")
        if not is_section:
            continue
        nums = [num(c.get_text()) for c in cells[1:]]
        for i, country in enumerate(countries):
            mo = nums[i * 2]
            ytd = nums[i * 2 + 1]
            section_label = HS_SECTIONS.get(code_raw, code_raw)
            data[country]["sections"][code_raw] = {
                "label": section_label,
                "month": mo,
                "ytd": ytd,
            }
    return data


def build():
    out = {
        "by_country": {},          # year -> month -> [country rows]
        "exports_commodities": {}, # year -> month -> [commodity rows]
        "imports_commodities": {}, # year -> month -> [commodity rows]
        "exports_by_country_hs": {},  # year -> month -> {country: ...}
        "imports_by_country_hs": {},
        "meta": {
            "hs_sections": HS_SECTIONS,
            "units": "US$1,000 (multiply by 1000 for USD)",
            "asof_year": 2026,
            "asof_month": 5,
        },
    }

    for path in sorted(RAW.glob("*.html")):
        if path.name.startswith("index_"):
            continue
        m = re.match(r"(\d{4})_(country|export_commodities|import_commodities|exports_by_country_hs|imports_by_country_hs)_(\w+)\.html", path.name)
        if not m:
            continue
        year, report, month = m.group(1), m.group(2), m.group(3)
        print(f"parsing {path.name}")
        if report == "country":
            data = parse_country_report(path)
            out["by_country"].setdefault(year, {})[month] = data
        elif report == "export_commodities":
            data = parse_commodity_report(path)
            out["exports_commodities"].setdefault(year, {})[month] = data
        elif report == "import_commodities":
            data = parse_commodity_report(path)
            out["imports_commodities"].setdefault(year, {})[month] = data
        elif report == "exports_by_country_hs":
            data = parse_country_hs_report(path)
            out["exports_by_country_hs"].setdefault(year, {})[month] = data
        elif report == "imports_by_country_hs":
            data = parse_country_hs_report(path)
            out["imports_by_country_hs"].setdefault(year, {})[month] = data

    out_path = ROOT / "data.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\nWrote {out_path} ({out_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    build()
