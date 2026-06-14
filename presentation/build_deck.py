"""Generate an editable PowerPoint deck (.pptx) for the panel presentation.
Opens in PowerPoint/Keynote and imports into Google Slides
(Drive → upload → Open with Google Slides).

Run:  ../.venv/bin/python build_deck.py
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import re

INK   = RGBColor(0x0C, 0x0E, 0x14)
INK2  = RGBColor(0x16, 0x1A, 0x26)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TXT   = RGBColor(0xE6, 0xE8, 0xEC)
MUT   = RGBColor(0x9A, 0xA3, 0xB2)
ORANGE  = RGBColor(0xFA, 0x58, 0x2D)
ORANGE2 = RGBColor(0xFF, 0x7A, 0x4D)
HI = RGBColor(0x41, 0xD6, 0x7E)
MED = RGBColor(0xF4, 0xB7, 0x40)
LO = RGBColor(0xFF, 0x6B, 0x5E)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = prs.slide_width, prs.slide_height


def slide(bg=INK):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = bg
    return s


def rect(s, l, t, w, h, color):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    shp.fill.solid(); shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def textbox(s, l, t, w, h):
    tb = s.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame; tf.word_wrap = True
    return tf


def setrun(p, text, size, color, bold=False, italic=False):
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.color.rgb = color
    r.font.bold = bold; r.font.italic = italic
    r.font.name = "Arial"
    return r


def rich(p, text, size, base=TXT):
    """Render **bold** segments in white-bold, rest in base color."""
    for i, seg in enumerate(re.split(r"(\*\*.*?\*\*)", text)):
        if not seg:
            continue
        if seg.startswith("**") and seg.endswith("**"):
            setrun(p, seg[2:-2], size, WHITE, bold=True)
        else:
            setrun(p, seg, size, base)


def eyebrow(s, text):
    tf = textbox(s, Inches(0.9), Inches(0.7), Inches(11.5), Inches(0.4))
    setrun(tf.paragraphs[0], text.upper(), 12.5, ORANGE2, bold=True)


def heading(s, text):
    rect(s, Inches(0.9), Inches(1.15), Inches(0.16), Inches(0.55), ORANGE)
    tf = textbox(s, Inches(1.2), Inches(1.05), Inches(11.3), Inches(0.9))
    setrun(tf.paragraphs[0], text, 30, WHITE, bold=True)


def footer(s, n):
    tf = textbox(s, Inches(0.9), Inches(7.0), Inches(6), Inches(0.4))
    setrun(tf.paragraphs[0], "paloalto  ·  Knowledge Agent", 10, MUT, bold=True)
    tf2 = textbox(s, Inches(11.0), Inches(7.0), Inches(1.6), Inches(0.4))
    p = tf2.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
    setrun(p, f"{n} / 17", 10, MUT)


def bullets(s, items, top=2.2, left=0.95, width=11.4, size=16, gap=10):
    tf = textbox(s, Inches(left), Inches(top), Inches(width), Inches(4.3))
    first = True
    for it in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(gap)
        setrun(p, "●  ", size, ORANGE, bold=True)
        rich(p, it, size)


def two_col(s, left_items, right_items, top=2.2, size=16):
    bullets(s, left_items, top=top, left=0.95, width=5.6, size=size)
    bullets(s, right_items, top=top, left=6.95, width=5.5, size=size)


def table(s, headers, rows, top=2.2, col_w=None, size=13):
    nrows, ncols = len(rows) + 1, len(headers)
    left, width = Inches(0.95), Inches(11.4)
    gtbl = s.shapes.add_table(nrows, ncols, left, Inches(top), width,
                              Inches(0.5 + 0.42 * len(rows))).table
    if col_w:
        for i, w in enumerate(col_w):
            gtbl.columns[i].width = Inches(w)
    for j, h in enumerate(headers):
        c = gtbl.cell(0, j); c.fill.solid(); c.fill.fore_color.rgb = INK2
        tf = c.text_frame; tf.word_wrap = True
        setrun(tf.paragraphs[0], h, size, MUT, bold=True)
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            c = gtbl.cell(i, j); c.fill.solid()
            c.fill.fore_color.rgb = INK if i % 2 else INK2
            tf = c.text_frame; tf.word_wrap = True
            p = tf.paragraphs[0]
            color = ORANGE2 if j == 0 else TXT
            rich(p, val, size, base=color)
    return gtbl


# ---------------------------------------------------------------- slides
# 1 TITLE
s = slide()
rect(s, 0, 0, SW, Inches(0.12), ORANGE)
tf = textbox(s, Inches(0.9), Inches(1.6), Inches(7.5), Inches(0.5))
shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.6), Inches(3.4), Inches(0.5))
shp.fill.solid(); shp.fill.fore_color.rgb = INK2; shp.line.color.rgb = ORANGE; shp.line.width = Pt(1)
shp.shadow.inherit = False
ptf = shp.text_frame; setrun(ptf.paragraphs[0], "TECHNICAL PM PANEL · 60 MIN", 12, ORANGE2, bold=True)
tf = textbox(s, Inches(0.9), Inches(2.45), Inches(10.5), Inches(2.2))
setrun(tf.paragraphs[0], "Evidence-Governed Knowledge Agent", 44, WHITE, bold=True)
p = tf.add_paragraph(); setrun(p, "for Technical Sales", 44, WHITE, bold=True)
tf = textbox(s, Inches(0.9), Inches(4.6), Inches(10.8), Inches(1.6))
rich(tf.paragraphs[0],
     "An evidence-governed RAG platform — not a chatbot. Every answer is grounded in "
     "approved sources, cites the exact text, and carries a **deterministically-calculated** "
     "confidence score. Weak evidence routes to an SME, whose answer becomes reusable knowledge.",
     18, base=RGBColor(0xD7, 0xDA, 0xE0))
tf = textbox(s, Inches(0.9), Inches(6.5), Inches(11), Inches(0.5))
setrun(tf.paragraphs[0], "Live build: FastAPI · LanceDB · Claude (Opus 4.8 / Haiku 4.5) · deterministic scoring engine", 13, MUT)

# 2 AGENDA
s = slide(); eyebrow(s, "Agenda"); heading(s, "How I'll use the 60 minutes")
table(s, ["Section", "Time", "What I'll prove"], [
    ["Introduction", "5", "My Technical-PM operating system"],
    ["Context & Problem", "5", "The user pain; why a chatbot fails"],
    ["Technical Deep Dive", "15", "Architecture, data pipeline, trade-offs"],
    ["Evaluation & Results", "10", "KPI-tied eval + the hard truths"],
    ["Panel Q&A", "25", "Defend the trade-offs and the roadmap"],
], top=2.3, col_w=[3.2, 1.2, 7.0], size=15); footer(s, 2)

# 3 PHILOSOPHY
s = slide(); eyebrow(s, "Introduction"); heading(s, "My Technical-PM operating system")
bullets(s, [
    "**Slice the risk.** Ship the thinnest vertical that retires the riskiest assumption first — here it's trust, not 'can an LLM answer.'",
    "**Determinism where trust lives.** The LLM classifies, drafts, and styles. It never decides confidence, citations, or whether to answer.",
    "**Make trust legible.** 'Medium because the only source is 241 days old' beats a bare label. Every score is explained; every claim shows its source.",
], top=2.3, size=17, gap=16); footer(s, 3)

# 4 PROBLEM
s = slide(); eyebrow(s, "Context & Problem"); heading(s, "The user, and the asymmetric cost of being wrong")
bullets(s, [
    "**Technical Sales / SEs**, live in a customer call: 'Does Product X support Y in version Z?'",
    "A confident-but-wrong answer loses **credibility** and the deal.",
    "Truth is scattered across docs, release notes, and wikis — and it **goes stale**.",
    "A generic chatbot makes it **worse** — it hallucinates with no proof and no audit trail.",
    "→ The task is an **evidence-governed RAG system**, not a chatbot.",
], top=2.3, size=17, gap=14); footer(s, 4)

# 5 PRINCIPLES
s = slide(); eyebrow(s, "Product principles"); heading(s, "Four non-negotiables")
two_col(s,
    ["**No citation → no answer.** Every claim maps to approved source text, in code — not by prompt.",
     "**Confidence is calculated, not generated.** The LLM never sets it."],
    ["**Brand voice is a presentation layer.** It can clarify; it can't add claims or drop caveats.",
     "**SME answers become governed knowledge** — owned, citable, review-dated."],
    top=2.4, size=16); footer(s, 5)

# 6 ARCHITECTURE
s = slide(); eyebrow(s, "Technical Deep Dive · Architecture"); heading(s, "End-to-end flow")
bullets(s, [
    "**1 Classify** (Haiku) — product / feature / intent.",
    "**2 Retrieve** (LanceDB) — vector search → rerank → freshness/reputation boost; drop deprecated/unapproved.",
    "**3 Evidence Pack** — hand the model ONLY the retrieved passages.",
    "**4 Facts engine** (Opus) — claim-first answer; every claim cites a passage.",
    "**5 GATES** (Python) — cited? approved? not deprecated? product match?  → fail = escalate.",
    "**6 SCORE** (Python) — Technical Trust Score + caps → High / Medium / Low.  → Low = escalate.",
    "**7 Style** (Opus) — brand voice over validated claims, then re-checked.",
], top=2.1, size=15, gap=9); footer(s, 6)

# 7 WALL
s = slide(); eyebrow(s, "Technical Deep Dive · the key idea"); heading(s, "The Facts ↔ Style wall")
bullets(s, [
    "**Facts engine** touches evidence → produces validated claims + caveats + a calculated confidence. Never styles.",
    "**Style layer** never sees raw docs → rewrites in brand voice, then is re-checked: no new claims, no dropped caveats.",
    "This is how you answer 'make it less robotic' **without** risking accuracy.",
    "Voice and trust are scored separately — **voice can never raise trust**.",
], top=2.3, size=17, gap=14); footer(s, 7)

# 8 DATA ACQUISITION
s = slide(); eyebrow(s, "Data Strategy · acquisition"); heading(s, "Three sources, on purpose")
bullets(s, [
    "**Real docs** — crawled docs.paloaltonetworks.com (Prisma Access, Cortex XDR, NGFW). ~17 pages, 68 passages.",
    "**PDFs** — ingested via pypdf with a metadata sidecar.",
    "**Synthetic** — hand-generated stale + deprecated edge cases. You can't test a freshness rule without a stale doc.",
    "**Hard truth:** the Cortex portal is JavaScript-rendered → couldn't crawl it → I named the gap instead of faking coverage.",
], top=2.3, size=16, gap=13); footer(s, 8)

# 9 DATA QUALITY
s = slide(); eyebrow(s, "Data Strategy · quality & alignment"); heading(s, "Metadata is a first-class citizen")
bullets(s, [
    "Every passage carries product, feature, version, source type, owner, **last-reviewed date**, **deprecated flag**, approval status, votes.",
    "Metadata **drives** retrieval (deprecated never surfaces), scoring (authority + freshness), and routing.",
    "Analogy: a governed Salesforce object with required fields — not a free-text notes field.",
], top=2.3, size=17, gap=16); footer(s, 9)

# 10 TRADE-OFFS
s = slide(); eyebrow(s, "Technical Deep Dive · trade-offs to defend"); heading(s, "Build the differentiator, buy the commodity")
table(s, ["Decision", "Chose", "Over", "Why"], [
    ["Confidence", "Deterministic rubric", "LLM-judged", "Auditable; can't be gamed by fluency"],
    ["Grounding", "Hard gates", "Prompt 'please cite'", "A gate guarantees; a prompt hopes"],
    ["Vector store", "LanceDB (embedded)", "Pinecone / pgvector", "Vectors+metadata+rerank, zero infra"],
    ["Facts model", "Opus 4.8", "Haiku", "Accuracy where hallucination hurts"],
    ["Classifier", "Haiku 4.5", "Opus", "Latency / cost on a routing call"],
    ["Embeddings", "Local", "Voyage / OpenAI", "Free/offline MVP; one-line swap"],
], top=2.1, col_w=[1.9, 2.6, 2.6, 4.3], size=12.5); footer(s, 10)

# 11 HITL
s = slide(); eyebrow(s, "Human in the Loop"); heading(s, "The interface between AI logic & the SE")
bullets(s, [
    "**Attribution UI** — the exact cited source text is shown inline; verify without leaving the screen.",
    "**Explainable confidence** — pill + score breakdown + the cap reason.",
    "**SME flywheel** — escalate → feature-level routing → email the SME → Approve & Publish → instantly citable.",
    "**Feedback → ranking, not retraining** — 'wrong answer' lowers reputation + opens a ticket.",
    "Analogy: Omni-Channel routing + Approval Process + Knowledge publishing.",
], top=2.2, size=16, gap=12); footer(s, 11)

# 12 EVAL KPIS
s = slide(); eyebrow(s, "Evaluation & Success"); heading(s, "Success = trust SLOs, tied to the business")
table(s, ["KPI", "Target", "Why it's the business metric"], [
    ["Factual claims with a citation", "100%", "The product promise"],
    ["Broken-citation rate", "< 1%", "A dead link kills credibility"],
    ["Unsupported-claim rate", "< 2%", "Hallucination ceiling"],
    ["Deprecated-source usage", "0%", "Wrong-version answers lose deals"],
    ["Low-confidence shown w/o escalation", "0%", "Know what you don't know"],
    ["SME-answer reuse", "↑ MoM", "The flywheel is working"],
], top=2.1, col_w=[5.0, 1.6, 4.8], size=13); footer(s, 12)

# 13 EVAL RESULTS
s = slide(); eyebrow(s, "Evaluation & Results"); heading(s, "The harness, and what it showed")
bullets(s, [
    "**5 easy / 5 medium / 5 hard** question set, run live → **5/5/5**: easy→High, medium→Medium (capped), hard→escalated.",
    "**33 unit tests** lock the deterministic scoring so it can't silently drift.",
    "Rubric demonstrated: a real 241-day-old source caps to Medium; >365 days → Low/escalate.",
], top=2.3, size=17, gap=16); footer(s, 13)

# 14 HARD TRUTHS
s = slide(); eyebrow(s, "Evaluation & Results · the hard truths"); heading(s, "What broke — and what it taught me")
bullets(s, [
    "**Rerankers aren't calibrated.** The correct passage scored lower than an off-topic one; rerankers order, the LLM judges sufficiency.",
    "**Opus deprecates `temperature`.** Chasing determinism I set it → error → the fail-safe escalated all 15. Determinism belongs in Python.",
    "**A fail-safe became bad UX.** It over-escalated answerable questions; I tuned it to answer when grounded.",
    "**One downvote shouldn't bury a source.** Added a 5-vote floor before reputation can cap.",
], top=2.2, size=15.5, gap=12); footer(s, 14)

# 15 RETRO
s = slide(); eyebrow(s, "Retrospective"); heading(s, "If I rebuilt it on today's stack")
two_col(s,
    ["**Would change:**",
     "Agentic (Corrective/Self-RAG) retrieval",
     "A tool-using agent for live lookups",
     "LLM-as-judge as a 2nd eval signal (never confidence)",
     "Voyage embeddings + hybrid + fine-tuned reranker",
     "Real connectors + streaming UX + agentic SME drafting"],
    ["**Would NOT change — the spine:**",
     "Deterministic confidence",
     "Hard citation gates",
     "The Facts ↔ Style wall",
     "",
     "These earned the trust; the rest is optimization."],
    top=2.2, size=15); footer(s, 15)

# 16 QA
s = slide(); eyebrow(s, "Panel Q&A"); heading(s, "Ready to defend")
two_col(s,
    ["Why deterministic confidence, not the model's?",
     "How do you actually stop hallucination?",
     "Brand voice vs accuracy — both, how?",
     "A doc is downvoted or stale — what happens?"],
    ["Build vs buy — justify LanceDB / local models",
     "Latency & cost at scale?",
     "How do you measure ROI to an exec?",
     "Biggest risk?  (stale knowledge, confidently presented)"],
    top=2.3, size=16); footer(s, 16)

# 17 CLOSE
s = slide()
rect(s, 0, 0, SW, Inches(0.12), ORANGE)
shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(2.0), Inches(2.0), Inches(0.5))
shp.fill.solid(); shp.fill.fore_color.rgb = INK2; shp.line.color.rgb = ORANGE; shp.line.width = Pt(1)
shp.shadow.inherit = False
setrun(shp.text_frame.paragraphs[0], "THANK YOU", 12, ORANGE2, bold=True)
tf = textbox(s, Inches(0.9), Inches(2.9), Inches(11), Inches(1.5))
setrun(tf.paragraphs[0], "A measurable, auditable agent Technical Sales can trust.", 34, WHITE, bold=True)
tf = textbox(s, Inches(0.9), Inches(4.6), Inches(11), Inches(1.2))
rich(tf.paragraphs[0],
     "Answer only from approved evidence · cite the exact text · calculate confidence "
     "deterministically · escalate the gaps · turn SME answers into reusable knowledge.",
     18, base=RGBColor(0xD7, 0xDA, 0xE0))

prs.save("Executive_Presentation.pptx")
print(f"Saved Executive_Presentation.pptx — {len(prs.slides.__iter__.__self__._sldIdLst)} slides")
