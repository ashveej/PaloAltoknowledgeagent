"""Retrieval = LanceDB vector search -> cross-encoder ordering -> deterministic
freshness/reputation boost. Deprecated and unapproved chunks are dropped here so
they can never reach the answer (ARCHITECTURE.md §1, §6).

Note on relevance: with a shared product vocabulary, neither vector similarity nor
the cross-encoder logit reliably separates on-topic from off-topic in absolute
terms (an off-topic chunk can score as high as an on-topic one). So the
cross-encoder is used only for ORDERING; the off-topic gate is the LLM facts
engine, which returns INSUFFICIENT_EVIDENCE. We keep only a lenient vector-
similarity floor to drop clearly-unrelated chunks."""
from __future__ import annotations

from datetime import date

from . import config
from .db import get_chunks_table

TODAY = date(2026, 6, 13)

# Lenient floor on vector cosine-ish similarity (1/(1+distance)). Good matches sit
# ~0.5; this only removes clearly-unrelated chunks. The LLM facts engine is the
# real off-topic defense.
MIN_VECTOR_SIM = 0.30

_ce = None


def _get_cross_encoder():
    global _ce
    if _ce is None:
        from sentence_transformers import CrossEncoder

        _ce = CrossEncoder(config.RERANK_MODEL)
    return _ce


def _days_since(iso: str) -> int:
    if not iso:
        return 9999
    try:
        # relative to the real current date; clamp so a doc reviewed today (or with
        # a slightly-future timestamp) reads as 0, never negative
        return max(0, (date.today() - date.fromisoformat(iso)).days)
    except ValueError:
        return 9999


MIN_REP_VOTES = 5  # need enough votes before reputation affects ranking


def _reputation_penalty(up: int, down: int) -> float:
    total = up + down
    if total < MIN_REP_VOTES:
        return 0.0
    ratio = down / total
    if ratio > 0.30:
        return 0.30
    if ratio > 0.15:
        return 0.15
    return 0.0


def _freshness_penalty(days: int) -> float:
    if days > 365:
        return 0.20
    if days > 180:
        return 0.10
    return 0.0


def retrieve(question: str, product: str | None = None, k: int = 5) -> list[dict]:
    """Return up to k approved, non-deprecated chunks, ranked best-first."""
    table = get_chunks_table()
    rows = table.search(question).limit(max(k * 4, 16)).to_list()  # vector order + _distance

    cand: list[dict] = []
    for r in rows:
        if r.get("deprecated") or r.get("approval_status") != "approved":
            continue  # gate: never surface deprecated/unapproved evidence
        if product and r.get("product") and r["product"].lower() != product.lower():
            continue
        sim = 1.0 / (1.0 + r.get("_distance", 1.0))  # calibrated relevance signal
        if sim < MIN_VECTOR_SIM:
            continue  # lenient floor: drop clearly-unrelated chunks
        r["_base_score"] = float(sim)
        r["_days_since_review"] = _days_since(r.get("last_reviewed_date", ""))
        cand.append(r)

    if not cand:
        return []

    # Cross-encoder for ORDERING only (not an absolute relevance gate).
    try:
        scores = _get_cross_encoder().predict([[question, c["text"]] for c in cand])
        for c, s in zip(cand, scores):
            c["_ce_score"] = float(s)
    except Exception:
        for c in cand:
            c["_ce_score"] = c["_base_score"]

    # Order by cross-encoder, nudged down by freshness/reputation penalties so stale
    # or downvoted sources fall in the ranking (feedback -> rerank, no retraining).
    for c in cand:
        penalty = _freshness_penalty(c["_days_since_review"]) \
            + _reputation_penalty(c.get("upvotes", 0), c.get("downvotes", 0))
        c["_boosted_score"] = c["_ce_score"] - 4.0 * penalty

    cand.sort(key=lambda x: x["_boosted_score"], reverse=True)
    return cand[:k]
