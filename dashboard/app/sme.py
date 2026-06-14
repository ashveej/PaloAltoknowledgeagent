"""SME light lifecycle: read the queue, then approve -> publish the SME answer
into LanceDB as an approved `sme_kb` source so it is instantly citable.
(ARCHITECTURE.md §7)."""
from __future__ import annotations

import uuid
from datetime import date

from . import config
from .db import get_chunks_table
from .escalate import close_escalation


def publish_sme_answer(escalation_id: str, approved_answer: str, product: str,
                       feature: str = "", version: str = "", owner: str = "SME",
                       source_url: str = "internal://sme-answer") -> dict:
    """Embed + insert the SME answer as a new approved chunk, then close the
    originating escalation."""
    sid = f"SME-{uuid.uuid4().hex[:6]}"
    chunk = {
        "chunk_id": f"{sid}#chunk-1",
        "text": approved_answer,
        "source_id": sid,
        "source_title": f"SME Approved Answer — {product} {feature}".strip(),
        "section_title": "SME Approved Answer",
        "anchor_url": source_url,
        "product": product,
        "feature": feature,
        "version": version,
        "source_type": "sme_kb",
        "approval_status": "approved",
        "last_reviewed_date": date.today().isoformat(),
        "deprecated": False,
        "upvotes": 0,
        "downvotes": 0,
    }
    table = get_chunks_table()
    table.add([chunk])  # embedding auto-generated from text

    close_escalation(escalation_id, resolution=f"published:{sid}")
    return {"published_source_id": sid, "chunk_id": chunk["chunk_id"],
            "escalation_id": escalation_id, "status": "published"}
