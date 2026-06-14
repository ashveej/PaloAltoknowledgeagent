"""Loader + deterministic primitives for the file-driven brand voice.

All brand-voice behavior is configured in brand_voice.yaml. This module loads it
(cached) and exposes the deterministic operations the style layer uses:
terminology enforcement, guard checks, and the per-metric rubric checks. The
intent mirrors the Technical Trust Score: weighted, deterministic, explainable."""
from __future__ import annotations

import re
from functools import lru_cache

import yaml

from . import config


@lru_cache(maxsize=1)
def load() -> dict:
    with open(config.BRAND_VOICE_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def reload() -> dict:
    load.cache_clear()
    return load()


def max_words() -> int:
    return int(load().get("max_answer_words", config.MAX_ANSWER_WORDS))


def system_prompt() -> str:
    """Build the style model's system prompt from config (voice + guardrails)."""
    cfg = load()
    terms = ", ".join(cfg.get("terminology", {}).keys())
    banned = "; ".join(cfg.get("banned_phrases", []) + cfg.get("banned_hype", []))
    return (
        "ROLE=STYLE. Rewrite the provided VALIDATED claims into a polished answer.\n"
        "You must NOT add any fact, number, condition, or guarantee not in the claims, "
        "must NOT remove caveats, and must NOT change technical meaning or citations.\n\n"
        f"Brand voice:\n{cfg.get('voice_principles', '').strip()}\n\n"
        f"Use these exact product names with correct capitalization: {terms}.\n"
        f"Never use these phrases: {banned}.\n"
        f"Keep the answer under {max_words()} words.\n\n"
        'Return ONLY JSON: {"styled_answer": "..."}'
    )


# --------------------------- terminology enforcement ----------------------- #
def normalize_terminology(text: str) -> tuple[str, int]:
    """Rewrite known wrong variants to the canonical product name.
    Returns (fixed_text, num_fixes). Only actual changes are counted (a variant
    that is case-insensitively equal to an already-correct term is a no-op)."""
    fixes = 0

    def _make_repl(canonical):
        def _repl(m):
            nonlocal fixes
            if m.group(0) != canonical:
                fixes += 1
            return canonical
        return _repl

    for canonical, variants in load().get("terminology", {}).items():
        for variant in sorted(variants, key=len, reverse=True):
            # Skip a variant that is a prefix of its own canonical (e.g. "palo alto"
            # inside "Palo Alto Networks") — replacing it would duplicate the tail.
            if (variant.lower() != canonical.lower()
                    and canonical.lower().startswith(variant.lower())):
                continue
            pattern = re.compile(rf"(?<![\w-]){re.escape(variant)}(?![\w-])", re.IGNORECASE)
            text = pattern.sub(_make_repl(canonical), text)
    return text, fixes


def remaining_variants(text: str) -> list[str]:
    """Wrong-cased/spelled variants still present (should be none after normalize).
    Case-SENSITIVE on purpose: the canonical form (e.g. 'PAN-OS') must not be
    flagged by its own lowercase variant ('pan-os')."""
    found = []
    for variants in load().get("terminology", {}).values():
        for v in variants:
            if re.search(rf"(?<![\w-]){re.escape(v)}(?![\w-])", text):
                found.append(v)
    return found


# ------------------------------- phrase checks ----------------------------- #
def banned_phrases_present(text: str) -> list[str]:
    low = text.lower()
    return [p for p in load().get("banned_phrases", []) if p in low]


def hype_present(text: str) -> list[str]:
    low = text.lower()
    return [p for p in load().get("banned_hype", []) if p in low]


def has_direct_answer(text: str) -> bool:
    first = re.split(r"(?<=[.!?])\s", text.strip(), maxsplit=1)[0].lower()
    return any(m in first for m in load().get("direct_answer_markers", []))


def has_positioning(text: str) -> bool:
    low = text.lower()
    return any(m in low for m in load().get("positioning_markers", []))
