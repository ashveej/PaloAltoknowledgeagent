# /pipeline_and_tests

The metric and the data-quality tests.

## The metric: a deterministic Confidence Score
In this product, the "metric" is the **Technical Trust Score** — a transparent,
reproducible 0–100 score that maps to **High / Medium / Low** confidence. The LLM never
sets it; it's plain Python.

`scoring.py` — the metric (review copy; source of truth `../dashboard/app/scoring.py`):
- **Citation integrity (40)** — are all claims actually backed by a cited passage?
- **Retrieval relevance (25)** — how well evidence matches the question.
- **Source authority (20)** — official docs/release notes top; SME-verified near-top.
- **Source freshness (15)** — how recently the source was reviewed.
- **Caps** override the number: stale (>180d→Medium, >365d→Low), downvoted (>15%→Medium,
  >30%→Low, after ≥5 votes), single non-official source → Medium.

## The data-quality tests / gates
`gates.py` — hard validation that runs **before** scoring (review copy; source of truth
`../dashboard/app/gates.py`). If any fails, the answer is **blocked** and escalated:
no-citation, unapproved source, deprecated source, product mismatch. *(Think Salesforce
Validation Rules for AI answers.)*

`tests/` — 33 deterministic unit tests locking the gates, scoring, caps, brand-voice
rubric, and SME routing so the metric can't silently drift.

## The evaluation harness
`make_report.py` — runs a **5 easy / 5 medium / 5 hard** question set through the live
pipeline and writes `REPORT.md` with full per-question score breakdowns. Result: **5/5/5**
(easy→High, medium→Medium/freshness-capped, hard→escalated).

## Run
```bash
# tests (no API key needed; deterministic logic only)
python -m pytest

# evaluation (makes live Claude calls — needs ANTHROPIC_API_KEY in dashboard/.env)
python make_report.py        # regenerates REPORT.md
```
