#!/usr/bin/env python3
"""
Better-for-You Indulgence: interactive 3D space market map generator.

Reads data/companies.json and emits docs/space.html (the secondary "space view"; the main page is build_landscape.py): a WebGL (three.js)
universe. Each consumer need-state is a glowing element star; click one and
the camera flies into its system, where companies orbit as lit, textured
planets. Click a planet for a full-screen, SpaceX-style company page.

Requires internet at view time (three.js + fonts from CDN).

Usage:  python3 build_map.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "companies.json"
OUT = ROOT / "docs" / "space.html"

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
<meta property="og:url" content="https://arjunadelaide.github.io/bfy-indulgence-market-map/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Inter:wght@400;600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<script type="importmap">
{ "imports": {
  "three": "https://cdn.jsdelivr.net/npm/three@0.165.0/build/three.module.js",
  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.165.0/examples/jsm/"
} }
</script>
<style>
  :root {
    --bg: #030509;
    --line: #1c2747;
    --text: #e8edf8;
    --muted: #8b97b8;
    --accent: #7aa2ff;
    --mono: "JetBrains Mono", ui-monospace, Menlo, monospace;
    --sans: "Inter", -apple-system, "Helvetica Neue", Arial, sans-serif;
    --display: "Space Grotesk", "Inter", -apple-system, sans-serif;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  :root { color-scheme: dark; }
  html, body { height: 100%; overflow: hidden; background: var(--bg); color: var(--text); font-family: var(--sans); }
  ::selection { background: rgba(122,162,255,.35); }

  #scene, #labels { position: fixed; inset: 0; }
  #scene { z-index: 1; }
  #labels { z-index: 2; pointer-events: none; }

  #vignette {
    position: fixed; inset: 0; z-index: 10; pointer-events: none;
    background: radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(0,0,0,.5) 100%);
  }

  /* ---------- chrome ---------- */
  header {
    position: fixed; top: 0; left: 0; right: 0; z-index: 40;
    display: flex; align-items: center; gap: 14px;
    padding: calc(16px + env(safe-area-inset-top, 0px)) 26px 16px;
    background: linear-gradient(180deg, rgba(3,5,9,.85), rgba(3,5,9,0));
    pointer-events: none;
  }
  header > * { pointer-events: auto; }
  .title-block h1 { font-family: var(--display); font-size: 14px; letter-spacing: .24em; text-transform: uppercase; font-weight: 700; }
  .title-block .sub { font-size: 10.5px; color: var(--muted); font-family: var(--mono); letter-spacing: .08em; margin-top: 3px; }
  .spacer { flex: 1; }
  .btn {
    font-family: var(--mono); font-size: 11px; letter-spacing: .2em; text-transform: uppercase;
    color: var(--text); background: none; border: none; border-bottom: 1px solid transparent;
    padding: 8px 4px; margin-left: 18px; cursor: pointer; transition: all .15s;
  }
  .btn:hover { color: #fff; border-bottom-color: rgba(255,255,255,.65); }
  .btn.hidden { display: none; }

  .crumb {
    position: fixed; top: calc(64px + env(safe-area-inset-top, 0px)); left: 28px; z-index: 40;
    font-family: var(--mono); font-size: 10px; letter-spacing: .14em;
    color: var(--muted); text-transform: uppercase;
    text-shadow: 0 1px 8px rgba(3,5,9,.9);
  }
  .crumb b { color: var(--accent); font-weight: 600; }

  .legend {
    position: fixed; left: 28px; bottom: calc(22px + env(safe-area-inset-bottom, 0px)); z-index: 40;
    display: flex; align-items: center; gap: 16px;
    font-family: var(--mono); font-size: 9px; letter-spacing: .16em; color: var(--muted);
    text-transform: uppercase; text-shadow: 0 1px 8px rgba(3,5,9,.9);
  }
  .legend span { display: flex; align-items: center; gap: 6px; }
  .legend .lsep { width: 1px; height: 12px; background: rgba(140,160,210,.3); }
  .dot { width: 7px; height: 7px; border-radius: 50%; flex: none; display: inline-block; }
  .dot.us { background: #6ea8ff; } .dot.au { background: #ffc861; } .dot.na { background: #58d6c9; }

  .hint {
    position: fixed; bottom: calc(22px + env(safe-area-inset-bottom, 0px)); right: 28px; z-index: 40;
    font-family: var(--mono); font-size: 10px; letter-spacing: .12em; color: var(--muted);
    text-transform: uppercase; text-shadow: 0 1px 8px rgba(3,5,9,.9);
  }
  .hint::after { content: "\258D"; margin-left: 6px; color: var(--accent); animation: blink 1.2s steps(1) infinite; }
  @keyframes blink { 50% { opacity: 0; } }

  /* ---------- 3D labels ---------- */
  .e-label { text-align: center; pointer-events: auto; cursor: pointer; user-select: none; transform: translateY(8px); }
  .e-label .k { font-family: var(--mono); font-size: 9px; letter-spacing: .3em; text-transform: uppercase; }
  .e-label .n { font-family: var(--display); font-size: 17px; font-weight: 500; letter-spacing: .06em; text-transform: uppercase; margin-top: 5px; color: #f2f5fc; }
  .e-label .d { font-size: 11px; color: var(--muted); max-width: 240px; margin: 5px auto 0; line-height: 1.5; }
  .e-label .m { font-family: var(--mono); font-size: 8.5px; letter-spacing: .14em; color: var(--muted); margin-top: 6px; }
  .e-label * { text-shadow: 0 1px 10px rgba(3,5,9,.95), 0 0 24px rgba(3,5,9,.8); }
  .e-label:hover .n { color: #fff; }

  .p-label { text-align: center; pointer-events: auto; cursor: pointer; user-select: none; transform: translateY(6px); }
  .p-label .n {
    display: inline-flex; align-items: center; gap: 7px;
    font-size: 11.5px; font-weight: 600; color: #eef2fb; white-space: nowrap;
    text-shadow: 0 1px 10px rgba(3,5,9,.95);
  }
  .p-label .n i { width: 6px; height: 6px; border-radius: 50%; flex: none; }
  .p-label .g { font-family: var(--mono); font-size: 8px; letter-spacing: .22em; color: var(--muted); margin-top: 3px; text-shadow: 0 1px 8px rgba(3,5,9,.95); }

  /* ---------- company page (full-screen, minimal) ---------- */
  #company {
    position: fixed; inset: 0; z-index: 55;
    background: rgba(3,5,9,.93); backdrop-filter: blur(16px);
    opacity: 0; pointer-events: none; transition: opacity .35s ease;
    overflow-y: auto;
  }
  #company.open { opacity: 1; pointer-events: auto; }
  #company .close { position: fixed; top: calc(18px + env(safe-area-inset-top, 0px)); right: 28px; z-index: 56; }
  #company::-webkit-scrollbar { width: 5px; }
  #company::-webkit-scrollbar-thumb { background: var(--line); border-radius: 3px; }
  .c-inner { max-width: 1020px; margin: 0 auto; padding: 110px 40px 90px; }
  .c-kicker { font-family: var(--mono); font-size: 10px; letter-spacing: .3em; text-transform: uppercase; color: var(--muted); }
  .c-name {
    font-family: var(--display); font-weight: 500; text-transform: uppercase;
    font-size: clamp(40px, 7vw, 76px); line-height: 1.04; letter-spacing: .02em;
    margin: 20px 0 16px;
  }
  .c-pos { font-size: 17px; line-height: 1.65; color: #c4d0ea; max-width: 640px; }
  .c-rule { height: 1px; margin: 42px 0; }
  .c-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 36px 44px; }
  #company .k { font-family: var(--mono); font-size: 9px; letter-spacing: .26em; text-transform: uppercase; color: var(--muted); margin-bottom: 10px; }
  .c-field .v { font-size: 13.5px; line-height: 1.75; color: #dbe3f4; }
  .c-signal { margin-top: 48px; }
  .c-signal .v { font-size: 16px; line-height: 1.7; color: #eef2fb; max-width: 760px; }
  .c-take { margin-top: 48px; padding-left: 28px; border-left: 1px solid rgba(255,255,255,.35); }
  .c-take .v { font-family: var(--display); font-weight: 500; font-size: 19px; line-height: 1.6; color: #f2f5fc; max-width: 720px; }
  .c-src { margin-top: 56px; }
  .c-src a {
    display: inline-block; margin: 0 26px 8px 0;
    font-family: var(--mono); font-size: 10px; letter-spacing: .08em;
    color: var(--muted); text-decoration: none;
    border-bottom: 1px solid rgba(255,255,255,.18); padding-bottom: 2px;
  }
  .c-src a:hover { color: #fff; border-color: #fff; }

  /* ---------- overlays ---------- */
  .overlay {
    position: fixed; inset: 0; z-index: 60; background: rgba(3,5,9,.92); backdrop-filter: blur(10px);
    display: none; align-items: flex-start; justify-content: center; overflow-y: auto; padding: 80px 20px 60px;
  }
  .overlay.open { display: flex; }
  .sheet { max-width: 740px; position: relative; padding: 0 20px; }
  .sheet .close { position: fixed; top: calc(18px + env(safe-area-inset-top, 0px)); right: 28px; }
  .sheet h2 { font-family: var(--display); font-size: 26px; font-weight: 500; letter-spacing: .1em; text-transform: uppercase; margin-bottom: 6px; }
  .sheet .mono-sub { font-family: var(--mono); font-size: 10px; letter-spacing: .2em; color: var(--muted); margin-bottom: 30px; text-transform: uppercase; }
  .sheet h3 { font-family: var(--mono); font-size: 10px; letter-spacing: .26em; text-transform: uppercase; color: var(--accent); margin: 30px 0 10px; }
  .sheet p, .sheet li { font-size: 14px; line-height: 1.75; color: #cfd8ec; }
  .sheet ul { padding-left: 20px; }
  .sheet b { color: var(--text); }

  #fallback {
    position: fixed; inset: 0; z-index: 5; display: none;
    align-items: center; justify-content: center; text-align: center;
    color: var(--muted); font-family: var(--mono); font-size: 12px; line-height: 2;
  }

  /* ---------- phone ---------- */
  @media (max-width: 720px) {
    header { padding: 12px 16px; gap: 8px; flex-wrap: wrap; }
    .title-block h1 { font-size: 11px; letter-spacing: .18em; }
    .title-block .sub { display: none; }
    .btn { margin-left: 12px; font-size: 10px; letter-spacing: .14em; }
    .crumb { top: 52px; left: 16px; right: 16px; font-size: 9px; }
    .legend { left: 16px; right: 16px; bottom: 16px; gap: 10px; flex-wrap: wrap; font-size: 8px; }
    .legend .lsep { display: none; }
    .hint { display: none; }
    .e-label .n { font-size: 13px; }
    .e-label .d { display: none; }
    .e-label .m { font-size: 7.5px; }
    .c-inner { padding: 86px 20px 70px; }
    .c-pos { font-size: 15px; }
    .c-take { padding-left: 16px; }
    .c-take .v { font-size: 16px; }
    .sheet { padding: 0 4px; }
    .sheet h2 { font-size: 20px; }
  }
</style>
</head>
<body>

<canvas id="scene"></canvas>
<div id="labels"></div>
<div id="vignette"></div>
<div id="fallback">3D scene requires an internet connection<br>(three.js loads from CDN)</div>

<header>
  <div class="title-block">
    <h1>__TITLE__</h1>
    <div class="sub">__SUBTITLE__ · UPDATED __UPDATED__</div>
  </div>
  <div class="spacer"></div>
  <a class="btn" href="./" style="text-decoration:none">&larr; Market map</a>
  <button class="btn" id="btn-thesis">Thesis</button>
  <button class="btn" id="btn-howto">How to read</button>
  <button class="btn hidden" id="btn-back">&larr; Universe</button>
</header>

<div class="crumb" id="crumb">UNIVERSE / <b>__COUNTS__</b></div>

<div class="legend">
  <span><i class="dot us"></i>US</span>
  <span><i class="dot au"></i>AU</span>
  <span><i class="dot na"></i>N.AM</span>
  <span class="lsep"></span>
  <span>RING = EXITED</span>
  <span>PULSE = BREAKOUT</span>
  <span>SIZE = SCALE</span>
</div>

<div class="hint" id="hint">Click an element star to fly in</div>

<section id="company"><button class="btn close" onclick="closeDossier()">Close &nbsp;&times;</button><div class="c-inner" id="company-body"></div></section>

<div class="overlay" id="ov-thesis">
  <div class="sheet">
    <button class="btn close" onclick="toggleOverlay('ov-thesis')">Close &nbsp;&times;</button>
    <h2>The 1-Page Thesis</h2>
    <div class="mono-sub">BETTER-FOR-YOU INDULGENCE · ARJUN KULSHRESTHA · __UPDATED__</div>
    <h3>Why now</h3>
    <p>Health stopped being a sacrifice aesthetic and became a status aesthetic. Protein, gut health and "no added sugar" are now how mainstream consumers shop the treat aisle, and GLP-1 adoption (~1 in 8 US adults) is compressing appetite while raising the bar for what a snack must justify. Indulgence occasions aren't disappearing; they're being re-priced and re-formulated.</p>
    <h3>The proof it's venture-scale</h3>
    <p>PepsiCo paid <b>$1.95B for Poppi</b> (2025). OLIPOP reached a <b>$1.85B valuation, profitably</b>. Hershey paid <b>~$750M for LesserEvil</b>; PepsiCo <b>$1.2B for Siete</b>. <b>David</b> hit ~$100M year-one revenue at a $725M valuation, then raised at <b>$2.25B</b> in September 2026. Strategics have stalled innovation engines and are paying 3–4x revenue for brands that own a need-state.</p>
    <h3>Why startups win</h3>
    <p>Incumbents can't make these products without indicting their core portfolio, and their brands carry zero permission in health. Startups win on founder taste, formulation speed, and audiences they bring with them (Feastables: $0&rarr;$250M in &lt;3 yrs on creator distribution).</p>
    <h3>The Australia angle</h3>
    <p>AU runs the US playbook with a 2–3 year lag, a chemist-channel beachhead US brands don't have (Chemist Warehouse), the world's most consolidated grocery duopoly (brutal, but national in one deal), and structural kids'-snack demand via school canteen policy. Remedy (~A$163M rev) and Noshu (A$4M&rarr;A$38M in 4 yrs) prove local scale; FUNDAY proves exportability; NOON went from national Woolworths (Jan 2026) to about 2,000 US Target stores (Aug 2026).</p>
    <h3>What the best companies understand</h3>
    <p>Taste parity is the entry ticket, not the win. The win is <b>repeat purchase</b> (habit formats beat novelty), <b>supply-chain ownership</b> (David bought its ingredient supplier; LesserEvil self-manufactures), and <b>distribution as moat</b>: a creator audience, a pharmacy chain, or a school canteen list.</p>
    <h3>Where I'd be careful</h3>
    <p>US healthy soda is post-peak for new entrants. Gummies are crowded. Claims risk is real (Poppi settled a prebiotic class action pre-exit). And the best operators (Chomps, ~$900M rev, near-bootstrapped) sometimes don't need venture money at all. Founder selection is the whole game.</p>
  </div>
</div>

<div class="overlay" id="ov-howto">
  <div class="sheet">
    <button class="btn close" onclick="toggleOverlay('ov-howto')">Close &nbsp;&times;</button>
    <h2>How to read this map</h2>
    <div class="mono-sub">ORIENTATION BRIEF · 30 SECONDS</div>
    <ul>
      <li><b>The six element stars are consumer need-states</b>, not product aisles. Fire is the drive to earn a treat (protein); Water is the ritual of refreshment; Crystal is sweetness with the sugar removed; Terra is grounded comfort food; Flora is the living gut; Wind is culture and the lunchbox.</li>
      <li><b>Click a star</b> and the camera flies into its system. <b>Planets are companies</b>: size = scale signal, a ring = acquired/exited (kept as pricing comps), a pulse = breakout in flight, the label dot = US / AU / North America.</li>
      <li><b>Click a planet</b> for the investor page: positioning, differentiation, channels, funding signal, and my take.</li>
      <li><b>__NC__ companies, startup-weighted, ~50/50 US and Australia.</b> Facts are flagged verified / company-reported / estimate, with sources.</li>
      <li>Press <b>Esc</b> to fly back out. Drag does nothing; this map flies itself.</li>
    </ul>
  </div>
</div>

<script>
/* non-module globals shared with the module scene code */
const DATA = __DATA__;
const ELEMENTS = {
  protein:   { label: "Fire",    kicker: "ELEMENT 01" },
  sugarfree: { label: "Crystal", kicker: "ELEMENT 02" },
  drinks:    { label: "Water",   kicker: "ELEMENT 03" },
  gut:       { label: "Flora",   kicker: "ELEMENT 04" },
  comfort:   { label: "Terra",   kicker: "ELEMENT 05" },
  culture:   { label: "Wind",    kicker: "ELEMENT 06" }
};
const geoColor = { US: '#6ea8ff', AU: '#ffc861', NA: '#58d6c9' };
const geoLabel = { US: 'USA', AU: 'AUS', NA: 'N.AM' };
const esc = s => (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;');

const company = document.getElementById('company');
function openDossier(c, g) {
  const statusTxt = { exited: 'ACQUIRED', breakout: 'BREAKOUT', independent: 'INDEPENDENT' }[c.status];
  const host = u => { try { return new URL(u).hostname.replace('www.', ''); } catch { return u; } };
  document.getElementById('company-body').innerHTML = `
    <div class="c-kicker"><span style="color:${g.color}">${ELEMENTS[g.id].label.toUpperCase()} / ${esc(g.name).toUpperCase()}</span>
      &nbsp;·&nbsp; ${geoLabel[c.geo]} &nbsp;·&nbsp; ${statusTxt}</div>
    <div class="c-name">${esc(c.name)}</div>
    <div class="c-pos">${esc(c.positioning)}.</div>
    <div class="c-rule" style="background:linear-gradient(90deg, ${g.color}, rgba(255,255,255,.05))"></div>
    <div class="c-grid">
      <div class="c-field"><div class="k">Core Product</div><div class="v">${esc(c.product)}</div></div>
      <div class="c-field"><div class="k">Target Consumer</div><div class="v">${esc(c.target)}</div></div>
      <div class="c-field"><div class="k">Differentiation</div><div class="v">${esc(c.differentiation)}</div></div>
      <div class="c-field"><div class="k">Distribution</div><div class="v">${esc(c.channels)}</div></div>
    </div>
    <div class="c-field c-signal"><div class="k">Funding / Scale Signal</div><div class="v">${esc(c.signal)}</div></div>
    <div class="c-take"><div class="k" style="color:${g.color}">Why It Matters</div><div class="v">${esc(c.vc_take)}</div></div>
    <div class="c-field c-src"><div class="k">Sources</div>
      ${c.sources.map((s, i) => `<a href="${s}" target="_blank" rel="noopener">[${String(i+1).padStart(2,'0')}] ${esc(host(s))}</a>`).join('')}
    </div>`;
  company.classList.add('open');
  company.scrollTop = 0;
}
function closeDossier() { company.classList.remove('open'); }
function toggleOverlay(id) { document.getElementById(id).classList.toggle('open'); }
document.getElementById('btn-thesis').onclick = () => toggleOverlay('ov-thesis');
document.getElementById('btn-howto').onclick = () => toggleOverlay('ov-howto');
</script>

<script type="module">
import * as THREE from 'three';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

/* ================= renderer / scene ================= */
const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x030509);
scene.fog = new THREE.FogExp2(0x030509, 0.0028);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 3000);

const labelRenderer = new CSS2DRenderer({ element: document.getElementById('labels') });
labelRenderer.setSize(innerWidth, innerHeight);

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), 0.9, 0.65, 0.18);
composer.addPass(bloom);

scene.add(new THREE.AmbientLight(0x445577, 0.55));

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  composer.setSize(innerWidth, innerHeight);
  labelRenderer.setSize(innerWidth, innerHeight);
});

/* ================= textures ================= */
function glowTexture(hex) {
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const x = c.getContext('2d');
  const g = x.createRadialGradient(64, 64, 0, 64, 64, 64);
  g.addColorStop(0, hex + 'ff');
  g.addColorStop(0.25, hex + '66');
  g.addColorStop(1, hex + '00');
  x.fillStyle = g; x.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
}

function planetTexture(baseHex, seed) {
  const c = document.createElement('canvas');
  c.width = 256; c.height = 128;
  const x = c.getContext('2d');
  const base = new THREE.Color(baseHex);
  let s = seed;
  const rand = () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
  // latitudinal bands, hue-shifted around the element colour
  for (let y = 0; y < 128; y += 2) {
    const f = 0.55 + 0.45 * Math.sin(y * 0.12 + seed) * rand();
    const col = base.clone().multiplyScalar(0.45 + f * 0.65);
    x.fillStyle = '#' + col.getHexString();
    x.fillRect(0, y, 256, 2);
  }
  // speckle
  for (let i = 0; i < 700; i++) {
    const a = 0.04 + rand() * 0.10;
    x.fillStyle = rand() > 0.5 ? `rgba(255,255,255,${a})` : `rgba(0,0,10,${a})`;
    x.fillRect(rand() * 256, rand() * 128, 1 + rand() * 2, 1 + rand() * 2);
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/* ================= starfield ================= */
const roundStarTex = (() => {
  const c = document.createElement('canvas');
  c.width = c.height = 32;
  const x = c.getContext('2d');
  const g = x.createRadialGradient(16, 16, 0, 16, 16, 16);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.4, 'rgba(255,255,255,.6)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  x.fillStyle = g; x.fillRect(0, 0, 32, 32);
  return new THREE.CanvasTexture(c);
})();

function starField(count, spreadMin, spreadMax, size, opacity, tint) {
  const pos = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const r = spreadMin + Math.random() * (spreadMax - spreadMin);
    const th = Math.random() * Math.PI * 2;
    const ph = Math.acos(Math.random() * 2 - 1);
    pos[i*3]     = r * Math.sin(ph) * Math.cos(th);
    pos[i*3 + 1] = r * Math.cos(ph) * 0.6;
    pos[i*3 + 2] = r * Math.sin(ph) * Math.sin(th);
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const mat = new THREE.PointsMaterial({
    color: tint, size, sizeAttenuation: true, map: roundStarTex,
    transparent: true, opacity, depthWrite: false, blending: THREE.AdditiveBlending
  });
  return new THREE.Points(geo, mat);
}
scene.add(starField(5200, 150, 900, 1.5, 0.85, 0xcfe0ff));
scene.add(starField(1400, 120, 700, 2.6, 0.6, 0xfff0d8));
scene.add(starField(2400, 300, 1400, 1.1, 0.5, 0x9fb6ff));

// faint distant nebula sprites, restrained, not wallpaper
const nebTints = ['#2a2a55', '#1d2b50', '#33224d'];
for (let i = 0; i < 5; i++) {
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({
    map: glowTexture(nebTints[i % 3]), transparent: true, opacity: 0.16,
    depthWrite: false, blending: THREE.AdditiveBlending
  }));
  const th = i / 5 * Math.PI * 2;
  sp.position.set(Math.cos(th) * 420, (Math.random() - 0.5) * 160, Math.sin(th) * 420);
  sp.scale.setScalar(500 + Math.random() * 350);
  scene.add(sp);
}

/* ================= element stars ================= */
const RING = 46;
const universe = new THREE.Group();
scene.add(universe);
const stars = [];   // {g, mesh, group, light, label, halo}

DATA.galaxies.forEach((g, i) => {
  const ang = i / DATA.galaxies.length * Math.PI * 2;
  const pos = new THREE.Vector3(
    Math.cos(ang) * RING,
    Math.sin(ang * 2) * 4,
    Math.sin(ang) * RING
  );
  const group = new THREE.Group();
  group.position.copy(pos);

  const isCrystal = g.id === 'sugarfree';
  const geo = isCrystal
    ? new THREE.IcosahedronGeometry(2.4, 0)
    : new THREE.SphereGeometry(2.2, 48, 48);
  const mesh = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: g.color }));
  if (isCrystal) {
    mesh.add(new THREE.LineSegments(
      new THREE.EdgesGeometry(geo),
      new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.5 })
    ));
  }
  mesh.userData = { type: 'star', idx: i };
  group.add(mesh);

  const halo = new THREE.Sprite(new THREE.SpriteMaterial({
    map: glowTexture(g.color), transparent: true, opacity: 0.85,
    depthWrite: false, blending: THREE.AdditiveBlending
  }));
  halo.scale.setScalar(10);
  halo.material.opacity = 0.6;
  group.add(halo);

  const light = new THREE.PointLight(new THREE.Color(g.color), 600, 90, 1.8);
  group.add(light);

  const n = DATA.companies.filter(c => c.galaxy === g.id).length;
  const div = document.createElement('div');
  div.className = 'e-label';
  div.innerHTML = `
    <div class="k" style="color:${g.color}">${ELEMENTS[g.id].kicker} · ${ELEMENTS[g.id].label.toUpperCase()}</div>
    <div class="n">${esc(g.name)}</div>
    <div class="d">&ldquo;${esc(g.need_state)}&rdquo;</div>
    <div class="m">${n} COMPANIES &middot; ${esc(g.maturity).toUpperCase()} &middot; VC ${esc(g.vc_attractiveness).toUpperCase()}</div>`;
  div.onclick = () => enterSystem(i);
  const label = new CSS2DObject(div);
  label.position.set(0, -5.8, 0);
  group.add(label);

  universe.add(group);
  stars.push({ g, mesh, group, light, label, halo });
});

/* ================= planets (built per system) ================= */
let planets = [];        // {c, mesh, label, angle, speed, radius, baseScale}
let planetGroup = null;

function buildSystem(star) {
  planetGroup = new THREE.Group();
  planetGroup.position.copy(star.group.position);
  const comps = DATA.companies.filter(c => c.galaxy === star.g.id)
    .sort((a, b) => b.scale - a.scale);
  comps.forEach((c, i) => {
    const radius = 6.5 + i * 2.9;
    const size = 0.55 + c.scale * 0.30;
    const tex = planetTexture(star.g.color, 7 + i * 131 + c.name.length);
    const mesh = new THREE.Mesh(
      new THREE.SphereGeometry(size, 36, 36),
      new THREE.MeshStandardMaterial({
        map: tex, roughness: 0.85, metalness: 0.05,
        emissive: new THREE.Color(c.status === 'breakout' ? star.g.color : '#000000'),
        emissiveIntensity: 0.0
      })
    );
    mesh.userData = { type: 'planet', c, g: star.g };
    mesh.rotation.z = 0.3;

    if (c.status === 'exited') {
      const ring = new THREE.Mesh(
        new THREE.RingGeometry(size * 1.5, size * 2.05, 48),
        new THREE.MeshBasicMaterial({ color: 0xdde6f8, transparent: true, opacity: 0.38, side: THREE.DoubleSide })
      );
      ring.rotation.x = Math.PI / 2.4;
      mesh.add(ring);
    }

    const div = document.createElement('div');
    div.className = 'p-label';
    div.innerHTML = `
      <div class="n"><i style="background:${geoColor[c.geo]}"></i>${esc(c.name)}</div>
      <div class="g">${geoLabel[c.geo]}</div>`;
    div.onclick = () => openDossier(c, star.g);
    const label = new CSS2DObject(div);
    label.position.set(0, -size - 0.9, 0);
    mesh.add(label);

    const angle = i * 2.39996;  // golden angle spread
    planetGroup.add(mesh);
    planets.push({ c, mesh, label, angle, speed: 0.10 / Math.sqrt(radius / 6.5), radius, baseScale: 1 });
  });
  scene.add(planetGroup);
}

function clearSystem() {
  if (!planetGroup) return;
  for (const p of planets) p.mesh.remove(p.label);
  scene.remove(planetGroup);
  planetGroup.traverse(o => {
    if (o.geometry) o.geometry.dispose();
    if (o.material) { if (o.material.map) o.material.map.dispose(); o.material.dispose(); }
  });
  planetGroup = null;
  planets = [];
}

/* ================= camera & modes ================= */
let mode = 'universe';
let activeStar = null;
let orbitAngle = 0.6;
let tween = null;
const camTarget = new THREE.Vector3(0, 0, 0);
const mouse = { x: 0, y: 0 };
addEventListener('mousemove', e => {
  mouse.x = e.clientX / innerWidth - 0.5;
  mouse.y = e.clientY / innerHeight - 0.5;
});

/* narrow viewports see a slimmer horizontal FOV, so pull the camera back so the
   whole ring still fits. Desktop (aspect >= 1.7) keeps its original framing. */
function aspectBoost() {
  const ref = 1.7;
  return camera.aspect >= ref ? 1 : ref / Math.max(camera.aspect, 0.42);
}
function universeCamPos(a) {
  const d = 105 * aspectBoost();
  return new THREE.Vector3(Math.sin(a) * d, (30 + Math.sin(a * 0.6) * 5) * aspectBoost(), Math.cos(a) * d);
}
function systemCamPos(p, mx, my) {
  const k = aspectBoost();
  return p.clone()
    .add(p.clone().normalize().multiplyScalar(24 * k))
    .add(new THREE.Vector3(mx, 9 * k - my, 0));
}
camera.position.copy(universeCamPos(orbitAngle));
camera.lookAt(0, 0, 0);

function flyTo(pos, target, dur) {
  tween = {
    t: 0, dur,
    fromPos: camera.position.clone(), toPos: pos.clone(),
    fromTarget: camTarget.clone(), toTarget: target.clone()
  };
}
const easeInOut = t => t < 0.5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3) / 2;

function enterSystem(idx) {
  if (mode === 'flying') return;
  const star = stars[idx];
  activeStar = star;
  mode = 'flying';
  clearSystem();
  buildSystem(star);
  // hide other labels
  stars.forEach(s => { s.label.element.style.display = 'none'; });
  const p = star.group.position;
  flyTo(systemCamPos(p, 0, 0), p, 1.8);
  setTimeout(() => { mode = 'system'; }, 1850);
  document.getElementById('btn-back').classList.remove('hidden');
  document.getElementById('crumb').innerHTML =
    `UNIVERSE / ${ELEMENTS[star.g.id].label.toUpperCase()} / <b>${esc(star.g.name).toUpperCase()}</b> · ${esc(star.g.maturity).toUpperCase()} · VC ${esc(star.g.vc_attractiveness).toUpperCase()}`;
  document.getElementById('hint').textContent = 'Click a planet for the investor page';
}

function backToUniverse() {
  if (mode === 'flying') return;
  closeDossier();
  mode = 'flying';
  stars.forEach(s => { s.label.element.style.display = ''; });
  flyTo(universeCamPos(orbitAngle), new THREE.Vector3(0, 0, 0), 1.6);
  setTimeout(() => { mode = 'universe'; clearSystem(); activeStar = null; }, 1650);
  document.getElementById('btn-back').classList.add('hidden');
  document.getElementById('crumb').innerHTML = 'UNIVERSE / <b>__COUNTS__</b>';
  document.getElementById('hint').textContent = 'Click an element star to fly in';
}
document.getElementById('btn-back').onclick = backToUniverse;
addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.overlay.open').forEach(o => o.classList.remove('open'));
    if (company.classList.contains('open')) closeDossier();
    else if (mode === 'system') backToUniverse();
  }
});

/* ================= picking ================= */
const ray = new THREE.Raycaster();
const clickPt = new THREE.Vector2();
canvas.addEventListener('click', e => {
  clickPt.x = (e.clientX / innerWidth) * 2 - 1;
  clickPt.y = -(e.clientY / innerHeight) * 2 + 1;
  ray.setFromCamera(clickPt, camera);
  if (mode === 'universe') {
    const hits = ray.intersectObjects(stars.map(s => s.mesh));
    if (hits.length) enterSystem(hits[0].object.userData.idx);
  } else if (mode === 'system') {
    const hits = ray.intersectObjects(planets.map(p => p.mesh));
    if (hits.length) {
      const u = hits[0].object.userData;
      openDossier(u.c, u.g);
    }
  }
});
canvas.addEventListener('mousemove', e => {
  clickPt.x = (e.clientX / innerWidth) * 2 - 1;
  clickPt.y = -(e.clientY / innerHeight) * 2 + 1;
  ray.setFromCamera(clickPt, camera);
  const targets = mode === 'universe' ? stars.map(s => s.mesh)
                : mode === 'system' ? planets.map(p => p.mesh) : [];
  canvas.style.cursor = targets.length && ray.intersectObjects(targets).length ? 'pointer' : 'default';
});

/* ================= main loop ================= */
const clock = new THREE.Clock();
function loop() {
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // element stars idle motion
  stars.forEach((s, i) => {
    s.mesh.rotation.y += dt * 0.25;
    if (s.g.id === 'sugarfree') s.mesh.rotation.x += dt * 0.18;
    const pulse = 1 + 0.04 * Math.sin(t * 1.4 + i);
    s.halo.scale.setScalar(10 * pulse);
    s.group.position.y += Math.sin(t * 0.7 + i * 1.1) * 0.0035;
  });

  // planets orbit
  for (const p of planets) {
    p.angle += p.speed * dt;
    p.mesh.position.set(Math.cos(p.angle) * p.radius, Math.sin(p.angle * 0.7) * 0.8, Math.sin(p.angle) * p.radius);
    p.mesh.rotation.y += dt * 0.5;
    if (p.c.status === 'breakout') {
      p.mesh.material.emissiveIntensity = 0.25 + 0.2 * Math.sin(t * 2.4);
    }
  }

  // camera
  if (tween) {
    tween.t += dt;
    const k = easeInOut(Math.min(tween.t / tween.dur, 1));
    camera.position.lerpVectors(tween.fromPos, tween.toPos, k);
    camTarget.lerpVectors(tween.fromTarget, tween.toTarget, k);
    if (tween.t >= tween.dur) tween = null;
  } else if (mode === 'universe') {
    orbitAngle += dt * 0.018;
    const base = universeCamPos(orbitAngle);
    camera.position.lerp(base.add(new THREE.Vector3(mouse.x * 6, -mouse.y * 4, 0)), 0.05);
    camTarget.lerp(new THREE.Vector3(0, 0, 0), 0.05);
  } else if (mode === 'system' && activeStar) {
    const p = activeStar.group.position;
    camera.position.lerp(systemCamPos(p, mouse.x * 4, mouse.y * 3), 0.04);
    camTarget.lerp(p, 0.06);
  }
  camera.lookAt(camTarget);

  composer.render();
  labelRenderer.render(scene, camera);
  requestAnimationFrame(loop);
}
loop();
window.THREE_OK = true;
</script>
<script>
/* CDN failure fallback */
setTimeout(() => {
  if (!window.THREE_OK) document.getElementById('fallback').style.display = 'flex';
}, 5000);
</script>
</body>
</html>
"""


def main() -> None:
    data = json.loads(DATA.read_text())
    html = (TEMPLATE
        .replace("__TITLE__", data["meta"]["title"])
        .replace("__DESC__", f"{len(data['companies'])} better-for-you food and beverage brands across the US and Australia, mapped by consumer need-state, with an investor memo. By Arjun Kulshrestha.")
        .replace("__SUBTITLE__", data["meta"]["subtitle"])
        .replace("__UPDATED__", data["meta"]["updated"].upper())
        .replace("__COUNTS__", f"{len(data['galaxies'])} ELEMENTS · {len(data['companies'])} COMPANIES · US + AU")
        .replace("__NC__", str(len(data["companies"])))
        .replace("__DATA__", json.dumps(data, ensure_ascii=False)))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html)
    print(f"Built {OUT}: {len(data['galaxies'])} element stars, "
          f"{len(data['companies'])} planets, {OUT.stat().st_size//1024} KB (WebGL)")


if __name__ == "__main__":
    main()
