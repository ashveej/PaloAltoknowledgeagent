# /dashboard

The runnable application — the agent engine + the web UI (the visualization prototype).
**This is the source of truth for all runnable code.**

## Run
```bash
# from the repo root: create env + install deps first (see root README), then:
cd dashboard
python -m app.ingest --reset                 # build the knowledge base (offline)
cp .env.example .env                          # optional: add ANTHROPIC_API_KEY for real answers
uvicorn app.main:app --reload --port 8077     # open http://localhost:8077
```
Without a key it runs in **MOCK mode** (deterministic stand-ins) so the full flow is
visible offline.

## What you'll see (4 tabs)
- **Ask** — question box + sample questions; answers show a confidence pill, the score
  breakdown, and the **exact cited source text inline**; feedback buttons.
- **Knowledge Base** — every approved source with freshness badges, votes, chunk counts
  (data transparency).
- **SME Queue** — routing table, open escalations, the email-notification status, and
  **Approve & Publish** to add SME knowledge back into the KB.
- **Dashboard** — trust/feedback metrics + confidence distribution.

## Layout
```
app/    the engine: classify · retrieve · facts · gates · scoring · style ·
        escalate · feedback · sme · notify · pipeline · main (FastAPI)
ui/     single-page web UI (vanilla HTML/CSS/JS) + the notification bell
data/   the vector store + runtime records (gitignored; rebuilt by ingest)
brand_voice.yaml   file-configurable brand voice (terminology, banned phrases, rubric)
```

## Key design choice
The LLM only **classifies, drafts, and styles**. Every **trust decision** — what counts as
a citation, whether to answer, how confident we are — is plain, auditable, tested Python
(in `app/gates.py` and `app/scoring.py`). That's deliberate.
