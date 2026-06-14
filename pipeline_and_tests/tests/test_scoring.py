"""Technical Trust Score + deterministic confidence bands/caps."""
from app.scoring import score
from tests.factories import make_chunk, make_facts


def test_fresh_official_is_high_100():
    out = score(make_facts(), [make_chunk()], detected_version="11.2")
    assert out["technical_trust_score"] == 100
    assert out["confidence"] == "High"
    assert out["breakdown"]["caps_applied"] == []


def test_stale_181_365_caps_to_medium():
    # raw score still high, but freshness 181-365d caps confidence at Medium
    c = make_chunk(_days_since_review=240, last_reviewed_date="2025-10-16")
    out = score(make_facts(), [c], detected_version=None)
    assert out["confidence"] == "Medium"
    assert any("180 days" in r for r in out["breakdown"]["caps_applied"])


def test_stale_over_365_caps_to_low():
    c = make_chunk(_days_since_review=800)
    out = score(make_facts(), [c], detected_version=None)
    assert out["confidence"] == "Low"


def test_high_downvote_ratio_caps_to_low():
    c = make_chunk(upvotes=10, downvotes=20)  # 66% downvotes
    out = score(make_facts(), [c], detected_version=None)
    assert out["confidence"] == "Low"
    assert any("downvote" in r for r in out["breakdown"]["caps_applied"])


def test_moderate_downvote_ratio_caps_to_medium():
    c = make_chunk(upvotes=80, downvotes=20)  # 20% -> >15%
    out = score(make_facts(), [c], detected_version=None)
    assert out["confidence"] == "Medium"


def test_single_downvote_does_not_cap():
    # one "wrong answer" click (0 up / 1 down) must NOT bury a source (min-votes floor)
    c = make_chunk(upvotes=0, downvotes=1)
    out = score(make_facts(), [c], detected_version="11.2")
    assert out["confidence"] == "High"
    assert not any("downvote" in r for r in out["breakdown"]["caps_applied"])


def test_sme_verified_sole_source_can_be_high():
    # a human-verified SME answer, alone, is trusted enough for High (not capped to Medium)
    c = make_chunk(source_type="sme_kb", version="")
    out = score(make_facts(), [c], detected_version=None)
    assert out["confidence"] == "High"


def test_single_non_official_source_caps_to_medium():
    c = make_chunk(source_type="approved_internal_confluence")
    out = score(make_facts(), [c], detected_version=None)
    assert out["confidence"] == "Medium"
    assert any("not official" in r for r in out["breakdown"]["caps_applied"])


def test_version_sensitive_without_version_caps_to_medium():
    c = make_chunk(version="")  # no version on evidence
    out = score(make_facts(), [c], detected_version="11.2")
    assert out["confidence"] == "Medium"


def test_low_relevance_drops_raw_below_band():
    # weak retrieval relevance pulls the raw score under 65 -> Low
    c = make_chunk(_base_score=0.30, source_type="approved_internal_confluence",
                   _days_since_review=400, upvotes=5, downvotes=5)
    out = score(make_facts(), [c], detected_version=None)
    assert out["technical_trust_score"] < 65
    assert out["confidence"] == "Low"


def test_partial_citation_coverage_lowers_citation_points():
    facts = make_facts(claims=[
        {"claim_id": "C1", "claim_text": "a", "source_chunk_ids": ["DOC-1#chunk-1"]},
        {"claim_id": "C2", "claim_text": "b", "source_chunk_ids": []},
    ])
    out = score(facts, [make_chunk()], detected_version=None)
    assert out["breakdown"]["citation_integrity"] == 20  # 40 * 1/2
