# NOTE: runnable source of truth is dashboard/app/seed.py. Run via: cd dashboard && python -m app.seed

"""Seed a small set of approved chunks so the pipeline is demoable.

Includes deliberately varied sources so you can see every confidence outcome:
  - fresh official docs            -> High
  - stale approved Confluence      -> capped to Medium
  - deprecated source              -> blocked (never cited)
Ingestion of real web/PDF sources is out of scope for the MVP (see ARCHITECTURE.md).

Run:  python -m app.seed
"""
from __future__ import annotations

from datetime import date, timedelta

from . import config
from .db import get_db
from .models import Chunk

TODAY = date(2026, 6, 13)


def _d(days_ago: int) -> str:
    return (TODAY - timedelta(days=days_ago)).isoformat()


SEED: list[dict] = [
    # --- Fresh official documentation (High-confidence material) ---
    {
        "chunk_id": "DOC-12345#chunk-008",
        "text": ("Prisma Access supports Remote Networks for site-to-site connectivity. "
                 "Feature Y is available in version 11.2 when Setting Z is enabled for the "
                 "deployment. This configuration is supported only when Setting Z is enabled."),
        "source_id": "DOC-12345",
        "source_title": "Prisma Access Admin Guide — Remote Networks",
        "section_title": "Configure Remote Networks",
        "anchor_url": "https://docs.example.com/prisma-access/remote-networks#configure",
        "product": "Prisma Access",
        "feature": "Remote Networks",
        "version": "11.2",
        "source_type": "official_documentation",
        "approval_status": "approved",
        "last_reviewed_date": _d(20),
        "deprecated": False,
        "upvotes": 48,
        "downvotes": 2,
    },
    {
        "chunk_id": "DOC-12350#chunk-002",
        "text": ("Prisma Access 11.2 Release Notes: Feature Y is generally available. "
                 "Enabling Setting Z is required for Remote Networks deployments."),
        "source_id": "DOC-12350",
        "source_title": "Prisma Access 11.2 Release Notes",
        "section_title": "What's New in 11.2",
        "anchor_url": "https://docs.example.com/prisma-access/release-notes/11-2#feature-y",
        "product": "Prisma Access",
        "feature": "Remote Networks",
        "version": "11.2",
        "source_type": "release_notes",
        "approval_status": "approved",
        "last_reviewed_date": _d(35),
        "deprecated": False,
        "upvotes": 30,
        "downvotes": 1,
    },
    # --- Stale approved internal Confluence page (caps confidence to Medium) ---
    {
        "chunk_id": "CONF-777#chunk-1",
        "text": ("Cortex XDR Endpoint Policy supports custom exclusion rules. "
                 "Administrators can scope policies per endpoint group."),
        "source_id": "CONF-777",
        "source_title": "Cortex XDR Endpoint Policy Notes (internal)",
        "section_title": "Endpoint Policy Exclusions",
        "anchor_url": "https://confluence.example.com/cortex-xdr/endpoint-policy#exclusions",
        "product": "Cortex XDR",
        "feature": "Endpoint Policy",
        "version": "",
        "source_type": "approved_internal_confluence",
        "approval_status": "approved",
        "last_reviewed_date": _d(240),  # > 180 days -> Medium cap
        "deprecated": False,
        "upvotes": 10,
        "downvotes": 3,
    },
    # --- Deprecated source: must never be cited ---
    {
        "chunk_id": "DOC-OLD-1#chunk-1",
        "text": ("NGFW PAN-OS upgrade path for legacy 9.x. This document is no longer "
                 "maintained."),
        "source_id": "DOC-OLD-1",
        "source_title": "Legacy PAN-OS 9.x Upgrade Guide",
        "section_title": "Upgrade Path",
        "anchor_url": "https://docs.example.com/ngfw/legacy-9x#upgrade",
        "product": "NGFW",
        "feature": "PAN-OS Upgrade",
        "version": "9.x",
        "source_type": "official_documentation",
        "approval_status": "approved",
        "last_reviewed_date": _d(800),
        "deprecated": True,
        "upvotes": 2,
        "downvotes": 9,
    },
]


def seed(reset: bool = True) -> int:
    db = get_db()
    mode = "overwrite" if reset else "create"
    table = db.create_table(config.CHUNKS_TABLE, schema=Chunk, mode=mode)
    # Add raw dicts: the embedding function auto-populates `vector` from `text`.
    table.add(SEED)
    return len(SEED)


if __name__ == "__main__":
    n = seed(reset=True)
    print(f"Seeded {n} chunks into LanceDB at {config.LANCEDB_DIR}")
