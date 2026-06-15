# Presenter's Study Guide
### Understand the whole system well enough to defend it.

> Companion to: `slides.html` (technical deck), `presentation.html` (visual deck),
> `PRESENTATION.md` (talk script + Q&A bank), `ARCHITECTURE.md` (diagrams).
> This file is for *learning* — read it twice and you can defend any question.

---

## 0. The mindset (read this first)
You are presenting as a **Technical PM**, not an ML engineer. Panels are not testing
whether you can hand-derive a neural network. They are testing whether you can:
1. **Frame a real user problem** and the cost of getting it wrong.
2. **Reason about trade-offs** (accuracy vs latency, build vs buy, deterministic vs AI).
3. **Define success with metrics** that tie to the business.
4. **Be honest** about what broke and what you'd change.

Your Salesforce background is a *strength*. This product maps almost 1:1 to things you
already know:

| This AI product | Your Salesforce world |
|---|---|
| Knowledge Base of approved docs | **Salesforce Knowledge** articles |
| "No citation, no answer" gates | **Validation Rules** |
| Route unanswered Q to an SME group | **Omni-Channel routing / Case escalation rules** |
| SME approves an answer → published | **Approval Processes** + publishing a Knowledge article |
| "This answer is wrong" button | **Article rating / Case feedback** |
| Confidence score (High/Med/Low) | **Einstein Lead/Opportunity Scoring** — but a transparent formula |
| Email + bell to notify SMEs | **Email alerts / notifications** |
| Freshness review dates | Knowledge **article review/expiration dates** |

Lead with that: "I'm a CRM PM. I've shipped knowledge and routing systems for sales
teams. I built this the way I'd build a trustworthy Service Cloud feature — grounded,
governed, and measurable."

---

## 1. AI vocabulary crash course (plain English + analogy)
Learn these eight terms. The panel will use them; you should too.

**1. LLM (Large Language Model)** — e.g. Claude. A very well-read assistant that predicts
text. Incredibly fluent, but it will **make things up confidently** ("hallucinate") if you
let it answer from memory. *Analogy: a brilliant new sales rep who never says "I don't
know" — dangerous in front of a customer.*

**2. RAG (Retrieval-Augmented Generation)** — the core pattern of this whole product.
Instead of letting the LLM answer from memory, you **first retrieve the relevant approved
documents, then say "answer ONLY using these."** *Analogy: hand the rep the official
product binder and say "only quote from this, and cite the page."* RAG = retrieval (find
the pages) + generation (write the answer from them).

**3. Embedding** — turning a piece of text into a list of numbers (coordinates) that
capture its *meaning*, so a computer can measure how similar two texts are in meaning, not
just keywords. *Analogy: how Salesforce can tell two leads are "basically the same
company" even if spelled differently — similarity matching, but for meaning.*

**4. Vector database (we used LanceDB)** — the filing cabinet that stores those number-
coordinates and instantly returns the most similar passages to a question. *Analogy: a
search index built on meaning instead of exact words.*

**5. Chunking** — splitting a long document into small passages (a few sentences each) so
you retrieve *just the relevant paragraph*, not a 200-page manual. *Analogy: breaking a
Knowledge article into snippets.*

**6. Reranking (cross-encoder)** — a second, smarter pass that re-orders the retrieved
passages by relevance to the exact question. *Analogy: Sales Ops re-prioritizing a call
list after the first rough sort.*

**7. Classifier** — a quick step that labels the question ("this is about Prisma Access,
the Remote Networks feature"). *Analogy: an auto-categorize/assignment rule.*

**8. Deterministic vs. generative** — *Deterministic* = plain code that always gives the
same answer (a formula, a rule). *Generative* = the LLM, which is probabilistic. **The
single most important design choice in this product: put trust decisions in deterministic
code, and only use the LLM for language.**

---

## 2. The product in one paragraph
Technical Sales reps get hard product questions live in customer calls. A wrong answer
loses credibility and deals. We built an **evidence-governed RAG agent**: it answers
*only* from approved Palo Alto sources, **cites the exact text**, and attaches a
**deterministically-calculated confidence score**. If it can't prove an answer, it doesn't
guess — it **routes the question to the right SME group**, notifies them, and when the SME
answers, that answer becomes **reusable approved knowledge** for everyone. Brand voice is a
separate layer so answers sound consultative without ever changing the facts.

---

## 3. The architecture — the 8 steps, what/why/how
This is your Technical Deep Dive. Memorize the flow; for each step know *what it does* and
*why it's there.*

```
Question
 1 Classify  → 2 Retrieve → 3 Evidence Pack → 4 Draft (facts) →
   5 GATES → 6 SCORE → 7 Style → Answer   |   (5 or 6 fail → ESCALATE to SME)
```

**Step 1 — Classify (LLM: Claude Haiku).** Detect product/feature/intent.
*Why Haiku (the small, fast, cheap model)?* It's a simple routing call — **latency/cost
trade-off**: don't pay for the big model on an easy task. Skipped entirely if the user
already picked a product.

**Step 2 — Retrieve (LanceDB + local models).** Embed the question, find the most similar
approved passages, **rerank** them, then nudge the order using **freshness** and
**reputation** (downvotes push a source down). Crucially, **deprecated, unapproved, or
wrong-product passages are dropped here** — they can never reach the answer.

**Step 3 — Evidence Pack.** We hand the LLM **only the retrieved passages** (text + ids) —
nothing else. *Why?* So it physically cannot answer from its training memory. This is what
makes hallucination structurally hard, not just discouraged.

**Step 4 — Draft / Facts engine (LLM: Claude Opus).** The model writes a **claim-first**
answer: every factual claim must name the passage id it came from. If the evidence doesn't
support an answer, it returns `INSUFFICIENT_EVIDENCE`.
*Why Opus (the big, accurate model) here?* This is where grounding fidelity matters most —
**accuracy over latency** for the step that can hurt you.

**Step 5 — GATES (plain Python, no AI).** Hard rules: every claim cited? all cited sources
approved and not deprecated? product matches? **If any fail, the answer is blocked and the
question is escalated.** *Analogy: Validation Rules.* This is the "no citation, no answer"
guarantee — a prompt only *asks*; a gate *guarantees*.

**Step 6 — SCORE (plain Python).** Calculate the **Technical Trust Score** (0–100) and
apply caps → **High / Medium / Low**. (Details in §5.) Low → escalate.

**Step 7 — Style / Brand voice (LLM: Claude Opus).** Rewrite the *validated claims* in
brand voice, then re-check it didn't add claims or drop caveats. (Details in §6.)

**Then:** format the answer (with the embedded source quotes) **or** create an SME
escalation, notify the group, and wait for a human.

**The one-liner to repeat:** *"The LLM only classifies, drafts, and styles. Every trust
decision — what counts as a citation, whether to answer, how confident we are — is plain,
auditable, tested Python. That's deliberate."*

---

## 4. Data Strategy (presentation topic #1)
**The ask: data acquisition / synthetic generation, and ensuring quality & alignment.**

**Acquisition — three sources, on purpose:**
1. **Real docs** — a helper agent crawled `docs.paloaltonetworks.com` (Prisma Access,
   Cortex XDR, NGFW/PAN-OS), pulled the technical text, and staged it as Markdown with a
   metadata header. Result: ~17 pages, 68 passages.
2. **PDFs** — we added PDF ingestion (sales engineers live in datasheet PDFs).
3. **Synthetic** — we hand-created a few edge cases we *needed* in order to test the
   governance: a deliberately **stale** document and a **deprecated** one.

**Why synthetic data?** This is a great PM point: *"You cannot validate a 'stale document
gets downgraded' rule without owning a stale document. I generated the exact edge cases my
evaluation required."*

**Quality & alignment — metadata is a first-class citizen.** Every passage carries:
product, feature, version, source type, owner, **last-reviewed date**, **deprecated flag**,
approval status, and up/down votes. That metadata isn't decoration — it **drives**
retrieval (deprecated never surfaces), scoring (authority + freshness), and routing.
*Analogy: a well-governed Salesforce object with required fields and record types — not a
free-text notes field.*

**The hard truth to tell (panels love honesty):** the Cortex XDR docs portal is
JavaScript-rendered, so our crawler couldn't read it. I didn't fake coverage — I sourced
Cortex content from pages that *did* render and **named the gap**. That gap is exactly why a
Cortex exploit-protection question correctly escalates in the demo. *Honest data boundaries
beat fake completeness.*

---

## 5. Confidence scoring — the rubric (your strongest "wow")
**This is the heart of the product and a guaranteed panel question** ("how did you build the
confidence rubric, especially for old/downvoted docs?"). Know it cold.

**Principle: the LLM never decides confidence.** A model's self-confidence tracks fluency,
not correctness — it's confidently wrong. So we *calculate* it. *Analogy: you'd never let a
rep self-report their deal's health; you use a scoring formula.*

**The Technical Trust Score = 100 points, weighted toward what prevents bad answers:**
- **Citation integrity — 40 pts** (are all claims actually backed by a quote?)
- **Retrieval relevance — 25 pts** (how well the evidence matches the question)
- **Source authority — 20 pts** (official docs/release notes = top; SME-verified = near-top)
- **Source freshness — 15 pts** (how recently the source was reviewed)

**Then "caps" override the number** (this answers the old/downvoted question directly):
- Source reviewed **> 180 days** ago → **capped to Medium**; **> 365 days** → **Low**.
- Downvote ratio **> 15%** → Medium; **> 30%** → Low — *but only after at least 5 votes*, so
  one angry click can't bury a good source.
- A single non-official source → Medium (SME-verified answers are exempt — a human checked
  them).

Score ≥ 85 = High, 65–84 = Medium, < 65 = Low. **Low always escalates.** And every score is
**explained** in the UI ("Medium because the only source is 241 days old") — *legible trust,
not a black box.*

There's also a **separate** Experience/Brand-voice score (also out of 100). The final
quality number is **80% trust + 20% experience** — accuracy first, polish second. **Brand
voice can never raise the trust score.**

---

## 6. The Human in the Loop (presentation topic #3) — your home turf
This is where your CRM experience shines. Two parts: the *attribution interface* and the
*SME workflow*.

**Attribution interface (verify the AI's work):**
- The answer shows a confidence pill, the score breakdown, and — most importantly — the
  **exact source passage quoted inline**. A rep can verify without leaving the screen.
- Clickable: official docs open the real page; SME answers open "View in Knowledge Base."

**The SME flywheel (this is Service Cloud, basically):**
1. Can't answer → **escalate** to the right SME group (feature-level routing — *like
   Omni-Channel skills-based routing*).
2. **Notify** the group by **email** (real SMTP or an offline outbox) **+ an in-app bell**.
3. SME opens the **Queue**, writes the answer, clicks **Approve & Publish** (*an Approval
   Process*).
4. It's saved as an approved Knowledge source and is **instantly citable** for everyone.
5. **Feedback loop:** "This answer is wrong" lowers that source's reputation **and** opens a
   correction ticket — *like rating a Knowledge article down and creating a Case.*

**The key insight to say:** *"The system gets smarter every time an expert answers —
yesterday's escalation is today's instant, cited answer. That's the knowledge flywheel, and
it's the long-term value, not the chatbot."*

**One subtlety to own:** "feedback → ranking, not retraining." We don't retrain a model on
feedback (expensive, slow); feedback adjusts **reputation**, which changes ranking and the
confidence cap. Cheap, immediate, auditable.

---

## 7. System design & trade-offs (presentation topic #2) — be ready to defend each
| Decision | We chose | Over | The reasoning to say out loud |
|---|---|---|---|
| **Confidence** | Deterministic formula | LLM-judged | Auditable & reproducible; a security buyer must see the math. The LLM is the *last* thing to trust with "how sure are you." |
| **Grounding** | Hard code gates | Prompt "please cite" | A prompt hopes; a gate guarantees. |
| **Vector DB** | LanceDB (embedded, free) | Pinecone / Postgres | Vectors + metadata + reranker in one file — **zero infra for an MVP**. Buy the managed service later at scale (build-vs-buy). |
| **Big model (Opus)** | Facts + Style | — | Accuracy where hallucination is the risk. |
| **Small model (Haiku)** | Classify | Opus everywhere | Latency/cost on an easy routing call. |
| **Embeddings** | Local (free, offline) | Voyage/OpenAI (paid) | Good enough for MVP, no key; **Anthropic has no embeddings API** (Voyage is their partner) — one-line swap later. |
| **Reranker** | Local cross-encoder | Cohere API | Free; and I learned its score isn't a reliable *absolute* signal (see §8). |

**The umbrella message:** *"Build the differentiator — the trust logic — because it must be
auditable and it's the moat. Buy/borrow the commodity infrastructure and swap it as we
scale."*

---

## 8. Evaluation & the "hard truths" (presentation topic #4)
**The ask: define a "successful" model beyond loss functions; tie to business KPIs.**

**Why "loss function" doesn't apply here:** there's no single right-answer label to
optimize — this is a *trust* product. So success = **trust/safety SLOs** that map to the
business outcome (a rep can rely on it live):

| KPI | Target | Why it's the business metric |
|---|---|---|
| Factual claims with a citation | 100% | The product promise |
| Broken-citation rate | < 1% | A dead link kills credibility |
| Unsupported-claim rate | < 2% | Hallucination ceiling |
| Deprecated-source usage | 0% | Wrong-version answers lose deals |
| Low-confidence shown without escalation | 0% | The system must know what it doesn't know |
| SME-answer reuse | ↑ over time | The flywheel is working |

**The evaluation harness (this is your "I did real eval" proof):**
- A **5 easy / 5 medium / 5 hard** question set, run live → result **5/5/5**: easy answered
  High, medium answered Medium (freshness-capped), hard correctly escalated. (`REPORT.md`.)
- **33 automated tests** lock the deterministic scoring so it can't silently drift.

**The hard truths — TELL THESE, they're your best material:**
1. **Rerankers aren't calibrated.** My first off-topic filter used the reranker's raw score
   as an absolute cutoff. It was wrong — the *correct* passage scored lower than an
   off-topic one. Lesson: rerankers are for *ordering*; let the LLM judge "is there an
   answer here."
2. **A swallowed error broke the eval.** I set the model's `temperature` to 0 for
   reproducibility; the newest model **deprecated that setting** and returned an error,
   which my "fail safe → escalate" design silently turned into *all 15 questions
   escalating*. Two lessons: determinism belongs in my Python, not model settings; and a
   swallowed error needs an alert.
3. **A fail-safe became bad UX.** The system was *too* cautious and escalated answerable
   questions. Since the citation gate already blocks hallucination, I tuned it to answer
   when grounded. *Trust isn't refusing — it's answering when you can prove it.*
4. **One downvote shouldn't bury a source** (the bug you caught). A single "wrong answer"
   made a source 100% downvoted → permanent Low. I added a 5-vote minimum before reputation
   can cap. *Sparse-data edge case — exactly the kind of thing real usage surfaces.*

---

## 9. Retrospective (presentation topic #5)
**If I rebuilt it on today's stack — what I'd change:**
- **Agentic retrieval** — let the agent *critique its own evidence and re-search* before
  answering (Corrective/Self-RAG), instead of one-shot retrieval.
- **A tool-using agent** that does a live doc lookup when the KB is thin, escalating only
  after it genuinely fails.
- **LLM-as-judge as a second *evaluation* signal** to auto-grade a big test set nightly and
  catch regressions — *a judge for evaluation, never for user-facing confidence.*
- **Better retrieval** — a hosted embedder (Voyage) + hybrid keyword-and-meaning search + a
  reranker fine-tuned on the accumulated feedback (closing the loop I stubbed).
- **Real connectors** (Confluence/Jira/ServiceNow) and a streaming, types-as-it-goes UX.
- **Agentic SME drafting** — pre-draft the expert's answer from partial evidence so they
  *edit* instead of *write*.

**What I would NOT change — the spine that earns trust:** deterministic confidence, the
hard citation gates, and the Facts↔Style wall. *Everything else is an optimization; those
three are the product.*

---

## 10. Mapping to your 60-minute agenda
| Section | Time | What to cover | Lean on |
|---|---|---|---|
| **Introduction** | 5 | Your CRM background as a strength; "Technical PM" philosophy = ship the slice that retires the riskiest assumption (trust), put determinism where trust lives, make trust legible. | §0, §1 |
| **Context & Problem** | 5 | The task is **RAG + human-in-the-loop**, not a chatbot. The SE's live-call pain; the asymmetric cost of a confident wrong answer. | §2 |
| **Technical Deep Dive** | 15 | The 8-step architecture (§3) + Data Strategy (§4) + the trade-offs table (§7). Show the live demo here. | §3, §4, §5, §7 |
| **Evaluation & Results** | 10 | The KPI table, the 5/5/5 harness, and the four hard truths. | §8 |
| **Panel Q&A** | 25 | Defend trade-offs (§7) and roadmap (§9). Use the Q&A bank in `PRESENTATION.md`. | §7, §9, §11 |

**Demo plan (in the Deep Dive):** ask a **High** question (show the answer + the embedded
quote + the score breakdown) → ask a **hard** one (watch it **escalate**) → go to **SME
Queue**, answer it, **publish** → **re-ask** and watch it answer with the new SME citation.
That single arc demonstrates grounding, honesty, and the flywheel in ~3 minutes.

---

## 11. Panel Q&A — quick-fire answers (rehearse out loud)
- **"Why not let the model give the confidence score?"** → Models are confidently wrong;
  self-confidence ≠ correctness. A buyer must audit *why* an answer is trusted. My score is
  a transparent formula; an LLM number is a black box.
- **"How do you actually stop hallucination?"** → The model only sees the evidence pack
  (can't use memory), every claim must cite a passage, and code gates block anything
  uncited or from an unapproved/deprecated/wrong-product source.
- **"Brand voice vs accuracy?"** → The style step only sees *already-validated* claims and
  is re-checked for added claims / dropped caveats. Voice is scored separately and can never
  raise trust.
- **"Old or downvoted docs?"** → Freshness caps (>180d Medium, >365d Low) and reputation
  caps (>15% Medium, >30% Low, after ≥5 votes). They can still inform an answer but can't be
  High.
- **"Build vs buy?"** → Build the trust logic (the moat, must be auditable); buy the
  commodity infra (vector DB, embeddings) and swap at scale.
- **"Latency?"** → Worst case 3 model calls (1 small + 2 big); classify is skipped when
  product is known; gates/scoring are instant. Stream the style pass, cache classification.
- **"ROI to an exec?"** → Deflection (% answered confidently), escalation rate falling as
  the KB fills, helpful-rate, time-to-answer, reduced SME interrupt load. The KB improves
  itself, so cost-per-answer drops over time.
- **"Biggest risk?"** → Stale knowledge presented confidently — which is exactly what the
  freshness caps, review-date governance, and "0% deprecated usage" SLO exist to prevent.
- **If you genuinely don't know something:** *"As the PM I optimized for X; the deeper
  implementation of Y I'd pair with an engineer on — here's how I'd reason about the
  trade-off."* Confidence + honesty beats bluffing. (You literally built a product about not
  bluffing — say that.)

---

## 12. Your 10-sentence elevator version (memorize this)
1. Technical Sales reps get hard product questions live, and a confident wrong answer loses
   deals.
2. A generic chatbot makes it worse — it hallucinates with no proof.
3. So I built an evidence-governed RAG agent, not a chatbot.
4. It answers only from approved Palo Alto sources and shows the exact quote behind every
   claim.
5. It attaches a confidence score that's *calculated* by transparent rules, never guessed by
   the AI.
6. If it can't prove an answer, it doesn't bluff — it routes to the right SME and emails
   them.
7. The SME's answer becomes approved knowledge, so the system gets smarter every day.
8. Brand voice is a separate layer that can polish wording but never change facts.
9. I defined success as trust SLOs — 100% cited, 0% from stale sources — and validated with
   a 15-question harness and 33 tests.
10. The spine is deterministic confidence, hard citation gates, and the facts/style wall —
    everything else I'd optimize with newer agentic tech.
