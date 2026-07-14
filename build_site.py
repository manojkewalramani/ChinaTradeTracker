#!/usr/bin/env python3
"""Generate a single self-contained index.html in site/ with all data inlined.

The page is a hash-routed SPA: home / countries / country/<name> / products.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.load(open(ROOT / "data.json"))
SITE = ROOT / "site"
SITE.mkdir(exist_ok=True)

# Compact the data for the bundle (drop is_category=False detail we won't use,
# but keep the full data — at 2.2MB it's fine for a local file).
data_js = json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>China Trade Tracker — 2024 · 2025 · 2026</title>
<style>
:root {
  --bg: #0f1419;
  --panel: #1a2027;
  --panel-2: #232a33;
  --border: #2d3640;
  --text: #e8eaed;
  --muted: #9aa3ad;
  --accent: #de2910;
  --accent-2: #ffd700;
  --green: #10b981;
  --red: #ef4444;
  --blue: #3b82f6;
  --amber: #f59e0b;
  --shadow: 0 4px 20px rgba(0,0,0,0.4);
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --mono: ui-monospace, SFMono-Regular, "Menlo", Consolas, monospace;
}
* { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  font-size: 15px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--accent-2); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Layout */
.header {
  background: linear-gradient(180deg, #181f27 0%, var(--bg) 100%);
  border-bottom: 1px solid var(--border);
  padding: 18px 32px;
  position: sticky; top: 0; z-index: 10;
  backdrop-filter: blur(8px);
}
.header-inner {
  max-width: 1280px; margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between;
  gap: 24px;
}
.brand {
  font-size: 20px; font-weight: 700;
  letter-spacing: -0.01em;
  display: flex; align-items: center; gap: 12px;
}
.brand-dot {
  width: 28px; height: 28px;
  background: var(--accent);
  border-radius: 50%;
  position: relative;
}
.brand-dot::before, .brand-dot::after {
  content: ""; position: absolute;
  color: var(--accent-2);
  font-size: 10px;
  left: 50%; top: 50%;
  transform: translate(-50%, -55%);
}
.brand-dot::before {
  content: "★";
  font-size: 16px;
  line-height: 1;
}
nav.main-nav {
  display: flex; gap: 4px;
}
nav.main-nav a {
  color: var(--muted);
  padding: 8px 14px;
  border-radius: 6px;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.15s;
}
nav.main-nav a:hover { color: var(--text); background: var(--panel); text-decoration: none; }
nav.main-nav a.active { color: var(--text); background: var(--panel); }

main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 32px;
}

h1 { font-size: 30px; margin: 0 0 8px; font-weight: 700; letter-spacing: -0.02em; }
h2 { font-size: 20px; margin: 32px 0 16px; font-weight: 600; letter-spacing: -0.01em; }
h3 { font-size: 16px; margin: 0 0 12px; font-weight: 600; color: var(--text); }

.subtitle { color: var(--muted); margin: 0 0 24px; font-size: 14px; }

/* Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin: 24px 0 32px;
}
.kpi {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px;
}
.kpi-label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-value { font-size: 26px; font-weight: 700; margin-top: 6px; }
.kpi-detail { color: var(--muted); font-size: 13px; margin-top: 4px; }
.kpi-trend { display: inline-block; margin-left: 8px; font-size: 14px; font-weight: 500; }
.up { color: var(--green); }
.down { color: var(--red); }
.flat { color: var(--muted); }

.card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
}
.card-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 14px;
}
.card-title { font-size: 16px; font-weight: 600; margin: 0; }
.card-hint { color: var(--muted); font-size: 12px; }

/* Tables */
table.data {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
table.data th, table.data td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}
table.data th {
  font-weight: 600;
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  background: var(--panel-2);
}
table.data td.num, table.data th.num {
  text-align: right;
  font-variant-numeric: tabular-nums;
  font-family: var(--mono);
  font-size: 13px;
}
table.data tr:hover td { background: rgba(255,255,255,0.02); }
table.data tr.row-link { cursor: pointer; }
table.data tr.row-total td {
  font-weight: 700;
  background: rgba(222, 41, 16, 0.08);
  border-top: 2px solid var(--border);
}

/* Tabs */
.tabs {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 20px;
}
.tab {
  padding: 10px 16px;
  cursor: pointer;
  color: var(--muted);
  font-size: 14px;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: all 0.15s;
}
.tab:hover { color: var(--text); }
.tab.active { color: var(--text); border-bottom-color: var(--accent); }

/* Country grid */
.country-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 14px;
}
.country-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.15s;
  display: block;
  color: var(--text);
}
.country-card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
  text-decoration: none;
}
.country-card .flag { font-size: 22px; margin-bottom: 8px; }
.country-card .name { font-weight: 600; font-size: 15px; margin-bottom: 4px; }
.country-card .value { font-size: 18px; font-weight: 700; font-family: var(--mono); }
.country-card .trend { font-size: 13px; margin-top: 4px; }

/* Bars */
.bar-chart { margin: 16px 0; }
.bar-row {
  display: grid;
  grid-template-columns: 200px 1fr 100px;
  gap: 12px;
  align-items: center;
  padding: 6px 0;
  font-size: 13px;
}
.bar-row .label { color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bar-row .bar-bg {
  background: var(--panel-2);
  height: 22px;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}
.bar-row .bar-fill {
  background: linear-gradient(90deg, var(--accent) 0%, #ff4d2e 100%);
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s;
}
.bar-row .bar-fill.exp { background: linear-gradient(90deg, var(--blue) 0%, #60a5fa 100%); }
.bar-row .bar-fill.imp { background: linear-gradient(90deg, var(--amber) 0%, #fbbf24 100%); }
.bar-row .value { text-align: right; font-family: var(--mono); font-size: 13px; }

/* Trend chart */
.spark {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 60px;
  margin: 12px 0;
}
.spark .col {
  flex: 1;
  background: var(--blue);
  border-radius: 3px 3px 0 0;
  position: relative;
  min-height: 4px;
}
.spark .col.imp { background: var(--amber); }
.spark .col-label {
  position: absolute;
  bottom: -22px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: var(--muted);
}

/* Two-col layout */
.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
@media (max-width: 900px) {
  .two-col { grid-template-columns: 1fr; }
  nav.main-nav { flex-wrap: wrap; }
  main { padding: 18px; }
}

.pill {
  display: inline-block;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.pill-green { background: rgba(16, 185, 129, 0.15); color: var(--green); }
.pill-red { background: rgba(239, 68, 68, 0.15); color: var(--red); }
.pill-blue { background: rgba(59, 130, 246, 0.15); color: var(--blue); }
.pill-amber { background: rgba(245, 158, 11, 0.15); color: var(--amber); }

.section-divider {
  border: none; border-top: 1px solid var(--border);
  margin: 32px 0;
}

.footer {
  margin-top: 40px;
  padding: 24px 32px;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 13px;
  text-align: center;
}

.note {
  background: rgba(245, 158, 11, 0.08);
  border-left: 3px solid var(--amber);
  padding: 10px 14px;
  margin: 12px 0;
  border-radius: 4px;
  font-size: 13px;
  color: var(--text);
}
.note-muted {
  color: var(--muted);
  font-size: 12px;
  margin-top: 8px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--muted);
  font-size: 13px;
  margin-bottom: 12px;
  cursor: pointer;
}
.back-link:hover { color: var(--text); }

/* Loading */
#app.loading { opacity: 0.4; pointer-events: none; }
</style>
</head>
<body>

<header class="header">
  <div class="header-inner">
    <div class="brand">
      <span class="brand-dot"></span>
      <span>China Trade Tracker</span>
    </div>
    <nav class="main-nav">
      <a href="#/" data-route="home">Overview</a>
      <a href="#/countries" data-route="countries">Countries</a>
      <a href="#/products" data-route="products">Products</a>
      <a href="#/about" data-route="about">About</a>
    </nav>
  </div>
</header>

<main id="app"><div style="text-align:center; padding: 60px; color: var(--muted)">Loading…</div></main>

<div class="footer">
  Source: <a href="http://english.customs.gov.cn/statics/report/monthly.html" target="_blank">General Administration of Customs of China (GACC)</a>.
  All figures in USD. Trade data as of June 2026 (latest publication).
</div>

<script>
const DATA = __DATA__;
const APP = document.getElementById("app");

const TARGET_COUNTRIES = [
  {key: "Germany",        flag: "🇩🇪", region: "EU"},
  {key: "France",         flag: "🇫🇷", region: "EU"},
  {key: "Italy",          flag: "🇮🇹", region: "EU"},
  {key: "United States",  flag: "🇺🇸", region: "North America"},
  {key: "India",          flag: "🇮🇳", region: "Asia"},
  {key: "Japan",          flag: "🇯🇵", region: "Asia"},
  {key: "Russia",         flag: "🇷🇺", region: "Europe"},
  {key: "Pakistan",       flag: "🇵🇰", region: "Asia"},
  {key: "Australia",      flag: "🇦🇺", region: "Oceania"},
  {key: "ASEAN",          flag: "🌏",   region: "ASEAN bloc",
                          composite: false, members: ["Myanmar","Indonesia","Malaysia","Philippines","Singapore","Thailand","Viet Nam"]},
  {key: "GCC",            flag: "🛢️",  region: "Gulf bloc", composite: true,
                          members: ["Saudi Arabia","United Arab Emirates","Oman","Kuwait","Bahrain","Qatar"]},
];

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

// ---------- helpers ----------
function $$(html) {
  const t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstChild;
}

function usd(value, opts={}) {
  // value is in thousands USD. Convert to readable format.
  if (value == null || isNaN(value)) return "—";
  const dollars = value * 1000;
  const abs = Math.abs(dollars);
  if (abs >= 1e12) return (dollars / 1e12).toFixed(opts.dp ?? 2) + "T";
  if (abs >= 1e9)  return "$" + (dollars / 1e9).toFixed(opts.dp ?? 2) + "B";
  if (abs >= 1e6)  return "$" + (dollars / 1e6).toFixed(opts.dp ?? 1) + "M";
  if (abs >= 1e3)  return "$" + (dollars / 1e3).toFixed(0) + "K";
  return "$" + dollars.toFixed(0);
}
function pct(v, opts={}) {
  if (v == null || isNaN(v)) return "—";
  const sign = v > 0 ? "+" : "";
  return sign + v.toFixed(opts.dp ?? 1) + "%";
}
function trendClass(v) {
  if (v == null || isNaN(v)) return "flat";
  if (v > 0.5) return "up";
  if (v < -0.5) return "down";
  return "flat";
}
function trendArrow(v) {
  if (v == null || isNaN(v)) return "·";
  if (v > 0.5) return "↑";
  if (v < -0.5) return "↓";
  return "→";
}

function findRow(rows, name) {
  return rows.find(r => r.name === name) || null;
}

function years() { return Object.keys(DATA.by_country).sort(); }

// Find latest month for 2026
function latest2026() {
  const months = Object.keys(DATA.by_country["2026"] || {});
  // Order by MONTH index
  months.sort((a,b) => MONTHS.indexOf(a) - MONTHS.indexOf(b));
  return months[months.length-1];
}

// Build a series of months for 2026 (full)
function months2026() {
  const months = Object.keys(DATA.by_country["2026"] || {});
  months.sort((a,b) => MONTHS.indexOf(a) - MONTHS.indexOf(b));
  return months;
}

// Aggregate country row across composite members (sum month/ytd values).
function aggregateGCC(rows) {
  const members = ["Saudi Arabia","United Arab Emirates","Oman","Kuwait","Bahrain","Qatar"];
  const found = members.map(m => findRow(rows, m)).filter(Boolean);
  if (!found.length) return null;
  const out = {
    name: "GCC",
    total_month: 0, total_ytd: 0,
    exports_month: 0, exports_ytd: 0,
    imports_month: 0, imports_ytd: 0,
    pct_total_yoy: null, pct_exports_yoy: null, pct_imports_yoy: null,
  };
  for (const k of ["total_month","total_ytd","exports_month","exports_ytd","imports_month","imports_ytd"]) {
    out[k] = found.reduce((s, r) => s + (r[k]||0), 0);
  }
  // Compose YoY% by reconstructing the prior-period sum from each member's
  // own reported YoY (curr / (1 + pct/100) gives prior-period value).
  function composePct(key, pctKey) {
    let curr = 0, prev = 0, valid = 0;
    for (const r of found) {
      const v = r[key];
      const p = r[pctKey];
      if (v == null || p == null) continue;
      curr += v;
      prev += v / (1 + p/100);
      valid++;
    }
    if (!valid || !prev) return null;
    return ((curr - prev) / prev) * 100;
  }
  out.pct_total_yoy   = composePct("total_ytd",   "pct_total_yoy");
  out.pct_exports_yoy = composePct("exports_ytd", "pct_exports_yoy");
  out.pct_imports_yoy = composePct("imports_ytd", "pct_imports_yoy");
  return out;
}

function rowForCountry(rows, key) {
  if (key === "GCC") return aggregateGCC(rows);
  return findRow(rows, key);
}

// Return the row for `key` from the most recent month of `year` that has it,
// plus which month was used. Falls back through months in reverse order.
function latestRowForCountry(year, key) {
  const months = Object.keys(DATA.by_country[year] || {});
  months.sort((a, b) => MONTHS.indexOf(a) - MONTHS.indexOf(b));
  for (let i = months.length - 1; i >= 0; i--) {
    const m = months[i];
    const row = rowForCountry(DATA.by_country[year][m], key);
    if (row && (row.total_month != null || row.total_ytd != null)) {
      return {row, month: m};
    }
  }
  return {row: null, month: null};
}

function computeMoM(series) {
  // series = [{month, value}, ...] sorted by month idx
  return series.map((p, i) => {
    if (i === 0) return {...p, mom: null};
    const prev = series[i-1].value;
    if (!prev) return {...p, mom: null};
    return {...p, mom: ((p.value - prev) / prev) * 100};
  });
}

// ---------- router ----------
function go(route) {
  if (window.location.hash !== route) {
    window.location.hash = route;
  } else {
    render();
  }
}
window.addEventListener("hashchange", render);

function getRoute() {
  const h = window.location.hash.slice(1) || "/";
  return h;
}

function setActiveNav(name) {
  document.querySelectorAll("nav.main-nav a").forEach(a => {
    a.classList.toggle("active", a.dataset.route === name);
  });
}

// ---------- views ----------
function renderHome() {
  setActiveNav("home");
  const t2024 = findRow(DATA.by_country["2024"]["Dec"], "TOTAL");
  const t2025 = findRow(DATA.by_country["2025"]["Dec"], "TOTAL");
  const latestM = latest2026();
  const t2026 = findRow(DATA.by_country["2026"][latestM], "TOTAL");

  const yoy24to25 = t2025.pct_total_yoy;
  const ytdYoY2026 = t2026.pct_total_yoy;
  const exp2026 = t2026.pct_exports_yoy;
  const imp2026 = t2026.pct_imports_yoy;

  // Compute MoM trade total series for 2026
  const monthly2026 = months2026().map(m => {
    const r = findRow(DATA.by_country["2026"][m], "TOTAL");
    return {month: m, total: r.total_month, exports: r.exports_month, imports: r.imports_month};
  });

  // Country cards (target list) — fall back per-country when the newest
  // monthly release doesn't include a country (e.g. Pakistan, GCC members
  // are missing from GACC's June summary table).
  const targetRows2026 = TARGET_COUNTRIES.map(t => {
    const lr = latestRowForCountry("2026", t.key);
    return {...t, row: lr.row, month: lr.month};
  });

  const maxMonth = Math.max(...monthly2026.map(p => p.total));

  const html = `
    <h1>China's Foreign Trade: 2024 — 2026</h1>
    <p class="subtitle">Imports, exports, country breakdowns and top commodities, sourced directly from the General Administration of Customs of China (GACC).</p>

    <div class="kpi-grid">
      <div class="kpi">
        <div class="kpi-label">2024 Total Trade</div>
        <div class="kpi-value">${usd(t2024.total_ytd)}</div>
        <div class="kpi-detail">YoY ${pct(t2024.pct_total_yoy)} <span class="kpi-trend ${trendClass(t2024.pct_total_yoy)}">${trendArrow(t2024.pct_total_yoy)}</span></div>
      </div>
      <div class="kpi">
        <div class="kpi-label">2025 Total Trade</div>
        <div class="kpi-value">${usd(t2025.total_ytd)}</div>
        <div class="kpi-detail">YoY ${pct(yoy24to25)} <span class="kpi-trend ${trendClass(yoy24to25)}">${trendArrow(yoy24to25)}</span></div>
      </div>
      <div class="kpi">
        <div class="kpi-label">2026 YTD (Jan – ${latestM})</div>
        <div class="kpi-value">${usd(t2026.total_ytd)}</div>
        <div class="kpi-detail">YTD YoY ${pct(ytdYoY2026)} <span class="kpi-trend ${trendClass(ytdYoY2026)}">${trendArrow(ytdYoY2026)}</span></div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Latest Month (${latestM} 2026)</div>
        <div class="kpi-value">${usd(t2026.total_month)}</div>
        <div class="kpi-detail">Exports ${usd(t2026.exports_month)} · Imports ${usd(t2026.imports_month)}</div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <h2 class="card-title">2026 monthly trade</h2>
        <span class="card-hint">Total / Exports / Imports per month, USD</span>
      </div>
      ${renderMonthlyBars(monthly2026)}
    </div>

    <h2>Key partners — latest position</h2>
    <p class="subtitle">${latestM} 2026 month value with year-to-date YoY change. Click a country for product detail.</p>
    <div class="country-grid">
      ${targetRows2026.map(t => {
        if (!t.row) return "";
        const yoy = t.row.pct_total_yoy;
        const stale = (t.month && t.month !== latestM);
        const monthTag = stale
          ? `<div style="margin-top:6px"><span class="pill pill-amber" title="Not in GACC's ${latestM} 2026 bulletin">Last updated ${t.month} 2026</span></div>`
          : `<div style="margin-top:6px"><span class="pill pill-green">${latestM} 2026</span></div>`;
        return `
          <a class="country-card" href="#/country/${encodeURIComponent(t.key)}">
            <div class="flag">${t.flag}</div>
            <div class="name">${t.key}</div>
            <div class="value">${usd(t.row.total_month)}</div>
            <div class="trend ${trendClass(yoy)}">YTD YoY ${pct(yoy)} ${trendArrow(yoy)}</div>
            ${monthTag}
          </a>
        `;
      }).join("")}
    </div>

    <h2>Top export & import categories (2026 YTD)</h2>
    <div class="two-col">
      <div class="card">
        <h3>Top exports</h3>
        ${renderCommodityList(DATA.exports_commodities["2026"][latestM], "exports")}
      </div>
      <div class="card">
        <h3>Top imports</h3>
        ${renderCommodityList(DATA.imports_commodities["2026"][latestM], "imports")}
      </div>
    </div>

    <div class="note">
      <b>How to read this site:</b> 2026 figures are year-to-date through ${latestM}. YoY percentages on cards are GACC's reported YTD-vs-YTD changes (cumulative period this year vs same period last year). Click <a href="#/products">Products</a> for biggest items and MoM/YoY ranks, or <a href="#/countries">Countries</a> for full country comparisons.
    </div>
  `;
  APP.innerHTML = html;
}

function renderMonthlyBars(series) {
  const maxV = Math.max(...series.map(s => s.total));
  return `
    <div class="bar-chart">
      ${series.map(s => `
        <div class="bar-row">
          <div class="label">${s.month} 2026</div>
          <div class="bar-bg" title="Total ${usd(s.total)}">
            <div class="bar-fill" style="width: ${(s.total/maxV)*100}%"></div>
          </div>
          <div class="value">${usd(s.total)}</div>
        </div>
        <div class="bar-row" style="margin-top:-6px">
          <div class="label" style="color:var(--muted); font-size:12px">  Exports / Imports</div>
          <div class="bar-bg" style="display:flex">
            <div class="bar-fill exp" style="width: ${(s.exports/maxV)*100}%"></div>
          </div>
          <div class="value" style="color:var(--blue); font-size:12px">${usd(s.exports)}</div>
        </div>
        <div class="bar-row" style="margin-top:-12px; margin-bottom: 8px">
          <div class="label"></div>
          <div class="bar-bg" style="display:flex">
            <div class="bar-fill imp" style="width: ${(s.imports/maxV)*100}%"></div>
          </div>
          <div class="value" style="color:var(--amber); font-size:12px">${usd(s.imports)}</div>
        </div>
      `).join("")}
    </div>
  `;
}

function renderCommodityList(rows, kind, limit=12) {
  // Take top-level categories, sorted by latest YTD value
  const items = rows.filter(r => r.is_category && r.value_ytd != null)
                    .sort((a,b) => b.value_ytd - a.value_ytd)
                    .slice(0, limit);
  const maxV = items[0]?.value_ytd || 1;
  return `
    <div class="bar-chart">
      ${items.map(it => `
        <div class="bar-row">
          <div class="label" title="${it.name}">${it.name}</div>
          <div class="bar-bg" title="${usd(it.value_ytd)}">
            <div class="bar-fill ${kind==='exports'?'exp':'imp'}" style="width: ${(it.value_ytd/maxV)*100}%"></div>
          </div>
          <div class="value">${usd(it.value_ytd)} <span class="${trendClass(it.pct_value_yoy)}" style="font-size:11px">${pct(it.pct_value_yoy)}</span></div>
        </div>
      `).join("")}
    </div>
  `;
}

// ---------- Countries page ----------
function renderCountries() {
  setActiveNav("countries");
  const latestM = latest2026();
  const r24 = DATA.by_country["2024"]["Dec"];
  const r25 = DATA.by_country["2025"]["Dec"];

  // Build rows for target countries + a wider list — per-country fallback for
  // 2026 latest, since the June bulletin only lists ~30 countries.
  const allRows = TARGET_COUNTRIES.map(t => {
    const a = rowForCountry(r24, t.key);
    const b = rowForCountry(r25, t.key);
    const lr = latestRowForCountry("2026", t.key);
    return {t, a, b, c: lr.row, cMonth: lr.month};
  });

  // Full partner list — prefer the newest month's row per country and fall
  // back to earlier months where the newer bulletin didn't include them
  // (GACC's June summary lists only ~30 partners; the May bulletin has ~250).
  const months2026s = months2026();
  const preferred = {};   // country name -> {row, month}
  for (let i = months2026s.length - 1; i >= 0; i--) {
    const m = months2026s[i];
    for (const row of (DATA.by_country["2026"][m] || [])) {
      if (row.name === "TOTAL") continue;
      if (!preferred[row.name]) preferred[row.name] = {row, month: m};
    }
  }
  const newestMonth = months2026s[months2026s.length-1];
  const others = Object.values(preferred)
                    .filter(({row}) => row.total_ytd > 5e6)
                    .sort((a, b) => b.row.total_ytd - a.row.total_ytd);

  const html = `
    <h1>Countries & Regions</h1>
    <p class="subtitle">Total trade in USD with year-on-year change since 2024.</p>

    <div class="card">
      <h3>Tracked partners</h3>
      <table class="data">
        <thead>
          <tr>
            <th>Country / Region</th>
            <th class="num">2024 total</th>
            <th class="num">2025 total</th>
            <th class="num">2025 vs 2024</th>
            <th class="num">2026 YTD (${latestM})</th>
            <th class="num">2026 YTD YoY</th>
          </tr>
        </thead>
        <tbody>
          ${allRows.map(({t, a, b, c, cMonth}) => {
            if (!c) return "";
            const v24 = a?.total_ytd;
            const v25 = b?.total_ytd;
            const v26 = c?.total_ytd;
            const yoy25 = v24 ? ((v25 - v24)/v24)*100 : null;
            const yoy26 = c?.pct_total_yoy;
            const stale = cMonth && cMonth !== latestM;
            const staleBadge = stale
              ? `<span class="pill pill-amber" style="margin-left:8px" title="GACC's ${latestM} 2026 by-country bulletin didn't include ${t.key}. Value below is through ${cMonth} 2026.">Last updated ${cMonth} 2026</span>` : "";
            return `
              <tr class="row-link" onclick="window.location.hash='#/country/${encodeURIComponent(t.key)}'">
                <td>${t.flag} <b>${t.key}</b> <span style="color:var(--muted); font-size:12px">${t.region}</span>${staleBadge}</td>
                <td class="num">${usd(v24)}</td>
                <td class="num">${usd(v25)}</td>
                <td class="num ${trendClass(yoy25)}">${pct(yoy25)}</td>
                <td class="num">${usd(v26)}</td>
                <td class="num ${trendClass(yoy26)}">${pct(yoy26)}</td>
              </tr>
            `;
          }).join("")}
        </tbody>
      </table>
    </div>

    <div class="card">
      <h3>All major partners (2026 YTD &gt; $5B)</h3>
      <p class="card-hint">June 2026 H1 totals where GACC has published them (~30 rows); May 2026 fallback for smaller partners the June summary omits.</p>
      <table class="data">
        <thead>
          <tr>
            <th>#</th>
            <th>Country / Region</th>
            <th class="num">2026 YTD total</th>
            <th class="num">Exports</th>
            <th class="num">Imports</th>
            <th class="num">YTD YoY</th>
            <th>Through</th>
          </tr>
        </thead>
        <tbody>
          ${others.slice(0, 60).map(({row, month}, i) => `
            <tr>
              <td>${i+1}</td>
              <td>${row.name}</td>
              <td class="num">${usd(row.total_ytd)}</td>
              <td class="num">${usd(row.exports_ytd)}</td>
              <td class="num">${usd(row.imports_ytd)}</td>
              <td class="num ${trendClass(row.pct_total_yoy)}">${pct(row.pct_total_yoy)}</td>
              <td>${month === newestMonth
                    ? `<span class="pill pill-green">${month}</span>`
                    : `<span class="pill pill-amber">${month}</span>`}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
  APP.innerHTML = html;
}

// ---------- Country detail ----------
function renderCountry(key) {
  setActiveNav("countries");
  const target = TARGET_COUNTRIES.find(t => t.key === key);
  if (!target) {
    APP.innerHTML = `<p>Country not found. <a href="#/countries">Back</a></p>`;
    return;
  }

  const latestM = latest2026();
  const r24 = DATA.by_country["2024"]["Dec"];
  const r25 = DATA.by_country["2025"]["Dec"];

  const a = rowForCountry(r24, key);
  const b = rowForCountry(r25, key);
  const lr = latestRowForCountry("2026", key);
  const c = lr.row;
  const cMonth = lr.month || latestM;

  // 2026 monthly series
  const monthlyAll = months2026().map(m => {
    const row = rowForCountry(DATA.by_country["2026"][m], key);
    return {month: m, total: row?.total_month, exports: row?.exports_month, imports: row?.imports_month};
  });
  const monthlySeries = computeMoM(monthlyAll.map(p => ({month: p.month, value: p.total})));

  const yoy25 = a?.total_ytd ? ((b.total_ytd - a.total_ytd) / a.total_ytd)*100 : null;

  // HS sections for this country. The (15)/(16) reports lag — take the
  // latest month that actually has an HS breakdown published.
  function latestHSMonth(bucket) {
    const months = Object.keys(bucket || {});
    months.sort((a, b) => MONTHS.indexOf(a) - MONTHS.indexOf(b));
    return months[months.length - 1];
  }
  const expHSMonth = latestHSMonth(DATA.exports_by_country_hs["2026"]);
  const impHSMonth = latestHSMonth(DATA.imports_by_country_hs["2026"]);
  const exportsHS = getCountrySections(DATA.exports_by_country_hs["2026"]?.[expHSMonth], key, target);
  const importsHS = getCountrySections(DATA.imports_by_country_hs["2026"]?.[impHSMonth], key, target);

  const html = `
    <a class="back-link" href="#/countries">← Back to countries</a>
    <h1>${target.flag} ${key}</h1>
    <p class="subtitle">${target.region}${target.members ? " · Aggregate of " + target.members.join(", ") : ""}</p>

    <div class="kpi-grid">
      <div class="kpi">
        <div class="kpi-label">2024 Annual Trade</div>
        <div class="kpi-value">${usd(a?.total_ytd)}</div>
        <div class="kpi-detail">Exp ${usd(a?.exports_ytd)} · Imp ${usd(a?.imports_ytd)}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">2025 Annual Trade</div>
        <div class="kpi-value">${usd(b?.total_ytd)}</div>
        <div class="kpi-detail ${trendClass(yoy25)}">vs 2024: ${pct(yoy25)} ${trendArrow(yoy25)}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">2026 YTD (Jan – ${cMonth})</div>
        <div class="kpi-value">${usd(c?.total_ytd)}</div>
        <div class="kpi-detail ${trendClass(c?.pct_total_yoy)}">YTD YoY: ${pct(c?.pct_total_yoy)} ${trendArrow(c?.pct_total_yoy)}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">${cMonth} 2026${cMonth !== latestM ? ' (' + latestM + ' not published)' : ''}</div>
        <div class="kpi-value">${usd(c?.total_month)}</div>
        <div class="kpi-detail">Exp ${usd(c?.exports_month)} · Imp ${usd(c?.imports_month)}</div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <h2 class="card-title">Monthly trade in 2026</h2>
        <span class="card-hint">Total / month, USD — with MoM change</span>
      </div>
      <table class="data">
        <thead>
          <tr>
            <th>Month</th>
            <th class="num">Total</th>
            <th class="num">Exports</th>
            <th class="num">Imports</th>
            <th class="num">MoM Δ (total)</th>
          </tr>
        </thead>
        <tbody>
          ${monthlyAll.map((m, i) => `
            <tr>
              <td>${m.month}</td>
              <td class="num">${usd(m.total)}</td>
              <td class="num">${usd(m.exports)}</td>
              <td class="num">${usd(m.imports)}</td>
              <td class="num ${trendClass(monthlySeries[i].mom)}">${pct(monthlySeries[i].mom)}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>

    <div class="two-col">
      <div class="card">
        <h3>Top categories China <span style="color: var(--blue)">EXPORTS</span> to ${key}</h3>
        <p class="card-hint" style="margin: 0 0 8px">HS Sections — 2026 YTD through ${expHSMonth || latestM}</p>
        ${exportsHS ? renderHSBars(exportsHS, "exp") : `<p class="card-hint">No HS-section detail available for ${key}.</p>`}
      </div>
      <div class="card">
        <h3>Top categories China <span style="color: var(--amber)">IMPORTS</span> from ${key}</h3>
        <p class="card-hint" style="margin: 0 0 8px">HS Sections — 2026 YTD through ${impHSMonth || latestM}</p>
        ${importsHS ? renderHSBars(importsHS, "imp") : `<p class="card-hint">No HS-section detail available for ${key}.</p>`}
      </div>
    </div>

    <div class="note-muted">
      Units: HS Section labels follow the WCO Harmonized System. Values are USD year-to-date, ranked by 2026 YTD. ${target.composite ? `Aggregate sums values for available members (${target.members.join(", ")}).` : ""}
    </div>
  `;
  APP.innerHTML = html;
}

function getCountrySections(snapshot, key, target) {
  if (!snapshot) return null;
  if (key === "GCC" || target?.composite) {
    // Aggregate available members
    const members = target.members.filter(m => snapshot[m]);
    if (!members.length) return null;
    const combined = {};
    for (const m of members) {
      const secs = snapshot[m]?.sections || {};
      for (const [code, val] of Object.entries(secs)) {
        if (code === "TOTAL") continue;
        if (!combined[code]) combined[code] = {label: val.label, month: 0, ytd: 0};
        combined[code].month += val.month || 0;
        combined[code].ytd += val.ytd || 0;
      }
    }
    return Object.entries(combined).map(([code, v]) => ({code, ...v}))
              .filter(x => x.ytd > 0)
              .sort((a,b) => b.ytd - a.ytd);
  }
  if (key === "ASEAN") {
    // ASEAN isn't broken out per-country in the HS report; sum its listed members
    const members = ["Myanmar","Indonesia","Malaysia","Philippines","Singapore","Thailand","Viet Nam"];
    const combined = {};
    for (const m of members) {
      const secs = snapshot[m]?.sections || {};
      for (const [code, val] of Object.entries(secs)) {
        if (code === "TOTAL") continue;
        if (!combined[code]) combined[code] = {label: val.label, month: 0, ytd: 0};
        combined[code].month += val.month || 0;
        combined[code].ytd += val.ytd || 0;
      }
    }
    return Object.entries(combined).map(([code, v]) => ({code, ...v}))
              .filter(x => x.ytd > 0)
              .sort((a,b) => b.ytd - a.ytd);
  }
  const secs = snapshot[key]?.sections;
  if (!secs) return null;
  return Object.entries(secs).filter(([code]) => code !== "TOTAL")
          .map(([code, v]) => ({code, label: v.label, month: v.month, ytd: v.ytd}))
          .filter(x => x.ytd > 0)
          .sort((a,b) => b.ytd - a.ytd);
}

function renderHSBars(items, kind) {
  const top = items.slice(0, 10);
  const maxV = top[0]?.ytd || 1;
  return `
    <div class="bar-chart">
      ${top.map(it => `
        <div class="bar-row">
          <div class="label" title="${it.label}">${it.label}</div>
          <div class="bar-bg">
            <div class="bar-fill ${kind}" style="width: ${(it.ytd/maxV)*100}%"></div>
          </div>
          <div class="value">${usd(it.ytd)}</div>
        </div>
      `).join("")}
    </div>
  `;
}

// ---------- Products page ----------
let productTab = "absolute"; // or "mom2026" or "yoy"
let productKind = "exports"; // or "imports"

function renderProducts() {
  setActiveNav("products");
  const latestM = latest2026();

  const html = `
    <h1>Top imports & exports</h1>
    <p class="subtitle">From GACC's "Major Commodities" tables. Filter between absolute value, 2026 month-on-month change, and year-on-year since 2024.</p>

    <div class="card">
      <div class="tabs" id="tabs-kind">
        <div class="tab ${productKind==='exports'?'active':''}" data-kind="exports">Exports</div>
        <div class="tab ${productKind==='imports'?'active':''}" data-kind="imports">Imports</div>
      </div>
      <div class="tabs" id="tabs-mode" style="margin-top:-12px">
        <div class="tab ${productTab==='absolute'?'active':''}" data-mode="absolute">Absolute value (2026 YTD)</div>
        <div class="tab ${productTab==='mom2026'?'active':''}" data-mode="mom2026">% MoM 2026</div>
        <div class="tab ${productTab==='yoy'?'active':''}" data-mode="yoy">% YoY since 2024</div>
      </div>
      <div id="prod-table"></div>
    </div>
  `;
  APP.innerHTML = html;

  document.querySelectorAll("#tabs-kind .tab").forEach(el => {
    el.onclick = () => { productKind = el.dataset.kind; renderProducts(); };
  });
  document.querySelectorAll("#tabs-mode .tab").forEach(el => {
    el.onclick = () => { productTab = el.dataset.mode; renderProducts(); };
  });

  document.getElementById("prod-table").innerHTML = renderProductTable();
}

function renderProductTable() {
  const latestM = latest2026();
  const set = productKind === "exports" ? DATA.exports_commodities : DATA.imports_commodities;
  const rows2026 = set["2026"][latestM];
  const rows2025 = set["2025"]["Dec"];
  const rows2024 = set["2024"]["Dec"];

  if (productTab === "absolute") {
    const items = rows2026
      .filter(r => r.value_ytd != null)
      .sort((a,b) => b.value_ytd - a.value_ytd)
      .slice(0, 40);
    return `
      <table class="data">
        <thead>
          <tr>
            <th>#</th>
            <th>Commodity</th>
            <th>Type</th>
            <th class="num">2026 YTD value</th>
            <th class="num">${latestM} 2026</th>
            <th class="num">YoY % (YTD)</th>
          </tr>
        </thead>
        <tbody>
          ${items.map((r, i) => `
            <tr>
              <td>${i+1}</td>
              <td>${r.name}</td>
              <td>${r.is_category ? '<span class="pill pill-blue">Category</span>' : '<span class="pill pill-amber">Item</span>'}</td>
              <td class="num">${usd(r.value_ytd)}</td>
              <td class="num">${usd(r.value_month)}</td>
              <td class="num ${trendClass(r.pct_value_yoy)}">${pct(r.pct_value_yoy)}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  }

  if (productTab === "mom2026") {
    // For each commodity, compute MoM from Jan→May 2026
    const months = months2026();
    // Build map: name -> [{m, val}]
    const map = new Map();
    for (const m of months) {
      const list = set["2026"][m] || [];
      for (const r of list) {
        if (r.value_month == null) continue;
        if (!map.has(r.name)) map.set(r.name, {name: r.name, is_category: r.is_category, series: {}});
        map.get(r.name).series[m] = r.value_month;
      }
    }
    // Compute latest MoM and average MoM
    const items = [];
    for (const v of map.values()) {
      const vals = months.map(m => v.series[m]).filter(x => x != null);
      if (vals.length < 2) continue;
      const last = v.series[months[months.length-1]];
      const prev = v.series[months[months.length-2]];
      if (!last || !prev) continue;
      const mom = ((last - prev) / prev) * 100;
      // Average MoM across all available pairs
      let pairs = 0, sum = 0;
      for (let i = 1; i < months.length; i++) {
        const a = v.series[months[i-1]], b = v.series[months[i]];
        if (a && b) { sum += ((b - a)/a)*100; pairs++; }
      }
      const avgMoM = pairs ? sum / pairs : null;
      items.push({...v, mom_latest: mom, avg_mom: avgMoM, latest_value: last});
    }
    items.sort((a,b) => Math.abs(b.mom_latest) - Math.abs(a.mom_latest));
    const top = items.slice(0, 40);
    return `
      <p class="card-hint">Sorted by largest absolute MoM change in latest month (${months[months.length-1]} 2026 vs ${months[months.length-2]} 2026).</p>
      <table class="data">
        <thead>
          <tr>
            <th>#</th>
            <th>Commodity</th>
            <th class="num">Last month value</th>
            <th class="num">Latest MoM Δ</th>
            <th class="num">Avg MoM Δ (2026)</th>
          </tr>
        </thead>
        <tbody>
          ${top.map((r, i) => `
            <tr>
              <td>${i+1}</td>
              <td>${r.name}</td>
              <td class="num">${usd(r.latest_value)}</td>
              <td class="num ${trendClass(r.mom_latest)}">${pct(r.mom_latest)} ${trendArrow(r.mom_latest)}</td>
              <td class="num ${trendClass(r.avg_mom)}">${pct(r.avg_mom)}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  }

  // yoy since 2024
  const map24 = new Map(rows2024.map(r => [r.name, r]));
  const map25 = new Map(rows2025.map(r => [r.name, r]));
  const items = [];
  for (const r of rows2026) {
    if (r.value_ytd == null) continue;
    const r25 = map25.get(r.name);
    const r24 = map24.get(r.name);
    // 2025 vs 2024 — use full year YTD values
    const yoy25 = (r24 && r24.value_ytd) ? ((r25.value_ytd - r24.value_ytd) / r24.value_ytd)*100 : null;
    // 2026 vs 2025 same-period — GACC's pct already gives us this (YTD vs YTD)
    const yoy26 = r.pct_value_yoy;
    // total since 2024 — 2026 YTD annualized vs 2024
    const annualized = r.value_ytd * (12 / months2026().length);
    const yoy26_vs_24 = (r24 && r24.value_ytd) ? ((annualized - r24.value_ytd) / r24.value_ytd) * 100 : null;
    items.push({
      name: r.name,
      is_category: r.is_category,
      v24: r24?.value_ytd,
      v25: r25?.value_ytd,
      v26ytd: r.value_ytd,
      yoy25, yoy26, annualized, yoy26_vs_24,
    });
  }
  items.sort((a,b) => (b.v26ytd||0) - (a.v26ytd||0));
  const top = items.slice(0, 40);
  return `
    <p class="card-hint">2024 and 2025 are annual totals; 2026 column is YTD through latest month, with YoY vs same-period 2025 (GACC). "vs 2024 (ann.)" annualizes the 2026 YTD pace and compares it to the 2024 full-year total.</p>
    <table class="data">
      <thead>
        <tr>
          <th>Commodity</th>
          <th class="num">2024</th>
          <th class="num">2025</th>
          <th class="num">'24→'25</th>
          <th class="num">2026 YTD</th>
          <th class="num">2026 YTD YoY</th>
          <th class="num">2026 ann. vs '24</th>
        </tr>
      </thead>
      <tbody>
        ${top.map(r => `
          <tr>
            <td>${r.name}</td>
            <td class="num">${usd(r.v24)}</td>
            <td class="num">${usd(r.v25)}</td>
            <td class="num ${trendClass(r.yoy25)}">${pct(r.yoy25)}</td>
            <td class="num">${usd(r.v26ytd)}</td>
            <td class="num ${trendClass(r.yoy26)}">${pct(r.yoy26)}</td>
            <td class="num ${trendClass(r.yoy26_vs_24)}">${pct(r.yoy26_vs_24)}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

// ---------- About ----------
function renderAbout() {
  setActiveNav("about");
  APP.innerHTML = `
    <h1>About this tracker</h1>
    <p class="subtitle">Methodology, sources, and known limits.</p>

    <div class="card">
      <h3>Data source</h3>
      <p>All figures come from the <a href="http://english.customs.gov.cn/statics/report/monthly.html" target="_blank">General Administration of Customs of China (GACC) — Monthly Bulletin</a>. The bulletin publishes 18 monthly tables in HTML format; this tracker pulls from five of them:</p>
      <ul>
        <li><b>(2) Imports and Exports by Country/Region</b> — country trade totals.</li>
        <li><b>(13) Major Export Commodities</b> — broad categories and named items.</li>
        <li><b>(14) Major Import Commodities</b> — same, for imports.</li>
        <li><b>(15) / (16) Exports/Imports by Selected Countries × HS Divisions</b> — per-country product breakdown at the HS Section level.</li>
      </ul>
    </div>

    <div class="card">
      <h3>Coverage</h3>
      <ul>
        <li><b>2024</b>: full-year annual figures (cumulative as published in Dec 2024).</li>
        <li><b>2025</b>: full-year annual figures.</li>
        <li><b>2026</b>: Jan – ${latest2026()} (latest GACC release).</li>
      </ul>
      <p>GACC did not publish Sep/Oct 2024 monthly tables; this doesn't affect annual totals.</p>
    </div>

    <div class="card">
      <h3>What the percentages mean</h3>
      <ul>
        <li><b>YoY % on country/commodity rows</b> comes directly from GACC and is the year-to-date comparison vs the same period a year earlier (e.g., Jan-May 2026 vs Jan-May 2025).</li>
        <li><b>MoM Δ</b> is computed from successive months of 2026 data.</li>
        <li><b>2026 ann. vs '24</b> annualizes the 2026 YTD pace (multiplies by 12 / months elapsed) and compares to 2024 full year. It's a directional indicator, not a forecast.</li>
      </ul>
    </div>

    <div class="card">
      <h3>Country groupings</h3>
      <p><b>ASEAN</b> figures in the country table come directly from GACC's aggregate row. For HS section breakdowns, ASEAN is approximated by summing the 7 ASEAN members GACC lists separately (Myanmar, Indonesia, Malaysia, Philippines, Singapore, Thailand, Viet Nam); Brunei, Cambodia, Laos and Timor-Leste are not in the per-country table.</p>
      <p><b>GCC</b> is computed by summing the six GCC member states present in GACC's report: Saudi Arabia, UAE, Oman, Kuwait, Bahrain, Qatar.</p>
    </div>

    <div class="card">
      <h3>Units</h3>
      <p>All money values originate as <code>US$1,000</code> (thousands of USD) in the source tables. The site multiplies by 1,000 and formats in M / B / T USD for display.</p>
    </div>
  `;
}

// ---------- Render dispatch ----------
function render() {
  APP.classList.add("loading");
  setTimeout(() => {
    const r = getRoute();
    if (r === "/" || r === "" || r === "/home") return finishRender(renderHome);
    if (r === "/countries") return finishRender(renderCountries);
    if (r === "/products") return finishRender(renderProducts);
    if (r === "/about") return finishRender(renderAbout);
    if (r.startsWith("/country/")) {
      const name = decodeURIComponent(r.slice("/country/".length));
      return finishRender(() => renderCountry(name));
    }
    finishRender(renderHome);
  }, 0);
}
function finishRender(fn) {
  try { fn(); }
  catch (e) {
    console.error(e);
    APP.innerHTML = `<div class="note">Render error: ${e.message}</div>`;
  }
  APP.classList.remove("loading");
  window.scrollTo(0, 0);
}

render();
</script>

</body>
</html>
"""

out = HTML.replace("__DATA__", data_js)
(SITE / "index.html").write_text(out, encoding="utf-8")
print(f"Wrote {SITE / 'index.html'} ({len(out):,} bytes)")
