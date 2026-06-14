"""Central configuration + filesystem paths."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LANCEDB_DIR = DATA / "lancedb"
ESCALATIONS_DIR = DATA / "escalations"
FEEDBACK_DIR = DATA / "feedback"
ANSWERS_DIR = DATA / "answers"
RAW_DOCS_DIR = DATA / "docs" / "raw"  # staging area for ingestible .md files
OUTBOX_DIR = DATA / "outbox"          # sent SME notification emails (.eml)
UI_DIR = ROOT / "ui"

for _d in (LANCEDB_DIR, ESCALATIONS_DIR, FEEDBACK_DIR, ANSWERS_DIR, RAW_DOCS_DIR, OUTBOX_DIR):
    _d.mkdir(parents=True, exist_ok=True)

CHUNKS_TABLE = "chunks"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
MOCK_LLM = not bool(ANTHROPIC_API_KEY)

CLASSIFY_MODEL = os.getenv("CLASSIFY_MODEL", "claude-haiku-4-5")
FACTS_MODEL = os.getenv("FACTS_MODEL", "claude-opus-4-8")
STYLE_MODEL = os.getenv("STYLE_MODEL", "claude-opus-4-8")

EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
RERANK_MODEL = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

MAX_ANSWER_WORDS = int(os.getenv("MAX_ANSWER_WORDS", "180"))

# Deterministic, file-driven brand voice (see brand_voice.yaml)
BRAND_VOICE_FILE = Path(os.getenv("BRAND_VOICE_FILE", str(ROOT / "brand_voice.yaml")))

# Product/feature -> SME group routing (see ARCHITECTURE.md §7).
# Feature rules are matched first (tolerant substring match on the detected
# feature); the (product, None) entry is the catch-all for that product.
SME_ROUTING = {
    # Prisma Access
    ("Prisma Access", "Remote Networks"):        "Prisma Access — SASE Networking SME",
    ("Prisma Access", "Service Connection"):     "Prisma Access — SASE Networking SME",
    ("Prisma Access", "Mobile Users"):           "Prisma Access — Mobile Users SME",
    ("Prisma Access", "GlobalProtect"):          "Prisma Access — Mobile Users SME",
    ("Prisma Access", "ZTNA Connector"):         "Prisma Access — ZTNA SME",
    ("Prisma Access", "Autonomous DEM"):         "Prisma Access — ADEM SME",
    ("Prisma Access", None):                     "Prisma Access SME",
    # Cortex XDR
    ("Cortex XDR", "Behavioral Threat"):         "Cortex XDR — Threat Prevention SME",
    ("Cortex XDR", "Exploit Protection"):        "Cortex XDR — Threat Prevention SME",
    ("Cortex XDR", "Endpoint Policy"):           "Cortex XDR — Endpoint SME",
    ("Cortex XDR", "Integration"):               "Cortex XDR — Integrations SME",
    ("Cortex XDR", None):                        "Cortex XDR SME",
    # NGFW / PAN-OS
    ("NGFW", "PAN-OS Upgrade"):                  "NGFW — Platform / PAN-OS SME",
    ("NGFW", "Decryption"):                      "NGFW — Decryption SME",
    ("NGFW", "App-ID"):                          "NGFW — App-ID SME",
    ("NGFW", "GlobalProtect"):                   "NGFW — Remote Access SME",
    ("NGFW", None):                              "NGFW Platform SME",
}
DEFAULT_SME_GROUP = "General Technical SME"   # no product detected / pricing / sizing


def route_sme(product: str | None, feature: str | None) -> str:
    """Route an escalation to an SME group. Tries a tolerant feature match first,
    then the product-level catch-all, then the global default."""
    if not product:
        return DEFAULT_SME_GROUP
    feat = (feature or "").lower()
    if feat:
        for (p, f), group in SME_ROUTING.items():
            if f and p == product and (f.lower() in feat or feat in f.lower()):
                return group
    return SME_ROUTING.get((product, None), DEFAULT_SME_GROUP)


# --- Email notifications ----------------------------------------------------
# If SMTP_HOST is set, escalations are emailed via SMTP. Otherwise they are
# written to data/outbox/ as .eml files (offline mode) so the workflow is fully
# demoable without mail credentials. Set SME_NOTIFY_TO to force all mail to one
# address (handy for testing against a real inbox).
SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASS = os.getenv("SMTP_PASS", "").strip()
SMTP_FROM = os.getenv("SMTP_FROM", "knowledge-agent@paloaltonetworks-demo.com").strip()
SME_NOTIFY_TO = os.getenv("SME_NOTIFY_TO", "").strip()
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8077").rstrip("/")
EMAIL_DOMAIN = os.getenv("SME_EMAIL_DOMAIN", "sme.paloaltonetworks-demo.com").strip()

# Explicit SME group -> distribution list overrides (others are auto-slugged).
SME_EMAILS: dict[str, str] = {}


def sme_email_for(group: str) -> str:
    """Distribution-list address for an SME group. SME_NOTIFY_TO overrides all."""
    if SME_NOTIFY_TO:
        return SME_NOTIFY_TO
    if group in SME_EMAILS:
        return SME_EMAILS[group]
    import re as _re
    slug = _re.sub(r"[^a-z0-9]+", "-", group.lower()).strip("-")
    return f"{slug}@{EMAIL_DOMAIN}"
