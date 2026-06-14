"""Style layer (brand voice). Operates ONLY on validated claims + caveats, never
raw KB. Everything is driven by brand_voice.yaml: the LLM is steered by the
config's voice, terminology is deterministically enforced, hard guards reject bad
rewrites, and the Experience Quality Score is a weighted, explainable rubric —
the same rigor as the Technical Trust Score. Style can raise the Experience score
but can never change technical meaning, drop caveats, or alter confidence.
(ARCHITECTURE.md §2, spec §15.)"""
from __future__ import annotations

import json
import re

from . import brand_voice as bv
from . import config
from .llm import call_json


# ----------------------------- caveat helpers ------------------------------ #
def _caveats_from_chunks(cited_chunks: list[dict]) -> list[str]:
    caveats = []
    for c in cited_chunks:
        for sent in re.split(r"(?<=[.])\s+", c.get("text", "")):
            low = sent.lower()
            if any(w in low for w in ("only when", "requires", "not ", "must ",
                                      "supported only", "up to", "maximum")):
                caveats.append(sent.strip())
    return caveats


def _key_term(caveat: str) -> str:
    m = re.search(r"(Setting \w+|version \d+(\.\d+)?|\d+\s?\w+|enabled|required|requires)",
                  caveat)
    return m.group(0) if m else ""


def _caveats_preserved(text: str, caveats: list[str]) -> bool:
    low = text.lower()
    for cav in caveats:
        key = _key_term(cav)
        if key and key.lower() not in low:
            return False
    return True


# ------------------------------ deterministic rubric ----------------------- #
def _check(check: str, text: str, ctx: dict) -> tuple[bool, str]:
    """Run one rubric check. Returns (passed, reason)."""
    if check == "direct_answer":
        ok = bv.has_direct_answer(text)
        return ok, "" if ok else "no direct yes/no/summary in the first sentence"

    if check == "terminology":
        bad = bv.remaining_variants(text)
        if bad:
            return False, f"non-canonical product term(s): {', '.join(sorted(set(bad)))}"
        return True, ""

    if check == "caveats_preserved":
        ok = _caveats_preserved(text, ctx.get("caveats", []))
        return ok, "" if ok else "a source caveat/limit was dropped"

    if check == "word_limit":
        n = len(text.split())
        ok = n <= bv.max_words()
        return ok, "" if ok else f"answer is {n} words (limit {bv.max_words()})"

    if check == "positioning":
        ok = bv.has_positioning(text)
        return ok, "" if ok else "no SE positioning / next-step line"

    if check == "citations_present":
        ok = any(c.get("source_chunk_ids") for c in ctx.get("claims", []))
        return ok, "" if ok else "no claim carries a citation"

    if check == "tone":
        banned = bv.banned_phrases_present(text)
        hype = bv.hype_present(text)
        if banned or hype:
            return False, f"off-brand language: {', '.join(banned + hype)}"
        return True, ""

    return True, ""  # unknown check -> non-blocking


def score_experience(text: str, ctx: dict) -> dict:
    """Weighted, deterministic Experience Quality Score with breakdown + reasons."""
    breakdown = []
    total = 0
    reasons = []
    for item in bv.load().get("rubric", []):
        passed, reason = _check(item["check"], text, ctx)
        awarded = item["points"] if passed else 0
        total += awarded
        breakdown.append({
            "id": item["id"], "label": item.get("label", item["id"]),
            "points": item["points"], "awarded": awarded, "passed": passed,
        })
        if not passed and reason:
            reasons.append(reason)
    why = (f"Experience {total}/100 — " +
           ("all brand-voice checks passed." if not reasons
            else "gaps: " + "; ".join(reasons) + "."))
    return {"experience_quality_score": total, "experience_breakdown": breakdown,
            "why_experience": why}


# ------------------------------ guards ------------------------------------- #
def _run_guards(text: str, caveats: list[str]) -> dict:
    failures = []
    for guard in bv.load().get("guards", []):
        if guard == "banned_phrase" and bv.banned_phrases_present(text):
            failures.append("banned_phrase")
        elif guard == "dropped_caveat" and not _caveats_preserved(text, caveats):
            failures.append("dropped_caveat")
    return {"passed": not failures, "failures": failures}


# ------------------------------ entry point -------------------------------- #
def apply_style(claims: list[dict], cited_chunks: list[dict],
                product: str | None = None) -> dict:
    caveats = _caveats_from_chunks(cited_chunks)
    payload = {
        "product": product,
        "claims": [{"claim_text": c["claim_text"]} for c in claims],
        "caveats": [{"caveat": c} for c in caveats],
    }
    try:
        out = call_json(config.STYLE_MODEL, bv.system_prompt(), json.dumps(payload),
                        max_tokens=700)
        styled = out.get("styled_answer", "").strip()
    except Exception:
        styled = ""

    plain = " ".join(c["claim_text"] for c in claims)
    if caveats:
        plain += " Caveat: " + " ".join(caveats)
    if not styled:
        styled = plain

    # Deterministic terminology enforcement (always applied).
    styled, _ = bv.normalize_terminology(styled)

    # Hard guards: never ship a guard-failing rewrite — fall back to plain claims.
    guards = _run_guards(styled, caveats)
    if not guards["passed"]:
        styled, _ = bv.normalize_terminology(plain)
        guards = _run_guards(styled, caveats)

    ctx = {"caveats": caveats, "claims": claims, "cited_chunks": cited_chunks,
           "product": product}
    scored = score_experience(styled, ctx)
    return {"styled_answer": styled, "guards": guards, **scored}
