"""Persistent ChromaDB client + collection for labeled distortion examples.

The collection lives at ``backend/data/chroma/distortions/`` and persists across
process restarts. ``rebuild_collection`` is idempotent — it drops the collection
if it exists and re-embeds the seed corpus from scratch. ``get_collection`` is
read-only and used by ``query.py``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.errors import NotFoundError

from .embed import OllamaEmbeddingFunction

COLLECTION_NAME = "distortions"

# backend/rag/distortions/store.py -> backend/
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
CHROMA_PATH = _BACKEND_ROOT / "data" / "chroma" / "distortions"


def _client() -> chromadb.PersistentClient:
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_PATH))


def get_collection() -> Collection:
    """Open the existing collection. Raises if it hasn't been seeded yet."""
    client = _client()
    return client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=OllamaEmbeddingFunction(),
    )


def rebuild_collection(examples: Iterable[dict]) -> Collection:
    """Drop and recreate the collection, then add every example.

    ``examples`` is an iterable of dicts with keys ``id``, ``label``, ``text``,
    and optionally ``explanation``. The text is what gets embedded; label and
    explanation ride along as metadata for retrieval-time use.
    """
    client = _client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except (NotFoundError, ValueError):
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=OllamaEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"},
    )

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []
    for ex in examples:
        ids.append(ex["id"])
        documents.append(ex["text"])
        metadatas.append(
            {
                "label": ex["label"],
                "explanation": ex.get("explanation") or "",
            }
        )

    if not ids:
        return collection

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return collection
