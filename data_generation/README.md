# /data_generation

How the knowledge base (the agent's "dataset") was acquired and generated.

## Three sources, on purpose
1. **Real product docs** — a helper agent crawled `docs.paloaltonetworks.com`
   (Prisma Access, Cortex XDR, NGFW/PAN-OS), extracted the technical text, and staged it as
   Markdown-with-frontmatter. See `source_documents/`.
2. **PDFs** — ingested via `pypdf` with a metadata sidecar (sales engineers live in
   datasheet PDFs). A sample PDF is included in `source_documents/`.
3. **Synthetic edge cases** — `seed.py` hand-generates records we *needed* in order to
   test the governance rules: a deliberately **stale** document and a **deprecated** one.
   *You cannot validate a "stale source gets downgraded" rule without owning a stale
   source — so I generated the exact edge cases the evaluation required.*

## Data quality / alignment
Every passage carries metadata that **drives** the system: product, feature, version,
source type, owner, **last-reviewed date**, **deprecated flag**, approval status, and
up/down votes. Deprecated/unapproved/off-product passages are dropped at retrieval and can
never reach an answer.

## Files
- `seed.py` — synthetic edge-case generator (review copy; runs from `/dashboard`).
- `ingest.py` — chunks + embeds `source_documents/` into the vector store (review copy).
- `source_documents/` — the staged dataset (Markdown + PDF).

## Build the dataset
```bash
cd ../dashboard
python -m app.ingest --reset     # builds the vector store from source_documents
# (or `python -m app.seed` for the tiny synthetic demo set)
```
> Runnable source of truth: `dashboard/app/seed.py` and `dashboard/app/ingest.py`.
