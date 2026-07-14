#!/usr/bin/env python3
"""Merge June 2026 data (from XLS/XLSX files) into data.json.

Sources:
  raw/june2026_country_EN.xlsx  — Report (4), by country, June 2026 (EN)
  raw/june2026_A.xls            — Report (6), major imports, June 2026 (ZH)
  raw/june2026_B.xls            — Report (5), major exports, June 2026 (ZH)

Values in the new files are in MILLION USD; existing data.json is in
THOUSAND USD, so we multiply new values by 1000 to keep units consistent.
"""
import json
from pathlib import Path
import openpyxl
import xlrd

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"

# --- Country name normalization (map EN file → keys used in data.json) ---
COUNTRY_MAP = {
    "Grand Total": "TOTAL",
    "European Union": "EU",
    "of which: Germany": "Germany",
    "Netherlands": "Netherlands",
    "France": "France",
    "Italy": "Italy",
    "United States": "United States",
    "Association of Southeast Asian Nations (ASEAN)": "ASEAN",
    "of which: Vietnam": "Viet Nam",
    "Malaysia": "Malaysia",
    "Thailand": "Thailand",
    "Singapore": "Singapore",
    "Indonesia": "Indonesia",
    "Philippines": "Philippines",
    "Japan": "Japan",
    "Hong Kong, China": "Hong Kong, China",
    "Republic of Korea": "Republic of Korea",
    "Taiwan, China": "Taiwan, China",
    "Australia": "Australia",
    "Russia": "Russia",
    "India": "India",
    "United Kingdom": "United Kingdom",
    "Canada": "Canada",
    "New Zealand": "New Zealand",
    "Latin America": "Latin America",
    "of which: Brazil": "Brazil",
    "Africa": "Africa",
    "of which: South Africa": "South Africa",
    "Member States of the Regional Comprehensive Economic Partnership (RCEP)": "RCEP",
    "Countries and Regions Participating in the Belt and Road Initiative": "BRI",
}

# --- Chinese commodity → English name (matched to the English May 2026 report) ---
COMMODITY_MAP = {
    # Imports (from Report 6)
    "农产品*": "Agriculture products*",
    "肉类（包括杂碎）": "Meat (including meat offal)",
    "干鲜瓜果及坚果": "Fresh or dried fruit and nuts",
    "粮食": "Grain food",
    "大豆": "Soybeans",
    "食用植物油": "Edible vegetable oil",
    "铁矿砂及其精矿": "Iron ores and concentrates",
    "铜矿砂及其精矿": "Copper ores and concentrates",
    "煤及褐煤": "Coal and lignite",
    "原油": "Crude oil",
    "成品油": "Refined oil products",
    "天然气": "Natural gas",
    "稀土": "Rare earths",
    "医药材及药品": "Medicinal materials and pharmaceuticals",
    "肥料": "Fertilizers",
    "美容化妆品及洗护用品": "Cosmetics and personal care products",
    "初级形状的塑料": "Plastics in primary forms",
    "天然及合成橡胶（包括胶乳）": "Natural and synthetic rubber",
    "原木及锯材": "Logs and sawn timber",
    "纸浆": "Wood pulp",
    "纺织纱线、织物及其制品": "Textile yarn, fabrics and articles thereof",
    "钢材": "Steel products",
    "未锻轧铜及铜材": "Unwrought copper and copper products",
    "机电产品*": "Mechanical and electrical products *",
    "机床": "Machine tools",
    "自动数据处理设备及其零部件": "Automatic data processing machines and parts thereof",
    "二极管及类似半导体器件": "Diodes and similar semiconductor devices",
    "集成电路": "Integrated circuits",
    "汽车(包括底盘）": "Motor vehicles (including chassis)",
    "汽车零配件": "Auto parts and components",
    "空载重量超过2吨的飞机": "Aircraft with empty weight exceeding 2 tons",
    "液晶平板显示模组": "LCD flat panel display modules",
    "医疗仪器及器械": "Medical instruments and equipment",
    "高新技术产品*": "Hi-tech products*",
    # Exports (from Report 5) — additions
    "水产品": "Aquatic products",
    "塑料制品": "Plastic articles",
    "箱包及类似容器": "Luggage and similar containers",
    "服装及衣着附件": "Garments and clothing accessories",
    "鞋靴": "Footwear",
    "陶瓷产品": "Ceramic products",
    "医药品": "Pharmaceutical products",
    "未锻轧铝及铝材": "Unwrought aluminium and aluminium products",
    "家具及其零件": "Furniture and parts thereof",
    "玩具": "Toys",
    "通用机械设备": "General machinery equipment",
    "手机": "Mobile phones",
    "家用电器": "Household appliances",
    "音视频设备及其零件": "Audio and video equipment",
    "汽车（包括底盘）": "Motor vehicles (including chassis)",
    "船舶": "Ships",
    "灯具、照明装置及其零件": "Lamps and lighting equipment",
}


def num(v):
    """Coerce spreadsheet cell to float, or None."""
    if v is None or v == "" or v == "-":
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


# ---------- COUNTRY (EN xlsx) ----------
def parse_country():
    wb = openpyxl.load_workbook(RAW / "june2026_country_EN.xlsx", data_only=True)
    ws = wb.active
    out = []
    for row in ws.iter_rows(min_row=5, values_only=True):
        # row layout: (_, name, imp_exp_month, imp_exp_ytd, exp_month, exp_ytd,
        #              imp_month, imp_ytd, pct_total, pct_exp, pct_imp)
        _, name_raw, tm, ty, em, ey, im, iy, pt, pe, pi = row[:11]
        if not name_raw or not isinstance(name_raw, str):
            continue
        name_raw = name_raw.strip()
        if name_raw.startswith("Notes"):
            continue
        # Map (strip "of which: " prefix already covered by COUNTRY_MAP)
        name = COUNTRY_MAP.get(name_raw)
        if name is None:
            # For names like "    of which: X" that we haven't mapped, skip.
            # Also skip anything we don't recognise so we don't corrupt data.
            continue
        # Values are in millions USD → convert to thousands
        def mult(x):
            v = num(x)
            return v * 1000 if v is not None else None
        out.append({
            "name": name,
            "total_month": mult(tm),
            "total_ytd": mult(ty),
            "exports_month": mult(em),
            "exports_ytd": mult(ey),
            "imports_month": mult(im),
            "imports_ytd": mult(iy),
            "pct_total_yoy": num(pt),
            "pct_exports_yoy": num(pe),
            "pct_imports_yoy": num(pi),
        })
    return out


# ---------- COMMODITIES (ZH xls) ----------
def parse_commodities(path: Path):
    wb = xlrd.open_workbook(str(path))
    ws = wb.sheet_by_index(0)
    out = []
    unknown = []
    # Data rows start at row 5 (rows 0-4 are titles/headers)
    for i in range(5, ws.nrows):
        row = [ws.cell_value(i, j) for j in range(ws.ncols)]
        # row: [_, name, unit, jun_qty, jun_val, ytd_qty, ytd_val,
        #       prev_qty, prev_val, pct_qty, pct_val]
        name_raw = row[1]
        if not name_raw or not isinstance(name_raw, str):
            continue
        if name_raw.startswith("注") or name_raw.startswith("2026年") or "商品名称" in name_raw:
            continue
        # Detect category (top-level, not indented)
        indented = name_raw.startswith("    ") or name_raw.startswith("　")
        clean_name = name_raw.strip().replace("\xa0", "")
        english = COMMODITY_MAP.get(clean_name)
        if not english:
            unknown.append(clean_name)
            continue
        unit = str(row[2]).strip() if row[2] else ""
        def mult(x):
            v = num(x)
            return v * 1000 if v is not None else None
        # For "-" quantity cells, num() returns None
        out.append({
            "name": english,
            "unit": unit,
            "qty_month": num(row[3]),
            "value_month": mult(row[4]),
            "qty_ytd": num(row[5]),
            "value_ytd": mult(row[6]),
            "prev_qty": num(row[7]),           # NEW: 2025 same-period qty
            "prev_value": mult(row[8]),        # NEW: 2025 same-period value
            "pct_qty_yoy": num(row[9]),
            "pct_value_yoy": num(row[10]),
            "is_category": not indented,
        })
    if unknown:
        print(f"  UNMAPPED COMMODITIES in {path.name}: {unknown}")
    return out


def main():
    print("Loading existing data.json…")
    data_path = ROOT / "data.json"
    data = json.load(open(data_path))

    print("Parsing June 2026 country file…")
    country = parse_country()
    print(f"  parsed {len(country)} country rows")

    print("Parsing June 2026 export commodities…")
    exports = parse_commodities(RAW / "june2026_B.xls")
    print(f"  parsed {len(exports)} export rows")

    print("Parsing June 2026 import commodities…")
    imports = parse_commodities(RAW / "june2026_A.xls")
    print(f"  parsed {len(imports)} import rows")

    # Insert into data structure
    data["by_country"].setdefault("2026", {})["Jun"] = country
    data["exports_commodities"].setdefault("2026", {})["Jun"] = exports
    data["imports_commodities"].setdefault("2026", {})["Jun"] = imports

    # Update meta
    data["meta"]["asof_year"] = 2026
    data["meta"]["asof_month"] = 6

    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"\nUpdated {data_path} ({data_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
