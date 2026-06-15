# Expected Panel Q&A — with answers you can say out loud

A companion to the deck. The Q&A slide just invites questions; these are the ones to expect
and crisp answers in your voice. Rehearse the **bold first line** of each — that's your
headline; the rest is backup if they probe.

> Golden rule: answer the *headline* in one sentence, then give one supporting detail, then
> stop. Let them ask the follow-up. You built a product about *not over-claiming* — model that.

---

## A. The two case-study "surgery" questions (most likely — prep these hardest)

**Q1. The sales team says the AI sounds too robotic. How do you do Brand Voice without sacrificing technical accuracy?**
**A.** *I separate "what's true" from "how it sounds," with a hard wall between them.* A
first AI step produces only **validated, cited claims**. A second, separate step rewrites
those in brand voice — and it **never sees the source documents**, only the approved claims.
Then I re-check its output: did it add a claim? drop a caveat? change a citation? If so, I
discard the polish and ship the plain facts. Brand voice is scored *separately* and can
**never raise the confidence score**. So the worst case is a slightly plainer answer — never
a wrong one. It's all tunable from a config file (`brand_voice.yaml`) without code changes.

**Q2. What if a document is downvoted or too old? How did you implement the confidence rubric?**
**A.** *Confidence is a transparent formula, not the AI's opinion, and freshness and
feedback are first-class inputs.* The score (0–100) is citation coverage + retrieval
relevance + source authority + freshness. Then **caps** override it: a source reviewed
>180 days ago caps the answer at **Medium**, >365 days at **Low**; a downvote ratio >15%
caps at Medium, >30% at Low — but only after at least **5 votes**, so one angry click can't
bury a good source. So a stale or downvoted doc can still inform an answer, but it can't be
"High." And the UI explains *why*: "Medium because the only source is 241 days old."

---

## B. Defending the technical trade-offs

**Q3. Why calculate confidence in code instead of asking the model how sure it is?**
**A.** *A model's self-confidence tracks fluency, not correctness — it's confidently wrong.*
A security buyer needs to **audit** why an answer is trusted. My score is a reproducible
formula anyone can inspect; an LLM's number is a black box. The LLM is the *last* thing I'd
trust with "how sure are you."

**Q4. How do you actually prevent hallucination — not just discourage it?**
**A.** *Three structural layers, not a polite prompt.* (1) The model only ever sees the
retrieved passages — it physically can't answer from training memory. (2) It must produce
claim-first output where every claim names its source passage. (3) Hard code "gates" block
the answer if any claim is uncited or cites an unapproved/deprecated/wrong-product source.
A prompt *asks*; a gate *guarantees*.

**Q5. Build vs. buy — justify LanceDB and local models.**
**A.** *Build the differentiator, buy the commodity.* The trust logic is the moat and must
be auditable, so I built it. The vector store and embeddings are commodities — I used an
embedded store (LanceDB) and local embeddings for zero-infra MVP velocity, and both are
one-line swaps to managed services (Pinecone, Voyage) when scale demands. Note: Anthropic
has no embeddings API, so the key doesn't touch that layer.

**Q6. Why two different models (Opus and Haiku)?**
**A.** *Latency vs. accuracy, matched to the job.* The cheap, fast model (Haiku) does the
simple routing/classification call. The accurate model (Opus) does the two steps where a
mistake hurts — drafting the grounded answer and styling. I don't pay for the big model on
an easy task, and I don't cut corners where hallucination is the risk.

**Q7. What's the latency, and how would you cut it?**
**A.** Worst case is three model calls (one small + two large); the classify call is
skipped when the product is already known, and the gates/scoring are instant Python. To cut
it: stream the styling step, cache classification, and at scale fine-tune a smaller model
for the common questions.

---

## C. Data

**Q8. How did you handle data, and how did you ensure quality?**
**A.** Three sources on purpose: **real** crawled product docs, **PDFs**, and **synthetic**
edge cases I generated because I needed them to test the rules — you can't validate a
"stale document gets downgraded" rule without owning a stale document. Quality comes from
**metadata as a first-class citizen**: every passage has product, version, review date,
deprecated flag, approval status — and that metadata *drives* retrieval, scoring, and
routing.

**Q9. What's a data limitation you hit?**
**A.** The Cortex XDR docs portal is JavaScript-rendered, so my crawler couldn't read it. I
**named the gap** instead of faking coverage — and it's exactly why a Cortex
exploit-protection question correctly escalates in the demo. Honest boundaries beat fake
completeness.

---

## D. Evaluation & success

**Q10. How did you define "successful" — beyond a loss function?**
**A.** *There's no single label to optimize — it's a trust product, so success is a set of
trust SLOs that map to the business:* 100% of claims cited, <2% unsupported claims, **0%**
use of deprecated sources, and **0** low-confidence answers shown without escalation. I
validated with a 5-easy / 5-medium / 5-hard question harness (it scored 5/5/5) and **33
unit tests** that lock the deterministic scoring so it can't drift.

**Q11. What were the "hard truths" you learned?**
**A.** Four. (1) Rerankers aren't calibrated — the *correct* passage scored lower than an
off-topic one, so I use the reranker only for ordering and let the LLM judge sufficiency.
(2) The newest model deprecated the `temperature` setting; I'd set it for determinism, it
errored, and my fail-safe silently escalated all 15 questions — determinism belongs in my
code, not model settings. (3) A fail-safe became bad UX (over-escalating), so I tuned it to
answer when grounded. (4) One downvote could bury a source, so I added a minimum-votes
floor. Each one shipped only because I was testing against real questions.

---

## E. Product & roadmap

**Q12. If you rebuilt it today, what would you change?**
**A.** I'd make retrieval **agentic** — let it critique its own evidence and re-search
before answering (Corrective/Self-RAG), and add a tool-using agent that does a live lookup
before escalating. I'd add LLM-as-judge as a *second evaluation* signal — never for
user-facing confidence. And real Confluence/Jira connectors plus a feedback-tuned reranker.
**What I'd keep: deterministic confidence, the hard citation gates, and the facts/style
wall** — those earned the trust.

**Q13. How would you measure ROI to an executive?**
**A.** Leading indicators: % of questions answered confidently (deflection), the escalation
rate *falling* as the knowledge base fills, helpful-rate, and time-to-answer. Lagging:
SE-reported deal impact and reduced expert-interrupt load. The KB improves itself via the
SME publish loop, so cost-per-answer drops over time.

**Q14. How does this scale to thousands of docs and many products?**
**A.** Retrieval is already metadata-filtered by product/version, so it scales horizontally
— swap to a managed vector DB and hybrid search. Governance scales through the review-date
SLAs and the dashboard that flags sources needing review. The real bottleneck is SME time,
which is why "agentic SME drafting" (pre-draft the expert's answer) is top of my roadmap.

**Q15. What's the single biggest risk?**
**A.** *Stale knowledge presented confidently.* That's exactly what the freshness caps, the
review-date governance, and the "0% deprecated usage" target exist to prevent — and why I
never let the model set its own confidence.

---

## F. Curveballs & honesty

**Q16. You're a CRM PM, not an ML engineer — how do I know you understand this?**
**A.** *As a PM my job is the right trade-offs, the user value, and the evaluation — and I
can defend all three.* I built this end-to-end to learn the stack, and my CRM background is
the strength here: this is Salesforce Knowledge + Omni-Channel routing + Approval Processes
+ Einstein scoring, rebuilt on an LLM with strict grounding. For the deepest model
internals I'd pair with an engineer — and here's how I'd reason about that trade-off.

**Q17. What would you do if you had two more weeks?**
**A.** Close the human-bottleneck gap: agentic SME drafting and a feedback-tuned reranker,
plus the first real connector (Confluence). Those compound the flywheel fastest.

**Q18. If you don't know an answer in the room:**
Say so cleanly — *"I haven't tested that; here's how I'd reason about it…"* — and reason out
loud. Confidence plus honesty beats bluffing, and you literally built a product whose whole
point is not bluffing. Use that line.
