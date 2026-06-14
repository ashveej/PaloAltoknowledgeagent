# Evidence-Governed Knowledge Agent for Technical Sales

A spec-driven AI prototype: an **evidence-governed RAG agent** that answers Palo Alto
product questions for Technical Sales **only from approved sources**, shows the **exact
cited text**, attaches a **deterministically-calculated confidence score** (High/Medium/
Low), and **routes anything it can't prove to the right SME** — whose answer then becomes
reusable, citable knowledge.

> Built with a spec-driven AI workflow (Claude Code + Markdown specs) — see `/specs`.

---

## Repository structure (maps to the exercise requirements)

| Folder | What's inside | Maps to |
| --- | --- | --- |
| **`/data_generation`** | Scripts that build the knowledge base (`seed.py` synthetic edge cases, `ingest.py` loader) + the staged `source_documents/` (real PA docs + PDFs). | *Data acquisition / synthetic data generation* |
| **`/specs`** | Product & technical specifications, architecture + diagrams, brand-voice spec, the presentation script, and a study guide. | *Markdown product & technical specs* |
| **`/pipeline_and_tests`** | The **confidence metric** (`scoring.py`), **data-quality gates** (`gates.py`), the **test suite** (`tests/`), and the **evaluation runner** (`make_report.py` → `REPORT.md`). | *Code for calculating the metric + data-quality tests* |
| **`/dashboard`** | The runnable application: the agent engine (`app/`) + the web UI (`ui/`, incl. the metrics Dashboard tab). **This is the source of truth for all runnable code.** | *Visualization prototype* |
| **`/presentation`** | The executive decks (`slides.html` technical, `presentation.html` visual) — open in a browser to present live — plus `SLIDES_OUTLINE.md` (paste-ready for Google Slides). | *Executive Presentation* |

> **A note on structure:** this is a single, cohesive application. The runnable source of
> truth lives in **`/dashboard`**. To honor the requested layout, the data-generation
> scripts, the metric/test code, and the specs are also surfaced into their named folders
> (a couple of engine files appear there for review, with a header pointing to the source
> of truth). The "metric" in this product is the **deterministic confidence score**; the
> "data-quality tests" are the **citation/approval/freshness gates** plus the unit tests.

---

## Run the dashboard locally (5 steps)

```bash
# 1. Create a Python 3.11 environment (uv shown; venv/conda also fine)
uv venv --python 3.11           # or: python3.11 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt   # (or: uv pip install -r requirements.txt)

# 3. Build the knowledge base (offline — no API key needed; uses local embeddings)
cd dashboard
python -m app.ingest --reset

# 4. (Optional) add a Claude key for real answers — without it the app runs in MOCK mode
cp .env.example .env             # then paste ANTHROPIC_API_KEY=...

# 5. Run
uvicorn app.main:app --reload --port 8077
#    open http://localhost:8077
```

- **No API key?** It still runs — LLM steps return deterministic stand-ins (MOCK mode) so
  you can see the full pipeline. Embeddings + the dashboard are real either way.
- **Run the tests / evaluation:**
  ```bash
  cd pipeline_and_tests
  python -m pytest                # 33 deterministic tests
  python make_report.py           # regenerates REPORT.md (needs a key — makes live calls)
  ```

---

## What it does (the 30-second tour)
1. **Ask** a product question → the agent retrieves approved passages, drafts a
   **claim-first** answer where every claim cites a passage, and shows the **exact quote**.
2. **Confidence** is *calculated* (citation coverage, relevance, source authority,
   freshness) — never guessed by the LLM — and **explained** in the UI.
3. **Can't prove it?** It doesn't bluff — it **escalates to the right SME group** and
   **emails** them.
4. **SME answers** in the queue → **Approve & Publish** → it becomes approved knowledge and
   is **instantly citable** for everyone (the knowledge flywheel).
5. **Feedback** ("this answer is wrong") lowers a source's reputation and opens a ticket.

## Tech stack
FastAPI · LanceDB (vector store + metadata) · Claude (Opus 4.8 facts/style, Haiku 4.5
classify) · local `sentence-transformers` embeddings + cross-encoder reranker · vanilla
HTML/JS UI · `pytest`.

## Executive presentation
Open [`presentation/slides.html`](presentation/slides.html) (technical) or
[`presentation/presentation.html`](presentation/presentation.html) (visual) in a browser
to present live — arrow keys to navigate. A paste-ready outline for Google Slides is in
[`presentation/SLIDES_OUTLINE.md`](presentation/SLIDES_OUTLINE.md).
**Google Slides:** _<add your link here>_

## Where to read more
- **Architecture + diagrams:** [`specs/architecture.md`](specs/architecture.md)
- **Evaluation results:** [`pipeline_and_tests/REPORT.md`](pipeline_and_tests/REPORT.md)
- **Presentation script + Q&A bank:** [`specs/presentation_script.md`](specs/presentation_script.md)
- **Learning companion (concepts explained):** [`specs/study_guide.md`](specs/study_guide.md)
