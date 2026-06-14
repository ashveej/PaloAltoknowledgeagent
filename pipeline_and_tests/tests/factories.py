"""Shared test helpers. All tests here are pure-Python: no LLM, no LanceDB."""
from __future__ import annotations


def make_chunk(**over) -> dict:
    """A retrieved+scored chunk dict as produced by retrieval.retrieve()."""
    base = {
        "chunk_id": "DOC-1#chunk-1",
        "source_id": "DOC-1",
        "source_title": "Test Source",
        "text": "Feature Y is supported only when Setting Z is enabled.",
        "product": "Prisma Access",
        "feature": "Remote Networks",
        "version": "11.2",
        "source_type": "official_documentation",
        "approval_status": "approved",
        "deprecated": False,
        "upvotes": 50,
        "downvotes": 1,
        "_base_score": 0.99,
        "_boosted_score": 0.99,
        "_days_since_review": 20,
    }
    base.update(over)
    return base


def make_facts(claims=None, insufficient=False) -> dict:
    if claims is None:
        claims = [{"claim_id": "C1", "claim_text": "Feature Y is supported.",
                   "source_chunk_ids": ["DOC-1#chunk-1"]}]
    return {"insufficient_evidence": insufficient, "claims": claims,
            "answer_text": "Yes. [DOC-1#chunk-1]"}
