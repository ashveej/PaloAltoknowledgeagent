"""SME escalation records (JSON files). The dashboard + SME queue read these."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from . import config


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_escalation(question: str, product: str | None, feature: str | None,
                      failed_reason: str, retrieved_sources: list[str],
                      confidence_score: int) -> dict:
    eid = f"ESC-{uuid.uuid4().hex[:8]}"
    record = {
        "escalation_id": eid,
        "question": question,
        "product": product,
        "feature": feature,
        "failed_reason": failed_reason,
        "retrieved_sources": retrieved_sources,
        "confidence_score": confidence_score,
        "user_context": "Technical Sales",
        "requested_sla": "2 business days",
        "assigned_sme_group": config.route_sme(product, feature),
        "status": "open",
        "created_at": _now(),
    }
    # Notify the SME group by email (real SMTP if configured, else outbox).
    try:
        from . import notify
        record["notification"] = notify.send_escalation_email(record)
    except Exception as e:  # never let notification failure block escalation
        record["notification"] = {"error": str(e), "transport": "failed"}
    (config.ESCALATIONS_DIR / f"{eid}.json").write_text(json.dumps(record, indent=2))
    return record


def list_escalations(status: str | None = None) -> list[dict]:
    out = []
    for p in sorted(config.ESCALATIONS_DIR.glob("ESC-*.json")):
        rec = json.loads(p.read_text())
        if status is None or rec.get("status") == status:
            out.append(rec)
    return out


def get_escalation(eid: str) -> dict | None:
    p = config.ESCALATIONS_DIR / f"{eid}.json"
    return json.loads(p.read_text()) if p.exists() else None


def close_escalation(eid: str, resolution: str) -> None:
    rec = get_escalation(eid)
    if rec:
        rec["status"] = "resolved"
        rec["resolution"] = resolution
        rec["resolved_at"] = _now()
        (config.ESCALATIONS_DIR / f"{eid}.json").write_text(json.dumps(rec, indent=2))
