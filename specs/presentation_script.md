# Evidence-Governed Knowledge Agent for Technical Sales
### Panel presentation — speaker script & prep (60 min)

> Slide deck: open **`slides.html`** in a browser (arrow keys to navigate, `P` to toggle
> the PDF print view). This file is the talk track + Q&A bank behind those slides.
> Live demo: `uvicorn app.main:app --port 8077` → http://localhost:8077

**One-line thesis:** I built an *evidence-governed RAG platform*, not a chatbot — every
answer is grounded in approved sources, cites the exact text, and carries a
**deterministically-calculated** confidence score; weak or missing evidence is routed
to the right SME, whose answer becomes reusable knowledge.

---

## 0. Time budget (60 min)
| Section | Time | What I'll prove |
|---|---|---|
| Introduction | 5 | My "Technical PM" operating system |
| Context & Problem | 5 | The user pain and why a generic chatbot fails |
| Technical Deep Dive | 15 | Architecture, data pipeline, the trade-offs I'd defend |
| Evaluation & Results | 10 | A KPI-tied eval framework + the hard truths |
| Panel Q&A | 25 | Defend the trade-offs and the roadmap |

---

## 1. Introduction (5 min) — Technical PM philosophy

I lead with three principles, and the whole build is an expression of them:

1. **Ship the thinnest vertical slice that retires the riskiest assumption first.**
   The riskiest assumption here isn't "can an LLM answer product questions" — it's
   "can Technical Sales *trust* it in front of a customer." So the first slice I built
   end-to-end was: question → cited answer → calculated confidence → escalation. Not the
   UI, not connectors — the trust loop.

2. **Put determinism where trust lives; put the LLM where language lives.**
   The LLM classifies, drafts claims, and styles. It never decides confidence, never
   decides what counts as a citation, never decides whether to answer. Those are pure
   Python, unit-tested, auditable. This is the single most important product decision.

3. **Make the system's trust legible.** A "Medium" label is useless. "Medium because the
   only source was reviewed 241 days ago" changes how an SE uses the answer. Every score
   is explained and every claim shows the exact source text inline.

I'll come back to all three.

---

## 2. Context & Problem (5 min)

**The user:** Technical Sales / Sales Engineers. In a live customer call they get asked
"Does Prisma Access support X in version Y?" The cost of a confident-but-wrong answer is
asymmetric — it loses technical credibility and can lose the deal.

**The pain, concretely:**
- Product truth is sprawled across admin guides, release notes, KB, Confluence — across
  multiple products and versions, and it goes stale.
- The real experts (SMEs) answer the same questions repeatedly in Slack; that knowledge
  never becomes reusable.
- A generic LLM chatbot makes this *worse*: it hallucinates with confidence and has no
  audit trail. For a security vendor, an unsourced claim is a liability.

**So the task is not "a chatbot."** It's an **evidence-governed RAG system** with a
human-in-the-loop knowledge flywheel. Reframed requirements:
- No citation → no answer. Every factual claim maps to approved source text.
- Confidence is **High/Medium/Low**, *calculated*, and *explained*.
- Missing/weak evidence → routed to the correct SME group (and they're notified).
- SME answers become governed, citable knowledge for everyone next time.
- A brand voice that's sales-ready without weakening technical accuracy.

---

## 3. Technical Deep Dive (15 min)

### 3a. Architecture (end-to-end)
```
Question
  → Classify (product/feature/intent)          ── Haiku (cheap, fast)
  → Retrieve  vector search → cross-encoder rerank → freshness/reputation boost
              → drop deprecated / unapproved / off-product   ── LanceDB, local models
  → Evidence Pack (ONLY chunk text + ids)
  → Facts engine: claim-first answer, every claim cites a chunk  ── Opus
  → HARD GATES (pure Python): every claim cited? sources approved & not deprecated?
              product match?  ── fail → ESCALATE
  → Scoring (pure Python): Technical Trust Score + confidence caps → High/Med/Low
              ── Low → ESCALATE
  → Style layer: brand voice over validated claims + guards     ── Opus
  → Answer (embeds exact evidence)  |  Escalation → route to SME → email → publish back
```
**The Facts↔Style wall:** the model that touches evidence never styles; the model that
styles never sees raw evidence — it only gets *already-validated* claims + caveats, and
its output is re-checked (no new claims, no dropped caveats). This is how I get brand
voice *without* risking accuracy — the answer to the classic "make it less robotic" ask.

### 3b. Data Strategy
**Acquisition (three sources, deliberately):**
- **Real docs** — a sub-agent crawled `docs.paloaltonetworks.com` (Prisma Access,
  Cortex XDR, NGFW/PAN-OS), extracted the technical text, and staged it as
  Markdown+frontmatter. ~17 pages, 68 chunks.
- **PDFs** — `pypdf` ingestion with a metadata sidecar (SEs live in PDF datasheets).
- **Synthetic** — hand-seeded edge cases I *needed* to exist to test governance: a
  deliberately stale doc, a deprecated doc. You can't validate a freshness cap without a
  stale document.

**Quality & alignment — metadata is a first-class citizen.** Every chunk carries product,
feature, version, source_type, owner, **last_reviewed_date**, **deprecated**, approval
status, and up/down votes. That metadata isn't decoration — it *drives* retrieval
(deprecated/unapproved are never surfaced), scoring (authority + freshness), and routing.

**Hard truth #1 (data):** the Cortex XDR docs portal is JavaScript-rendered — the fetch
tool returned nothing. I didn't paper over it; I sourced Cortex content from
server-rendered pages and *named the coverage gap*. That gap is exactly why a Cortex
exploit-protection question correctly escalates in the demo. Honest data boundaries beat
fake completeness.

### 3c. System design trade-offs (the part to defend)
| Decision | Chose | Over | Why |
|---|---|---|---|
| **Confidence** | Deterministic Pareto rubric (Python) | LLM-judged confidence | Auditable, reproducible, can't be gamed by a fluent answer; a security buyer needs to see the math. The LLM is the *least* trustworthy thing to ask "how sure are you?" |
| **Grounding** | Hard gates ("no citation, no answer") | Prompt-only "please cite" | Prompts are probabilistic; a gate is a guarantee. |
| **Vector store** | LanceDB (embedded) | Pinecone / pgvector | Vectors **+** metadata **+** reranker in one file-based store → zero infra, MVP velocity. Buy-the-managed-service later when scale demands. |
| **Facts/Style model** | Opus 4.8 | Haiku | Grounding fidelity and caveat preservation matter most where hallucination is the risk. |
| **Classifier model** | Haiku | Opus | Latency/cost — it's a cheap routing call; skipped entirely if product is known. |
| **Embeddings** | Local sentence-transformers | Voyage/OpenAI | Free, offline, no key for the MVP. Note: Anthropic has **no** embeddings API — Voyage is the recommended partner; swap is one line. |
| **Reranker** | Local cross-encoder (ordering only) | Cohere Rerank API | No key/cost; and I learned its score isn't a reliable *absolute* signal (see hard truth #2). |

This is a **Build-vs-Buy** story: build the trust logic (it's the differentiator and must
be auditable), buy/borrow the commodity infra (vector store, embeddings) and swap as we
scale.

---

## 4. Evaluation & Results (10 min)

### 4a. Beyond loss functions — success tied to business KPIs
There's no single label to optimize; "loss" is meaningless for a trust product. I defined
success as **trust/safety SLOs**, because those map to the business outcome (an SE can
rely on it live):

| KPI | Target | Why it's the business metric |
|---|---|---|
| Factual claims with a citation | 100% | Trust precondition; this is the product promise |
| Broken-citation rate | < 1% | A dead link destroys credibility |
| Unsupported-claim rate | < 2% | Hallucination ceiling |
| Deprecated-source usage | 0% | Wrong-version answers lose deals |
| Low-confidence shown without escalation | 0% | The system must know what it doesn't know |
| SME answer reuse | ↑ month/month | The knowledge flywheel is working |

### 4b. The eval harness
- A **5-easy / 5-medium / 5-hard** question set, run live, producing `REPORT.md` with
  full per-question score breakdowns. Result: **5/5/5** — easy→High, medium→Medium
  (freshness-capped), hard→escalated.
- The deterministic core (gates, scoring, caps, brand-voice rubric, routing) is locked by
  **31 unit tests** — the scoring can't silently drift.
- The confidence rubric is *demonstrated*, not asserted: real docs aged ~241 days cap to
  Medium; >365 days pushes to Low/escalate, with the reason shown in the UI.

### 4c. Hard truths (the "what I learned" — lead with these, panels love them)
1. **Cross-encoder logits aren't calibrated.** My first off-topic filter used an absolute
   reranker-score floor. It was *wrong*: the correct chunk scored −1.0 while an off-topic
   chunk scored +1.5. Lesson: rerankers are for *ordering*, not absolute relevance. I
   moved the off-topic gate to the LLM facts engine (which returns INSUFFICIENT_EVIDENCE)
   and used calibrated vector similarity for scoring.
2. **`temperature` is deprecated on Opus 4.8.** I added `temperature=0` chasing
   determinism; it 400'd, and my fail-closed design silently escalated *all 15* eval
   questions. Two lessons: (a) determinism belongs in the Python scoring layer, not
   sampling; (b) fail-closed is right, but a swallowed error needs an alert.
3. **A fail-safe can become bad UX.** The facts engine was over-cautious — it escalated
   answerable questions. Since the citation gate already prevents hallucination, I biased
   it toward answering. Trust ≠ refusing; trust = answering *when grounded*.
4. **Determinism has sharp edges.** A terminology normalizer turned "Palo Alto Networks"
   into "Palo Alto Networks **Networks**" (a variant was a prefix of the canonical). Small
   bug, but it's why I write tests for the deterministic layer.

### 4d. The Human-in-the-Loop (interface between AI logic and the user)
- **Attribution UI:** the answer embeds the **exact cited chunk text** inline (not just a
  link) — an SE verifies the AI's work without leaving the page.
- **Explainable confidence:** pill + score breakdown (citation/relevance/authority/
  freshness) + the cap reason, all visible.
- **SME flywheel:** escalation → **feature-level routing** → **email notification** to the
  SME group → SME answers in the queue → **Approve & Publish** writes it back to the KB →
  instantly citable. I demoed this end-to-end.
- **Feedback loop without retraining:** "This answer is wrong" lowers source reputation
  (feeds reranking *and* the confidence cap) and opens an SME ticket. Feedback → ranking,
  not feedback → retrain.
- **Brand voice as a separate, file-configurable layer** (`brand_voice.yaml`): deterministic
  terminology enforcement, banned-phrase guards, and a scored rubric — tunable without code.

---

## 5. Retrospective (woven into deep-dive/results, ~2 min)

**If I rebuilt it on today's stack:**
- **Agentic retrieval** — query decomposition + Corrective/Self-RAG: the agent critiques
  its own evidence and re-queries before answering, instead of one-shot retrieval.
- **A tool-using agent** that can do a live doc lookup when the KB is thin, rather than
  escalating immediately (escalate only after the agent fails).
- **LLM-as-judge as a *second* eval signal** — to auto-grade a large eval set nightly and
  catch regressions. Note: a judge for *evaluation*, never for *user-facing confidence*.
- **Better retrieval** — Voyage embeddings + hybrid (BM25 + dense) + a fine-tuned reranker
  trained on the accumulated feedback (closing the loop I stubbed).
- **Real connectors** (Confluence/Jira/ServiceNow) and streaming token UX.
- **Agentic SME drafting** — pre-draft the SME answer from partial evidence so the SME
  edits instead of writes.

**What I would NOT change — the things that earned trust:** deterministic confidence, the
hard citation gates, and the Facts↔Style wall. Those are the spine.

---

## 6. Panel Q&A bank (prepare to defend)

**Q: Why deterministic confidence instead of asking the model for a confidence score?**
A model's self-reported confidence correlates with fluency, not correctness — it's
confidently wrong. A buyer in security needs to audit *why* an answer is trusted. My score
is a transparent function of citation coverage, retrieval relevance, source authority, and
freshness, with explicit caps. It's reproducible and testable; an LLM number is neither.

**Q: How do you actually prevent hallucination?**
Three layers. (1) The model only ever sees an Evidence Pack — it can't draw on training
data for facts. (2) Claim-first output: every claim must name a chunk id. (3) Hard Python
gates reject the answer if any claim is uncited, cites an unapproved/deprecated source, or
mismatches the product — and route to SME. Prompting asks; gates guarantee.

**Q: Brand voice vs. technical accuracy — how do you get both?**
The Facts↔Style wall. Style runs on *validated claims only*, never raw docs, and its output
is re-checked: no new claims, no dropped caveats, citations intact, banned phrases blocked.
A beautifully-worded answer with weak evidence is still Low confidence — voice and trust are
scored separately (80/20) and voice can never raise trust.

**Q: A document is downvoted or old — what happens?**
Both are first-class signals. Freshness: >180 days caps to Medium, >365 to Low/escalate.
Reputation: downvote ratio >15% caps to Medium, >30% to Low; it also pushes the source down
in ranking. So a stale/downvoted doc can still inform an answer but can't produce High
confidence — and it surfaces for review.

**Q: Build vs buy — justify LanceDB / local models.**
For an MVP I optimize for velocity and auditability of the *differentiator* (trust logic),
and for zero-infra on the *commodity* (vector store, embeddings). LanceDB gives vectors +
metadata + reranking in one embedded store. At scale I'd move to a managed vector DB and
Voyage embeddings — both are one-line swaps because I kept them behind boundaries.

**Q: Latency?**
Worst case is 3 LLM calls (Haiku classify + Opus facts + Opus style). Classify is skipped
when product is known; gates/scoring are sub-millisecond Python. To cut latency: stream the
style pass, cache classification, and (at scale) a smaller fine-tuned model for facts on
common questions.

**Q: How do you measure ROI / success to an exec?**
Leading indicators: % questions answered with High/Medium confidence (deflection), SME
escalation rate (and its decline as the flywheel fills the KB), helpful-rate, and time-to-
answer. Lagging: SE-reported deal-impact and reduced SME interrupt load. The KB *improves
itself* via SME publish + feedback, so cost-per-answer drops over time.

**Q: How does this scale to thousands of docs / many products?**
Retrieval is already metadata-filtered (product/version), so it scales horizontally; swap
to a managed vector DB + hybrid search. Governance scales via the review-date SLAs and the
reputation signals (the dashboard already flags "sources needing review"). The human
bottleneck is SMEs — which is why agentic SME drafting is top of the roadmap.

**Q: What about data governance / compliance?**
Only `approved`, non-deprecated sources are citable; every answer is audit-logged with its
claim→source map and score breakdown; SME-published knowledge has an owner and review date.
That audit trail is the compliance story.

**Q: What's the single biggest risk?**
Stale knowledge presented confidently. That's *exactly* what the freshness caps, review-date
governance, and the "0% deprecated usage" SLO are designed to prevent — and why I'd never
let the LLM set confidence.

---

### Appendix — repo map for live demo
- `app/pipeline.py` — the orchestration (the 8 steps).
- `app/gates.py`, `app/scoring.py` — the deterministic trust core (+ `tests/`).
- `app/brand_voice.py` / `brand_voice.yaml` — file-configurable voice.
- `app/notify.py` — SME email workflow.
- `REPORT.md` — the 5/5/5 evaluation. `ARCHITECTURE.md` — diagrams.
