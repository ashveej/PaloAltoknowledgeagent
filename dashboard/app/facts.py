"""Facts engine: claim-first, evidence-grounded answer generation.
Receives ONLY the Evidence Pack. Never styles. (ARCHITECTURE.md §2, §5)."""
from __future__ import annotations

import json

from . import config
from .llm import call_json

SYSTEM = (
    "ROLE=FACTS. You answer using ONLY the provided Evidence Pack.\n"
    "Rules:\n"
    "1. Every technical claim must cite one or more chunk_ids from the evidence.\n"
    "2. Do not introduce facts, guarantees, or conditions not present in the evidence.\n"
    "3. Preserve every limitation/condition stated in the evidence.\n"
    "4. Default to answering. Make at least one cited claim whenever any evidence "
    "chunk is on-topic for the question. Set insufficient_evidence=true ONLY when NO "
    "chunk is relevant (the topic is simply absent). Release notes or feature lists "
    "with version markers (e.g. 'Introduced in PAN-OS 11.2') ARE sufficient to answer "
    "'what's new / what features' questions. Do not escalate just because the answer "
    "is incomplete — answer what is supported and note the limits as caveats.\n"
    "Return ONLY JSON:\n"
    '{"insufficient_evidence": <bool>, '
    '"claims": [{"claim_id": "C1", "claim_text": "...", "source_chunk_ids": ["..."]}], '
    '"answer_text": "..."}'
)


def build_evidence_pack(question: str, product: str | None, intent: str,
                        chunks: list[dict]) -> dict:
    return {
        "question": question,
        "detected_product": product,
        "detected_intent": intent,
        "evidence_chunks": [
            {
                "chunk_id": c["chunk_id"],
                "source_title": c["source_title"],
                "source_url": c["anchor_url"],
                "exact_text": c["text"],
            }
            for c in chunks
        ],
    }


def generate(evidence_pack: dict) -> dict:
    """Return {insufficient_evidence, claims[], answer_text}."""
    user = json.dumps(evidence_pack, ensure_ascii=False)
    try:
        out = call_json(config.FACTS_MODEL, SYSTEM, user, max_tokens=1200)
    except Exception:
        return {"insufficient_evidence": True, "claims": [], "answer_text": ""}
    out.setdefault("insufficient_evidence", not out.get("claims"))
    out.setdefault("claims", [])
    out.setdefault("answer_text", "")
    return out
