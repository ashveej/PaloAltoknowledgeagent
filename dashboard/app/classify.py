"""Lightweight product/feature/intent classifier (Claude haiku, or mock)."""
from __future__ import annotations

from . import config
from .llm import call_json

SYSTEM = (
    "ROLE=CLASSIFY. You classify a Technical Sales question. "
    "Return ONLY a JSON object: "
    '{"product": <string|null>, "feature": <string|null>, "intent": <string>}. '
    "Known products: Prisma Access, Cortex XDR, NGFW. "
    "Intent is one of: technical_capability_question, configuration_question, "
    "compatibility_question, other."
)


def classify(question: str, product_hint: str | None = None) -> dict:
    if product_hint:
        # Caller already knows the product; skip the LLM call.
        return {"product": product_hint, "feature": None,
                "intent": "technical_capability_question"}
    try:
        out = call_json(config.CLASSIFY_MODEL, SYSTEM, f"Question: {question}", max_tokens=200)
    except Exception:
        out = {}
    return {
        "product": out.get("product"),
        "feature": out.get("feature"),
        "intent": out.get("intent", "other"),
    }
