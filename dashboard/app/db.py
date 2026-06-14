"""LanceDB connection + table access."""
from __future__ import annotations

import lancedb

from . import config
from .models import Chunk

_db = None


def get_db():
    global _db
    if _db is None:
        _db = lancedb.connect(str(config.LANCEDB_DIR))
    return _db


def get_chunks_table(create: bool = False):
    db = get_db()
    if config.CHUNKS_TABLE in db.table_names():
        return db.open_table(config.CHUNKS_TABLE)
    if create:
        return db.create_table(config.CHUNKS_TABLE, schema=Chunk)
    raise RuntimeError(
        f"Table '{config.CHUNKS_TABLE}' not found. Run `python -m app.seed` first."
    )
