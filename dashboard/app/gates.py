"""Deterministic hard gates. Any failure blocks the answer and routes to SME.
Pure Python — no LLM. (ARCHITECTURE.md §4, spec §6.1)."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GateResult:
    passed: bool
    failed_gates: list[str] = field(default_factory=list)
    detail: dict = field(default_factory=dict)


def run_gates(facts: dict, chunks_by_id: dict[str, dict],
              detected_product: str | None) -> GateResult:
    failed: list[str] = []

    # Gate: evidence exists
    if not chunks_by_id:
        return GateResult(False, ["evidence_exists"], {"reason": "no approved evidence retrieved"})

    # Gate: model signalled insufficiency
    if facts.get("insufficient_evidence"):
        return GateResult(False, ["insufficient_evidence"],
                          {"reason": "facts engine returned INSUFFICIENT_EVIDENCE"})

    claims = facts.get("claims", [])
    if not claims:
        return GateResult(False, ["citation_coverage"], {"reason": "no claims produced"})

    cited_ids: set[str] = set()
    for c in claims:
        ids = c.get("source_chunk_ids") or []
        # Gate: citation coverage — every claim cited
        if not ids:
            failed.append("citation_coverage")
        for cid in ids:
            cited_ids.add(cid)
            chunk = chunks_by_id.get(cid)
            # Gate: citation validity — cited id must be a real retrieved chunk
            if chunk is None:
                failed.append("citation_validity")
                continue
            # Gate: source approval
            if chunk.get("approval_status") != "approved":
                failed.append("source_approval")
            # Gate: deprecated source
            if chunk.get("deprecated"):
                failed.append("deprecated_source")
            # Gate: product match
            if detected_product and chunk.get("product") \
                    and chunk["product"].lower() != detected_product.lower():
                failed.append("product_match")

    failed = sorted(set(failed))
    return GateResult(
        passed=not failed,
        failed_gates=failed,
        detail={"cited_chunk_ids": sorted(cited_ids), "num_claims": len(claims)},
    )
