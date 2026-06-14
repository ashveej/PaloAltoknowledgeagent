"""Generate REPORT.md: run a curated 5 easy / 5 medium / 5 hard question set
through the live pipeline and dump every score + breakdown.

Usage:  .venv/bin/python make_report.py
"""
from __future__ import annotations

from datetime import datetime, timezone

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "dashboard"))

from app import config
from app.pipeline import ask

QUESTIONS = [
    # ---- EASY: expect High (fresh official docs / the ingested PDF) ----
    ("easy", "How much bandwidth and how many connectors does a ZTNA Connector group support?"),
    ("easy", "What is the supported PAN-OS upgrade path to 11.1 and can I skip versions?"),
    ("easy", "What new networking features arrived in PAN-OS 11.2?"),
    ("easy", "How many monitored users does an ADEM tenant support and what license does ADEM need?"),
    ("easy", "What is the maximum number of BGP IP addresses per remote network?"),
    # ---- MEDIUM: expect Medium (sources reviewed 181-365 days ago -> freshness cap) ----
    ("medium", "What are the decryption types on the NGFW and which is unsupported in Strata Cloud Manager?"),
    ("medium", "What is SSL Forward Proxy decryption used for on the firewall?"),
    ("medium", "What is the maximum bandwidth per tunnel on high-performance remote networks?"),
    ("medium", "How many service endpoint addresses do high-performance remote networks use per Gbps?"),
    ("medium", "How does App-ID identify evasive or encrypted traffic?"),
    # ---- HARD: expect SME escalation (not covered / off-topic / unanswerable) ----
    ("hard", "How do I configure a Behavioral Threat Protection exception and exploit-protection ROP modules in Cortex XDR?"),
    ("hard", "What is the App-ID throughput sizing for a PA-5450 in a multi-vsys HA deployment?"),
    ("hard", "Does Prisma Access integrate with SAP S/4HANA accounting modules?"),
    ("hard", "Does Cortex XSIAM support MITRE ATT&CK technique mapping?"),
    ("hard", "What is the per-user list price of Prisma Access?"),
]

CONF_ICON = {"High": "🟢 High", "Medium": "🟡 Medium", "Low": "🔴 Low"}


def run() -> list[dict]:
    rows = []
    for tier, q in QUESTIONS:
        r = ask(q)
        rows.append({"tier": tier, "q": q, "r": r})
    return rows


def md_table_summary(rows) -> str:
    out = ["| # | Tier | Question | Confidence | Trust | Exp | Final | Escalated | Sources |",
           "|---|------|----------|-----------|------:|----:|------:|-----------|---------|"]
    for i, row in enumerate(rows, 1):
        r = row["r"]
        cites = ", ".join(c["chunk_id"].split("#")[0] for c in r["citations"]) or "—"
        out.append(
            f"| {i} | {row['tier']} | {row['q'][:60]} | {CONF_ICON.get(r['confidence'], r['confidence'])} "
            f"| {r['technical_trust_score']} | {r['experience_quality_score']} "
            f"| {r['final_response_quality_score']} | {'yes' if r['escalated_to_sme'] else 'no'} | {cites} |")
    return "\n".join(out)


def md_detail(i, row) -> str:
    r = row["r"]
    bd = r.get("score_breakdown", {})
    lines = [f"### {i}. [{row['tier'].upper()}] {row['q']}",
             "",
             f"- **Confidence:** {CONF_ICON.get(r['confidence'], r['confidence'])}  "
             f"(Trust {r['technical_trust_score']}/100 · Experience {r['experience_quality_score']}/100 "
             f"· Final {r['final_response_quality_score']})",
             f"- **Escalated to SME:** {'yes' if r['escalated_to_sme'] else 'no'}",
             f"- **Detected product:** {r.get('product') or '—'}",
             f"- **Why confidence:** {r['why_confidence']}"]
    if bd:
        lines.append(f"- **Trust breakdown:** citation {bd.get('citation_integrity')}/40 · "
                     f"relevance {bd.get('retrieval_relevance')}/25 · authority {bd.get('source_authority')}/20 · "
                     f"freshness {bd.get('source_freshness')}/15 → raw {bd.get('raw_total')}"
                     + (f" · caps: {', '.join(bd['caps_applied'])}" if bd.get("caps_applied") else ""))
    if r.get("why_experience"):
        lines.append(f"- **Why brand voice:** {r['why_experience']}")
    if r.get("experience_breakdown"):
        chips = " · ".join(f"{'✓' if b['passed'] else '✗'} {b['label']} {b['awarded']}/{b['points']}"
                           for b in r["experience_breakdown"])
        lines.append(f"- **Brand-voice rubric:** {chips}")
    if r["citations"]:
        lines.append("- **Citations:** " + "; ".join(f"[{c['chunk_id']}]({c['url']})" for c in r["citations"]))
    ans = r["answer"].split("Confidence:")[0].replace("Answer:", "").strip()
    lines += ["", "> " + ans.replace("\n", "\n> ")[:700], ""]
    return "\n".join(lines)


def main():
    rows = run()
    tiers = {"easy": [], "medium": [], "hard": []}
    for row in rows:
        tiers[row["tier"]].append(row["r"]["confidence"])

    def dist(t):
        from collections import Counter
        return dict(Counter(tiers[t]))

    doc = [
        "# Evaluation Report — 5 Easy / 5 Medium / 5 Hard",
        "",
        f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · "
        f"models: {config.FACTS_MODEL} (facts/style), {config.CLASSIFY_MODEL} (classify) · "
        f"embeddings: {config.EMBED_MODEL} (local) · MOCK_LLM={config.MOCK_LLM}_",
        "",
        "Confidence is computed deterministically; brand-voice (Experience) is scored "
        "from `brand_voice.yaml`. 'Hard' questions are intentionally outside the "
        "knowledge base to exercise SME escalation.",
        "",
        "## Tier outcomes",
        f"- **Easy** (expect High): {dist('easy')}",
        f"- **Medium** (expect Medium): {dist('medium')}",
        f"- **Hard** (expect escalation/Low): {dist('hard')}",
        "",
        "## Summary",
        md_table_summary(rows),
        "",
        "## Details",
    ]
    for i, row in enumerate(rows, 1):
        doc.append(md_detail(i, row))

    out = config.ROOT / "REPORT.md"
    out.write_text("\n".join(doc), encoding="utf-8")
    print(f"Wrote {out}")
    print("Tier outcomes:", {t: dist(t) for t in tiers})


if __name__ == "__main__":
    main()
