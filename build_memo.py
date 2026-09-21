#!/usr/bin/env python3
"""
Better-for-You Indulgence — concise VC memo (PDF).

Reads data/companies.json and emits output/BFY-Indulgence-Memo-Arjun-Kulshrestha.pdf.
Dark NASA/SpaceX aesthetic to match the interactive space map.

Usage:  python3 build_memo.py
"""

import json
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).parent
DATA = json.loads((ROOT / "data" / "companies.json").read_text())
OUT = ROOT / "output" / "BFY-Indulgence-Memo-Arjun-Kulshrestha.pdf"

# ---------- palette ----------
BG = HexColor("#070b16")
PANEL = HexColor("#0e1528")
LINE = HexColor("#22305a")
TEXT = HexColor("#e8edf8")
MUTED = HexColor("#93a0c2")
ACCENT = HexColor("#7aa2ff")
GOOD = HexColor("#43d9a3")
WARN = HexColor("#ffc861")
PINK = HexColor("#e84393")

W, H = A4

# ---------- styles ----------
def st(name, **kw):
    base = dict(fontName="Helvetica", fontSize=9.2, leading=13.6, textColor=TEXT)
    base.update(kw)
    return ParagraphStyle(name, **base)

S = {
    "kicker": st("kicker", fontName="Courier", fontSize=8, leading=11, textColor=MUTED),
    "h1": st("h1", fontName="Helvetica-Bold", fontSize=19, leading=23, textColor=TEXT, spaceAfter=4),
    "h2": st("h2", fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=ACCENT, spaceBefore=12, spaceAfter=4),
    "h3": st("h3", fontName="Helvetica-Bold", fontSize=9.6, leading=13, textColor=WARN, spaceBefore=8, spaceAfter=2),
    "body": st("body", spaceAfter=5),
    "small": st("small", fontSize=8.2, leading=11.6, textColor=MUTED, spaceAfter=4),
    "quote": st("quote", fontName="Helvetica-Oblique", fontSize=10.5, leading=15.5, textColor=HexColor("#c4d2f2"), leftIndent=10, spaceAfter=6),
    "cover_t": st("cover_t", fontName="Helvetica-Bold", fontSize=30, leading=35, textColor=TEXT, alignment=TA_CENTER),
    "cover_s": st("cover_s", fontName="Courier", fontSize=10, leading=15, textColor=MUTED, alignment=TA_CENTER),
    "cell": st("cell", fontSize=7.4, leading=10.2),
    "cellm": st("cellm", fontSize=7.4, leading=10.2, textColor=MUTED),
    "cellh": st("cellh", fontName="Helvetica-Bold", fontSize=7.4, leading=10, textColor=ACCENT),
}

def sanitize(text):
    return (text.replace("\u2192", "-&gt;")   # arrow
                .replace("\u2248", "~")       # approx
                .replace("\u25cf", "&bull;")
                .replace("\u25c9", "&bull;")
                .replace("\u25cb", "o"))


def P(text, style="body"):
    return Paragraph(sanitize(text), S[style])


# ---------- page furniture ----------
def paint(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0, 0, W, H, stroke=0, fill=1)
    # star speckle, deterministic
    canvas.setFillColor(HexColor("#2c3a66"))
    seed = 49297
    for i in range(110):
        seed = (seed * 9301 + 49297) % 233280
        x = (seed / 233280) * W
        seed = (seed * 9301 + 49297) % 233280
        y = (seed / 233280) * H
        r = 0.5 + (i % 3) * 0.25
        canvas.circle(x, y, r, stroke=0, fill=1)
    # footer
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(18 * mm, 13 * mm, W - 18 * mm, 13 * mm)
    canvas.setFont("Courier", 6.8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9.2 * mm, "BETTER-FOR-YOU INDULGENCE - MARKET MAP & MEMO - ARJUN KULSHRESTHA")
    canvas.drawRightString(W - 18 * mm, 9.2 * mm, f"JUNE 2026 - PAGE {doc.page:02d}")
    canvas.restoreState()


def rule(color=LINE, width=0.7, space=6):
    t = Table([[""]], colWidths=[W - 36 * mm], rowHeights=[0.1])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), width, color)]))
    return [Spacer(1, space), t, Spacer(1, space)]


def box(flowables, border=LINE, back=PANEL, pad=8):
    t = Table([[flowables]], colWidths=[W - 36 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), back),
        ("BOX", (0, 0), (-1, -1), 0.8, border),
        ("LEFTPADDING", (0, 0), (-1, -1), pad + 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad + 2),
        ("TOPPADDING", (0, 0), (-1, -1), pad),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
    ]))
    return t


# ---------- build story ----------
story = []
A = story.append

# ===== COVER =====
A(Spacer(1, 60 * mm))
A(P("MISSION BRIEF / CONSUMER DIVISION", "cover_s"))
A(Spacer(1, 6))
A(P("BETTER-FOR-YOU<br/>INDULGENCE", "cover_t"))
A(Spacer(1, 8))
A(P("An orbital market map of guilt-free food &amp; beverage", "cover_s"))
A(P("UNITED STATES + AUSTRALIA &nbsp;&middot;&nbsp; 6 NEED-STATE GALAXIES &nbsp;&middot;&nbsp; 30 COMPANIES", "cover_s"))
A(Spacer(1, 26 * mm))
A(P("ARJUN KULSHRESTHA &nbsp;&middot;&nbsp; JUNE 2026", "cover_s"))
A(P("Companion to the interactive space map (output/index.html)", "cover_s"))
A(PageBreak())

# ===== PERSONAL INTRO =====
A(P("00 / WHO IS WRITING THIS", "kicker"))
A(P("A note before the numbers", "h1"))
A(P("I'm Arjun Kulshrestha, and I want to work in consumer venture. Not because consumer is "
    "the glamorous end of VC — it usually isn't — but because consumer outcomes are decided by "
    "operating skill and taste in a way no other category is. The cap table doesn't save you in the "
    "snack aisle. Velocity does. This memo and its companion interactive map are my attempt to show, "
    "rather than claim, how I think about a category."))
A(P("Why this category", "h2"))
A(P("I chose better-for-you indulgence — what consumers honestly call <b>guilt-free food</b> — because it sits at "
    "the intersection of the two biggest forces reshaping food: <b>premiumisation</b> and <b>health becoming a "
    "lifestyle aesthetic rather than a sacrifice</b>. It also produced the most instructive exits in recent consumer "
    "memory (Poppi, Siete, LesserEvil, SmartSweets) while still being early in my second market, Australia. "
    "And it is ruthlessly founder-dependent: every breakout on my map traces to an operator with unusual taste "
    "in product, brand, or distribution. That's the kind of investing I want to learn."))
A(P("What I believe (opinions, not consensus)", "h2"))
beliefs = [
    ("1.", "Taste parity is a ticket, not a thesis. The moat is repeat purchase plus something structural: David bought its ingredient supplier; LesserEvil owned its manufacturing; Feastables owns its audience. 'It's healthy AND delicious' is table stakes."),
    ("2.", "The diet aisle is dead; the permission aisle replaced it. Winners sell in the candy aisle, the chemist, the canteen — never next to meal shakes. Placement IS positioning."),
    ("3.", "GLP-1 is a re-rating event, not a demand shock. Fewer eating occasions means each snack must justify itself — protein, fibre, portion logic. That advantages exactly this map."),
    ("4.", "Australia is a 2–3 year time machine with structural cheats: Chemist Warehouse as a health-channel beachhead, a grocery duopoly that makes national distribution one deal, and school canteen policy that legislates kids' BFY demand."),
    ("5.", "The best operators in this category increasingly don't need venture (Chomps ~$900M revenue, near-bootstrapped; FUNDAY, Denada, Macro Mike all self-funded to national shelf). Sourcing here means earning allocation, not just finding deals."),
    ("6.", "Celebrity is distribution, not brand. Feastables works because the audience is the channel; most talent-led launches confuse reach with repeat. I'd underwrite the repeat-purchase curve, never the launch week."),
    ("7.", "Claims risk is the category's quiet killer. Poppi paid a class-action settlement on its way to a $1.95B exit. The next generation must formulate to survive scrutiny, not just to pass a TikTok taste test."),
]
for n, b in beliefs:
    A(P(f"<font color='#7aa2ff'><b>{n}</b></font> {b}", "body"))
A(PageBreak())

# ===== EXECUTIVE THESIS =====
A(P("01 / EXECUTIVE THESIS", "kicker"))
A(P("Indulgence isn't dying. It's being re-priced.", "h1"))
A(P("<b>Why now.</b> Health flipped from restriction to status. Protein, gut health and 'no added sugar' are how "
    "mainstream shoppers — not dieters — now buy treats. Roughly 1 in 8 US adults is on a GLP-1 (AlixPartners / "
    "Food Institute reporting), compressing snacking occasions 40–60% while spend shifts to protein (+65%) and "
    "fibre-forward foods. Every remaining indulgence occasion must now earn its place. That is a formulation and "
    "brand problem incumbents are structurally bad at."))
A(P("<b>The proof.</b> PepsiCo paid <b>$1.95B for Poppi</b> (2025) off ~$500M sales. <b>OLIPOP</b> reached <b>$1.85B, "
    "profitably</b>. Hershey paid <b>~$750M for LesserEvil</b>; PepsiCo <b>$1.2B for Siete</b> (2024). <b>David</b> did "
    "~$100M first-year revenue and raised at <b>$725M</b>. This is no longer niche CPG — it's the most reliable strategic "
    "M&amp;A lane in food."))
A(P("<b>Why incumbents are vulnerable.</b> Their core brands carry zero health permission (Coke can't sell you gut "
    "health), reformulating flagship products indicts the portfolio, and their innovation cycles run in years while "
    "challengers iterate in weeks. Their rational move is to buy — which is exactly what they're doing, at 3–4x revenue."))
A(P("<b>Why startups win.</b> Founder taste compounds: product taste (David's macro maths), brand taste (BelliWelli "
    "made IBS funny), and distribution taste (Feastables skipped DTC for Walmart; FUNDAY launched in pharmacies). "
    "Speed plus permission plus owned audiences beats shelf-buying budgets early."))
A(P("<b>Venture-scale vs. niche CPG.</b> The line is need-state ownership. Venture outcomes happen when a brand owns "
    "a sentence in the consumer's head ('soda that's good for me', 'candy without sugar') and rides it across formats "
    "and channels. Niche outcomes happen when a brand owns a SKU. I'd underwrite: repeat rate &gt;40%, gross margin "
    "&gt;40% with a path to 50, velocity that survives the end of launch promo, and a founder who can hire a supply "
    "chain before it breaks."))
A(box([
    P("THE ONE-LINE THESIS", "h3"),
    P("Back founder-operators who give consumers <b>permission to enjoy</b> — with taste parity as the entry fee, "
      "repeat purchase as the scoreboard, and supply-chain or audience ownership as the moat. Overweight Australia, "
      "where the US playbook re-runs with structural shortcuts and half the competition.", "body"),
]))
A(PageBreak())

# ===== CATEGORY DEFINITION =====
A(P("02 / CATEGORY DEFINITION", "kicker"))
A(P("What counts as better-for-you indulgence", "h1"))
A(P("Food and beverage whose <b>job is pleasure</b> — treats, snacks, desserts, comfort food, soda — engineered and "
    "branded so the consumer feels <b>healthier, more values-aligned, or less regretful</b> choosing it. The product must "
    "win a blind taste test against the 'bad' original, or it isn't in the category; it's diet food."))
A(P("<b>In:</b> zero-sugar candy and chocolate, dessert-coded protein, prebiotic soda, gut-friendly and allergen-free "
    "treats, clean-label comfort food (ramen, mac &amp; cheese, chips), kids' lunchbox-compliant treats, portion-logic "
    "snacking for GLP-1 appetites.", "body"))
A(P("<b>Out:</b> meal replacements and medical nutrition (function without joy), supplements, raw 'whole foods' "
    "(an apple needs no permission), legacy diet brands (the consumer's job there is restriction, not pleasure), "
    "and alcohol alternatives (adjacent, different drivers).", "body"))
A(P("The language shift", "h2"))
lang = [
    ["1990s–2000s DIET ERA", "2020s PERMISSION ERA"],
    ["'Low fat', 'lite', 'guilt' framing", "'28g protein', 'no added sugar', '150 calories' — specs, not shame"],
    ["Aspartame apologetics", "Allulose, monk fruit, prebiotic fibre — sweeteners as features"],
    ["Diet aisle ghetto", "Candy aisle, chemist, canteen, c-store — placed beside the original"],
    ["Target: dieters (mostly women, mostly guilt)", "Target: everyone — fitness, GLP-1, parents, 'healthy hedonists'"],
    ["Taste sacrifice accepted", "Taste parity mandatory; health is the tiebreak, not the pitch"],
]
t = Table([[P(f"<b>{r[0]}</b>", "cellm"), P(r[1], "cell")] for r in lang], colWidths=[(W-36*mm)*0.38, (W-36*mm)*0.62])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), PANEL),
    ("GRID", (0,0), (-1,-1), 0.5, LINE),
    ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING", (0,0), (-1,-1), 7), ("RIGHTPADDING", (0,0), (-1,-1), 7),
]))
A(t)
A(Spacer(1, 8))
A(P("Sourcing note: thesis shaped by trade press (Food Dive, FoodNavigator, NOSH), funding databases (Crunchbase, "
    "Tracxn, PitchBook), founder interviews, and consumer-investing media — e.g. The Consumer Ascent (Substack, "
    "channel-check research on emerging brands), The Consumer VC, and Express Checkout / The Curious Consumer "
    "podcast. Full source links sit inside each company dossier in the interactive map and in the appendix.", "small"))
A(PageBreak())

# ===== CONSUMER SEGMENTS =====
A(P("03 / CONSUMER BEHAVIOUR", "kicker"))
A(P("Seven buyers, one need: permission", "h1"))
segs = [
    ("Protein-first (post-gym-bro)", "Macros as daily budget; protein = default heuristic", "Supplement aesthetics; chalky textures", "High ($2.50–4.50/bar)", "C-store, grocery, DTC subs", "'Candy-grade taste, athlete-grade specs' — David, Magic Spoon, Vitawerx"),
    ("GLP-1 / appetite-conscious", "Fewer occasions; each bite must justify itself; muscle preservation, fibre", "Big portions; food waste; nausea triggers", "High, low volume — premium per-unit", "Pharmacy, grocery, DTC", "Portion logic + density: 'small, complete, worth it'"),
    ("Parents & lunchbox buyers", "Rules (school policy, sugar caps) decide; kids must actually eat it", "Kid taste-veto; label policing; price-per-box maths", "Medium-high, repeat-heavy", "Grocery, Costco, chemist (AU)", "'Treats you say yes to' — Twisted Healthy Treats, Blue Dinosaur, Sweet Loren's"),
    ("Gen Z wellness", "Health as identity content; gut health &gt; calories; brand as social object", "Scepticism of legacy claims; broke-but-premium", "Medium; trial-happy, fickle", "TikTok-to-Target, c-store", "Humour + aesthetics + one hero claim — Poppi, BelliWelli, Bobby"),
    ("Busy professionals", "Convenient upgrade of existing habits (ramen, coffee, dessert)", "Time; decision fatigue; office snack drawer guilt", "High; subscription-friendly", "DTC, Amazon, premium grocery", "'Your 3pm fix, fixed' — immi, Goodles, Remedy"),
    ("Dietary-restricted households", "Safety first (allergens, FODMAP, diabetes); whole family converts", "Exclusion from normal treats; cross-contamination trust", "Highest WTP, lowest churn", "Specialty + mainstream grocery, pharmacy", "Certification + 'eat like everyone else' — Fodbods, Sweet Loren's, Noshu"),
    ("Healthy hedonists / premium grocers", "Indulgence without compromise as a values statement; ingredient literacy", "Greenwashing fatigue; premium price needs premium experience", "Highest basket; taste-led", "Whole Foods / premium indies, hospitality", "Provenance + design + zero apology — StrangeLove, Mid-Day Squares, Mingle"),
]
rows = [[P("<b>SEGMENT</b>", "cellh"), P("<b>MOTIVATION</b>", "cellh"), P("<b>PAIN</b>", "cellh"), P("<b>WTP</b>", "cellh"), P("<b>CHANNEL</b>", "cellh"), P("<b>MESSAGE THAT LANDS</b>", "cellh")]]
for s_ in segs:
    rows.append([P(f"<b>{s_[0]}</b>", "cell")] + [P(x, "cellm") for x in s_[1:]])
cw = [(W-36*mm)*f for f in (0.16, 0.20, 0.16, 0.12, 0.14, 0.22)]
t = Table(rows, colWidths=cw, repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), PANEL),
    ("GRID", (0,0), (-1,-1), 0.5, LINE),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
]))
A(t)
A(Spacer(1, 8))
A(P("The premiumisation thread: across every segment, consumers are trading fewer, better occasions — paying 2–4x "
    "the legacy price for a snack that carries identity. The losing position is the middle: not cheap, not credible.", "small"))
A(PageBreak())

# ===== TAXONOMY =====
A(P("04 / MARKET MAP TAXONOMY", "kicker"))
A(P("Six elements, organised by need-state", "h1"))
A(P("I deliberately mapped need-states, not product aisles — consumers don't shop 'low-sugar confectionery', they shop "
    "'I refuse to give up sweets'. In the interactive map each need-state is a living element — Fire (protein), Crystal "
    "(sugar-free), Water (drinks), Flora (gut), Terra (comfort), Wind (culture &amp; kids) — and each is a clickable system; "
    "planets are companies, sized by scale signal, ringed when acquired (kept as pricing comps), pulsing when breaking out."))
rows = [[P("<b>ELEMENT / NEED-STATE</b>", "cellh"), P("<b>WHY CONSUMERS CARE</b>", "cellh"), P("<b>REPRESENTATIVE</b>", "cellh"), P("<b>MATURITY</b>", "cellh"), P("<b>VC</b>", "cellh"), P("<b>KEY RISKS</b>", "cellh")]]
for g in DATA["galaxies"]:
    comps = [c["name"] for c in DATA["companies"] if c["galaxy"] == g["id"]]
    rows.append([
        P(f"<b>{ {'protein':'Fire','sugarfree':'Crystal','drinks':'Water','gut':'Flora','comfort':'Terra','culture':'Wind'}[g['id']] } — {g['name']}</b><br/><i>&ldquo;{g['need_state']}&rdquo;</i>", "cell"),
        P(g["why_care"], "cellm"),
        P(", ".join(comps), "cellm"),
        P(g["maturity"], "cellm"),
        P(g["vc_attractiveness"], "cell"),
        P(g["risks"], "cellm"),
    ])
cw = [(W-36*mm)*f for f in (0.17, 0.27, 0.17, 0.10, 0.08, 0.21)]
t = Table(rows, colWidths=cw, repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), PANEL),
    ("GRID", (0,0), (-1,-1), 0.5, LINE),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
]))
A(t)
A(PageBreak())

# ===== COMPETITIVE DYNAMICS =====
A(P("05 / COMPETITIVE DYNAMICS", "kicker"))
A(P("The physics of the category", "h1"))
dyn = [
    ("Taste vs. health", "Non-negotiable: lose the blind taste test, lose the repeat. Every dossier on my map starts with whether taste parity is real (David, FUNDAY) or marketing (most of the long tail)."),
    ("Trust & ingredient credibility", "One viral 'actually it's full of seed oils / sugar alcohols' moment can kill a brand. SmartSweets' gut-distress complaints opened the door FUNDAY walked through with no sugar alcohols."),
    ("DTC vs. retail", "DTC is a lab, not a business: CAC inflation killed DTC-only food. The modern arc is DTC for data → retail for scale (David, Magic Spoon) — or skip DTC entirely when you own an audience (Feastables → Walmart)."),
    ("Repeat & basket", "Habit formats (soda, ramen, pantry staples, lunchbox) structurally beat novelty formats (gifting chocolate). The basket question: does it enter the weekly shop or the occasional treat run?"),
    ("Gross margin & supply chain", "BFY ingredients (allulose, EPG, grass-fed, allergen-free lines) cost more; target 40%+ now, 50% at scale. The biggest outcomes internalised supply: David bought Epogee; LesserEvil self-manufactures."),
    ("Retail & private label", "Slotting fees, promo cadence and velocity reviews are existential; Coles/Woolworths private label moves faster than US chains. Differentiation must survive a knockoff at 60% of price."),
    ("Incumbent response", "Buy, not build — Soulboost died, then Pepsi bought Poppi. Strategic appetite is the exit floor; it's also a ceiling on how long a window stays open before the acquired brand gets the incumbent's distribution."),
    ("Regulatory / claims", "FDA scrutiny of 'healthy' labelling, prebiotic/probiotic claims litigation (Poppi's settlement), FSANZ novel-ingredient approvals in AU (EPG isn't approved there yet — a real expansion gate for David-style formulations)."),
]
for k, v in dyn:
    A(P(f"<font color='#ffc861'><b>{k}.</b></font> {v}", "body"))
A(PageBreak())

# ===== WHITE SPACES =====
A(P("06 / WHITE SPACES", "kicker"))
A(P("Ten places I'd go hunting", "h1"))
ws = [
    ("GLP-1-native snacking", "Compressed appetites need dense, small, complete bites — nobody owns the format yet", "US first, AU as fast-follow; pharmacy + grocery", "Repeat rate among medicated users; pharmacy velocity; RD/clinician endorsements"),
    ("Australia's healthy soda window", "Poppi/OLIPOP playbook is 2–3 yrs behind in AU; Remedy proved scale, nobody owns 'fun'", "Brand-led launch via c-store + duopoly grocery; Bobby is the early contender", "C-store reorder rates; Gen Z social pull; duopoly ranging review survival"),
    ("Sugar-free chocolate that's actually good", "Gummies are solved (FUNDAY, SmartSweets); chocolate taste parity isn't", "Premium gifting + everyday block; chemist channel in AU", "Blind taste wins vs. Lindt; repeat &gt;40%; margin &gt;45%"),
    ("Kids' canteen-compliant treats at scale", "AU school traffic-light policy legislates demand; fragmented supply", "B2B2C canteen lists + grocery; export the compliance playbook to US schools", "Canteen list penetration; parent repeat; school-term seasonality survival"),
    ("Allergen-free indulgence platform", "Whole households convert on one member's allergy; US has Sweet Loren's, AU has no leader", "Mainstream grocery freezer/chiller, not health aisle", "Household (not individual) retention; certification moat; cross-format expansion"),
    ("High-fibre as the next protein", "GLP-1 constipation + gut-health wave; fibre is where protein was in 2015", "Snack formats with 8–10g fibre that taste indulgent; grocery + TikTok education", "Claim comprehension in ads; repeat after first GI experience (dose matters)"),
    ("Protein frozen desserts done right", "Halo Top proved demand then taste-collapsed; tech (allulose, EPG-style fats) has moved", "Grocery freezer; AU first via Denada-style distribution then US", "Velocity vs. Ben &amp; Jerry's adjacency; second-purchase rate; cold-chain margin"),
    ("Clean-label Asian comfort formats", "immi proved ramen; dumplings, bao, instant noodles in AU (high Asian-Australian population) untouched", "DTC trial → Asian grocers → mainstream; founder authenticity essential", "Community organic pull; non-Asian crossover; freezer economics"),
    ("Functional coffee & 3pm energy", "The afternoon treat occasion (coffee + biscuit) has no BFY owner; beforeyouspeak-style AU brands sub-scale", "Office channel + grocery pods + c-store RTD", "Workplace reorder; RTD margin; caffeine-claims hygiene"),
    ("Trust infrastructure / 'verified label' brands", "Claims-risk era rewards brands built on radical transparency (batch testing, open COAs)", "DTC-first with retail halo; possibly the platform play across categories", "Willingness to pay for verification; press/regulator goodwill; licensing interest"),
]
for i, (name, need, dist, sig) in enumerate(ws, 1):
    A(box([
        P(f"<font color='#7aa2ff'><b>W{i:02d} — {name}</b></font>", "body"),
        P(f"<b>The gap:</b> {need}. <b>Playbook:</b> {dist}. <b>Traction I'd look for:</b> {sig}.", "cellm"),
    ], pad=6))
    A(Spacer(1, 4))
A(PageBreak())

# ===== BEAR CASE =====
A(P("07 / BEAR CASE", "kicker"))
A(P("The skeptical read", "h1"))
bears = [
    ("Overhyped where?", "US functional soda (post-Poppi, the strategics have shopped), protein bars (David's heat is pulling in undifferentiated me-toos), and anything whose pitch deck leads with 'the GLP-1 opportunity' instead of a product."),
    ("Too crowded", "Low-sugar gummies, US prebiotic beverages, generic 'clean' protein powders, keto legacy formats. In each, shelf is allocated, CAC is bid up, and differentiation is a flavour, not a moat."),
    ("Retention is the lie most often told", "Novelty velocity masquerades as product-market fit. Celebrity and creator brands are most exposed: launch-week sellouts say nothing about week 26. The only honest metrics are second-purchase rate and post-promo velocity."),
    ("Undifferentiated branding", "Half the category is the same brand: pastel can, lowercase wordmark, 'finally, X without the bad stuff'. When the design language is a commodity, the brand isn't doing any work — price and shelf position decide."),
    ("Claims that won't survive", "Prebiotic doses below clinical relevance, 'gut health' on products with 2g of fibre, 'natural' sweetener halos. Poppi settled a class action; FDA 'healthy' rules and FSANZ approvals will catch the sloppy."),
    ("What caps venture outcomes", "Food brands rarely become platforms; most are single-need-state businesses sold at 2–4x revenue. If the entry price assumes software multiples, even a $750M exit can return badly. And the best operators (Chomps) may simply never sell you equity."),
]
for k, v in bears:
    A(P(f"<font color='#e84393'><b>{k}</b></font> {v}", "body"))
A(Spacer(1, 6))

A(P("08 / INVESTOR LENS", "kicker"))
A(P("How I'd evaluate a deal here", "h1"))
lens = [
    ("Founder-market fit", "Has the founder personally lived the need-state, and shipped product before? (Rahal/RXBAR → David is the archetype.)"),
    ("Product velocity", "Time from insight to shelf; SKU iteration cadence; kill-rate honesty."),
    ("Repeat purchase", "&gt;40% repeat, rising cohort curves, subscription or weekly-basket entry."),
    ("Gross margin", "&gt;40% now, structural path to 50%+ (supply ownership, scale pricing)."),
    ("Retail velocity", "Units/store/week vs. category norms after promo ends; reorder breadth."),
    ("Community & organic demand", "Searches, UGC, and waitlists the brand didn't pay for; earned distribution (FUNDAY's pharmacy pull, BelliWelli's virality)."),
    ("Channel expansion logic", "Each new channel adds margin or audience, not just volume; AU→US or US→AU plan that respects regulatory gates."),
    ("Category creation", "Does the brand own a sentence? ('soda that's good for you') — that's what strategics pay 4x revenue for."),
    ("Acquirer map", "PepsiCo, Hershey, Mondelez, Nestlé, Unilever in the US; in AU, also the path of US strategics buying their ANZ beachhead."),
]
for k, v in lens:
    A(P(f"<font color='#43d9a3'><b>{k}.</b></font> {v}", "body"))
A(PageBreak())

# ===== PERSONAL CONVICTION =====
A(P("09 / MY PERSONAL CONVICTION", "kicker"))
A(P("Companies I'd want to meet, and what I'd ask", "h1"))
A(P("The shortlist", "h2"))
meets = [
    ("FUNDAY (AU)", "the most exportable AU brand on the map; I want to understand the US pharmacy/grocery entry maths and whether they'll finally take external capital"),
    ("Bobby (AU)", "the live test of whether the Poppi playbook re-runs in Australia before the window closes"),
    ("Noshu (AU)", "first external raise after A$4M to A$38M in four years inside the duopoly — rare growth-stage entry in AU BFY"),
    ("BelliWelli (US)", "the cleanest community-wedge-to-retail story; I want the cohort curves behind the virality"),
    ("immi (US)", "the highest-frequency habit format on the map; if repeat holds, this compounds quietly"),
    ("Chief Nutrition (AU)", "small, profitable, community-funded — exactly the kind of operator AU venture overlooks"),
    ("David (US)", "not because I could win the allocation, but because every question I have about supply-chain moats in food runs through Epogee"),
]
for n, why in meets:
    A(P(f"<font color='#7aa2ff'><b>{n}</b></font> — {why}.", "body"))
A(P("Questions I'd ask founders", "h2"))
qs = [
    "What's your second-purchase rate, and what was it before you knew I'd ask?",
    "Show me velocity in your oldest 50 doors after the launch promo ended.",
    "Which ingredient or claim in your product would survive a hostile lab test going viral?",
    "What do you control in your supply chain that a copycat with $5M can't buy in 12 months?",
    "If your biggest retailer launches a private-label version at 60% of your price, what happens to you?",
    "Who is the acquirer, what sentence do you own in their strategy deck, and why can't they build it?",
    "What did you taste-test and kill last quarter?",
]
for q in qs:
    A(P(f"&bull;&nbsp; {q}", "body"))
A(P("What this project taught me", "h2"))
A(P("Three things changed my mind while building this. First, I started believing distribution stories beat product "
    "stories — then David's Epogee acquisition and LesserEvil's self-manufacturing convinced me the deepest moats here "
    "are upstream, not downstream. Second, Australia isn't a smaller US: the chemist channel, the duopoly, and canteen "
    "policy create different winning playbooks, which is precisely why a 50/50 US-AU lens finds mispriced deals. Third, "
    "the hardest discipline in consumer is ignoring launch heat — every embarrassing outcome in this category was "
    "visible early in one number, the second-purchase rate. I'd rather be the analyst who asks for that number than "
    "the one who forwards the TikTok.", "body"))
A(PageBreak())

# ===== APPENDIX =====
A(P("10 / APPENDIX", "kicker"))
A(P("Company database — 30 planets", "h1"))
A(P("Status: IND independent &nbsp;/&nbsp; BRK breakout &nbsp;/&nbsp; EXIT acquired (kept as pricing comps). Facts are flagged verified / "
    "company-reported / estimate inside each signal. Full dossiers and clickable sources live in the interactive map.", "small"))
rows = [[P("<b>COMPANY</b>", "cellh"), P("<b>GEO</b>", "cellh"), P("<b>ELEMENT</b>", "cellh"), P("<b>CORE PRODUCT</b>", "cellh"), P("<b>FUNDING / SCALE SIGNAL</b>", "cellh")]]
ELNAME = {"protein": "Fire", "sugarfree": "Crystal", "drinks": "Water", "gut": "Flora", "comfort": "Terra", "culture": "Wind"}
gname = {g["id"]: ELNAME[g["id"]] + " / " + g["name"] for g in DATA["galaxies"]}
mark = {"independent": "IND", "breakout": "<font color='#43d9a3'>BRK</font>", "exited": "<font color='#93a0c2'>EXIT</font>"}
for c in sorted(DATA["companies"], key=lambda c: (c["galaxy"], -c["scale"])):
    rows.append([
        P(f"<b>{c['name']}</b> <font size=6>{mark[c['status']]}</font>", "cell"),
        P(c["geo"], "cellm"),
        P(gname[c["galaxy"]], "cellm"),
        P(c["product"], "cellm"),
        P(c["signal"], "cellm"),
    ])
cw = [(W-36*mm)*f for f in (0.16, 0.07, 0.15, 0.27, 0.35)]
t = Table(rows, colWidths=cw, repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), PANEL),
    ("GRID", (0,0), (-1,-1), 0.5, LINE),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("TOPPADDING", (0,0), (-1,-1), 3.5), ("BOTTOMPADDING", (0,0), (-1,-1), 3.5),
    ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
]))
A(t)
A(Spacer(1, 10))
A(P("Key sources", "h2"))
srcs = sorted({s for c in DATA["companies"] for s in c["sources"]})
for s_ in srcs:
    A(P(s_, "small"))

# ---------- render ----------
doc = BaseDocTemplate(str(OUT), pagesize=A4,
                      leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=18*mm,
                      title="Better-for-You Indulgence — Market Map & Memo",
                      author="Arjun Kulshrestha")
frame = Frame(18*mm, 18*mm, W-36*mm, H-34*mm, id="main")
doc.addPageTemplates([PageTemplate(id="dark", frames=[frame], onPage=paint)])
doc.build(story)
print(f"Built {OUT} ({OUT.stat().st_size//1024} KB)")
