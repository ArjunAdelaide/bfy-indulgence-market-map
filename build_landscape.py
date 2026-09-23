"""
Better-for-You Indulgence: clickable market map (the main page).

Reads data/companies.json and emits docs/index.html: a landscape grid of the six
consumer need-states, split US / Australia, where every company is a tile that
opens an investor dossier. Dossiers deep-link via the URL hash (e.g. /#noon).
Also has a sortable table view and the one-page thesis.

    python3 build_landscape.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "companies.json"
SPACE_SRC = ROOT / "build_map.py"
OUT = ROOT / "docs" / "index.html"
SITE = "https://arjunadelaide.github.io/bfy-indulgence-market-map/"
MEMO = "BFY-Indulgence-Memo-Arjun-Kulshrestha.pdf"
REPO = "https://github.com/ArjunAdelaide/bfy-indulgence-market-map"


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def thesis_sections() -> list[dict]:
    """Reuse the thesis copy that lives in the space-view template, so there is one source."""
    src = SPACE_SRC.read_text()
    block = src.split("<h2>The 1-Page Thesis</h2>", 1)[1].split('<div class="overlay" id="ov-howto">', 1)[0]
    pairs = re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", block, re.S)
    return [{"h": h.strip(), "p": p.strip()} for h, p in pairs]


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>__TITLE__: Market Map</title>
<meta name="description" content="__DESC__">
<meta property="og:title" content="__TITLE__: a US + Australia market map">
<meta property="og:description" content="__DESC__">
<meta property="og:type" content="website">
<meta property="og:url" content="__SITE__">
<meta name="theme-color" content="#070b16">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    color-scheme: dark;
    --bg: #070b16;
    --panel: #0d1426;
    --panel-2: #111a31;
    --line: #1f2b4d;
    --line-2: #2a3963;
    --text: #e8ecf7;
    --muted: #93a0c2;
    --faint: #5d6a8f;
    --accent: #7aa2ff;
    --good: #43d9a3;
    --warn: #ffb547;
    --sans: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
    --mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace;
    --radius: 10px;
  }
  * { box-sizing: border-box; }
  html { -webkit-text-size-adjust: 100%; }
  body { margin: 0; background: var(--bg); color: var(--text); font: 15px/1.55 var(--sans); }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  button { font: inherit; color: inherit; }
  .wrap { max-width: 1320px; margin: 0 auto; padding: 0 24px; }
  .kicker { font: 500 11px/1.4 var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }

  /* ---------- header ---------- */
  header.top { border-bottom: 1px solid var(--line); background: rgba(7,11,22,.85); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 30; }
  .top-in { display: flex; align-items: center; justify-content: space-between; gap: 16px; min-height: 56px; }
  .brand { font: 600 13px var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--text); white-space: nowrap; }
  .brand span { color: var(--faint); }
  nav.links { display: flex; gap: 18px; flex-wrap: wrap; justify-content: flex-end; }
  nav.links a { white-space: nowrap; font: 500 12px var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
  nav.links a:hover { color: var(--text); text-decoration: none; }

  .hero { padding: 40px 0 22px; }
  .hero h1 { font-size: clamp(28px, 4vw, 44px); line-height: 1.1; margin: 10px 0 12px; letter-spacing: -.02em; font-weight: 700; }
  .hero p.lede { max-width: 760px; color: var(--muted); font-size: 16px; margin: 0; }
  .stats { display: flex; flex-wrap: wrap; gap: 10px 28px; margin-top: 22px; }
  .stat b { display: block; font: 600 22px var(--sans); color: var(--text); }
  .stat span { font: 500 11px var(--mono); letter-spacing: .1em; text-transform: uppercase; color: var(--faint); }

  /* ---------- controls ---------- */
  .controls { display: flex; flex-wrap: wrap; gap: 10px 14px; align-items: center; padding: 14px 0 18px; border-top: 1px solid var(--line); }
  .seg { display: inline-flex; border: 1px solid var(--line-2); border-radius: 8px; overflow: hidden; }
  .seg button { white-space: nowrap; background: none; border: 0; padding: 7px 12px; font: 500 12px var(--mono); letter-spacing: .04em; color: var(--muted); cursor: pointer; border-right: 1px solid var(--line-2); }
  .seg button:last-child { border-right: 0; }
  .seg button[aria-pressed="true"] { background: var(--panel-2); color: var(--text); }
  .seg button:hover { color: var(--text); }
  .search { flex: 1 1 200px; max-width: 320px; background: var(--panel); border: 1px solid var(--line-2); border-radius: 8px; padding: 7px 12px; color: var(--text); font: 14px var(--sans); }
  .search::placeholder { color: var(--faint); }
  .count { margin-left: auto; font: 500 12px var(--mono); color: var(--faint); }

  /* ---------- the map ---------- */
  .map { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; padding-bottom: 20px; }
  .seg-card { background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; display: flex; flex-direction: column; }
  .seg-head { all: unset; cursor: pointer; display: block; padding: 14px 16px 12px; border-top: 3px solid var(--c); background: linear-gradient(180deg, color-mix(in srgb, var(--c) 10%, transparent), transparent); }
  .seg-head:hover .seg-name, .seg-head:focus-visible .seg-name { text-decoration: underline; text-decoration-color: var(--c); text-underline-offset: 3px; }
  .seg-head:focus-visible { outline: 2px solid var(--c); outline-offset: -2px; }
  .seg-num { font: 600 11px var(--mono); letter-spacing: .14em; color: var(--c); }
  .seg-name { font-weight: 700; font-size: 17px; margin: 2px 0 4px; }
  .seg-need { color: var(--muted); font-size: 13px; font-style: italic; margin: 0; }
  .seg-meta { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
  .pill { font: 500 10.5px var(--mono); letter-spacing: .06em; text-transform: uppercase; padding: 3px 7px; border-radius: 999px; border: 1px solid var(--line-2); color: var(--muted); white-space: nowrap; }
  .geo-row { padding: 10px 16px 14px; border-top: 1px solid var(--line); }
  .geo-row:first-of-type { border-top: 0; }
  .geo-label { font: 500 10.5px var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--faint); margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
  .tiles { display: flex; flex-wrap: wrap; gap: 8px; }
  .tile { position: relative; cursor: pointer; background: var(--panel-2); border: 1px solid var(--line-2); border-radius: 8px; padding: 8px 10px 8px 10px; min-width: 104px; max-width: 100%; text-align: left; transition: border-color .15s, transform .15s, opacity .2s; }
  .tile:hover, .tile:focus-visible { border-color: var(--c); transform: translateY(-1px); outline: none; }
  .tile .t-name { display: block; font-weight: 600; font-size: 14px; line-height: 1.25; white-space: nowrap; }
  .tile .t-sub { display: flex; align-items: center; gap: 7px; margin-top: 5px; }
  .bars { display: inline-flex; gap: 2px; }
  .bars i { width: 4px; height: 9px; border-radius: 1px; background: var(--line-2); }
  .bars i.on { background: var(--c); }
  .badge { font: 600 9.5px var(--mono); letter-spacing: .08em; text-transform: uppercase; padding: 1px 5px; border-radius: 4px; }
  .badge.breakout { color: #06140e; background: var(--good); }
  .badge.exited { color: var(--muted); border: 1px solid var(--line-2); }
  .tile.dim { opacity: .18; }
  .tile.hit { border-color: var(--c); box-shadow: 0 0 0 1px var(--c); }
  .empty-row { color: var(--faint); font-size: 12px; font-style: italic; }
  .legend { display: flex; flex-wrap: wrap; gap: 8px 22px; padding: 4px 0 30px; color: var(--faint); font: 500 11px var(--mono); letter-spacing: .05em; }
  .legend .bars i.on { background: var(--muted); }
  .legend span { display: inline-flex; align-items: center; gap: 7px; }

  /* ---------- table ---------- */
  .table-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: var(--radius); margin-bottom: 30px; }
  table { width: 100%; border-collapse: collapse; font-size: 13.5px; min-width: 820px; }
  th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--line); vertical-align: top; }
  th { font: 500 11px var(--mono); letter-spacing: .1em; text-transform: uppercase; color: var(--muted); background: var(--panel); position: sticky; top: 0; cursor: pointer; user-select: none; white-space: nowrap; }
  th[aria-sort="ascending"]::after { content: " ↑"; } th[aria-sort="descending"]::after { content: " ↓"; }
  tbody tr { cursor: pointer; }
  tbody tr:hover { background: var(--panel); }
  td.nm { font-weight: 600; white-space: nowrap; }
  td .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--c); margin-right: 7px; }
  td.sig { color: var(--muted); max-width: 460px; }

  /* ---------- thesis ---------- */
  section.block { padding: 34px 0; border-top: 1px solid var(--line); }
  section.block h2 { font-size: 24px; margin: 8px 0 18px; letter-spacing: -.01em; }
  .thesis { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
  .thesis article { background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius); padding: 16px 18px; }
  .thesis h3 { font-size: 15px; margin: 0 0 6px; }
  .thesis p { margin: 0; color: var(--muted); font-size: 14px; }
  .thesis b { color: var(--text); font-weight: 600; }
  footer { border-top: 1px solid var(--line); padding: 24px 0 40px; color: var(--faint); font-size: 13px; }
  footer p { margin: 4px 0; max-width: 900px; }

  /* ---------- drawer ---------- */
  .scrim { position: fixed; inset: 0; background: rgba(3,5,10,.55); opacity: 0; pointer-events: none; transition: opacity .2s; z-index: 40; }
  .scrim.open { opacity: 1; pointer-events: auto; }
  aside.drawer { position: fixed; top: 0; right: 0; height: 100%; width: min(560px, 100%); background: var(--panel); border-left: 1px solid var(--line-2); transform: translateX(100%); transition: transform .25s ease; z-index: 50; display: flex; flex-direction: column; }
  aside.drawer.open { transform: none; }
  .d-bar { display: flex; align-items: center; gap: 8px; padding: 12px 16px; border-bottom: 1px solid var(--line); }
  .d-bar .sp { flex: 1; }
  .icon-btn { background: var(--panel-2); border: 1px solid var(--line-2); border-radius: 7px; padding: 5px 10px; cursor: pointer; font: 500 12px var(--mono); color: var(--muted); }
  .icon-btn:hover { color: var(--text); border-color: var(--muted); }
  .d-body { overflow-y: auto; padding: 20px 22px 40px; border-top: 3px solid var(--c); }
  .d-body h2 { font-size: 30px; margin: 6px 0 6px; letter-spacing: -.02em; }
  .d-pos { color: var(--text); font-size: 16px; margin: 0 0 16px; }
  .d-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 18px; margin: 18px 0; }
  .d-grid div.full { grid-column: 1 / -1; }
  .d-grid h4, .d-body h4 { font: 500 10.5px var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--faint); margin: 0 0 4px; }
  .d-grid p { margin: 0; font-size: 14px; color: #cdd4e8; }
  .take { border-left: 3px solid var(--c); background: var(--panel-2); padding: 12px 14px; border-radius: 0 8px 8px 0; margin: 18px 0; }
  .take p { margin: 0; font-size: 14.5px; }
  .signal { background: var(--bg); border: 1px solid var(--line); border-radius: 8px; padding: 12px 14px; }
  .signal p { margin: 0 0 8px; font-size: 14px; }
  .conf { font: 600 10px var(--mono); letter-spacing: .08em; text-transform: uppercase; padding: 2px 6px; border-radius: 4px; }
  .conf.verified { color: #06140e; background: var(--good); }
  .conf.reported { color: #1c1300; background: var(--warn); }
  .conf.estimate { color: var(--text); border: 1px solid var(--muted); }
  ul.src { list-style: none; padding: 0; margin: 6px 0 0; }
  ul.src li { font-size: 12.5px; margin: 4px 0; word-break: break-all; }
  .peers { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
  .peers button { background: var(--panel-2); border: 1px solid var(--line-2); border-radius: 6px; padding: 4px 9px; cursor: pointer; font-size: 13px; }
  .peers button:hover { border-color: var(--c); }
  .copied { color: var(--good); font: 500 11px var(--mono); }

  [hidden] { display: none !important; }

  @media (max-width: 1080px) { .map, .thesis { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 700px) {
    .wrap { padding: 0 16px; }
    .map, .thesis { grid-template-columns: 1fr; }
    nav.links { gap: 12px; }
    nav.links a.hide-sm { display: none; }
    .brand span { display: none; }
    .seg button { padding: 7px 10px; }
    .count { margin-left: 0; width: 100%; }
    .search { max-width: none; }
    aside.drawer { top: auto; bottom: 0; height: 88%; width: 100%; border-left: 0; border-top: 1px solid var(--line-2); border-radius: 14px 14px 0 0; transform: translateY(100%); }
    .d-grid { grid-template-columns: 1fr; }
    .tile { min-width: 0; }
  }
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
</head>
<body>

<header class="top">
  <div class="wrap top-in">
    <div class="brand">BFY Indulgence <span>/ Market Map</span></div>
    <nav class="links">
      <a href="#thesis">Thesis</a>
      <a href="__MEMO__" target="_blank" rel="noopener">Memo (PDF)</a>
      <a class="hide-sm" href="space.html">Space view</a>
      <a class="hide-sm" href="__REPO__" target="_blank" rel="noopener">GitHub</a>
    </nav>
  </div>
</header>

<main class="wrap">
  <section class="hero">
    <div class="kicker">US + Australia &middot; Updated __UPDATED__ &middot; Arjun Kulshrestha</div>
    <h1>Better-for-You Indulgence</h1>
    <p class="lede">Brands that let people keep their treats while feeling healthier about them. Mapped by the consumer need each one serves, not by aisle. Click any company for its positioning, channels, funding signal and my investor take.</p>
    <div class="stats" id="stats"></div>
  </section>

  <div class="controls" role="toolbar" aria-label="Filters">
    <div class="seg" id="f-geo" aria-label="Geography"></div>
    <div class="seg" id="f-status" aria-label="Status"></div>
    <input class="search" id="q" type="search" placeholder="Search brands, channels, investors" aria-label="Search">
    <div class="seg" id="f-view" aria-label="View"></div>
    <div class="count" id="count" aria-live="polite"></div>
  </div>

  <div id="view-map">
    <div class="map" id="map"></div>
    <div class="legend">
      <span><span class="bars" style="--c:var(--muted)"><i class="on"></i><i class="on"></i><i class="on"></i><i></i><i></i></span> Scale signal (1 to 5)</span>
      <span><span class="badge breakout">Breakout</span> Growth in flight</span>
      <span><span class="badge exited">Exited</span> Acquired, kept as a pricing comp</span>
      <span>Click a column header for the segment view</span>
    </div>
  </div>

  <div id="view-table" hidden>
    <div class="table-wrap">
      <table id="tbl">
        <thead><tr>
          <th data-k="name">Company</th><th data-k="seg">Need-state</th><th data-k="geo">Geo</th>
          <th data-k="status">Status</th><th data-k="scale" aria-sort="descending">Scale</th><th data-k="signal">Funding / scale signal</th>
        </tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <section class="block" id="thesis">
    <div class="kicker">The thesis</div>
    <h2>Indulgence isn't dying. It's being re-priced.</h2>
    <div class="thesis" id="thesis-grid"></div>
  </section>
</main>

<footer>
  <div class="wrap">
    <p><b style="color:var(--muted)">Method.</b> Every funding or scale figure carries a confidence flag: verified (primary source or major outlet), company-reported, or estimate. Sources are linked in each dossier and listed in the <a href="__MEMO__" target="_blank" rel="noopener">13-page memo</a>.</p>
    <p>Built by Arjun Kulshrestha &middot; <a href="https://linkedin.com/in/arjun-kulshrestha" target="_blank" rel="noopener">LinkedIn</a> &middot; <a href="__REPO__" target="_blank" rel="noopener">Source and data</a> &middot; Updated __UPDATED__</p>
  </div>
</footer>

<div class="scrim" id="scrim"></div>
<aside class="drawer" id="drawer" role="dialog" aria-modal="true" aria-labelledby="d-title" aria-hidden="true">
  <div class="d-bar">
    <button class="icon-btn" id="d-prev" aria-label="Previous company">&larr;</button>
    <button class="icon-btn" id="d-next" aria-label="Next company">&rarr;</button>
    <span class="sp"></span>
    <span class="copied" id="copied" hidden>Link copied</span>
    <button class="icon-btn" id="d-link">Copy link</button>
    <button class="icon-btn" id="d-close" aria-label="Close">Close &times;</button>
  </div>
  <div class="d-body" id="d-body"></div>
</aside>

<script>
const DATA = __DATA__;
const THESIS = __THESIS__;
const GEO = { US: "United States", NA: "Canada", AU: "Australia" };
const GEO_SHORT = { US: "US", NA: "CA", AU: "AU" };
const STATUS = { breakout: "Breakout", independent: "Independent", exited: "Exited" };
const SEGS = DATA.galaxies;
const segById = Object.fromEntries(SEGS.map((g, i) => [g.id, { ...g, n: i + 1 }]));
const slug = s => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const CO = DATA.companies.map(c => ({ ...c, id: slug(c.name) }));
// stable order: segment order, then scale desc, then name
CO.sort((a, b) => SEGS.findIndex(g => g.id === a.galaxy) - SEGS.findIndex(g => g.id === b.galaxy) || b.scale - a.scale || a.name.localeCompare(b.name));
const byId = Object.fromEntries(CO.map(c => [c.id, c]));

function confidence(sig) {
  const s = sig.toLowerCase();
  if (s.includes("estimate") && !s.includes("verified")) return ["estimate", "Estimate"];
  if (s.includes("company-reported") && !s.includes("verified")) return ["reported", "Company-reported"];
  if (s.includes("verified")) return ["verified", "Verified"];
  return ["reported", "Company-reported"];
}
const bars = n => `<span class="bars" aria-label="Scale ${n} of 5">${[1,2,3,4,5].map(i => `<i class="${i <= n ? "on" : ""}"></i>`).join("")}</span>`;
const badge = s => s === "independent" ? "" : `<span class="badge ${s}">${STATUS[s]}</span>`;

/* ---------- state ---------- */
const state = { geo: "all", status: "all", q: "", view: "map", sortK: "scale", sortDir: -1 };
function matches(c) {
  if (state.geo !== "all" && c.geo !== state.geo) return false;
  if (state.status !== "all" && c.status !== state.status) return false;
  if (state.q) {
    const hay = [c.name, c.product, c.positioning, c.channels, c.signal, c.target, c.differentiation, segById[c.galaxy].name].join(" ").toLowerCase();
    if (!state.q.split(/\s+/).every(w => hay.includes(w))) return false;
  }
  return true;
}

/* ---------- controls ---------- */
function seg(el, opts, key) {
  el.innerHTML = opts.map(([v, label]) => `<button type="button" data-v="${v}" aria-pressed="${state[key] === v}">${label}</button>`).join("");
  el.addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    state[key] = b.dataset.v;
    el.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", x === b));
    render();
  });
}
const nGeo = g => CO.filter(c => c.geo === g).length;
seg(document.getElementById("f-geo"), [["all", "All"], ["US", `US ${nGeo("US")}`], ["AU", `AU ${nGeo("AU")}`], ["NA", `CA ${nGeo("NA")}`]], "geo");
seg(document.getElementById("f-status"), [["all", "Any"], ["breakout", "Breakout"], ["independent", "Independent"], ["exited", "Exited"]], "status");
seg(document.getElementById("f-view"), [["map", "Map"], ["table", "Table"]], "view");
document.getElementById("q").addEventListener("input", e => { state.q = e.target.value.trim().toLowerCase(); render(); });

/* ---------- stats ---------- */
document.getElementById("stats").innerHTML = [
  [CO.length, "Companies"], [SEGS.length, "Need-states"], [nGeo("AU"), "Australian"], [nGeo("US") + nGeo("NA"), "North American"],
  [CO.filter(c => c.status === "exited").length, "Exits as comps"],
].map(([b, s]) => `<div class="stat"><b>${b}</b><span>${s}</span></div>`).join("");

/* ---------- map ---------- */
function renderMap() {
  const rows = [["US", "NA"], ["AU"]];
  document.getElementById("map").innerHTML = SEGS.map((g, i) => {
    const inSeg = CO.filter(c => c.galaxy === g.id);
    const rowHtml = rows.map(geos => {
      const list = inSeg.filter(c => geos.includes(c.geo));
      const label = geos.includes("US") ? "US &amp; Canada" : "Australia";
      const tiles = list.length ? list.map(c => {
        const on = matches(c);
        return `<button type="button" class="tile${on ? "" : " dim"}${on && state.q ? " hit" : ""}" data-id="${c.id}" ${on ? "" : 'tabindex="-1" aria-hidden="true"'}>
          <span class="t-name">${esc(c.name)}</span>
          <span class="t-sub">${bars(c.scale)}${c.geo === "NA" ? '<span class="badge exited" style="border-style:dashed">CA</span>' : ""}${badge(c.status)}</span>
        </button>`;
      }).join("") : `<span class="empty-row">No companies mapped yet</span>`;
      return `<div class="geo-row"><div class="geo-label">${label} &middot; ${list.length}</div><div class="tiles">${tiles}</div></div>`;
    }).join("");
    return `<section class="seg-card" style="--c:${g.color}">
      <button type="button" class="seg-head" data-seg="${g.id}" aria-label="Open segment ${esc(g.name)}">
        <div class="seg-num">${String(i + 1).padStart(2, "0")} &middot; ${inSeg.length} COMPANIES</div>
        <div class="seg-name">${esc(g.name)}</div>
        <p class="seg-need">&ldquo;${esc(g.need_state)}&rdquo;</p>
        <div class="seg-meta"><span class="pill">${esc(g.maturity)}</span><span class="pill">VC appeal: ${esc(g.vc_attractiveness)}</span></div>
      </button>${rowHtml}</section>`;
  }).join("");
}

/* ---------- table ---------- */
const sortVal = (c, k) => k === "seg" ? segById[c.galaxy].n : k === "status" ? ["breakout", "independent", "exited"].indexOf(c.status) : k === "geo" ? c.geo : k === "scale" ? c.scale : String(c[k]).toLowerCase();
function renderTable() {
  const list = CO.filter(matches).sort((a, b) => {
    const x = sortVal(a, state.sortK), y = sortVal(b, state.sortK);
    return (x < y ? -1 : x > y ? 1 : 0) * state.sortDir || a.name.localeCompare(b.name);
  });
  document.querySelector("#tbl tbody").innerHTML = list.map(c => {
    const g = segById[c.galaxy];
    return `<tr data-id="${c.id}" tabindex="0" style="--c:${g.color}">
      <td class="nm"><span class="dot"></span>${esc(c.name)}</td><td>${esc(g.name)}</td><td>${GEO_SHORT[c.geo]}</td>
      <td>${STATUS[c.status]}</td><td>${bars(c.scale)}</td><td class="sig">${esc(c.signal)}</td></tr>`;
  }).join("") || `<tr><td colspan="6" style="color:var(--faint)">No companies match these filters.</td></tr>`;
  document.querySelectorAll("#tbl th").forEach(th => th.setAttribute("aria-sort", th.dataset.k === state.sortK ? (state.sortDir > 0 ? "ascending" : "descending") : "none"));
}
document.querySelector("#tbl thead").addEventListener("click", e => {
  const th = e.target.closest("th"); if (!th) return;
  if (state.sortK === th.dataset.k) state.sortDir *= -1; else { state.sortK = th.dataset.k; state.sortDir = th.dataset.k === "scale" ? -1 : 1; }
  renderTable();
});

function render() {
  document.getElementById("view-map").hidden = state.view !== "map";
  document.getElementById("view-table").hidden = state.view !== "table";
  renderMap(); renderTable();
  const n = CO.filter(matches).length;
  document.getElementById("count").textContent = n === CO.length ? `Showing all ${n}` : `${n} of ${CO.length} match`;
}

/* ---------- thesis ---------- */
document.getElementById("thesis-grid").innerHTML = THESIS.map(t => `<article><h3>${t.h}</h3><p>${t.p}</p></article>`).join("");

/* ---------- drawer ---------- */
const drawer = document.getElementById("drawer"), scrim = document.getElementById("scrim"), body = document.getElementById("d-body");
let current = null, lastFocus = null;
function sources(list) {
  return `<ul class="src">${list.map(u => { let host = u; try { host = new URL(u).hostname.replace(/^www\./, ""); } catch (e) {}
    return `<li><a href="${esc(u)}" target="_blank" rel="noopener">${esc(host)}</a></li>`; }).join("")}</ul>`;
}
function companyHtml(c) {
  const g = segById[c.galaxy], [cls, label] = confidence(c.signal);
  const peers = CO.filter(p => p.galaxy === c.galaxy && p.id !== c.id);
  return `<div class="kicker" style="color:${g.color}">${String(g.n).padStart(2, "0")} &middot; ${esc(g.name)}</div>
    <h2 id="d-title">${esc(c.name)}</h2>
    <div class="seg-meta" style="margin:0 0 14px"><span class="pill">${GEO[c.geo]}</span><span class="pill">${STATUS[c.status]}</span><span class="pill">Scale ${c.scale}/5</span></div>
    <p class="d-pos">${esc(c.positioning)}</p>
    <div class="d-grid">
      <div class="full"><h4>Product</h4><p>${esc(c.product)}</p></div>
      <div><h4>Target consumer</h4><p>${esc(c.target)}</p></div>
      <div><h4>Differentiation</h4><p>${esc(c.differentiation)}</p></div>
      <div class="full"><h4>Channels</h4><p>${esc(c.channels)}</p></div>
    </div>
    <div class="signal"><h4>Funding / scale signal <span class="conf ${cls}">${label}</span></h4><p>${esc(c.signal)}</p></div>
    <div class="take"><h4>My take</h4><p>${esc(c.vc_take)}</p></div>
    <h4>Sources</h4>${sources(c.sources)}
    <h4 style="margin-top:18px">Also in ${esc(g.name)}</h4>
    <div class="peers">${peers.map(p => `<button type="button" data-id="${p.id}">${esc(p.name)}</button>`).join("")}</div>`;
}
function segmentHtml(g) {
  const list = CO.filter(c => c.galaxy === g.id);
  return `<div class="kicker" style="color:${g.color}">Segment ${String(g.n).padStart(2, "0")} &middot; ${list.length} companies</div>
    <h2 id="d-title">${esc(g.name)}</h2>
    <p class="d-pos">${esc(g.tagline)}</p>
    <div class="take"><h4>The need-state</h4><p>&ldquo;${esc(g.need_state)}&rdquo;</p></div>
    <div class="d-grid">
      <div class="full"><h4>Why it matters</h4><p>${esc(g.why_care)}</p></div>
      <div><h4>Maturity</h4><p>${esc(g.maturity)}</p></div>
      <div><h4>VC attractiveness</h4><p>${esc(g.vc_attractiveness)}</p></div>
      <div class="full"><h4>Risks</h4><p>${esc(g.risks)}</p></div>
    </div>
    <h4>Companies</h4>
    <div class="peers">${list.map(p => `<button type="button" data-id="${p.id}">${esc(p.name)} <span style="color:var(--faint)">${GEO_SHORT[p.geo]}</span></button>`).join("")}</div>`;
}
function open(key, push = true) {
  const isSeg = key.startsWith("segment-");
  const c = isSeg ? null : byId[key];
  const g = isSeg ? segById[key.slice(8)] : c && segById[c.galaxy];
  if (!g) return;
  current = key;
  body.style.setProperty("--c", g.color);
  body.innerHTML = isSeg ? segmentHtml(g) : companyHtml(c);
  body.scrollTop = 0;
  document.getElementById("d-prev").hidden = document.getElementById("d-next").hidden = isSeg;
  if (!drawer.classList.contains("open")) lastFocus = document.activeElement;
  drawer.classList.add("open"); scrim.classList.add("open"); drawer.setAttribute("aria-hidden", "false");
  document.getElementById("d-close").focus({ preventScroll: true });
  if (push && location.hash.slice(1) !== key) history.pushState(null, "", "#" + key);
  document.title = (isSeg ? g.name : c.name) + " | BFY Indulgence Market Map";
}
function close(push = true) {
  if (!drawer.classList.contains("open")) return;
  drawer.classList.remove("open"); scrim.classList.remove("open"); drawer.setAttribute("aria-hidden", "true");
  current = null; document.title = "__TITLE__: Market Map";
  if (push && location.hash) history.pushState(null, "", location.pathname + location.search);
  if (lastFocus) lastFocus.focus({ preventScroll: true });
}
function step(d) {
  if (!current || current.startsWith("segment-")) return;
  const list = CO.filter(matches).length ? CO.filter(matches) : CO;
  let i = list.findIndex(c => c.id === current);
  i = i < 0 ? 0 : (i + d + list.length) % list.length;
  open(list[i].id);
}
document.addEventListener("click", e => {
  const t = e.target.closest("[data-id]"); if (t) { open(t.dataset.id); return; }
  const s = e.target.closest("[data-seg]"); if (s) open("segment-" + s.dataset.seg);
});
document.querySelector("#tbl tbody").addEventListener("keydown", e => { const r = e.target.closest("tr[data-id]"); if (r && e.key === "Enter") open(r.dataset.id); });
scrim.addEventListener("click", () => close());
document.getElementById("d-close").addEventListener("click", () => close());
document.getElementById("d-prev").addEventListener("click", () => step(-1));
document.getElementById("d-next").addEventListener("click", () => step(1));
document.getElementById("d-link").addEventListener("click", async () => {
  const url = location.origin + location.pathname + "#" + current;
  try { await navigator.clipboard.writeText(url); } catch (e) { prompt("Copy this link", url); return; }
  const m = document.getElementById("copied"); m.hidden = false; setTimeout(() => m.hidden = true, 1600);
});
document.addEventListener("keydown", e => {
  if (!drawer.classList.contains("open")) return;
  if (e.key === "Escape") close();
  if (e.key === "ArrowRight" && e.target.tagName !== "INPUT") step(1);
  if (e.key === "ArrowLeft" && e.target.tagName !== "INPUT") step(-1);
});
function fromHash() { const h = decodeURIComponent(location.hash.slice(1)); if (h && (byId[h] || h.startsWith("segment-"))) open(h, false); else close(false); }
window.addEventListener("popstate", fromHash);

render();
fromHash();
</script>
</body>
</html>
"""


def main() -> None:
    data = json.loads(DATA.read_text())
    n = len(data["companies"])
    desc = (f"{n} better-for-you food and beverage brands across the US and Australia, mapped by consumer "
            f"need-state. Click any brand for its positioning, channels, funding signal and an investor take.")
    html = (TEMPLATE
            .replace("__TITLE__", data["meta"]["title"])
            .replace("__DESC__", desc)
            .replace("__SITE__", SITE)
            .replace("__MEMO__", MEMO)
            .replace("__REPO__", REPO)
            .replace("__UPDATED__", data["meta"]["updated"])
            .replace("__THESIS__", json.dumps(thesis_sections(), ensure_ascii=False))
            .replace("__DATA__", json.dumps(data, ensure_ascii=False)))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"Built {OUT}: {len(data['galaxies'])} segments, {n} companies, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
