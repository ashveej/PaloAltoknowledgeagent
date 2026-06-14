# Evidence-Governed Knowledge Agent — MVP Architecture

An evidence-governed RAG agent for Technical Sales. It answers product questions
**only** from approved sources, cites every factual claim, computes a
**deterministic** confidence score, and escalates weak/missing evidence to SMEs.

**Stack:** Python · FastAPI · LanceDB (vectors + metadata + built-in local
cross-encoder reranker) · Claude (`claude-haiku-4-5` classify, `claude-opus-4-8`
facts + style) · feedback → reputation → rerank (**no retraining**).

**Core principle — a hard wall between Facts and Style:** the model that touches
evidence never styles; the model that styles never touches raw evidence. Brand
voice can raise the Experience score but can **never** change the Technical Trust
Score or confidence.

---

## 1. High-Level Architecture

```mermaid
flowchart TD
    Q[User Question] --> CLS[Classify<br/>product / feature / intent<br/>haiku]

    subgraph FACTS["🔒 FACTS ENGINE — touches evidence"]
        direction TB
        CLS --> RET[Retrieve<br/>LanceDB vector search top-K]
        RET --> RR[Rerank<br/>cross-encoder + freshness/reputation boost]
        RR --> EP[Evidence Pack<br/>question + chunk text + ids only]
        EP --> GEN[Claim-first Answer<br/>opus → claims[] + answer_text]
        GEN --> GATE[Gates + Citation Validation<br/>pure Python]
        GATE --> SCORE[Technical Trust Score<br/>+ confidence + caps]
    end

    SCORE -->|validated claims + caveats only| STYLE

    subgraph STYLEBOX["🎨 STYLE LAYER — never sees raw KB"]
        direction TB
        STYLE[Brand-voice Rewrite<br/>opus] --> GUARD[Style Guards<br/>no new claims / no dropped caveats<br/>citations intact / banned-phrase]
        GUARD --> EXP[Experience Quality Score]
    end

    EXP --> DEC{Confidence?}
    DEC -->|High / Medium| ANS[Final Answer<br/>§16 format]
    DEC -->|Low / blocked| ESC[SME Escalation]

    ANS --> FB[Feedback]
    ESC --> SMEQ[SME Queue]
    SMEQ --> PUB[Approve → Publish<br/>back into LanceDB as approved source]
    PUB -.new approved chunk.-> RET

    FB --> REP[Update source reputation<br/>upvotes / downvotes]
    REP -.rerank boost.-> RR
    REP -.confidence cap.-> SCORE

    classDef facts fill:#e8f0fe,stroke:#3367d6,color:#0b2a6b;
    classDef style fill:#fef7e8,stroke:#d68a33,color:#6b450b;
    class FACTS facts;
    class STYLEBOX style;
```

---

## 2. The Facts / Style Wall

The single most important design constraint. Evidence flows **one way**: from the
Facts engine into the Style layer as already-validated claims. Style output is
re-checked to guarantee it added nothing and removed no caveats.

```mermaid
flowchart LR
    KB[(Approved KB<br/>LanceDB)] --> F

    subgraph F["FACTS ENGINE"]
        F1[Evidence Pack] --> F2[Claim-first generation]
        F2 --> F3[Gates + validation]
        F3 --> F4[Trust Score + Confidence]
    end

    F4 -- "claims + caveats + confidence<br/>(NO raw KB)" --> S

    subgraph S["STYLE LAYER"]
        S1[Brand-voice rewrite] --> S2[Guards:<br/>claim set unchanged?<br/>caveats preserved?<br/>citations intact?<br/>banned phrases?]
        S2 --> S3[Experience Score]
    end

    S3 --> OUT[User-facing answer]

    X1["❌ Style cannot add claims"] -.-> S
    X2["❌ Style cannot change confidence"] -.-> S
    X3["❌ Style never reads KB"] -.-> S

    style F fill:#e8f0fe,stroke:#3367d6
    style S fill:#fef7e8,stroke:#d68a33
```

---

## 3. `/agent/ask` Request Sequence

```mermaid
sequenceDiagram
    autonumber
    actor U as User (Tech Sales)
    participant API as FastAPI /agent/ask
    participant CL as Classifier (haiku)
    participant DB as LanceDB
    participant RK as Reranker (cross-encoder)
    participant FA as Facts (opus)
    participant GT as Gates (Python)
    participant SC as Scoring (Python)
    participant ST as Style (opus)
    participant ESC as Escalation

    U->>API: question (+ optional product)
    API->>CL: classify (skip if product given)
    CL-->>API: {product, feature, intent}
    API->>DB: vector search top-K
    DB-->>API: candidate chunks + metadata
    API->>RK: rerank + freshness/reputation boost
    RK-->>API: top-5 evidence
    API->>FA: Evidence Pack
    FA-->>API: claims[] + answer_text | INSUFFICIENT_EVIDENCE

    API->>GT: run hard gates
    alt any gate fails
        GT-->>API: BLOCK
        API->>ESC: write escalation record
        API-->>U: "Not enough approved evidence — routed to SME"
    else gates pass
        GT-->>API: OK
        API->>SC: Technical Trust Score + caps
        SC-->>API: confidence (High/Med/Low) + breakdown
        alt confidence Low
            API->>ESC: write escalation record
            API-->>U: Low-confidence notice + SME routed
        else High/Medium
            API->>ST: validated claims + caveats only
            ST-->>API: styled answer + Experience Score
            API-->>U: §16 formatted answer + citations + confidence
        end
    end
```

---

## 4. Hard Gates (No Citation, No Answer)

All deterministic, pure Python — runs **before** scoring. Any failure blocks the
answer and routes to SME.

```mermaid
flowchart TD
    A[Claims + Citations] --> G1{Evidence exists?}
    G1 -->|no| BLOCK[🚫 Block + Escalate to SME]
    G1 -->|yes| G2{Every claim cited?}
    G2 -->|no| BLOCK
    G2 -->|yes| G3{Cited chunk ids real?}
    G3 -->|no| BLOCK
    G3 -->|yes| G4{All cited sources approved?}
    G4 -->|no| BLOCK
    G4 -->|yes| G5{Any cited source deprecated?}
    G5 -->|yes| BLOCK
    G5 -->|no| G6{Product matches question?}
    G6 -->|no| BLOCK
    G6 -->|yes| PASS[✅ Proceed to Scoring]

    style BLOCK fill:#fdecea,stroke:#d93025,color:#5c0a02
    style PASS fill:#e6f4ea,stroke:#1e8e3e,color:#0b3d1a
```

---

## 5. Technical Trust Score & Confidence

Score is **calculated, not generated by the LLM**. Caps can pull a numerically
high score down to Medium/Low.

```mermaid
flowchart TD
    subgraph CALC["Technical Trust Score (0–100)"]
        C1[Citation integrity<br/>40] --> SUM((Σ))
        C2[Retrieval relevance<br/>25] --> SUM
        C3[Source authority<br/>20] --> SUM
        C4[Source freshness<br/>15] --> SUM
    end

    SUM --> CAPS{Apply caps}
    CAPS -->|stale > 180d| MAXM[max Medium]
    CAPS -->|stale > 365d / downvote > 30%| MAXL[max Low]
    CAPS -->|downvote > 15%| MAXM
    CAPS -->|single non-official source| MAXM
    CAPS -->|version missing & required| MAXM
    CAPS -->|none| RAW[use raw score]

    MAXM --> BAND
    MAXL --> BAND
    RAW --> BAND

    BAND{Band} -->|>=85, no caps| HIGH[🟢 High]
    BAND -->|65–84| MED[🟡 Medium]
    BAND -->|<65 or Low route| LOW[🔴 Low → SME]

    style HIGH fill:#e6f4ea,stroke:#1e8e3e
    style MED fill:#fef7e8,stroke:#d68a33
    style LOW fill:#fdecea,stroke:#d93025
```

---

## 6. Feedback → Reputation → Rerank Loop (No Retraining)

User feedback updates a per-source reputation signal that feeds **two** places:
the reranker (ordering) and the confidence cap. No model is retrained.

```mermaid
flowchart LR
    U[User feedback<br/>Helpful / Wrong / Outdated] --> FBR[Feedback record]
    FBR --> REP[Update source<br/>upvotes / downvotes]
    REP --> RATIO[Downvote ratio]

    RATIO -->|rerank boost| RR[Reranker<br/>push stale/downvoted chunks down]
    RATIO -->|confidence cap| SC[Scoring<br/>cap High→Medium/Low]

    FBR -->|wrong answer| TICK[SME review ticket]
    FBR -->|outdated| FLAG[Flag source for refresh]

    RR --> BETTER[Better future retrieval]
    SC --> SAFER[Safer future confidence]

    style REP fill:#e8f0fe,stroke:#3367d6
```

---

## 7. SME Escalation & Publish Loop (Light Lifecycle)

```mermaid
flowchart TD
    TRIG[Trigger:<br/>no evidence / Low confidence /<br/>gate block / 'answer is wrong'] --> ROUTE[Route by product→SME group]
    ROUTE --> QUEUE[(Escalation Queue<br/>JSON records)]
    QUEUE --> UI[SME Queue UI]
    UI --> SME[SME writes answer]
    SME --> APPROVE{Approve?}
    APPROVE -->|no| QUEUE
    APPROVE -->|yes| EMB[Embed answer]
    EMB --> PUB[Write to LanceDB<br/>source_type = sme_kb<br/>approval_status = approved]
    PUB --> CITE[Instantly citable on<br/>future questions]
    CITE -.-> QUEUE

    style PUB fill:#e6f4ea,stroke:#1e8e3e
```

> MVP skips the full Draft → Reviewed → Periodic-review lifecycle. Just:
> **queue → SME answer → approve → publish.**

---

## 8. Data Model

LanceDB holds vectors **and** metadata in one `chunks` table (source-level fields
ride on the chunk for MVP). Audit lives in an `answers` table; feedback and
escalations are JSON files the dashboard reads.

```mermaid
erDiagram
    CHUNKS {
        string chunk_id PK
        vector embedding
        string text
        string source_id
        string section_title
        string anchor_url
        string product
        string feature
        string version
        string source_type
        string approval_status
        date   last_reviewed_date
        bool   deprecated
        int    upvotes
        int    downvotes
    }
    ANSWERS {
        string answer_id PK
        string question
        string answer
        json   claims_json
        json   citations_json
        int    technical_trust_score
        int    experience_quality_score
        string confidence
        json   gate_results
        datetime created_at
    }
    FEEDBACK {
        string feedback_id PK
        string answer_id FK
        string feedback_type
        string comment
        string product
        string status
    }
    ESCALATIONS {
        string escalation_id PK
        string question
        string product
        string failed_reason
        json   retrieved_sources
        int    confidence_score
        string assigned_sme_group
        string status
    }

    ANSWERS ||--o{ FEEDBACK : "receives"
    ANSWERS ||--o{ ESCALATIONS : "may trigger"
    CHUNKS ||--o{ ANSWERS : "cited by"
```

---

## 9. Module Map

```mermaid
flowchart TB
    subgraph api["API layer"]
        MAIN[main.py<br/>FastAPI routes]
    end
    subgraph facts["Facts engine"]
        CLASSIFY[classify.py]
        RETRIEVAL[retrieval.py]
        FACTS[facts.py]
        GATES[gates.py]
        SCORING[scoring.py]
    end
    subgraph style["Style layer"]
        STYLE[style.py]
    end
    subgraph gov["Governance"]
        ESCALATE[escalate.py]
        FEEDBACK[feedback.py]
        SME[sme.py]
        DASH[dashboard]
    end
    subgraph data["Data / setup"]
        SEED[seed.py]
        DBL[(LanceDB)]
    end

    MAIN --> CLASSIFY --> RETRIEVAL --> FACTS --> GATES --> SCORING --> STYLE --> MAIN
    SCORING --> ESCALATE
    GATES --> ESCALATE
    MAIN --> FEEDBACK --> RETRIEVAL
    MAIN --> SME --> DBL
    SEED --> DBL
    RETRIEVAL --> DBL
    MAIN --> DASH
```

---

## 10. Build Order

```mermaid
flowchart LR
    S1[1. Skeleton] --> S2[2. seed.py]
    S2 --> S3[3. retrieval.py]
    S3 --> S5[5. facts.py]
    S5 --> S6[6. gates.py]
    S6 --> S7[7. scoring.py]
    S7 --> S12[12. main.py<br/>/agent/ask runnable]
    S12 --> S8[8. style.py]
    S8 --> S9[9-10. escalate + feedback]
    S9 --> S11[11. SME publish]
    S11 --> S13[13-14. dashboard + UI]

    style S12 fill:#e6f4ea,stroke:#1e8e3e
```

**Fastest proof:** `1 → 2 → 3 → 5 → 6 → 7 → 12` gives a working cited answer with
deterministic confidence over the API. Then layer style, governance, and UI.

---

## 11. Scope Summary

| In (MVP core) | Deferred / Out |
| --- | --- |
| LanceDB retrieval + cross-encoder rerank | Web/PDF ingestion pipeline |
| Facts engine: claim-first + gates + Trust Score | Conflict-with-newer-source check |
| Style layer: brand voice + guards + Experience Score | Full 100-pt 7-category scorer |
| Confidence bands + caps | Reranker training / model retraining |
| Feedback → reputation → rerank + cap | Slack/Jira/ServiceNow integrations |
| SME light queue → approve → publish | Full SME lifecycle (draft/review states) |
| Light read-only dashboard | Heavy analytics stack |
