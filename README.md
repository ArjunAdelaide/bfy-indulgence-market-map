# Better-for-You Indulgence: Market Map & Memo

**Live map:** https://arjunadelaide.github.io/bfy-indulgence-market-map/
**Memo (PDF):** https://arjunadelaide.github.io/bfy-indulgence-market-map/BFY-Indulgence-Memo-Arjun-Kulshrestha.pdf

A portfolio project by **Arjun Kulshrestha**: a US + Australia map of "guilt-free food", the brands that let
consumers enjoy treats while feeling healthier, more values-aligned, or less regretful. 31 companies across six
consumer need-states, each with positioning, channels, a funding or scale signal, sources, and my investor take.

## What's here

| File | What it is |
|---|---|
| `docs/index.html` | **The market map.** Six consumer need-states as columns, split US & Canada / Australia, with every company as a clickable tile. A tile opens the investor dossier: positioning, product, target, differentiation, channels, funding signal with a confidence flag, my take, sources, and peers. Filter by geography and status, search across every field, or switch to a sortable table. Every dossier has its own link (e.g. [`/#noon`](https://arjunadelaide.github.io/bfy-indulgence-market-map/#noon)); segment views too (`/#segment-drinks`). |
| `docs/space.html` | **Space view.** The original 3D (three.js) version: each need-state is an element star and the companies orbit it as planets. |
| `docs/BFY-Indulgence-Memo-Arjun-Kulshrestha.pdf` | **13-page memo** in the same visual language: thesis, category definition, 7 consumer segments, taxonomy, competitive dynamics, 10 white spaces, bear case, investor lens, personal conviction, full company appendix with sources. |
| `data/companies.json` | The company database: 31 brands (16 AU, 13 US, 2 Canada) with funding and scale signals flagged as verified, company-reported or estimate, plus source links. |
| `build_landscape.py` | Generates the market map. `python3 build_landscape.py` |
| `build_map.py` | Generates the space view; also holds the thesis copy both pages use. `python3 build_map.py` |
| `build_memo.py` | Generates the memo PDF (requires `reportlab`). `python3 build_memo.py` |

## How to read the map in 30 seconds

- **Columns are need-states, not aisles.** "I refuse to give up sweets", not "low-sugar confectionery". Click a column header for the segment view (why it matters, maturity, risks).
- **Bars** = scale signal from 1 to 5 (revenue / funding). **Breakout** = growth in flight. **Exited** = acquired, kept as a pricing comp.
- In a dossier, use the arrow keys or the arrow buttons to step through companies, `Esc` to close, and **Copy link** to share it.

## Changelog

**September 2026**
- Rebuilt the main page as a clickable 2D market map with dossiers, filters, search, a table view and deep links. The 3D version is kept as the space view.
- Added **NOON** (Protein as Pleasure): the Australian liquid-breakfast brand that launched nationally in
  Woolworths in January 2026, then in about 2,000 US Target stores in August 2026 on a $2.5M pre-seed led by BFG Partners.
- Updated **David**: parent Medici Brands raised a $250M Series B at a $2.25B valuation (2 Sep 2026), up from $725M
  at the May 2025 Series A; now in 35,000+ retail locations.
- Company counts are now computed from the data rather than hardcoded.
- Published the map and memo on GitHub Pages; added page metadata and fixed a missing document head.

**June 2026**: first version, 30 companies.

## Editing

All content lives in `data/companies.json`. Add or edit a company, then re-run the three build scripts.

## How it was built

Built with Claude Code as the implementation tool. The thesis, the six need-state segments, the company research and
the investor take on each brand are mine, with funding and scale signals flagged as verified, company-reported or
estimate rather than stated flatly. The model wrote the web pages and the PDF generator against that structure.
