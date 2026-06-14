"""FastAPI app: Ask, Feedback, SME queue/publish, metrics, and the UI."""
from __future__ import annotations

from collections import Counter

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .audit import list_answers
from .escalate import list_escalations
from .feedback import list_feedback, record_feedback
from .models import (AskRequest, AskResponse, FeedbackRequest, SMEAnswerRequest)
from .pipeline import ask
from .sme import publish_sme_answer

app = FastAPI(title="Evidence-Governed Knowledge Agent", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "mock_llm": config.MOCK_LLM}


@app.post("/agent/ask", response_model=AskResponse)
def agent_ask(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(400, "question is required")
    rec = ask(req.question, product_hint=req.product)
    return AskResponse(**{k: rec[k] for k in AskResponse.model_fields})


@app.post("/agent/feedback")
def agent_feedback(req: FeedbackRequest):
    return record_feedback(req.answer_id, req.feedback_type, req.comment)


@app.get("/sme/escalations")
def sme_escalations(status: str | None = "open"):
    return list_escalations(status=status)


@app.post("/sme/answer")
def sme_answer(req: SMEAnswerRequest):
    return publish_sme_answer(
        escalation_id=req.escalation_id, approved_answer=req.approved_answer,
        product=req.product, feature=req.feature, version=req.version,
        owner=req.owner, source_url=req.source_url,
    )


@app.get("/metrics")
def metrics():
    answers = list_answers()
    fb = list_feedback()
    escs = list_escalations(status=None)
    n = len(answers) or 1
    conf = Counter(a.get("confidence") for a in answers)
    cited = sum(1 for a in answers if a.get("citations"))
    helpful = sum(1 for f in fb if f.get("feedback_type") == "helpful")
    wrong = sum(1 for f in fb if f.get("feedback_type") == "answer_is_wrong")
    return {
        "total_answers": len(answers),
        "answers_with_citations_pct": round(100 * cited / n),
        "confidence_distribution": dict(conf),
        "escalations_open": sum(1 for e in escs if e.get("status") == "open"),
        "escalations_total": len(escs),
        "feedback_total": len(fb),
        "helpful": helpful,
        "wrong_answer": wrong,
    }


@app.get("/sources")
def sources():
    """Transparent view of the knowledge base: every approved source, its metadata,
    chunk count, and freshness — so users can see exactly what the agent draws on."""
    from .db import get_chunks_table
    from .retrieval import _days_since

    rows = get_chunks_table().search().limit(10000).to_list()
    by_src: dict[str, dict] = {}
    for r in rows:
        s = by_src.setdefault(r["source_id"], {
            "source_id": r["source_id"], "title": r["source_title"],
            "product": r["product"], "feature": r.get("feature", ""),
            "source_type": r["source_type"], "version": r.get("version", ""),
            "url": (r.get("anchor_url") or "").split("#")[0],
            "last_reviewed_date": r.get("last_reviewed_date", ""),
            "deprecated": bool(r.get("deprecated", False)),
            "upvotes": int(r.get("upvotes", 0)), "downvotes": int(r.get("downvotes", 0)),
            "chunks": 0,
        })
        s["chunks"] += 1
    out = []
    for s in by_src.values():
        days = _days_since(s["last_reviewed_date"])
        s["days_since_review"] = days
        s["freshness"] = "Fresh" if days <= 180 else "Aging" if days <= 365 else "Stale"
        out.append(s)
    out.sort(key=lambda x: (x["product"], x["source_id"]))
    return {"total_sources": len(out), "total_chunks": sum(s["chunks"] for s in out),
            "sources": out}


@app.get("/sample-questions")
def sample_questions():
    """Curated, KB-grounded examples grouped by expected outcome (drives the UI)."""
    return [
        # High — fresh, official sources cover these directly
        {"tier": "High", "product": "Prisma Access",
         "q": "How much bandwidth and how many connectors does a ZTNA Connector group support?"},
        {"tier": "High", "product": "Prisma Access",
         "q": "What is the maximum number of BGP IP addresses per remote network, and how does ECMP affect it?"},
        {"tier": "High", "product": "Prisma Access",
         "q": "How many monitored users does an ADEM tenant support and what license does it need?"},
        {"tier": "High", "product": "NGFW",
         "q": "What is the supported PAN-OS upgrade path from 10.0 to 11.1, and can I skip versions?"},
        {"tier": "High", "product": "NGFW",
         "q": "Which quantum-resistant and HTTP/2 networking features arrived in PAN-OS 11.2?"},
        {"tier": "High", "product": "NGFW",
         "q": "How do I configure multiple GlobalProtect gateways with priorities for failover?"},
        {"tier": "High", "product": "Cortex XDR",
         "q": "What API key security level and role are required to integrate Cortex XDR with another product?"},
        # Medium — answer is correct but the source doc is aging (freshness cap)
        {"tier": "Medium", "product": "NGFW",
         "q": "What are the three decryption types on the NGFW, and which one is unsupported in Strata Cloud Manager?"},
        {"tier": "Medium", "product": "NGFW",
         "q": "What is SSL Forward Proxy decryption used for, and how does the firewall act as an intermediary?"},
        {"tier": "Medium", "product": "NGFW",
         "q": "How does App-ID identify applications that use evasive tactics or encryption?"},
        {"tier": "Medium", "product": "Prisma Access",
         "q": "What is the maximum bandwidth per tunnel and per node on high-performance remote networks?"},
        {"tier": "Medium", "product": "Prisma Access",
         "q": "How many Service Endpoint addresses do high-performance remote networks use per Gbps?"},
        # Escalation — not in the knowledge base -> routed to the right SME group
        {"tier": "Escalation", "product": "Cortex XDR",
         "q": "How do I configure a Behavioral Threat Protection exception and exploit-protection ROP modules in Cortex XDR?"},
        {"tier": "Escalation", "product": "NGFW",
         "q": "What is the App-ID throughput sizing for a PA-5450 in a multi-vsys HA deployment?"},
        {"tier": "Escalation", "product": "NGFW",
         "q": "What is the end-of-life date for PAN-OS 9.1?"},
        {"tier": "Escalation", "product": "Prisma Access",
         "q": "What is the per-user list price of Prisma Access, and what discounts apply at 5,000 seats?"},
        {"tier": "Escalation", "product": "Cortex XDR",
         "q": "Does Cortex XSIAM support MITRE ATT&CK technique mapping out of the box?"},
    ]


@app.get("/sme/outbox")
def sme_outbox():
    """Sent SME notification emails (audit copies) — proves the notify workflow."""
    from .notify import list_outbox
    return list_outbox()


@app.get("/sme/routing")
def sme_routing():
    """Expose the SME routing table (transparency: which group a gap goes to)."""
    rules = [{"product": p, "feature": f or "(any other feature)", "sme_group": g}
             for (p, f), g in config.SME_ROUTING.items()]
    return {"rules": rules, "default": config.DEFAULT_SME_GROUP}


# --- UI (served last so /api routes win) ---
@app.get("/")
def index():
    # no-store so UI edits show on refresh instead of serving a cached page
    return FileResponse(config.UI_DIR / "index.html",
                        headers={"Cache-Control": "no-store, must-revalidate"})


app.mount("/ui", StaticFiles(directory=str(config.UI_DIR)), name="ui")
