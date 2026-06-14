# Slide Outline — paste-ready for Google Slides

The visual decks (`slides.html` technical · `presentation.html` visual) render perfectly
in a browser and can be **presented live**. This outline mirrors the **technical deck**
(agenda-aligned) so you can rebuild it in Google Slides in ~15 minutes — paste each slide's
title + bullets, or feed this file to an AI slide tool (Gamma, SlidesAI, Plus AI).

> Tip to build fast: open `slides.html` in Chrome as your **visual reference**, then
> recreate each slide in Google Slides using the text below. Keep it sparse — bullets are
> talking-point anchors, not paragraphs.

---

## Slide 1 — Title
**Evidence-Governed Knowledge Agent for Technical Sales**
- An evidence-governed RAG platform — not a chatbot.
- Every answer is grounded in approved sources, cites the exact text, and carries a deterministically-calculated confidence score.
- Weak evidence routes to an SME, whose answer becomes reusable knowledge.
- _Live build: FastAPI · LanceDB · Claude (Opus 4.8 / Haiku 4.5) · deterministic scoring engine_

## Slide 2 — Agenda (60 min)
| Section | Time | What I'll prove |
|---|---|---|
| Introduction | 5 | My Technical-PM operating system |
| Context & Problem | 5 | The user pain; why a chatbot fails |
| Technical Deep Dive | 15 | Architecture, data pipeline, trade-offs |
| Evaluation & Results | 10 | KPI-tied eval + the hard truths |
| Panel Q&A | 25 | Defend trade-offs & roadmap |

## Slide 3 — My Technical-PM operating system (Introduction)
1. **Slice the risk** — ship the thinnest vertical that retires the riskiest assumption first (here it's *trust*, not "can an LLM answer").
2. **Determinism where trust lives** — the LLM classifies, drafts, and styles; it never decides confidence, citations, or whether to answer.
3. **Make trust legible** — "Medium because the only source is 241 days old" beats a bare label. Every score is explained; every claim shows its source.
- _Speaker note: lead with your CRM background — you've shipped Knowledge + routing for sales teams._

## Slide 4 — The problem (Context)
- **Technical Sales / SEs**, live in a customer call: "Does Product X support Y in version Z?"
- A confident-but-wrong answer loses **credibility** and the deal.
- Truth is scattered across docs/release-notes/wikis and **goes stale**.
- A generic chatbot makes it **worse** — it hallucinates with no proof, no audit trail.
- → The task is an **evidence-governed RAG system**, not a chatbot.

## Slide 5 — Four product principles
1. **No citation → no answer** (enforced in code, not by prompt).
2. **Confidence is calculated, not generated** (the LLM never sets it).
3. **Brand voice is a presentation layer** (can clarify; can't add claims or drop caveats).
4. **SME answers become governed knowledge** (owned, citable, review-dated).

## Slide 6 — Architecture: end-to-end flow (Technical Deep Dive)
`Question → 1 Classify (Haiku) → 2 Retrieve (LanceDB + rerank + freshness/reputation) → 3 Evidence Pack → 4 Facts engine (Opus, claim-first) → 5 GATES (Python) → 6 SCORE (Python) → 7 Style (Opus) → Answer` — with `gate/Low → escalate to SME`.
- The LLM does only steps 1, 4, 7. Gates (5) and Score (6) are auditable Python.

## Slide 7 — The Facts ↔ Style wall (key idea)
- **Facts engine** touches evidence → produces validated claims + caveats + a calculated confidence. Never styles.
- **Style layer** never sees raw docs → rewrites in brand voice, then is re-checked (no new claims, no dropped caveats).
- This is how you answer "make it less robotic" **without** risking accuracy. Voice can never raise trust.

## Slide 8 — Data Strategy: acquisition
- **Real docs** — crawled docs.paloaltonetworks.com (Prisma Access, Cortex XDR, NGFW). ~17 pages, 68 passages.
- **PDFs** — ingested via pypdf + metadata sidecar.
- **Synthetic** — hand-generated stale + deprecated edge cases (you can't test a freshness rule without a stale doc).
- **Hard truth:** the Cortex portal is JS-rendered → couldn't crawl it → I named the gap instead of faking coverage.

## Slide 9 — Data Strategy: quality & alignment
- Every passage carries product, feature, version, source type, owner, **last-reviewed date**, **deprecated flag**, approval status, votes.
- Metadata **drives** retrieval (deprecated never surfaces), scoring (authority + freshness), and routing.
- _Analogy: a governed Salesforce object with required fields — not a free-text notes field._

## Slide 10 — System design & trade-offs
| Decision | Chose | Over | Why |
|---|---|---|---|
| Confidence | Deterministic rubric | LLM-judged | Auditable, can't be gamed by fluency |
| Grounding | Hard gates | Prompt "please cite" | A gate guarantees; a prompt hopes |
| Vector store | LanceDB (embedded) | Pinecone/pgvector | Vectors+metadata+rerank, zero infra |
| Facts model | Opus 4.8 | Haiku | Accuracy where hallucination hurts |
| Classifier | Haiku 4.5 | Opus | Latency/cost on a routing call |
| Embeddings | Local | Voyage/OpenAI | Free/offline MVP; one-line swap |
- **Umbrella:** build the differentiator (trust logic), buy the commodity infra.

## Slide 11 — The Human in the Loop
- **Attribution UI** — the exact cited source text is shown **inline**; verify without leaving the screen.
- **Explainable confidence** — pill + score breakdown + cap reason.
- **SME flywheel** — escalate → feature-level routing → **email the SME** → Approve & Publish → instantly citable.
- **Feedback → ranking, not retraining** — "wrong answer" lowers reputation + opens a ticket.
- _Analogy: Omni-Channel routing + Approval Process + Knowledge publishing._

## Slide 12 — Evaluation: success beyond loss (Evaluation & Results)
- No single label to optimize — it's a **trust** product. Success = trust SLOs:
| KPI | Target |
|---|---|
| Factual claims with a citation | 100% |
| Broken-citation rate | < 1% |
| Unsupported-claim rate | < 2% |
| Deprecated-source usage | 0% |
| Low-confidence shown without escalation | 0% |
| SME-answer reuse | ↑ over time |

## Slide 13 — Evaluation: the harness & results
- **5 easy / 5 medium / 5 hard** question set, run live → **5/5/5** (easy→High, medium→Medium/capped, hard→escalated).
- **33 unit tests** lock the deterministic scoring so it can't drift.
- The rubric is *demonstrated*: a real 241-day-old doc caps to Medium; >365 days → Low/escalate.

## Slide 14 — The hard truths (what broke)
1. **Rerankers aren't calibrated** — the correct passage scored *lower* than an off-topic one; rerankers order, the LLM judges sufficiency.
2. **Opus deprecates `temperature`** — chasing determinism I set it → error → fail-safe escalated all 15. Determinism belongs in Python.
3. **A fail-safe became bad UX** — it over-escalated answerable questions; I tuned it to answer when grounded.
4. **One downvote shouldn't bury a source** — added a 5-vote floor before reputation can cap.

## Slide 15 — Retrospective
**Would change:** agentic (Corrective/Self-RAG) retrieval; a tool-using agent for live lookups; LLM-as-judge as a *second eval* signal (never confidence); hosted embeddings + hybrid search + feedback-fine-tuned reranker; real Confluence/Jira connectors; streaming UX; agentic SME drafting.
**Would NOT change (the spine):** deterministic confidence · hard citation gates · the Facts↔Style wall.

## Slide 16 — Panel Q&A: ready to defend
- Why deterministic confidence, not the model's? · How do you actually stop hallucination? · Brand voice vs accuracy? · Old/downvoted docs? · Build vs buy? · Latency? · ROI to an exec? · Biggest risk (stale knowledge, confidently presented)?
- _Full answers: specs/study_guide.md §11 and specs/presentation_script.md._

## Slide 17 — Close
**A measurable, auditable agent Technical Sales can trust.**
- Answer only from approved evidence · cite the exact text · calculate confidence deterministically · escalate the gaps · turn SME answers into reusable knowledge.

---

### Visual deck (alternate, for a non-technical room) — `presentation.html`
A lighter 13-slide version with charts (donut of KB by product, 5/5/5 results bars, KPI
scorecards, a plain-language 5-step architecture). Use it if the audience is non-technical;
otherwise the 17-slide technical deck above maps to the panel agenda.
