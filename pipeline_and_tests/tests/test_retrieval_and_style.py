"""Pure helpers: retrieval boosts + style guards/experience score + SME routing."""
from app import retrieval as R
from app import style as S
from app.config import route_sme
from tests.factories import make_chunk


# ----------------------------- retrieval -------------------------------- #
def test_freshness_penalty_buckets():
    assert R._freshness_penalty(30) == 0.0
    assert R._freshness_penalty(200) == 0.10
    assert R._freshness_penalty(400) == 0.20


def test_reputation_penalty_buckets():
    assert R._reputation_penalty(100, 1) == 0.0       # ~1%
    assert R._reputation_penalty(80, 20) == 0.15      # 20%
    assert R._reputation_penalty(10, 90) == 0.30      # 90%
    assert R._reputation_penalty(0, 0) == 0.0         # no data


def test_days_since_handles_blank():
    assert R._days_since("") == 9999
    assert R._days_since("not-a-date") == 9999


# ------------------------------- style ---------------------------------- #
def test_caveats_extracted_from_text():
    cavs = S._caveats_from_chunks([make_chunk()])
    assert any("Setting Z" in c for c in cavs)


def test_guard_flags_banned_phrase():
    g = S._run_guards("As an AI language model, yes it is supported.", [])
    assert not g["passed"]
    assert "banned_phrase" in g["failures"]


def test_guard_flags_dropped_caveat():
    caveats = ["Feature Y is supported only when Setting Z is enabled."]
    g = S._run_guards("Yes, it is fully supported.", caveats)  # 'Setting Z' missing
    assert not g["passed"]
    assert "dropped_caveat" in g["failures"]


def test_guard_passes_when_caveat_preserved():
    caveats = ["Feature Y is supported only when Setting Z is enabled."]
    g = S._run_guards("Yes — supported only when Setting Z is enabled.", caveats)
    assert g["passed"]


def test_experience_score_rewards_direct_answer_and_positioning():
    claims = [{"claim_text": "Feature Y is supported.", "source_chunk_ids": ["DOC-1#chunk-1"]}]
    styled = ("Yes — Prisma Access supports Feature Y in 11.2. For a customer "
              "conversation, position this as supported but configuration-dependent.")
    ctx = {"caveats": [], "claims": claims, "cited_chunks": [make_chunk()],
           "product": "Prisma Access"}
    out = S.score_experience(styled, ctx)
    assert out["experience_quality_score"] >= 80
    assert any(b["id"] == "direct_answer_first" and b["passed"]
               for b in out["experience_breakdown"])


# ------------------------- brand voice (deterministic) ------------------------ #
def test_terminology_normalization_fixes_casing():
    from app import brand_voice as bv
    fixed, n = bv.normalize_terminology("prisma access and pan-os and cortex xdr")
    assert "Prisma Access" in fixed and "PAN-OS" in fixed and "Cortex XDR" in fixed
    assert n == 3


def test_terminology_does_not_duplicate_canonical_tail():
    # "palo alto" is a prefix of "Palo Alto Networks"; must not become "Networks Networks"
    from app import brand_voice as bv
    fixed, _ = bv.normalize_terminology("Palo Alto Networks recommends upgrading.")
    assert "Networks Networks" not in fixed
    assert fixed == "Palo Alto Networks recommends upgrading."


def test_terminology_check_flags_wrong_casing():
    ctx = {"caveats": [], "claims": [], "cited_chunks": [], "product": None}
    passed, reason = S._check("terminology", "We support prisma access today.", ctx)
    assert not passed and "prisma access" in reason


def test_tone_check_flags_hype():
    ctx = {"caveats": [], "claims": [], "cited_chunks": [], "product": None}
    passed, reason = S._check("tone", "This is a bulletproof, 100% secure solution.", ctx)
    assert not passed


def test_hard_hype_does_not_pass_tone_but_is_not_a_guard():
    # hype costs tone points (rubric) but is not in the hard guard list
    from app import brand_voice as bv
    assert "banned_phrase" in [g for g in bv.load()["guards"]]
    assert bv.hype_present("a revolutionary game-changing platform")


# ------------------------------ routing --------------------------------- #
def test_sme_routing():
    # feature-specific rule wins (tolerant substring match)
    assert route_sme("Cortex XDR", "Behavioral Threat Protection") == "Cortex XDR — Threat Prevention SME"
    assert route_sme("NGFW", "Decryption / SSL") == "NGFW — Decryption SME"
    # unknown feature -> product catch-all
    assert route_sme("Cortex XDR", "something else") == "Cortex XDR SME"
    assert route_sme("Cortex XDR", None) == "Cortex XDR SME"
    # no product -> global default
    assert route_sme("Unknown", None) == "General Technical SME"
    assert route_sme(None, None) == "General Technical SME"
