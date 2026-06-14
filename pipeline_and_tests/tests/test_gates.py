"""Hard gates: no citation -> no answer; deprecated/unapproved/off-product blocked."""
from app.gates import run_gates
from tests.factories import make_chunk, make_facts


def _by_id(*chunks):
    return {c["chunk_id"]: c for c in chunks}


def test_happy_path_passes():
    c = make_chunk()
    res = run_gates(make_facts(), _by_id(c), "Prisma Access")
    assert res.passed
    assert res.failed_gates == []


def test_no_evidence_fails():
    res = run_gates(make_facts(), {}, "Prisma Access")
    assert not res.passed
    assert "evidence_exists" in res.failed_gates


def test_insufficient_evidence_flag_fails():
    res = run_gates(make_facts(insufficient=True), _by_id(make_chunk()), "Prisma Access")
    assert not res.passed
    assert "insufficient_evidence" in res.failed_gates


def test_uncited_claim_fails():
    facts = make_facts(claims=[{"claim_id": "C1", "claim_text": "x", "source_chunk_ids": []}])
    res = run_gates(facts, _by_id(make_chunk()), "Prisma Access")
    assert not res.passed
    assert "citation_coverage" in res.failed_gates


def test_citation_to_unknown_chunk_fails():
    facts = make_facts(claims=[{"claim_id": "C1", "claim_text": "x",
                                "source_chunk_ids": ["GHOST#1"]}])
    res = run_gates(facts, _by_id(make_chunk()), "Prisma Access")
    assert not res.passed
    assert "citation_validity" in res.failed_gates


def test_deprecated_source_blocked():
    c = make_chunk(deprecated=True)
    res = run_gates(make_facts(), _by_id(c), "Prisma Access")
    assert not res.passed
    assert "deprecated_source" in res.failed_gates


def test_unapproved_source_blocked():
    c = make_chunk(approval_status="draft")
    res = run_gates(make_facts(), _by_id(c), "Prisma Access")
    assert not res.passed
    assert "source_approval" in res.failed_gates


def test_product_mismatch_blocked():
    c = make_chunk(product="Cortex XDR")
    res = run_gates(make_facts(), _by_id(c), "Prisma Access")
    assert not res.passed
    assert "product_match" in res.failed_gates
