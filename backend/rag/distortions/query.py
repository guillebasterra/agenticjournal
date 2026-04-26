"""Public retrieval API for the distortions collection.

Downstream worktrees (the dual-retrieval orchestrator) call ``query_distortions``
and treat the returned list as opaque ``RetrievedDistortionExample`` objects.
"""

from __future__ import annotations

from typing import cast

from schemas import DistortionLabel, RetrievedDistortionExample

from .store import get_collection


def query_distortions(text: str, k: int = 5) -> list[RetrievedDistortionExample]:
    """Return the top-k labeled examples most similar to ``text``.

    ``score`` is a cosine similarity in [0, 1] (1 = identical direction). The
    collection is configured with ``hnsw:space=cosine``; Chroma reports the
    distance, so we convert with ``1 - distance`` and clamp.
    """
    if k <= 0:
        return []

    collection = get_collection()
    result = collection.query(
        query_texts=[text],
        n_results=k,
    )

    ids = (result.get("ids") or [[]])[0]
    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    out: list[RetrievedDistortionExample] = []
    for i, doc_id in enumerate(ids):
        meta = metadatas[i] or {}
        distance = distances[i] if i < len(distances) else 1.0
        similarity = max(0.0, min(1.0, 1.0 - float(distance)))
        out.append(
            RetrievedDistortionExample(
                id=doc_id,
                label=cast(DistortionLabel, meta.get("label")),
                text=documents[i],
                explanation=(meta.get("explanation") or None),
                score=similarity,
            )
        )
    return out
