"""Pydantic API models + the LanceDB chunk schema."""
from __future__ import annotations

from typing import Optional

from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from pydantic import BaseModel

from . import config

# Local sentence-transformers embedding function bound to the schema.
_embed_fn = get_registry().get("sentence-transformers").create(name=config.EMBED_MODEL)


class Chunk(LanceModel):
    """One retrievable, citable unit of approved knowledge.
    Source-level metadata rides on the chunk for MVP simplicity."""

    chunk_id: str
    text: str = _embed_fn.SourceField()
    vector: Vector(_embed_fn.ndims()) = _embed_fn.VectorField()
    source_id: str
    source_title: str
    section_title: str
    anchor_url: str
    product: str
    feature: str = ""
    version: str = ""
    source_type: str = "official_documentation"
    approval_status: str = "approved"
    last_reviewed_date: str = ""  # ISO date
    deprecated: bool = False
    upvotes: int = 0
    downvotes: int = 0


# ----------------------------- API contracts ------------------------------- #
class AskRequest(BaseModel):
    question: str
    product: Optional[str] = None
    user_role: str = "Technical Sales"


class Citation(BaseModel):
    title: str
    url: str
    chunk_id: str
    section_title: str = ""
    text: str = ""          # the exact cited chunk, embedded for in-page verification
    product: str = ""
    source_type: str = ""
    freshness: str = ""     # Fresh | Aging | Stale


class AskResponse(BaseModel):
    answer_id: str
    answer: str
    confidence: str
    technical_trust_score: int
    experience_quality_score: int
    final_response_quality_score: float
    why_confidence: str
    citations: list[Citation]
    escalated_to_sme: bool
    score_breakdown: dict
    why_experience: str = ""
    experience_breakdown: list[dict] = []


class FeedbackRequest(BaseModel):
    answer_id: str
    feedback_type: str  # helpful | answer_is_wrong | citation_does_not_support | source_outdated | wrong_version | missing_caveat | too_robotic
    comment: str = ""


class SMEAnswerRequest(BaseModel):
    escalation_id: str
    approved_answer: str
    product: str
    feature: str = ""
    version: str = ""
    owner: str = "SME"
    source_url: str = "internal://sme-answer"
