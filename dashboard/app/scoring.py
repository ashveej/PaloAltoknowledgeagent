"""Deterministic Technical Trust Score + confidence bands/caps.
Confidence is CALCULATED here, never by the LLM. (ARCHITECTURE.md §5, spec §9-10)."""
from __future__ import annotations

AUTHORITY = {
    "official_documentation": 20,
    "release_notes": 20,
    "security_advisory": 20,
    "sme_kb": 19,            # human-verified SME answer — near top authority
    "sme_approved_kb": 19,
    "approved_internal_confluence": 13,
}

# Sources trusted enough to ground a confident answer on their own (exempt from the
# "single non-official source -> Medium" cap). SME-approved knowledge counts: a human
# expert verified it, so re-asking after an SME answers boosts confidence.
TRUSTED_SOLE_SOURCE = {"official_documentation", "release_notes", "security_advisory",
                       "sme_kb", "sme_approved_kb"}

# A source needs at least this many total votes before its downvote ratio can
# cap confidence — otherwise one "wrong answer" click (0→1 downvote = 100%) would
# permanently bury a good source.
MIN_REP_VOTES = 5


def _authority_points(source_type: str) -> int:
    return AUTHORITY.get(source_type, 8)


def _freshness_points(days: int) -> int:
    if days <= 90:
        return 15
    if days <= 180:
        return 12
    if days <= 365:
        return 8
    return 3


def _relevance_points(top_base: float) -> int:
    # _base_score is vector similarity 1/(1+distance). For the MiniLM embedding a
    # strong on-topic match sits ~0.50; calibrate buckets to that scale.
    if top_base >= 0.50:
        return 25
    if top_base >= 0.45:
        return 19
    if top_base >= 0.40:
        return 12
    if top_base >= 0.34:
        return 6
    return 2


def score(facts: dict, cited_chunks: list[dict], detected_version: str | None) -> dict:
    """cited_chunks: the chunk dicts actually cited by the claims."""
    claims = facts.get("claims", [])
    n_claims = len(claims) or 1
    cited = sum(1 for c in claims if c.get("source_chunk_ids"))

    # --- Citation integrity: 40 ---
    citation_pts = round(40 * cited / n_claims)

    # --- Retrieval relevance: 25 ---
    top_base = max((c.get("_base_score", 0.0) for c in cited_chunks), default=0.0)
    relevance_pts = _relevance_points(top_base)

    # --- Source authority: 20 (best cited source) ---
    authority_pts = max((_authority_points(c.get("source_type", "")) for c in cited_chunks),
                        default=0)

    # --- Source freshness: 15 (freshest cited source) ---
    min_days = min((c.get("_days_since_review", 9999) for c in cited_chunks), default=9999)
    freshness_pts = _freshness_points(min_days)

    raw = citation_pts + relevance_pts + authority_pts + freshness_pts

    # ----------------------------- Caps ----------------------------- #
    caps: list[str] = []
    max_band = "High"

    def cap(to: str, why: str):
        nonlocal max_band
        order = {"High": 2, "Medium": 1, "Low": 0}
        if order[to] < order[max_band]:
            max_band = to
        caps.append(why)

    if min_days > 365:
        cap("Low", "primary source reviewed over 365 days ago")
    elif min_days > 180:
        cap("Medium", "primary source reviewed over 180 days ago")

    # downvote ratio cap (worst cited source). Requires a minimum number of votes
    # so a single "wrong answer" click can't tank a source from 0 votes to 100%.
    worst_ratio = 0.0
    for c in cited_chunks:
        total = c.get("upvotes", 0) + c.get("downvotes", 0)
        if total >= MIN_REP_VOTES:
            worst_ratio = max(worst_ratio, c.get("downvotes", 0) / total)
    if worst_ratio > 0.30:
        cap("Low", f"source downvote ratio {worst_ratio:.0%} > 30%")
    elif worst_ratio > 0.15:
        cap("Medium", f"source downvote ratio {worst_ratio:.0%} > 15%")

    # single non-trusted source -> Medium (official docs + SME-verified are exempt)
    if len(cited_chunks) == 1 and cited_chunks[0].get("source_type") not in TRUSTED_SOLE_SOURCE:
        cap("Medium", "single source and not official documentation")

    # version-sensitive question but no version on cited evidence -> Medium
    if detected_version and not any(c.get("version") for c in cited_chunks):
        cap("Medium", "version-sensitive question but evidence has no explicit version")

    # ----------------------------- Band ----------------------------- #
    if raw >= 85:
        band = "High"
    elif raw >= 65:
        band = "Medium"
    else:
        band = "Low"

    order = {"High": 2, "Medium": 1, "Low": 0}
    confidence = band if order[band] <= order[max_band] else max_band

    breakdown = {
        "citation_integrity": citation_pts,
        "retrieval_relevance": relevance_pts,
        "source_authority": authority_pts,
        "source_freshness": freshness_pts,
        "raw_total": raw,
        "caps_applied": caps,
        "band_before_caps": band,
    }

    why = _explain(confidence, breakdown, cited_chunks, min_days, caps)
    return {
        "technical_trust_score": raw,
        "confidence": confidence,
        "why_confidence": why,
        "breakdown": breakdown,
    }


def _explain(confidence, breakdown, cited_chunks, min_days, caps) -> str:
    titles = ", ".join(sorted({c.get("source_title", "?") for c in cited_chunks})) or "no source"
    base = (f"Score {breakdown['raw_total']}/100 from cited source(s): {titles}. "
            f"Freshest cited source reviewed {min_days} days ago.")
    if caps:
        base += " Confidence capped because: " + "; ".join(caps) + "."
    if confidence == "Low":
        base += " Routed to SME."
    return base
