# Product & Technical Spec — Evidence-Governed Knowledge Agent

## 1. Problem & users
**User:** Technical Sales / Sales Engineers answering product questions live in customer
calls. **Pain:** a confident-but-wrong answer loses credibility and deals; product truth is
scattered across docs/release-notes/wikis and goes stale; SMEs re-answer the same questions
in Slack and that knowledge is never reused.

**Task:** an **evidence-governed RAG system** (not a chatbot) with a human-in-the-loop
knowledge flywheel.

## 2. Requirements (from the case study) → status
| Requirement | Status |
| --- | --- |
| Ask technical questions about a **specific Palo Alto product** | ✅ classifier + product-filtered retrieval |
| Find best answer from the **Knowledge Base** (files, Confluence, release notes) | ✅ (Confluence as a *type* is supported; a live connector is a documented next step) |
| **Generate a response** | ✅ claim-first facts engine |
| If KB lacks details → **route to a specific SME group** | ✅ feature-level routing |
| SME provides info → **referenced for all future questions** | ✅ publish → instantly citable |
| **Source citations** on every response | ✅ enforced by hard gates |
| **Confidence score** High/Medium/Low | ✅ deterministic |
| **Attribution UI** (clickable, verify the AI) | ✅ exact cited text shown inline |
| **SMEs can update the KB** | ✅ Approve & Publish |
| **"This answer is wrong" button** | ✅ reputation hit + SME ticket |
| **SME notifications** | ✅ email (SMTP/outbox) + in-app bell |
| **Brand voice** without losing accuracy | ✅ Facts↔Style wall + `brand_voice.yaml` |
| **Confidence rubric for old/downvoted docs** | ✅ freshness + reputation caps |

## 3. Product principles
1. **No citation, no answer.** Every factual claim maps to approved source text, or it
   doesn't ship (enforced in code, not by prompt).
2. **Confidence is calculated, not generated.** The LLM never sets confidence.
3. **Brand voice is a presentation layer.** It can clarify; it can't add claims or drop
   caveats.
4. **SME answers become governed knowledge** — owned, citable, review-dated assets.

## 4. Architecture (summary)
```
Question → Classify (Haiku) → Retrieve (LanceDB + rerank + freshness/reputation) →
Evidence Pack → Facts engine (Opus, claim-first) → GATES (Python) → SCORE (Python) →
Style/brand voice (Opus) → Answer   |   gate/Low → escalate → SME → publish → citable
```
Full diagrams: [`architecture.md`](architecture.md).

## 5. Key technical decisions (trade-offs)
| Decision | Chose | Over | Why |
| --- | --- | --- | --- |
| Confidence | Deterministic rubric | LLM-judged | Auditable, reproducible, can't be gamed by fluency |
| Grounding | Hard code gates | Prompt "please cite" | A gate guarantees; a prompt hopes |
| Vector store | LanceDB (embedded) | Pinecone / pgvector | Vectors + metadata + reranker in one, zero infra |
| Facts/Style model | Claude Opus 4.8 | Haiku | Accuracy where hallucination is the risk |
| Classifier model | Claude Haiku 4.5 | Opus | Latency/cost on a cheap routing call |
| Embeddings | Local `sentence-transformers` | Voyage/OpenAI | Free/offline MVP; one-line swap at scale (Anthropic has no embeddings API) |
| Reranker | Local cross-encoder (ordering only) | Cohere API | Free; reranker scores aren't a reliable absolute signal |

## 6. Evaluation
Success = **trust SLOs** (100% claims cited, 0% deprecated-source usage, 0% low-confidence
shown without escalation), validated by a **5/5/5** question harness (`../pipeline_and_tests/REPORT.md`)
and **33 unit tests**.

## 7. Roadmap / retrospective
Agentic (Corrective/Self-RAG) retrieval; a tool-using agent for live lookups before
escalating; LLM-as-judge as a second *evaluation* signal (never for confidence); hosted
embeddings + hybrid search + a feedback-fine-tuned reranker; real Confluence/Jira/ServiceNow
connectors; streaming UX; agentic SME drafting. **Keep the spine:** deterministic
confidence, hard gates, the Facts↔Style wall.
