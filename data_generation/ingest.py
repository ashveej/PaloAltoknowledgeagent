# NOTE: runnable source of truth is dashboard/app/ingest.py. Run via: cd dashboard && python -m app.ingest --reset

"""Real ingestion: read Markdown-with-frontmatter docs from data/docs/raw/,
chunk them by section, and embed into LanceDB.

Each source file looks like:

    ---
    source_id: PA-REMOTE-NETWORKS-ONBOARD
    title: Onboard a Remote Network
    url: https://docs.paloaltonetworks.com/...
    source_type: official_documentation   # or release_notes / security_advisory
    product: Prisma Access
    feature: Remote Networks
    version: 5.0                           # optional; "" if version-neutral
    last_reviewed_date: 2026-01-15         # optional; defaults to today
    ---

    # Heading
    body text...

Run:  python -m app.ingest            # append to existing table
      python -m app.ingest --reset    # rebuild table from scratch
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

import yaml

from . import config
from .db import get_db
from .models import Chunk

MAX_WORDS = 220   # target chunk size
MIN_WORDS = 25    # drop tiny fragments


# --------------------------- frontmatter parsing --------------------------- #
def parse_frontmatter(raw: str) -> tuple[dict, str]:
    meta: dict = {}
    body = raw
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            block = raw[3:end].strip()
            body = raw[end + 4:].lstrip("\n")
            for line in block.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


# ------------------------------- PDF reading ------------------------------- #
def _load_sidecar(pdf_path: Path) -> dict:
    """Metadata for a PDF: <stem>.yaml or <stem>.json next to it (optional).
    Values are coerced to strings (YAML auto-parses dates/numbers, but the chunk
    schema is all-string)."""
    for ext in (".yaml", ".yml", ".json"):
        side = pdf_path.with_suffix(ext)
        if side.exists():
            raw = side.read_text(encoding="utf-8")
            data = yaml.safe_load(raw) if ext != ".json" else json.loads(raw)
            return {k: ("" if v is None else str(v)) for k, v in (data or {}).items()}
    return {}


def read_pdf(pdf_path: Path) -> tuple[dict, str]:
    """Extract text per page -> a markdown body (one ## section per page) plus
    metadata from an optional sidecar."""
    from pypdf import PdfReader

    meta = _load_sidecar(pdf_path)
    meta.setdefault("source_id", _slug(pdf_path.stem).upper())
    meta.setdefault("title", pdf_path.stem.replace("-", " ").title())
    meta.setdefault("source_type", "official_documentation")

    reader = PdfReader(str(pdf_path))
    parts = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            parts.append(f"## Page {i}\n{text}")
    return meta, "\n\n".join(parts)


# ------------------------------- chunking ---------------------------------- #
def chunk_markdown(body: str) -> list[tuple[str, str]]:
    """Split into (section_title, text) by headings, then by size."""
    sections: list[tuple[str, list[str]]] = []
    current_title = "Overview"
    current: list[str] = []
    for line in body.splitlines():
        if re.match(r"^#{1,6}\s", line):
            if current:
                sections.append((current_title, current))
            current_title = re.sub(r"^#{1,6}\s", "", line).strip()
            current = []
        else:
            current.append(line)
    if current:
        sections.append((current_title, current))

    chunks: list[tuple[str, str]] = []
    for title, lines in sections:
        text = "\n".join(lines).strip()
        if not text:
            continue
        words = text.split()
        if len(words) <= MAX_WORDS:
            if len(words) >= MIN_WORDS:
                chunks.append((title, text))
            continue
        # split oversized sections into word windows
        for i in range(0, len(words), MAX_WORDS):
            piece = " ".join(words[i:i + MAX_WORDS])
            if len(piece.split()) >= MIN_WORDS:
                chunks.append((title, piece))
    return chunks


# ------------------------------- ingestion --------------------------------- #
def build_chunks(meta: dict, body: str) -> list[dict]:
    source_id = meta.get("source_id") or _slug(meta.get("title", "doc"))
    url = meta.get("url", "")
    rows = []
    for n, (section_title, text) in enumerate(chunk_markdown(body), start=1):
        rows.append({
            "chunk_id": f"{source_id}#chunk-{n:03d}",
            "text": text,
            "source_id": source_id,
            "source_title": meta.get("title", source_id),
            "section_title": section_title,
            "anchor_url": f"{url}#{_slug(section_title)}" if url else url,
            "product": meta.get("product", ""),
            "feature": meta.get("feature", ""),
            "version": meta.get("version", ""),
            "source_type": meta.get("source_type", "official_documentation"),
            "approval_status": "approved",
            "last_reviewed_date": meta.get("last_reviewed_date") or date.today().isoformat(),
            "deprecated": str(meta.get("deprecated", "")).lower() == "true",
            "upvotes": 0,
            "downvotes": 0,
        })
    return rows


def ingest(reset: bool = False) -> dict:
    files = sorted([p for p in config.RAW_DOCS_DIR.glob("*")
                    if p.suffix.lower() in (".md", ".pdf")])
    if not files:
        return {"files": 0, "chunks": 0, "sources": [],
                "note": "no .md or .pdf files in staging"}

    all_rows: list[dict] = []
    sources: list[str] = []
    for f in files:
        if f.suffix.lower() == ".pdf":
            meta, body = read_pdf(f)
        else:
            meta, body = parse_frontmatter(f.read_text(encoding="utf-8"))
        rows = build_chunks(meta, body)
        if rows:
            all_rows.extend(rows)
            sources.append(f"{meta.get('source_id', f.stem)} [{f.suffix.lstrip('.')}]"
                           f" ({len(rows)} chunks)")

    db = get_db()
    if reset or config.CHUNKS_TABLE not in db.list_tables():
        table = db.create_table(config.CHUNKS_TABLE, schema=Chunk,
                                mode="overwrite" if reset else "create")
    else:
        table = db.open_table(config.CHUNKS_TABLE)
    if all_rows:
        table.add(all_rows)

    return {"files": len(files), "chunks": len(all_rows), "sources": sources}


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    result = ingest(reset=reset)
    print(f"Ingested {result['chunks']} chunks from {result['files']} files "
          f"(reset={reset}).")
    for s in result["sources"]:
        print("  -", s)
