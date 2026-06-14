"""Answer audit records (JSON files) — used for analytics + feedback lookup."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from . import config


def save_answer(record: dict) -> None:
    record = {**record, "created_at": datetime.now(timezone.utc).isoformat()}
    (config.ANSWERS_DIR / f"{record['answer_id']}.json").write_text(json.dumps(record, indent=2))


def get_answer(answer_id: str) -> dict | None:
    p = config.ANSWERS_DIR / f"{answer_id}.json"
    return json.loads(p.read_text()) if p.exists() else None


def list_answers() -> list[dict]:
    return [json.loads(p.read_text())
            for p in sorted(config.ANSWERS_DIR.glob("ANS-*.json"))]
