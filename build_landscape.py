"""
Better-for-You Indulgence: clickable market map (the main page).

Reads data/companies.json and emits docs/index.html: a landscape grid of the six
consumer need-states, split US / Australia, where every company is a tile that
opens an investor dossier. Dossiers deep-link via the URL hash (e.g. /#noon).
Also has a sortable table view and the one-page thesis. Space styling: starfield
canvas, planets whose size = scale, ring = exited, pulse = breakout.

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
<meta name="theme-color" content="#000000">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    color-scheme: dark;
    --bg: #000;
    --glass: rgba(10, 14, 26, .55);
    --glass-2: rgba(18, 24, 42, .72);
    --hair: rgba(255, 255, 255, .07);
    --hair-2: rgba(255, 255, 255, .14);
    --text: #eef1f8;
    --muted: #8d97b3;
    --faint: #525c78;
    --accent: #9db6ff;
    --good: #43d9a3;
    --warn: #ffb547;
    --display: "Space Grotesk", "Inter", system-ui, sans-serif;
    --sans: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
    --mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace;
  }
  * { box-sizing: border-box; }
  html { -webkit-text-size-adjust: 100%; }
  body { margin: 0; background: var(--bg); color: var(--text); font: 15px/1.6 var(--sans); -webkit-font-smoothing: antialiased; }
  body::before { content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
    background: radial-gradient(1100px 520px at 50% -8%, rgba(90, 120, 255, .10), transparent 70%),
                radial-gradient(700px 400px at 90% 110%, rgba(255, 107, 53, .05), transparent 70%); }
  #stars { position: fixed; inset: 0; width: 100%; height: 100%; z-index: -2; pointer-events: none; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { color: #fff; }
  button { font: inherit; color: inherit; }
  ::selection { background: rgba(157, 182, 255, .3); }
  .wrap { max-width: 1240px; margin: 0 auto; padding: 0 28px; }
  .kicker { font: 500 10.5px/1.4 var(--mono); letter-spacing: .22em; text-transform: uppercase; color: var(--muted); }

  /* ---------- header ---------- */
  header.top { position: sticky; top: 0; z-index: 30; background: linear-gradient(180deg, rgba(0,0,0,.85), rgba(0,0,0,.35)); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); border-bottom: 1px solid var(--hair); }
  .top-in { display: flex; align-items: center; justify-content: space-between; gap: 16px; height: 58px; }
  .brand { font: 500 11px var(--mono); letter-spacing: .28em; text-transform: uppercase; color: var(--text); white-space: nowrap; display: flex; align-items: center; gap: 10px; }
  .brand i { width: 7px; height: 7px; border-radius: 50%; background: #fff; box-shadow: 0 0 10px 2px rgba(157,182,255,.8); }
  nav.links { display: flex; gap: 26px; }
  nav.links a { white-space: nowrap; font: 500 10.5px var(--mono); letter-spacing: .2em; text-transform: uppercase; color: var(--muted); transition: color .2s; }
  nav.links a:hover { color: var(--text); }

  /* ---------- hero ---------- */
  .hero { padding: 88px 0 48px; text-align: center; }
  .hero h1 { font: 300 clamp(34px, 5.4vw, 64px)/1.04 var(--display); letter-spacing: -.035em; margin: 18px 0 18px; }
  .hero h1 b { font-weight: 500; }
  .hero p.lede { max-width: 560px; margin: 0 auto; color: var(--muted); font-size: 15.5px; }
  .stats { display: flex; justify-content: center; flex-wrap: wrap; gap: 8px 30px; margin-top: 34px; font: 500 10.5px var(--mono); letter-spacing: .2em; text-transform: uppercase; color: var(--faint); }
  .stats b { color: var(--text); font-weight: 500; margin-right: 6px; }

  /* ---------- controls ---------- */
  .controls { display: flex; flex-wrap: wrap; align-items: center; gap: 12px 26px; padding: 16px 0; margin-bottom: 22px; border-top: 1px solid var(--hair); border-bottom: 1px solid var(--hair); }
  .seg { display: inline-flex; gap: 16px; }
  .seg button { white-space: nowrap; background: none; border: 0; padding: 4px 0; cursor: pointer; font: 500 10.5px var(--mono); letter-spacing: .16em; text-transform: uppercase; color: var(--faint); border-bottom: 1px solid transparent; transition: color .2s, border-color .2s; }
  .seg button:hover { color: var(--muted); }
  .seg button[aria-pressed="true"] { color: var(--text); border-bottom-color: var(--text); }
  .divider { width: 1px; height: 14px; background: var(--hair-2); }
  .search { flex: 1 1 180px; max-width: 280px; background: none; border: 0; border-bottom: 1px solid var(--hair-2); padding: 5px 0; color: var(--text); font: 13.5px var(--sans); outline: none; transition: border-color .2s; }
  .search:focus { border-bottom-color: var(--muted); }
  .search::placeholder { color: var(--faint); }
  .count { margin-left: auto; font: 500 10.5px var(--mono); letter-spacing: .16em; text-transform: uppercase; color: var(--faint); }

  /* ---------- the map ---------- */
  .map { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1px; background: var(--hair); border: 1px solid var(--hair); border-radius: 14px; overflow: hidden; }
  .seg-card { background: rgba(3, 5, 12, .82); backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); display: flex; flex-direction: column; position: relative; }
  .seg-card::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 120px; pointer-events: none; background: radial-gradient(260px 90px at 34px 0, color-mix(in srgb, var(--c) 16%, transparent), transparent 75%); }
  .seg-head { all: unset; cursor: pointer; display: block; position: relative; padding: 24px 24px 16px; }
  .seg-head:focus-visible { outline: 1px solid var(--c); outline-offset: -4px; }
  .seg-top { display: flex; align-items: center; gap: 10px; }
  .star { width: 9px; height: 9px; border-radius: 50%; background: var(--c); box-shadow: 0 0 12px 2px color-mix(in srgb, var(--c) 70%, transparent); flex: none; }
  .seg-num { font: 500 10px var(--mono); letter-spacing: .22em; color: var(--faint); }
  .seg-name { font: 500 19px/1.25 var(--display); letter-spacing: -.01em; margin: 12px 0 6px; transition: color .2s; }
  .seg-head:hover .seg-name { color: #fff; text-shadow: 0 0 18px color-mix(in srgb, var(--c) 55%, transparent); }
  .seg-need { color: var(--muted); font-size: 13px; margin: 0; }
  .seg-more { display: inline-block; margin-top: 10px; font: 500 9.5px var(--mono); letter-spacing: .2em; text-transform: uppercase; color: var(--faint); transition: color .2s; }
  .seg-head:hover .seg-more { color: var(--c); }
  .geo-row { padding: 12px 24px 18px; }
  .geo-row + .geo-row { border-top: 1px dashed var(--hair); }
  .geo-row:last-child { padding-bottom: 26px; }
  .geo-label { font: 500 9.5px var(--mono); letter-spacing: .24em; text-transform: uppercase; color: var(--faint); margin-bottom: 10px; }
  .tiles { display: flex; flex-wrap: wrap; gap: 6px; }
  .tile { cursor: pointer; display: inline-flex; align-items: center; gap: 9px; background: rgba(255,255,255,.015); border: 1px solid var(--hair); border-radius: 999px; padding: 6px 13px 6px 10px; transition: border-color .2s, background .2s, opacity .25s, box-shadow .2s; }
  .tile:hover, .tile:focus-visible { outline: none; border-color: color-mix(in srgb, var(--c) 60%, transparent); background: color-mix(in srgb, var(--c) 8%, transparent); box-shadow: 0 0 18px -4px color-mix(in srgb, var(--c) 60%, transparent); }
  .t-name { font-size: 13.5px; font-weight: 500; white-space: nowrap; letter-spacing: -.005em; }
  .t-geo { font: 500 9px var(--mono); letter-spacing: .14em; color: var(--faint); }
  .tile.dim { opacity: .14; }
  .tile.hit { border-color: color-mix(in srgb, var(--c) 70%, transparent); }
  .empty-row { color: var(--faint); font: 500 10px var(--mono); letter-spacing: .14em; text-transform: uppercase; }

  /* planets: size = scale, ring = exited, pulse = breakout */
  .planet { position: relative; flex: none; border-radius: 50%; width: var(--s); height: var(--s); background: radial-gradient(circle at 32% 30%, #fff 0 8%, var(--c) 45%, color-mix(in srgb, var(--c) 40%, #000) 100%); box-shadow: 0 0 8px color-mix(in srgb, var(--c) 55%, transparent); }
  .planet.exited { background: transparent; box-shadow: none; border: 1.5px solid var(--c); opacity: .75; }
  .planet.exited::after { content: ""; position: absolute; left: -4px; right: -4px; top: 50%; height: 1px; background: var(--c); transform: rotate(-22deg); opacity: .8; }
  .planet.breakout::after { content: ""; position: absolute; inset: -3px; border-radius: 50%; border: 1px solid var(--c); animation: pulse 2.4s ease-out infinite; }
  @keyframes pulse { from { transform: scale(1); opacity: .9; } to { transform: scale(1.9); opacity: 0; } }

  .legend { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px 30px; padding: 22px 0 10px; color: var(--faint); font: 500 9.5px var(--mono); letter-spacing: .2em; text-transform: uppercase; }
  .legend span { display: inline-flex; align-items: center; gap: 9px; }
  .legend .planet { --c: #9aa6c6; }

  /* ---------- table ---------- */
  .table-wrap { overflow-x: auto; border: 1px solid var(--hair); border-radius: 14px; background: rgba(3,5,12,.82); }
  table { width: 100%; border-collapse: collapse; font-size: 13.5px; min-width: 820px; }
  th, td { text-align: left; padding: 13px 16px; border-bottom: 1px solid var(--hair); vertical-align: middle; }
  th { font: 500 9.5px var(--mono); letter-spacing: .2em; text-transform: uppercase; color: var(--faint); cursor: pointer; user-select: none; white-space: nowrap; }
  th:hover { color: var(--muted); }
  th[aria-sort="ascending"]::after { content: " ↑"; } th[aria-sort="descending"]::after { content: " ↓"; }
  tbody tr { cursor: pointer; transition: background .15s; }
  tbody tr:hover { background: rgba(255,255,255,.025); }
  tbody tr:last-child td { border-bottom: 0; }
  td.nm { font-weight: 500; white-space: nowrap; }
  td.nm .planet { display: inline-block; vertical-align: middle; margin-right: 10px; }
  td.sig { color: var(--muted); max-width: 440px; font-size: 13px; }
  td.mono { font: 500 10.5px var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }

  /* ---------- thesis ---------- */
  section.block { padding: 110px 0 40px; }
  section.block h2 { font: 300 clamp(26px, 3.4vw, 38px)/1.15 var(--display); letter-spacing: -.025em; margin: 16px 0 40px; text-align: center; }
  section.block > .kicker { text-align: center; }
  .thesis { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 44px 48px; }
  .thesis article { border-top: 1px solid var(--hair-2); padding-top: 18px; }
  .thesis .n { font: 500 9.5px var(--mono); letter-spacing: .22em; color: var(--faint); }
  .thesis h3 { font: 500 16px var(--display); margin: 8px 0 8px; }
  .thesis p { margin: 0; color: var(--muted); font-size: 14px; }
  .thesis b { color: var(--text); font-weight: 500; }
  footer { padding: 70px 0 60px; text-align: center; color: var(--faint); font-size: 12.5px; }
  footer p { margin: 6px auto; max-width: 640px; }
  footer .mono { font: 500 9.5px var(--mono); letter-spacing: .22em; text-transform: uppercase; margin-top: 18px; }

  /* ---------- drawer ---------- */
  .scrim { position: fixed; inset: 0; background: rgba(0,0,0,.6); backdrop-filter: blur(2px); opacity: 0; pointer-events: none; transition: opacity .3s; z-index: 40; }
  .scrim.open { opacity: 1; pointer-events: auto; }
  aside.drawer { position: fixed; top: 0; right: 0; height: 100%; width: min(540px, 100%); background: rgba(5, 8, 18, .9); backdrop-filter: blur(22px); -webkit-backdrop-filter: blur(22px); border-left: 1px solid var(--hair-2); transform: translateX(100%); transition: transform .35s cubic-bezier(.2,.8,.2,1); z-index: 50; display: flex; flex-direction: column; }
  aside.drawer.open { transform: none; }
  .d-bar { display: flex; align-items: center; gap: 18px; padding: 16px 26px; border-bottom: 1px solid var(--hair); }
  .d-bar .sp { flex: 1; }
  .icon-btn { background: none; border: 0; padding: 4px 0; cursor: pointer; font: 500 10px var(--mono); letter-spacing: .2em; text-transform: uppercase; color: var(--faint); transition: color .2s; }
  .icon-btn:hover { color: var(--text); }
  .icon-btn:focus { outline: none; }
  .icon-btn:focus-visible { color: var(--text); outline: 1px solid var(--hair-2); outline-offset: 6px; border-radius: 3px; }
  .tile:focus-visible, .seg button:focus-visible { outline: 1px solid var(--hair-2); outline-offset: 3px; }
  .d-body { overflow-y: auto; padding: 34px 30px 60px; position: relative; }
  .d-body::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 220px; pointer-events: none; background: radial-gradient(420px 160px at 40px 0, color-mix(in srgb, var(--c) 18%, transparent), transparent 75%); }
  .d-head { display: flex; align-items: center; gap: 16px; position: relative; }
  .d-head .planet { --s: 34px; }
  .d-body h2 { font: 400 36px/1.05 var(--display); letter-spacing: -.03em; margin: 0; }
  .d-kick { position: relative; margin-bottom: 22px; }
  .d-tags { font: 500 9.5px var(--mono); letter-spacing: .2em; text-transform: uppercase; color: var(--faint); margin: 16px 0 24px; }
  .d-pos { font: 300 19px/1.45 var(--display); color: var(--text); margin: 0 0 30px; letter-spacing: -.01em; }
  .d-list { border-top: 1px solid var(--hair); }
  .d-row { display: grid; grid-template-columns: 128px 1fr; gap: 18px; padding: 14px 0; border-bottom: 1px solid var(--hair); }
  .d-row h4, .d-body h4 { font: 500 9.5px/1.9 var(--mono); letter-spacing: .2em; text-transform: uppercase; color: var(--faint); margin: 0; }
  .d-row p { margin: 0; font-size: 14px; color: #c9d0e3; }
  .take { margin: 30px 0; padding-left: 18px; border-left: 1px solid var(--c); }
  .take p { margin: 6px 0 0; font: 400 16px/1.55 var(--display); color: var(--text); }
  .conf { font: 500 9px var(--mono); letter-spacing: .16em; text-transform: uppercase; padding: 2px 7px; border-radius: 999px; margin-left: 8px; vertical-align: 1px; }
  .conf.verified { color: var(--good); border: 1px solid rgba(67,217,163,.45); }
  .conf.reported { color: var(--warn); border: 1px solid rgba(255,181,71,.45); }
  .conf.estimate { color: var(--muted); border: 1px solid var(--hair-2); }
  ul.src { list-style: none; padding: 0; margin: 8px 0 26px; display: flex; flex-wrap: wrap; gap: 6px 16px; }
  ul.src li { font-size: 12.5px; }
  .peers { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
  .copied { color: var(--good); font: 500 9.5px var(--mono); letter-spacing: .2em; text-transform: uppercase; }

  [hidden] { display: none !important; }

  @media (max-width: 1080px) { .map { grid-template-columns: repeat(2, minmax(0, 1fr)); } .thesis { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 700px) {
    .wrap { padding: 0 16px; }
    .hero { padding: 56px 0 34px; }
    .map, .thesis { grid-template-columns: 1fr; }
    nav.links { gap: 16px; }
    nav.links a.hide-sm { display: none; }
    .divider { display: none; }
    .count { margin-left: 0; width: 100%; }
    .search { max-width: none; }
    .seg-head { padding: 22px 18px 14px; } .geo-row { padding-left: 18px; padding-right: 18px; }
    aside.drawer { top: auto; bottom: 0; height: 90%; width: 100%; border-left: 0; border-top: 1px solid var(--hair-2); border-radius: 18px 18px 0 0; transform: translateY(100%); }
    .d-body { padding: 26px 20px 50px; }
    .d-row { grid-template-columns: 1fr; gap: 4px; }
  }
  @media (prefers-reduced-motion: reduce) { *, *::after { transition: none !important; animation: none !important; } }
</style>
</head>
<body>
<canvas id="stars" aria-hidden="true"></canvas>

<header class="top">
  <div class="wrap top-in">
    <div class="brand"><i></i>BFY Indulgence</div>
    <nav class="links">
      <a href="#thesis">Thesis</a>
      <a href="__MEMO__" target="_blank" rel="noopener">Memo</a>
      <a class="hide-sm" href="space.html">3D</a>
      <a class="hide-sm" href="__REPO__" target="_blank" rel="noopener">Source</a>
    </nav>
  </div>
</header>

<main class="wrap">
  <section class="hero">
    <div class="kicker">A market map &middot; United States + Australia &middot; __UPDATED__</div>
    <h1>Better-for-You <b>Indulgence</b></h1>
    <p class="lede">Brands that let people keep the treat and lose the guilt, mapped by the need each one serves. Select any company for the investor view.</p>
    <div class="stats" id="stats"></div>
  </section>

  <div class="controls" role="toolbar" aria-label="Filters">
    <div class="seg" id="f-geo" aria-label="Geography"></div>
    <span class="divider"></span>
    <div class="seg" id="f-status" aria-label="Status"></div>
    <span class="divider"></span>
    <input class="search" id="q" type="search" placeholder="Search" aria-label="Search brands, channels, investors">
    <div class="count" id="count" aria-live="polite"></div>
    <div class="seg" id="f-view" aria-label="View"></div>
  </div>

  <div id="view-map">
    <div class="map" id="map"></div>
    <div class="legend">
      <span><span class="planet" style="--s:6px"></span><span class="planet" style="--s:11px"></span> Size = scale</span>
      <span><span class="planet breakout" style="--s:9px"></span> Breakout</span>
      <span><span class="planet exited" style="--s:9px"></span> Exited</span>
    </div>
  </div>

  <div id="view-table" hidden>
    <div class="table-wrap">
      <table id="tbl">
        <thead><tr>
          <th data-k="name">Company</th><th data-k="seg">Need-state</th><th data-k="geo">Geo</th>
          <th data-k="status">Status</th><th data-k="scale" aria-sort="descending">Scale</th><th data-k="signal">Signal</th>
        </tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <section class="block" id="thesis">
    <div class="kicker">The thesis</div>
    <h2>Indulgence isn't dying.<br>It's being re-priced.</h2>
    <div class="thesis" id="thesis-grid"></div>
  </section>
</main>

<footer>
  <div class="wrap">
    <p>Every funding or scale figure is flagged as verified, company-reported or estimate, with sources in each dossier and in the <a href="__MEMO__" target="_blank" rel="noopener">13-page memo</a>.</p>
    <p class="mono">Arjun Kulshrestha &middot; <a href="https://linkedin.com/in/arjun-kulshrestha" target="_blank" rel="noopener">LinkedIn</a> &middot; <a href="__REPO__" target="_blank" rel="noopener">GitHub</a></p>
  </div>
</footer>

<div class="scrim" id="scrim"></div>
<aside class="drawer" id="drawer" role="dialog" aria-modal="true" aria-labelledby="d-title" aria-hidden="true">
  <div class="d-bar">
    <button class="icon-btn" id="d-prev" aria-label="Previous company">&larr; Prev</button>
    <button class="icon-btn" id="d-next" aria-label="Next company">Next &rarr;</button>
    <span class="sp"></span>
    <span class="copied" id="copied" hidden>Copied</span>
    <button class="icon-btn" id="d-link">Copy link</button>
    <button class="icon-btn" id="d-close" aria-label="Close">Close</button>
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
const pad = n => String(n).padStart(2, "0");
const CO = DATA.companies.map(c => ({ ...c, id: slug(c.name) }));
CO.sort((a, b) => SEGS.findIndex(g => g.id === a.galaxy) - SEGS.findIndex(g => g.id === b.galaxy) || b.scale - a.scale || a.name.localeCompare(b.name));
const byId = Object.fromEntries(CO.map(c => [c.id, c]));

function confidence(sig) {
  const s = sig.toLowerCase();
  if (s.includes("estimate") && !s.includes("verified")) return ["estimate", "Estimate"];
  if (s.includes("company-reported") && !s.includes("verified")) return ["reported", "Company-reported"];
  if (s.includes("verified")) return ["verified", "Verified"];
  return ["reported", "Company-reported"];
}
const planet = (c, size) => `<span class="planet ${c.status}" style="--s:${size || 5 + c.scale * 1.6}px" aria-hidden="true"></span>`;

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
seg(document.getElementById("f-geo"), [["all", "All"], ["US", "US"], ["AU", "AU"], ["NA", "CA"]], "geo");
seg(document.getElementById("f-status"), [["all", "Any"], ["breakout", "Breakout"], ["independent", "Independent"], ["exited", "Exited"]], "status");
seg(document.getElementById("f-view"), [["map", "Map"], ["table", "Table"]], "view");
document.getElementById("q").addEventListener("input", e => { state.q = e.target.value.trim().toLowerCase(); render(); });

document.getElementById("stats").innerHTML = [
  [CO.length, "Companies"], [SEGS.length, "Need-states"], [nGeo("AU"), "Australia"], [nGeo("US") + nGeo("NA"), "North America"],
  [CO.filter(c => c.status === "exited").length, "Exits"],
].map(([b, s]) => `<span><b>${b}</b>${s}</span>`).join("");

/* ---------- map ---------- */
function renderMap() {
  const rows = [["US", "NA"], ["AU"]];
  document.getElementById("map").innerHTML = SEGS.map((g, i) => {
    const inSeg = CO.filter(c => c.galaxy === g.id);
    const rowHtml = rows.map(geos => {
      const list = inSeg.filter(c => geos.includes(c.geo));
      const label = geos.includes("US") ? "North America" : "Australia";
      const tiles = list.length ? list.map(c => {
        const on = matches(c);
        return `<button type="button" class="tile${on ? "" : " dim"}${on && state.q ? " hit" : ""}" data-id="${c.id}" ${on ? "" : 'tabindex="-1" aria-hidden="true"'}>${planet(c)}<span class="t-name">${esc(c.name)}</span>${c.geo === "NA" ? '<span class="t-geo">CA</span>' : ""}</button>`;
      }).join("") : `<span class="empty-row">Open</span>`;
      return `<div class="geo-row"><div class="geo-label">${label}</div><div class="tiles">${tiles}</div></div>`;
    }).join("");
    return `<section class="seg-card" style="--c:${g.color}">
      <button type="button" class="seg-head" data-seg="${g.id}" aria-label="Segment view: ${esc(g.name)}">
        <div class="seg-top"><span class="star"></span><span class="seg-num">${pad(i + 1)} / ${pad(SEGS.length)}</span></div>
        <div class="seg-name">${esc(g.name)}</div>
        <p class="seg-need">${esc(g.need_state)}</p>
        <span class="seg-more">${inSeg.length} companies &middot; Segment view &rarr;</span>
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
      <td class="nm">${planet(c)}${esc(c.name)}</td><td>${esc(g.name)}</td><td class="mono">${GEO_SHORT[c.geo]}</td>
      <td class="mono">${STATUS[c.status]}</td><td class="mono">${c.scale} / 5</td><td class="sig">${esc(c.signal)}</td></tr>`;
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
  document.getElementById("count").textContent = n === CO.length ? `${n} companies` : `${n} of ${CO.length}`;
}

document.getElementById("thesis-grid").innerHTML = THESIS.map((t, i) => `<article><div class="n">${pad(i + 1)}</div><h3>${t.h}</h3><p>${t.p}</p></article>`).join("");

/* ---------- drawer ---------- */
const drawer = document.getElementById("drawer"), scrim = document.getElementById("scrim"), body = document.getElementById("d-body");
let current = null, lastFocus = null;
const row = (h, p) => `<div class="d-row"><h4>${h}</h4><p>${esc(p)}</p></div>`;
function sources(list) {
  return `<ul class="src">${list.map(u => { let host = u; try { host = new URL(u).hostname.replace(/^www\./, ""); } catch (e) {}
    return `<li><a href="${esc(u)}" target="_blank" rel="noopener">${esc(host)} &nearr;</a></li>`; }).join("")}</ul>`;
}
const peerTiles = list => `<div class="peers">${list.map(p => `<button type="button" class="tile" data-id="${p.id}">${planet(p)}<span class="t-name">${esc(p.name)}</span><span class="t-geo">${GEO_SHORT[p.geo]}</span></button>`).join("")}</div>`;
function companyHtml(c) {
  const g = segById[c.galaxy], [cls, label] = confidence(c.signal);
  return `<div class="kicker d-kick" style="color:${g.color}">${pad(g.n)} &middot; ${esc(g.name)}</div>
    <div class="d-head">${planet(c, 34)}<h2 id="d-title">${esc(c.name)}</h2></div>
    <div class="d-tags">${GEO[c.geo]} &middot; ${STATUS[c.status]} &middot; Scale ${c.scale} / 5</div>
    <p class="d-pos">${esc(c.positioning)}</p>
    <div class="d-list">
      ${row("Product", c.product)}${row("Target", c.target)}${row("Edge", c.differentiation)}${row("Channels", c.channels)}
      <div class="d-row"><h4>Signal</h4><p>${esc(c.signal)}<span class="conf ${cls}">${label}</span></p></div>
    </div>
    <div class="take"><h4>My take</h4><p>${esc(c.vc_take)}</p></div>
    <h4>Sources</h4>${sources(c.sources)}
    <h4>Also in ${esc(g.name)}</h4>${peerTiles(CO.filter(p => p.galaxy === c.galaxy && p.id !== c.id))}`;
}
function segmentHtml(g) {
  return `<div class="kicker d-kick" style="color:${g.color}">Segment ${pad(g.n)} / ${pad(SEGS.length)}</div>
    <div class="d-head"><span class="star" style="width:16px;height:16px"></span><h2 id="d-title">${esc(g.name)}</h2></div>
    <div class="d-tags">${esc(g.maturity)} &middot; VC appeal: ${esc(g.vc_attractiveness)}</div>
    <p class="d-pos">&ldquo;${esc(g.need_state)}&rdquo;</p>
    <div class="d-list">${row("Why it matters", g.why_care)}${row("Risks", g.risks)}</div>
    <h4 style="margin-top:30px">Companies</h4>${peerTiles(CO.filter(c => c.galaxy === g.id))}`;
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
  document.title = (isSeg ? g.name : c.name) + " | BFY Indulgence";
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

/* ---------- starfield: sparse, slow, parallax on scroll; static when motion is reduced ---------- */
(function stars() {
  const cv = document.getElementById("stars"), ctx = cv.getContext("2d");
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  let W, H, dpr, pts = [];
  function seed() {
    dpr = Math.min(devicePixelRatio || 1, 2); W = innerWidth; H = innerHeight;
    cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const n = Math.round(W * H / 5200);
    pts = Array.from({ length: n }, () => {
      const z = Math.random();
      return { x: Math.random() * W, y: Math.random() * H * 1.6, z, r: z < .92 ? .35 + z * .55 : 1 + Math.random() * .6,
               a: .18 + z * .55, tw: Math.random() * 6.28, sp: .4 + Math.random() * 1.2, warm: Math.random() < .12 };
    });
  }
  function draw(t) {
    ctx.clearRect(0, 0, W, H);
    const sy = scrollY;
    for (const p of pts) {
      const y = ((p.y - sy * (.04 + p.z * .12)) % (H * 1.6) + H * 1.6) % (H * 1.6);
      if (y > H) continue;
      const a = still ? p.a : p.a * (.7 + .3 * Math.sin(p.tw + t * .001 * p.sp));
      ctx.fillStyle = p.warm ? `rgba(255,214,170,${a})` : `rgba(210,222,255,${a})`;
      ctx.beginPath(); ctx.arc(p.x, y, p.r, 0, 6.2832); ctx.fill();
    }
  }
  let raf = 0;
  const loop = t => { draw(t); raf = requestAnimationFrame(loop); };
  seed();
  if (still) { draw(0); addEventListener("scroll", () => draw(0), { passive: true }); }
  else raf = requestAnimationFrame(loop);
  addEventListener("resize", () => { seed(); if (still) draw(0); });
  document.addEventListener("visibilitychange", () => { if (still) return; cancelAnimationFrame(raf); if (!document.hidden) raf = requestAnimationFrame(loop); });
})();

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
