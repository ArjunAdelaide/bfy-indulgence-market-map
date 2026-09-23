# Better-for-You Indulgence: Market Map & Memo

**Live map:** https://arjunadelaide.github.io/bfy-indulgence-market-map/
**Memo (PDF):** https://arjunadelaide.github.io/bfy-indulgence-market-map/BFY-Indulgence-Memo-Arjun-Kulshrestha.pdf

A portfolio project by **Arjun Kulshrestha**: a US + Australia map of "guilt-free food", the brands that let
consumers enjoy treats while feeling healthier, more values-aligned, or less regretful. 31 companies across six
consumer need-states, each with positioning, channels, a funding or scale signal, sources, and my investor take.

## What's here

| File | What it is |
|---|---|
| `docs/index.html` | **Interactive 3D space map** (three.js). Each consumer need-state is an element star: Fire (protein), Crystal (sugar-free sweets), Water (functional drinks), Flora (gut health), Terra (clean-label comfort), Wind (culture-led & kids). Click a star to fly into its system, where the planets are companies. Click a planet for the investor dossier: positioning, differentiation, channels, funding signal, my take, sources. Served by GitHub Pages. |
| `docs/BFY-Indulgence-Memo-Arjun-Kulshrestha.pdf` | **13-page memo** in the same visual language: thesis, category definition, 7 consumer segments, taxonomy, competitive dynamics, 10 white spaces, bear case, investor lens, personal conviction, full company appendix with sources. |
| `data/companies.json` | The company database: 31 brands (16 AU, 13 US, 2 Canada) with funding and scale signals flagged as verified, company-reported or estimate, plus source links. |
| `build_map.py` | Generates the map from the data. `python3 build_map.py` |
| `build_memo.py` | Generates the memo PDF (requires `reportlab`). `python3 build_memo.py` |

## How to read the map in 30 seconds

- **Elements are need-states, not aisles.** "I refuse to give up sweets" (Crystal), not "low-sugar confectionery".
- **Planet size** = scale signal (revenue / funding). **Ring** = acquired/exited (kept as pricing comps).
  **Pulse** = breakout in flight. **Colour chip** = US / AU / North America.
- Press `Esc` to go back; the **Thesis** button holds the 1-page summary.

## Changelog

**September 2026**
- Added **NOON** (Fire / Protein as Pleasure): the Australian liquid-breakfast brand that launched nationally in
  Woolworths in January 2026, then in about 2,000 US Target stores in August 2026 on a $2.5M pre-seed led by BFG Partners.
- Updated **David**: parent Medici Brands raised a $250M Series B at a $2.25B valuation (2 Sep 2026), up from $725M
  at the May 2025 Series A; now in 35,000+ retail locations.
- Company counts are now computed from the data rather than hardcoded.
- Published the map and memo on GitHub Pages; added page metadata and fixed a missing document head.

**June 2026**: first version, 30 companies.

## Editing

All content lives in `data/companies.json`. Add or edit a company, then re-run both build scripts.

## How it was built

Built with Claude Code as the implementation tool. The thesis, the six need-state segments, the company research and
the investor take on each brand are mine, with funding and scale signals flagged as verified, company-reported or
estimate rather than stated flatly. The model wrote the 3D rendering and the PDF generator against that structure.
