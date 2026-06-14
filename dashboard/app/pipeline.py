"""Ask orchestration: classify -> retrieve -> facts -> gates -> score -> style.
Blocks/escalates on failed gates or Low confidence. (ARCHITECTURE.md §1, §3)."""
from __future__ import annotations

import re
import uuid

from . import classify as classify_mod
from . import facts as facts_mod
from . import scoring as scoring_mod
from . import style as style_mod
from .audit import save_answer
from .escalate import create_escalation
from .gates import run_gates
from .retrieval import retrieve

INSUFFICIENT_MSG = (
    "I could not find enough approved source material to answer this confidently. "
    "I've routed this question to the appropriate SME group."
)
LOW_CONFIDENCE_MSG = (
    "I found related approved material, but it isn't current or reliable enough to "
    "answer this confidently. I've routed this question to the appropriate SME group "
    "for a verified answer."
)


def _detect_version(question: str) -> str | None:
    m = re.search(r"\b\d+\.\d+\b", question)
    return m.group(0) if m else None


def _final_format(answer_body: str, caveat: str, confidence: str, why: str,
                  citations: list[dict]) -> str:
    src_lines = "\n".join(f"{i+1}. {c['title']} — {c['url']}"
                          for i, c in enumerate(citations)) or "None"
    return (
        f"Answer:\n{answer_body}\n\n"
        f"Important caveats:\n{caveat or 'See cited sources.'}\n\n"
        f"Confidence:\n{confidence}\n\n"
        f"Why this confidence:\n{why}\n\n"
        f"Sources:\n{src_lines}\n\n"
        f"Feedback:\n[Helpful] [This answer is wrong] [Source is outdated]"
    )


def _escalate_response(answer_id, question, product, feature, reason,
                       sources, score, why, message=INSUFFICIENT_MSG) -> dict:
    create_escalation(question, product, feature, reason, sources, score)
    rec = {
        "answer_id": answer_id, "question": question, "product": product,
        "feature": feature, "answer": message, "confidence": "Low",
        "technical_trust_score": score, "experience_quality_score": 0,
        "final_response_quality_score": round(0.8 * score, 1),
        "why_confidence": why, "citations": [], "cited_source_ids": [],
        "escalated_to_sme": True, "score_breakdown": {},
        "why_experience": "", "experience_breakdown": [],
    }
    save_answer(rec)
    return rec


def ask(question: str, product_hint: str | None = None) -> dict:
    answer_id = f"ANS-{uuid.uuid4().hex[:8]}"

    cls = classify_mod.classify(question, product_hint)
    product = cls["product"]
    feature = cls["feature"]
    detected_version = _detect_version(question)

    chunks = retrieve(question, product=product, k=5)
    chunks_by_id = {c["chunk_id"]: c for c in chunks}
    retrieved_sources = sorted({c["source_id"] for c in chunks})

    # --- Facts engine ---
    pack = facts_mod.build_evidence_pack(question, product, cls["intent"], chunks)
    facts = facts_mod.generate(pack)

    # --- Hard gates ---
    gate = run_gates(facts, chunks_by_id, product)
    if not gate.passed:
        reason = "insufficient_evidence" if "evidence_exists" in gate.failed_gates \
            or "insufficient_evidence" in gate.failed_gates else \
            f"gate_failed:{','.join(gate.failed_gates)}"
        return _escalate_response(answer_id, question, product, feature, reason,
                                  retrieved_sources, 0,
                                  f"Blocked by gates: {', '.join(gate.failed_gates)}.")

    # --- Cited chunks only ---
    cited_ids = {cid for c in facts["claims"] for cid in c.get("source_chunk_ids", [])}
    cited_chunks = [chunks_by_id[cid] for cid in cited_ids if cid in chunks_by_id]

    # --- Deterministic scoring + confidence ---
    sc = scoring_mod.score(facts, cited_chunks, detected_version)

    if sc["confidence"] == "Low":
        return _escalate_response(answer_id, question, product, feature,
                                  "low_confidence", retrieved_sources,
                                  sc["technical_trust_score"], sc["why_confidence"],
                                  message=LOW_CONFIDENCE_MSG)

    # --- Style layer (High/Medium only) ---
    styled = style_mod.apply_style(facts["claims"], cited_chunks, product=product)

    def _fresh(days: int) -> str:
        return "Fresh" if days <= 180 else "Aging" if days <= 365 else "Stale"
    citations = [{"title": c["source_title"], "url": c["anchor_url"],
                  "chunk_id": c["chunk_id"], "section_title": c.get("section_title", ""),
                  "text": c["text"], "product": c.get("product", ""),
                  "source_type": c.get("source_type", ""),
                  "freshness": _fresh(c.get("_days_since_review", 9999))}
                 for c in cited_chunks]
    caveat = next((c for c in style_mod._caveats_from_chunks(cited_chunks)), "")
    final_answer = _final_format(styled["styled_answer"], caveat, sc["confidence"],
                                 sc["why_confidence"], citations)

    tech = sc["technical_trust_score"]
    exp = styled["experience_quality_score"]
    rec = {
        "answer_id": answer_id, "question": question, "product": product,
        "feature": feature, "answer": final_answer, "confidence": sc["confidence"],
        "technical_trust_score": tech, "experience_quality_score": exp,
        "final_response_quality_score": round(0.8 * tech + 0.2 * exp, 1),
        "why_confidence": sc["why_confidence"], "citations": citations,
        "cited_source_ids": sorted({c["source_id"] for c in cited_chunks}),
        "escalated_to_sme": False, "score_breakdown": sc["breakdown"],
        "why_experience": styled["why_experience"],
        "experience_breakdown": styled["experience_breakdown"],
    }
    save_answer(rec)
    return rec
