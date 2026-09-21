# Better-for-You Indulgence — Market Map & Memo

A portfolio project by **Arjun Kulshrestha** for consumer VC analyst / associate / scout applications.
US + Australia map of "guilt-free food": brands that let consumers enjoy treats while feeling
healthier, more values-aligned, or less regretful.

## What's here

| File | What it is |
|---|---|
| `output/index.html` | **Interactive elemental space map.** A dark NASA-style universe where each consumer need-state is a living, animated pseudo-3D element — Fire (protein), Crystal (sugar-free sweets), Water (functional drinks), Flora (gut health), Terra (clean-label comfort), Wind (culture-led & kids). Click an element to enter its solar system; the element becomes the sun and the 30 planets are companies. Click a planet for the investor dossier (positioning, differentiation, channels, funding signal, my take, sources). All animation is hand-rolled canvas — no libraries, no internet needed. |
| `output/BFY-Indulgence-Memo-Arjun-Kulshrestha.pdf` | **13-page VC memo** in the same visual language: thesis, category definition, 7 consumer segments, taxonomy, competitive dynamics, 10 white spaces, bear case, investor lens, personal conviction, full company appendix with sources. |
| `data/companies.json` | The company database: 30 brands (15 US/NA, 15 AU) with positioning, target, differentiation, channels, funding/scale signals (flagged verified / company-reported / estimate) and source links. |
| `build_map.py` | Python generator for the interactive map. `python3 build_map.py` |
| `build_memo.py` | Python generator for the memo PDF (requires `reportlab`). `python3 build_memo.py` |

## How to read the map in 30 seconds

- **Elements are need-states, not aisles** — "I refuse to give up sweets" (Crystal), not "low-sugar confectionery".
- **Planet size** = scale signal (revenue / funding). **Ring** = acquired/exited (kept as pricing comps).
  **Pulse** = breakout in flight. **Colour chip** = US / AU / North America.
- Press `Esc` to go back; the **Thesis** button holds the 1-page summary.

## Editing

All content lives in `data/companies.json`. Add or edit a company, then re-run both build scripts.

## How it was built

Built with Claude Code as the implementation tool. The thesis, the six need-state segments, the company research and the investor take on each brand are mine, with funding and scale signals flagged as verified, company-reported or estimate rather than stated flatly. The model wrote the canvas rendering and the PDF generator against that structure.
