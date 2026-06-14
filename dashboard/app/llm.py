"""Thin Claude wrapper. Falls back to deterministic MOCK output when no API key
is set, so the full pipeline is runnable offline for demos."""
from __future__ import annotations

import json
import re

from . import config

_client = None


def _get_client():
    global _client
    if _client is None:
        from anthropic import Anthropic

        _client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model response (handles code fences)."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1].lstrip("json").strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError(f"No JSON object found in model output: {text[:200]}")
    return json.loads(m.group(0))


def call_json(model: str, system: str, user: str, max_tokens: int = 1024) -> dict:
    """Call Claude and parse the JSON object from the response. The system prompt
    instructs JSON-only; the extractor tolerates code fences / minor preamble.

    Note: claude-opus-4-8 deprecates the `temperature` parameter, so we don't set
    it. Determinism in confidence/gates comes from the Python scoring layer, not
    from sampling settings."""
    if config.MOCK_LLM:
        return _mock(system, user)
    msg = _get_client().messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system + "\nRespond with ONLY the JSON object and nothing else.",
        messages=[{"role": "user", "content": user}],
    )
    return _extract_json(msg.content[0].text)


# --------------------------------------------------------------------------- #
# MOCK mode: deterministic stand-ins so the pipeline runs without a key.
# Keyed off markers we embed in the system prompt.
# --------------------------------------------------------------------------- #
def _mock(system: str, user: str) -> dict:
    if "ROLE=CLASSIFY" in system:
        product = None
        for p in ("Prisma Access", "Cortex XDR", "NGFW"):
            if p.lower() in user.lower():
                product = p
                break
        return {"product": product, "feature": None, "intent": "technical_capability_question"}

    if "ROLE=FACTS" in system:
        # Build a claim per evidence chunk, citing it verbatim. If no evidence,
        # signal insufficiency exactly like the real prompt would.
        chunk_ids = re.findall(r'"chunk_id"\s*:\s*"([^"]+)"', user)
        if not chunk_ids:
            return {"insufficient_evidence": True, "claims": [], "answer_text": ""}
        texts = re.findall(r'"exact_text"\s*:\s*"([^"]*)"', user)
        first = texts[0] if texts else "the configuration described in the source"
        claims = [{
            "claim_id": "C1",
            "claim_text": first[:240],
            "source_chunk_ids": [chunk_ids[0]],
        }]
        return {
            "insufficient_evidence": False,
            "claims": claims,
            "answer_text": f"{first[:240]} [{chunk_ids[0]}]",
        }

    if "ROLE=STYLE" in system:
        # Echo claims into the branded template without adding/removing meaning.
        claims = re.findall(r'"claim_text"\s*:\s*"([^"]*)"', user)
        caveats = re.findall(r'"caveat"\s*:\s*"([^"]*)"', user)
        body = " ".join(claims) if claims else "See cited sources."
        cav = caveats[0] if caveats else "Based strictly on the cited approved sources."
        styled = (f"Yes — {body} For a customer conversation, position this as supported but "
                  f"configuration-dependent. Caveat: {cav}")
        return {"styled_answer": styled}

    return {}
