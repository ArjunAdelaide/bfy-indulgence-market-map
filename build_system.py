"""
Better-for-You Indulgence: the main page.

A minimal landing page that assembles into a top-down solar system as you scroll.
The sun is the thesis, each orbit is a consumer need-state, each planet is a company
(size = scale, pulse = breakout, ring = exited). Click a planet for the investor
dossier, an orbit's legend entry for the segment view, the sun for the thesis.
Dossiers deep-link via the URL hash (e.g. /#noon).

    python3 build_system.py      ->  docs/index.html
"""
import json
from pathlib import Path

from build_landscape import thesis_sections

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "companies.json"
OUT = ROOT / "docs" / "index.html"
SITE = "https://arjunadelaide.github.io/bfy-indulgence-market-map/"
MEMO = "BFY-Indulgence-Memo-Arjun-Kulshrestha.pdf"
REPO = "https://github.com/ArjunAdelaide/bfy-indulgence-market-map"

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<meta property="og:title" content="__TITLE__: a US + Australia market map">
<meta property="og:description" content="__DESC__">
<meta property="og:type" content="website">
<meta property="og:url" content="__SITE__">
<meta name="theme-color" content="#000000">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    color-scheme: dark;
    --bg: #000;
    --hair: rgba(255,255,255,.07);
    --hair-2: rgba(255,255,255,.14);
    --text: #eef1f8;
    --muted: #8d97b3;
    --faint: #525c78;
    --accent: #9db6ff;
    --good: #43d9a3;
    --warn: #ffb547;
    --display: "Space Grotesk", "Inter", system-ui, sans-serif;
    --sans: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
    --mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace;
    --p: 0;
  }
  * { box-sizing: border-box; }
  html { -webkit-text-size-adjust: 100%; }
  body { margin: 0; background: var(--bg); color: var(--text); font: 15px/1.6 var(--sans); -webkit-font-smoothing: antialiased; overflow-x: hidden; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { color: #fff; }
  button { font: inherit; color: inherit; text-transform: inherit; letter-spacing: inherit; }
  #stars { position: fixed; inset: 0; width: 100%; height: 100%; z-index: 0; pointer-events: none; }
  .mono { font: 500 10px/1.4 var(--mono); letter-spacing: .24em; text-transform: uppercase; }

  /* ---------- chrome ---------- */
  header.top { position: fixed; top: 0; left: 0; right: 0; z-index: 30; display: flex; align-items: center; justify-content: space-between; padding: 22px 30px; pointer-events: none; }
  header.top > * { pointer-events: auto; }
  .brand { display: flex; align-items: center; gap: 12px; color: var(--text); background: none; border: 0; cursor: pointer; padding: 0; }
  .brand i { width: 6px; height: 6px; border-radius: 50%; background: #fff; box-shadow: 0 0 10px 2px rgba(255,210,150,.9); }
  nav.links { display: flex; gap: 28px; }
  nav.links a, nav.links button { background: none; border: 0; padding: 0; cursor: pointer; color: var(--muted); transition: color .2s; }
  nav.links a:hover, nav.links button:hover { color: var(--text); }

  /* ---------- stage: landing that assembles into the system ---------- */
  #stage { position: relative; height: 240vh; z-index: 1; }
  .sticky { position: sticky; top: 0; height: 100vh; height: 100svh; overflow: hidden; }
  .hero { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 0 24px;
          opacity: calc(1 - var(--p) * 3); transform: translateY(calc(var(--p) * -80px)); pointer-events: none; z-index: 3; }
  .hero h1 { font: 300 clamp(40px, 7.4vw, 104px)/.98 var(--display); letter-spacing: -.045em; margin: 22px 0 22px; }
  .hero h1 b { font-weight: 500; }
  .hero p { color: var(--muted); max-width: 420px; margin: 0; font-size: 15px; }
  .enter { pointer-events: auto; margin-top: 44px; display: inline-flex; flex-direction: column; align-items: center; gap: 14px; background: none; border: 0; cursor: pointer; color: var(--muted); }
  .enter:hover { color: var(--text); }
  .enter .line { width: 1px; height: 46px; background: linear-gradient(var(--muted), transparent); position: relative; overflow: hidden; }
  .enter .line::after { content: ""; position: absolute; left: 0; width: 1px; height: 14px; background: #fff; animation: drip 2.2s ease-in-out infinite; }
  @keyframes drip { from { top: -14px; } to { top: 46px; } }

  .system { position: absolute; left: 50%; top: 50%; width: min(96vw, 96vh); height: min(96vw, 96vh); transform: translate(-50%, -50%); z-index: 2; }
  .system svg { width: 100%; height: 100%; overflow: visible; display: block; }
  .orbit { fill: none; stroke-width: 1; transition: opacity .35s, stroke-width .35s; }
  .planet-g { cursor: pointer; opacity: 0; }
  .planet-g .hit { fill: transparent; }
  .planet-g .body { transition: r .2s; }
  .planet-g .lbl { font: 500 11px var(--mono); letter-spacing: .06em; fill: #b7c0d8; paint-order: stroke; stroke: #000; stroke-width: 4px; stroke-linejoin: round; pointer-events: none; transition: fill .2s, opacity .3s; }
  .planet-g:hover .lbl, .planet-g:focus .lbl, .planet-g.hl .lbl { fill: #fff; }
  .planet-g:focus { outline: none; }
  .planet-g:focus-visible .ring-focus { stroke: #fff; }
  .ring-focus { fill: none; stroke: transparent; stroke-width: 1; }
  .pulse { fill: none; stroke-width: 1; transform-box: fill-box; transform-origin: center; animation: pulse 2.6s ease-out infinite; }
  @keyframes pulse { from { transform: scale(1); opacity: .9; } to { transform: scale(2.2); opacity: 0; } }
  .dim { opacity: .12; }
  .sun { cursor: pointer; }
  .sun-core { transition: r .3s; }
  .sun:hover .sun-core { r: 30; }
  .sun-lbl { font: 500 10px var(--mono); letter-spacing: .28em; fill: #1a1206; pointer-events: none; }

  /* legend + bar fade in once the system has assembled */
  .ui { opacity: clamp(0, calc((var(--p) - .82) * 6), 1); transition: opacity .2s; }
  .ui.off { pointer-events: none; }
  .legend { position: absolute; left: 30px; top: 50%; transform: translateY(-50%); z-index: 4; display: flex; flex-direction: column; gap: 2px; }
  .legend button { display: grid; grid-template-columns: 14px 1fr auto; align-items: center; gap: 12px; width: 250px; text-align: left; background: none; border: 0; padding: 9px 0; cursor: pointer; color: var(--muted); border-bottom: 1px solid var(--hair); transition: color .2s; }
  .legend button:last-child { border-bottom: 0; }
  .legend button:hover, .legend button.on { color: var(--text); }
  .legend .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--c); box-shadow: 0 0 10px var(--c); }
  .legend .nm { font: 400 14px var(--display); letter-spacing: -.005em; }
  .legend .ct { font: 500 10px var(--mono); color: var(--faint); letter-spacing: .1em; }
  .legend .hd { color: var(--faint); margin-bottom: 8px; }
  .bar { position: absolute; left: 50%; bottom: 26px; transform: translateX(-50%); z-index: 4; display: flex; align-items: center; gap: 22px; padding: 10px 20px; border: 1px solid var(--hair-2); border-radius: 999px; background: rgba(4,6,14,.6); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); white-space: nowrap; }
  .bar button { background: none; border: 0; padding: 2px 0; cursor: pointer; color: var(--faint); border-bottom: 1px solid transparent; transition: color .2s; }
  .bar button:hover { color: var(--muted); }
  .bar button[aria-pressed="true"] { color: var(--text); border-bottom-color: var(--text); }
  .bar .sep { width: 1px; height: 12px; background: var(--hair-2); }
  .keys { position: absolute; right: 30px; bottom: 30px; z-index: 4; display: flex; flex-direction: column; gap: 10px; color: var(--faint); }
  .keys span { display: flex; align-items: center; gap: 10px; justify-content: flex-end; }
  .keys svg { overflow: visible; }

  footer { position: relative; z-index: 1; padding: 90px 30px 70px; text-align: center; color: var(--faint); }
  footer p { margin: 8px 0; }
  footer .big { font: 300 clamp(22px, 3vw, 32px)/1.2 var(--display); color: var(--text); letter-spacing: -.02em; margin-bottom: 22px; }

  /* ---------- panels: dossier, thesis, index ---------- */
  .scrim { position: fixed; inset: 0; background: rgba(0,0,0,.55); backdrop-filter: blur(2px); opacity: 0; pointer-events: none; transition: opacity .3s; z-index: 40; }
  .scrim.open { opacity: 1; pointer-events: auto; }
  aside.drawer { position: fixed; top: 0; right: 0; height: 100%; width: min(520px, 100%); background: rgba(5,8,18,.9); backdrop-filter: blur(22px); -webkit-backdrop-filter: blur(22px); border-left: 1px solid var(--hair-2); transform: translateX(100%); transition: transform .4s cubic-bezier(.2,.8,.2,1); z-index: 50; display: flex; flex-direction: column; }
  aside.drawer.open { transform: none; }
  .d-bar { display: flex; align-items: center; gap: 20px; padding: 18px 28px; border-bottom: 1px solid var(--hair); }
  .d-bar .sp { flex: 1; }
  .icon-btn { background: none; border: 0; padding: 4px 0; cursor: pointer; color: var(--faint); transition: color .2s; }
  .icon-btn:hover { color: var(--text); }
  .icon-btn:focus { outline: none; }
  .icon-btn:focus-visible { color: var(--text); outline: 1px solid var(--hair-2); outline-offset: 6px; border-radius: 3px; }
  .d-body { overflow-y: auto; padding: 36px 30px 60px; position: relative; }
  .d-body::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 240px; pointer-events: none; background: radial-gradient(420px 170px at 40px 0, color-mix(in srgb, var(--c) 20%, transparent), transparent 75%); }
  .d-kick { position: relative; color: var(--c); margin-bottom: 22px; }
  .d-head { display: flex; align-items: center; gap: 18px; position: relative; }
  .orb { flex: none; border-radius: 50%; width: 36px; height: 36px; background: radial-gradient(circle at 32% 30%, #fff 0 7%, var(--c) 45%, color-mix(in srgb, var(--c) 35%, #000) 100%); box-shadow: 0 0 26px color-mix(in srgb, var(--c) 50%, transparent); }
  .orb.exited { background: transparent; box-shadow: none; border: 1.5px solid var(--c); }
  .d-body h2 { font: 400 38px/1.05 var(--display); letter-spacing: -.03em; margin: 0; }
  .d-tags { color: var(--faint); margin: 16px 0 26px; }
  .d-pos { font: 300 20px/1.45 var(--display); margin: 0 0 30px; letter-spacing: -.01em; }
  .d-list { border-top: 1px solid var(--hair); }
  .d-row { display: grid; grid-template-columns: 110px 1fr; gap: 18px; padding: 14px 0; border-bottom: 1px solid var(--hair); }
  .d-row h4, .d-body h4 { font: 500 9.5px/1.9 var(--mono); letter-spacing: .22em; text-transform: uppercase; color: var(--faint); margin: 0; }
  .d-row p { margin: 0; font-size: 14px; color: #c9d0e3; }
  .take { margin: 30px 0; padding-left: 18px; border-left: 1px solid var(--c); }
  .take p { margin: 6px 0 0; font: 400 16px/1.55 var(--display); }
  .conf { font: 500 9px var(--mono); letter-spacing: .16em; text-transform: uppercase; padding: 2px 7px; border-radius: 999px; margin-left: 8px; vertical-align: 1px; white-space: nowrap; }
  .conf.verified { color: var(--good); border: 1px solid rgba(67,217,163,.45); }
  .conf.reported { color: var(--warn); border: 1px solid rgba(255,181,71,.45); }
  .conf.estimate { color: var(--muted); border: 1px solid var(--hair-2); }
  ul.src { list-style: none; padding: 0; margin: 8px 0 28px; display: flex; flex-wrap: wrap; gap: 6px 16px; font-size: 12.5px; }
  .chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
  .chip { display: inline-flex; align-items: center; gap: 8px; cursor: pointer; background: rgba(255,255,255,.02); border: 1px solid var(--hair); border-radius: 999px; padding: 5px 12px 5px 9px; font-size: 13px; transition: border-color .2s, background .2s; }
  .chip:hover { border-color: color-mix(in srgb, var(--c) 60%, transparent); background: color-mix(in srgb, var(--c) 8%, transparent); }
  .chip i { width: 7px; height: 7px; border-radius: 50%; background: var(--c); }
  .chip small { font: 500 9px var(--mono); letter-spacing: .12em; color: var(--faint); }
  .thesis-item { padding: 18px 0; border-bottom: 1px solid var(--hair); }
  .thesis-item h3 { font: 500 16px var(--display); margin: 0 0 6px; }
  .thesis-item p { margin: 0; color: var(--muted); font-size: 14px; }
  .thesis-item b { color: var(--text); font-weight: 500; }
  .idx-seg { margin-bottom: 26px; }
  .idx-seg h4 { display: flex; align-items: center; gap: 10px; color: var(--muted) !important; }
  .idx-seg h4 i { width: 7px; height: 7px; border-radius: 50%; background: var(--c); }
  .copied { color: var(--good); }
  [hidden] { display: none !important; }

  @media (max-width: 1100px) { .legend { display: none; } .keys { display: none; } }
  @media (max-width: 700px) {
    header.top { padding: 18px 18px; }
    nav.links { gap: 18px; }
    nav.links .hide-sm { display: none; }
    .system { width: 100vw; height: 100vw; top: 47%; }
    .planet-g .lbl { opacity: 0; }
    .planet-g.hl .lbl { opacity: 1; }
    .bar { gap: 14px; padding: 9px 16px; bottom: 22px; }
    aside.drawer { top: auto; bottom: 0; height: 90%; width: 100%; border-left: 0; border-top: 1px solid var(--hair-2); border-radius: 18px 18px 0 0; transform: translateY(100%); }
    .d-body { padding: 28px 20px 50px; }
    .d-row { grid-template-columns: 1fr; gap: 4px; }
    .mobile-legend { display: flex !important; }
  }
  .mobile-legend { display: none; position: absolute; left: 0; right: 0; top: 64px; z-index: 4; gap: 6px; overflow-x: auto; padding: 0 18px 6px; scrollbar-width: none; }
  .mobile-legend::-webkit-scrollbar { display: none; }
  .mobile-legend button { flex: none; display: inline-flex; align-items: center; gap: 7px; background: rgba(4,6,14,.6); border: 1px solid var(--hair-2); border-radius: 999px; padding: 6px 11px; font: 400 12.5px var(--display); color: var(--muted); cursor: pointer; }
  .mobile-legend button i { width: 6px; height: 6px; border-radius: 50%; background: var(--c); }
  @media (prefers-reduced-motion: reduce) { .pulse, .enter .line::after { animation: none; } * { transition: none !important; } }
</style>
</head>
<body>
<canvas id="stars" aria-hidden="true"></canvas>

<header class="top">
  <button class="brand mono" id="home" aria-label="Back to top"><i></i>BFY Indulgence</button>
  <nav class="links mono">
    <button id="nav-thesis">Thesis</button>
    <button id="nav-index">Index</button>
    <a class="hide-sm" href="__MEMO__" target="_blank" rel="noopener">Memo</a>
  </nav>
</header>

<div id="stage">
  <div class="sticky">
    <div class="hero">
      <div class="mono" style="color:var(--muted)">A market map &middot; US + Australia</div>
      <h1>Better-for-You<br><b>Indulgence</b></h1>
      <p>__N__ brands that let people keep the treat and lose the guilt, orbiting the needs they serve.</p>
      <button class="enter mono" id="enter">Enter the system<span class="line"></span></button>
    </div>

    <div class="system"><svg id="sys" viewBox="-500 -500 1000 1000" role="group" aria-label="Solar system market map"></svg></div>

    <div class="legend ui off" id="legend"><div class="mono hd">Need-states</div></div>
    <div class="mobile-legend ui off" id="mlegend"></div>

    <div class="bar ui off mono" id="bar">
      <button data-geo="all" aria-pressed="true">All</button>
      <button data-geo="US" aria-pressed="false">US</button>
      <button data-geo="AU" aria-pressed="false">AU</button>
      <button data-geo="NA" aria-pressed="false">CA</button>
      <span class="sep"></span>
      <button id="bar-index" aria-pressed="false">Index</button>
    </div>

    <div class="keys ui off mono">
      <span>Size = scale <svg width="22" height="10"><circle cx="3" cy="5" r="2.5" fill="#8d97b3"/><circle cx="16" cy="5" r="5" fill="#8d97b3"/></svg></span>
      <span>Breakout <svg width="10" height="10"><circle cx="5" cy="5" r="3.5" fill="#8d97b3"/><circle cx="5" cy="5" r="5" fill="none" stroke="#8d97b3"/></svg></span>
      <span>Exited <svg width="10" height="10"><circle cx="5" cy="5" r="4" fill="none" stroke="#8d97b3" stroke-width="1.3"/></svg></span>
      <span>Tap the sun for the thesis</span>
    </div>
  </div>
</div>

<footer>
  <p class="big">Every figure is flagged verified, company-reported or estimate.</p>
  <p class="mono"><a href="__MEMO__" target="_blank" rel="noopener">13-page memo</a> &middot; <a href="list.html">List view</a> &middot; <a href="space.html">3D</a> &middot; <a href="__REPO__" target="_blank" rel="noopener">Source</a></p>
  <p class="mono" style="margin-top:22px">Arjun Kulshrestha &middot; <a href="https://linkedin.com/in/arjun-kulshrestha" target="_blank" rel="noopener">LinkedIn</a> &middot; __UPDATED__</p>
</footer>

<div class="scrim" id="scrim"></div>
<aside class="drawer" id="drawer" role="dialog" aria-modal="true" aria-labelledby="d-title" aria-hidden="true">
  <div class="d-bar mono">
    <button class="icon-btn mono" id="d-prev" aria-label="Previous company">&larr; Prev</button>
    <button class="icon-btn mono" id="d-next" aria-label="Next company">Next &rarr;</button>
    <span class="sp"></span>
    <span class="copied" id="copied" hidden>Copied</span>
    <button class="icon-btn mono" id="d-link">Copy link</button>
    <button class="icon-btn mono" id="d-close">Close</button>
  </div>
  <div class="d-body" id="d-body"></div>
</aside>

<script>
const DATA = __DATA__;
const THESIS = __THESIS__;
const GEO = { US: "United States", NA: "Canada", AU: "Australia" };
const GEO_SHORT = { US: "US", NA: "CA", AU: "AU" };
const STATUS = { breakout: "Breakout", independent: "Independent", exited: "Exited" };
const SEGS = DATA.galaxies.map((g, i) => ({ ...g, n: i + 1 }));
const segById = Object.fromEntries(SEGS.map(g => [g.id, g]));
const slug = s => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const pad = n => String(n).padStart(2, "0");
const CO = DATA.companies.map(c => ({ ...c, id: slug(c.name) }));
CO.sort((a, b) => segById[a.galaxy].n - segById[b.galaxy].n || b.scale - a.scale || a.name.localeCompare(b.name));
const byId = Object.fromEntries(CO.map(c => [c.id, c]));
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
const NS = "http://www.w3.org/2000/svg";
const el = (tag, attrs = {}, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };

/* ---------- build the system: fewer companies on inner orbits ---------- */
const svg = document.getElementById("sys");
const defs = el("defs", {}, svg);
const sunGrad = el("radialGradient", { id: "sunG" }, defs);
[["0", "#fff6e6"], ["0.35", "#ffd08a"], ["0.7", "#ff9a3c"], ["1", "#ff6b1a"]].forEach(([o, c]) => el("stop", { offset: o, "stop-color": c }, sunGrad));
const glowGrad = el("radialGradient", { id: "glowG" }, defs);
[["0", "rgba(255,190,120,.55)"], ["0.4", "rgba(255,150,80,.14)"], ["1", "rgba(255,120,60,0)"]].forEach(([o, c]) => el("stop", { offset: o, "stop-color": c }, glowGrad));

const ringOrder = [...SEGS].sort((a, b) => CO.filter(c => c.galaxy === a.id).length - CO.filter(c => c.galaxy === b.id).length || a.n - b.n);
const R0 = 128, RSTEP = 56;
ringOrder.forEach((g, i) => { g.r = R0 + i * RSTEP; g.phase = i * 0.9 + 0.4; g.speed = 0.018 * Math.pow(R0 / g.r, 1.5); });

const glow = el("circle", { r: 300, fill: "url(#glowG)" }, svg);
const orbitG = el("g", {}, svg), planetG = el("g", {}, svg);
const orbits = {};
ringOrder.forEach(g => {
  orbits[g.id] = el("circle", { class: "orbit", r: g.r, stroke: g.color, "stroke-opacity": .38, pathLength: 1, "stroke-dasharray": 1, "stroke-dashoffset": 1, transform: "rotate(-90)" }, orbitG);
});
const planets = [];
ringOrder.forEach(g => {
  const list = CO.filter(c => c.galaxy === g.id);
  list.forEach((c, k) => {
    const r = 4.5 + c.scale * 1.9;
    const grp = el("g", { class: "planet-g", tabindex: 0, role: "button", "aria-label": `${c.name}, ${g.name}`, "data-id": c.id }, planetG);
    el("circle", { class: "hit", r: Math.max(r + 8, innerWidth < 700 ? 30 : 16) }, grp);
    if (c.status === "breakout") el("circle", { class: "pulse", r: r + 2, stroke: g.color }, grp);
    const body = el("circle", c.status === "exited"
      ? { class: "body", r, fill: "#000", stroke: g.color, "stroke-width": 1.6 }
      : { class: "body", r, fill: g.color }, grp);
    if (c.status !== "exited") el("circle", { r: r * .45, cx: -r * .3, cy: -r * .3, fill: "#fff", opacity: .35 }, grp);
    el("circle", { class: "ring-focus", r: r + 5 }, grp);
    const lbl = el("text", { class: "lbl", x: r + 7, y: 4 }, grp);
    lbl.textContent = c.name;
    planets.push({ c, g, grp, a0: g.phase + (k / list.length) * Math.PI * 2, delay: 0 });
  });
});
planets.forEach((p, i) => p.delay = i / planets.length);
const sun = el("g", { class: "sun", tabindex: 0, role: "button", "aria-label": "Open the thesis" }, svg);
el("circle", { r: 40, fill: "transparent" }, sun);
el("circle", { class: "sun-core", r: 26, fill: "url(#sunG)" }, sun);
const sunTxt = el("text", { class: "sun-lbl", "text-anchor": "middle", y: 4 }, sun); sunTxt.textContent = CO.length;

/* ---------- scroll-driven assembly ---------- */
const stage = document.getElementById("stage"), root = document.documentElement;
const ui = [...document.querySelectorAll(".ui")];
let P = 0;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ease = t => 1 - Math.pow(1 - t, 3);
// ?assembled skips the intro and opens straight on the finished system
const ASSEMBLED = new URLSearchParams(location.search).has("assembled");
if (ASSEMBLED) stage.style.height = "100vh";
function progress() { if (ASSEMBLED) return 1; const span = stage.offsetHeight - innerHeight; return span > 0 ? clamp(scrollY / span) : 1; }
function applyProgress() {
  P = progress();
  root.style.setProperty("--p", P.toFixed(4));
  // sunrise glow collapses into a crisp sun
  glow.setAttribute("r", 300 - ease(clamp(P / .45)) * 200);
  glow.setAttribute("opacity", 1 - ease(clamp(P / .6)) * .55);
  sun.style.opacity = clamp((P - .05) / .25);
  // orbits draw outward, one after another
  ringOrder.forEach((g, i) => orbits[g.id].setAttribute("stroke-dashoffset", 1 - ease(clamp((P - .18 - i * .06) / .28))));
  // planets drop onto their orbits
  planets.forEach(p => { p.t = ease(clamp((P - .42 - p.delay * .38) / .18)); });
  ui.forEach(u => u.classList.toggle("off", P < .9));
  document.getElementById("enter").style.visibility = P > .3 ? "hidden" : "visible";
  planetG.style.pointerEvents = P > .85 ? "auto" : "none";
}

/* ---------- motion: slow Kepler-ish rotation, paused while you hover or read ---------- */
let rot = 0, last = 0, paused = false, hoverId = null;
function place() {
  planets.forEach(p => {
    const a = p.a0 + rot * p.g.speed * 60;
    const rr = p.g.r * (0.35 + 0.65 * p.t);
    const x = Math.cos(a) * rr, y = Math.sin(a) * rr;
    p.grp.setAttribute("transform", `translate(${x.toFixed(2)} ${y.toFixed(2)})`);
    p.grp.style.opacity = p.grp.classList.contains("dim") ? "" : p.t;
  });
}
function frame(t) {
  const dt = last ? Math.min(t - last, 50) / 1000 : 0; last = t;
  if (!paused && !REDUCED && P > .98 && !drawerOpen()) rot += dt;
  place();
  requestAnimationFrame(frame);
}
svg.addEventListener("pointerover", e => { if (e.target.closest(".planet-g")) paused = true; });
svg.addEventListener("pointerout", e => { if (e.target.closest(".planet-g")) paused = false; });

/* ---------- filters and highlighting ---------- */
const state = { geo: "all", seg: null };
function applyFilters() {
  planets.forEach(p => {
    const off = (state.geo !== "all" && p.c.geo !== state.geo) || (state.seg && p.g.id !== state.seg);
    p.grp.classList.toggle("dim", off);
    p.grp.classList.toggle("hl", !!state.seg && !off);
  });
  ringOrder.forEach(g => orbits[g.id].classList.toggle("dim", !!state.seg && state.seg !== g.id));
  document.querySelectorAll("[data-seg]").forEach(b => b.classList.toggle("on", b.dataset.seg === state.seg));
}
document.getElementById("bar").addEventListener("click", e => {
  const b = e.target.closest("[data-geo]"); if (!b) return;
  state.geo = b.dataset.geo;
  document.querySelectorAll("[data-geo]").forEach(x => x.setAttribute("aria-pressed", x === b));
  applyFilters();
});
const legend = document.getElementById("legend"), mlegend = document.getElementById("mlegend");
SEGS.forEach(g => {
  const n = CO.filter(c => c.galaxy === g.id).length;
  legend.insertAdjacentHTML("beforeend", `<button data-seg="${g.id}" style="--c:${g.color}"><span class="dot"></span><span class="nm">${esc(g.name)}</span><span class="ct">${n}</span></button>`);
  mlegend.insertAdjacentHTML("beforeend", `<button data-seg="${g.id}" style="--c:${g.color}"><i></i>${esc(g.name)}</button>`);
});
[legend, mlegend].forEach(L => {
  L.addEventListener("pointerover", e => { const b = e.target.closest("[data-seg]"); if (b && e.pointerType === "mouse") { state.seg = b.dataset.seg; applyFilters(); } });
  L.addEventListener("pointerleave", e => { if (e.pointerType === "mouse") { state.seg = null; applyFilters(); } });
  L.addEventListener("click", e => { const b = e.target.closest("[data-seg]"); if (b) open("segment-" + b.dataset.seg); });
});

/* ---------- panels ---------- */
const drawer = document.getElementById("drawer"), scrim = document.getElementById("scrim"), body = document.getElementById("d-body");
const drawerOpen = () => drawer.classList.contains("open");
let current = null, lastFocus = null;
function confidence(sig) {
  const s = sig.toLowerCase();
  if (s.includes("estimate") && !s.includes("verified")) return ["estimate", "Estimate"];
  if (s.includes("company-reported") && !s.includes("verified")) return ["reported", "Company-reported"];
  if (s.includes("verified")) return ["verified", "Verified"];
  return ["reported", "Company-reported"];
}
const row = (h, p) => `<div class="d-row"><h4>${h}</h4><p>${esc(p)}</p></div>`;
const chips = list => `<div class="chips">${list.map(p => `<button type="button" class="chip" data-id="${p.id}" style="--c:${segById[p.galaxy].color}"><i></i>${esc(p.name)}<small>${GEO_SHORT[p.geo]}</small></button>`).join("")}</div>`;
function sources(list) {
  return `<ul class="src">${list.map(u => { let h = u; try { h = new URL(u).hostname.replace(/^www\./, ""); } catch (e) {} return `<li><a href="${esc(u)}" target="_blank" rel="noopener">${esc(h)} &nearr;</a></li>`; }).join("")}</ul>`;
}
const VIEWS = {
  company(c) {
    const g = segById[c.galaxy], [cls, label] = confidence(c.signal);
    return { color: g.color, title: c.name, html: `<div class="mono d-kick">${pad(g.n)} &middot; ${esc(g.name)}</div>
      <div class="d-head"><span class="orb ${c.status}"></span><h2 id="d-title">${esc(c.name)}</h2></div>
      <div class="mono d-tags">${GEO[c.geo]} &middot; ${STATUS[c.status]} &middot; Scale ${c.scale} / 5</div>
      <p class="d-pos">${esc(c.positioning)}</p>
      <div class="d-list">${row("Product", c.product)}${row("Target", c.target)}${row("Edge", c.differentiation)}${row("Channels", c.channels)}
        <div class="d-row"><h4>Signal</h4><p>${esc(c.signal)}<span class="conf ${cls}">${label}</span></p></div></div>
      <div class="take"><h4>My take</h4><p>${esc(c.vc_take)}</p></div>
      <h4>Sources</h4>${sources(c.sources)}
      <h4>Same orbit</h4>${chips(CO.filter(p => p.galaxy === c.galaxy && p.id !== c.id))}` };
  },
  segment(g) {
    return { color: g.color, title: g.name, html: `<div class="mono d-kick">Orbit ${pad(g.n)} / ${pad(SEGS.length)}</div>
      <div class="d-head"><span class="orb" style="width:18px;height:18px"></span><h2 id="d-title">${esc(g.name)}</h2></div>
      <div class="mono d-tags">${esc(g.maturity)} &middot; VC appeal: ${esc(g.vc_attractiveness)}</div>
      <p class="d-pos">&ldquo;${esc(g.need_state)}&rdquo;</p>
      <div class="d-list">${row("Why it matters", g.why_care)}${row("Risks", g.risks)}</div>
      <h4 style="margin-top:30px">On this orbit</h4>${chips(CO.filter(c => c.galaxy === g.id))}` };
  },
  thesis() {
    return { color: "#ff9a3c", title: "Thesis", html: `<div class="mono d-kick">The sun</div>
      <h2 id="d-title">Indulgence isn't dying. It's being re-priced.</h2>
      <div style="margin-top:22px">${THESIS.map(t => `<div class="thesis-item"><h3>${t.h}</h3><p>${t.p}</p></div>`).join("")}</div>
      <p style="margin-top:24px"><a class="mono" href="__MEMO__" target="_blank" rel="noopener">Read the 13-page memo &nearr;</a></p>` };
  },
  index() {
    return { color: "#9db6ff", title: "Index", html: `<div class="mono d-kick">Index</div><h2 id="d-title">All ${CO.length} companies</h2><div style="margin-top:28px">
      ${SEGS.map(g => `<div class="idx-seg" style="--c:${g.color}"><h4><i></i>${esc(g.name)}</h4>${chips(CO.filter(c => c.galaxy === g.id))}</div>`).join("")}</div>` };
  },
};
function resolve(key) {
  if (key === "thesis") return VIEWS.thesis();
  if (key === "index") return VIEWS.index();
  if (key.startsWith("segment-") && segById[key.slice(8)]) return VIEWS.segment(segById[key.slice(8)]);
  if (byId[key]) return VIEWS.company(byId[key]);
  return null;
}
function open(key, push = true) {
  const v = resolve(key); if (!v) return;
  current = key;
  body.style.setProperty("--c", v.color);
  body.innerHTML = v.html; body.scrollTop = 0;
  const isCo = !!byId[key];
  document.getElementById("d-prev").hidden = document.getElementById("d-next").hidden = !isCo;
  if (!drawerOpen()) lastFocus = document.activeElement;
  drawer.classList.add("open"); scrim.classList.add("open"); drawer.setAttribute("aria-hidden", "false");
  document.getElementById("d-close").focus({ preventScroll: true });
  if (push && location.hash.slice(1) !== key) history.pushState(null, "", "#" + key);
  document.title = v.title + " | BFY Indulgence";
  if (isCo) { state.seg = byId[key].galaxy; applyFilters(); planets.forEach(p => p.grp.classList.toggle("hl", p.c.id === key)); }
}
function close(push = true) {
  if (!drawerOpen()) return;
  drawer.classList.remove("open"); scrim.classList.remove("open"); drawer.setAttribute("aria-hidden", "true");
  current = null; document.title = "__TITLE__"; state.seg = null; applyFilters();
  if (push && location.hash) history.pushState(null, "", location.pathname + location.search);
  if (lastFocus) lastFocus.focus({ preventScroll: true });
}
function step(d) {
  if (!byId[current]) return;
  const list = state.geo === "all" ? CO : CO.filter(c => c.geo === state.geo);
  let i = list.findIndex(c => c.id === current);
  open(list[(i + d + list.length) % list.length].id);
}
function toSystem(smooth = true) { window.scrollTo({ top: stage.offsetHeight - innerHeight, behavior: smooth && !REDUCED ? "smooth" : "auto" }); }

document.addEventListener("click", e => {
  const t = e.target.closest("[data-id]"); if (t) { open(t.dataset.id); return; }
  if (e.target.closest(".sun")) open("thesis");
});
svg.addEventListener("keydown", e => {
  if (e.key !== "Enter" && e.key !== " ") return;
  const t = e.target.closest("[data-id]"); if (t) { e.preventDefault(); open(t.dataset.id); }
  if (e.target.closest(".sun")) { e.preventDefault(); open("thesis"); }
});
document.getElementById("enter").addEventListener("click", () => toSystem());
document.getElementById("home").addEventListener("click", () => { close(); window.scrollTo({ top: 0, behavior: REDUCED ? "auto" : "smooth" }); });
document.getElementById("nav-thesis").addEventListener("click", () => open("thesis"));
document.getElementById("nav-index").addEventListener("click", () => open("index"));
document.getElementById("bar-index").addEventListener("click", () => open("index"));
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
  if (!drawerOpen()) return;
  if (e.key === "Escape") close();
  if (e.key === "ArrowRight") step(1);
  if (e.key === "ArrowLeft") step(-1);
});
function fromHash() {
  const h = decodeURIComponent(location.hash.slice(1));
  if (h && resolve(h)) { toSystem(false); open(h, false); } else close(false);
}
window.addEventListener("popstate", fromHash);
addEventListener("scroll", applyProgress, { passive: true });
addEventListener("resize", applyProgress);

/* ---------- starfield ---------- */
(function stars() {
  const cv = document.getElementById("stars"), ctx = cv.getContext("2d");
  let W, H, pts = [];
  function seed() {
    const dpr = Math.min(devicePixelRatio || 1, 2); W = innerWidth; H = innerHeight;
    cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    pts = Array.from({ length: Math.round(W * H / 4200) }, () => {
      const z = Math.random();
      return { x: Math.random() * W, y: Math.random() * H, z, r: z < .93 ? .3 + z * .55 : 1 + Math.random() * .7, a: .15 + z * .6, tw: Math.random() * 6.28, sp: .4 + Math.random() * 1.2, warm: Math.random() < .12 };
    });
  }
  function draw(t) {
    ctx.clearRect(0, 0, W, H);
    for (const p of pts) {
      const y = ((p.y - scrollY * (.02 + p.z * .08)) % H + H) % H;
      const a = REDUCED ? p.a : p.a * (.7 + .3 * Math.sin(p.tw + t * .001 * p.sp));
      ctx.fillStyle = p.warm ? `rgba(255,214,170,${a})` : `rgba(210,222,255,${a})`;
      ctx.beginPath(); ctx.arc(p.x, y, p.r, 0, 6.2832); ctx.fill();
    }
  }
  seed();
  addEventListener("resize", seed);
  const loop = t => { draw(t); requestAnimationFrame(loop); };
  requestAnimationFrame(loop);
})();

applyProgress();
applyFilters();
fromHash();
requestAnimationFrame(frame);
</script>
</body>
</html>
"""


def main() -> None:
    data = json.loads(DATA.read_text())
    n = len(data["companies"])
    desc = (f"{n} better-for-you food and beverage brands across the US and Australia, mapped as a solar system "
            f"of consumer need-states. Click any brand for its positioning, channels, funding signal and an investor take.")
    html = (TEMPLATE
            .replace("__TITLE__", data["meta"]["title"])
            .replace("__DESC__", desc)
            .replace("__SITE__", SITE)
            .replace("__MEMO__", MEMO)
            .replace("__REPO__", REPO)
            .replace("__UPDATED__", data["meta"]["updated"])
            .replace("__N__", str(n))
            .replace("__THESIS__", json.dumps(thesis_sections(), ensure_ascii=False))
            .replace("__DATA__", json.dumps(data, ensure_ascii=False)))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"Built {OUT}: {len(data['galaxies'])} orbits, {n} planets, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
