"""User feedback -> stored record + source reputation update in LanceDB.
Reputation feeds BOTH the reranker boost and the confidence cap. No retraining.
(ARCHITECTURE.md §6, spec §14)."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from . import config
from .audit import get_answer
from .db import get_chunks_table
from .escalate import create_escalation

# feedback_type -> system action (spec §14.3)
NEGATIVE = {
    "answer_is_wrong",
    "citation_does_not_support",
    "source_outdated",
    "wrong_version",
    "missing_caveat",
}


def _bump_reputation(source_ids: list[str], positive: bool) -> None:
    """Increment up/downvotes on every chunk belonging to the cited sources."""
    if not source_ids:
        return
    table = get_chunks_table()
    field = "upvotes" if positive else "downvotes"
    for sid in set(source_ids):
        rows = table.search().where(f"source_id = '{sid}'").limit(100).to_list()
        for r in rows:
            new_val = int(r.get(field, 0)) + 1
            table.update(where=f"chunk_id = '{r['chunk_id']}'", values={field: new_val})


def record_feedback(answer_id: str, feedback_type: str, comment: str = "") -> dict:
    ans = get_answer(answer_id) or {}
    source_ids = ans.get("cited_source_ids", [])
    product = ans.get("product")

    positive = feedback_type == "helpful"
    _bump_reputation(source_ids, positive=positive)

    fid = f"FB-{uuid.uuid4().hex[:8]}"
    record = {
        "feedback_id": fid,
        "answer_id": answer_id,
        "feedback_type": feedback_type,
        "comment": comment,
        "product": product,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Hard negatives spin up an SME review ticket.
    if feedback_type in NEGATIVE:
        esc = create_escalation(
            question=ans.get("question", "(unknown)"),
            product=product,
            feature=ans.get("feature"),
            failed_reason=f"user_feedback:{feedback_type}",
            retrieved_sources=source_ids,
            confidence_score=ans.get("technical_trust_score", 0),
        )
        record["escalation_id"] = esc["escalation_id"]

    (config.FEEDBACK_DIR / f"{fid}.json").write_text(json.dumps(record, indent=2))
    return record


def list_feedback() -> list[dict]:
    return [json.loads(p.read_text())
            for p in sorted(config.FEEDBACK_DIR.glob("FB-*.json"))]
