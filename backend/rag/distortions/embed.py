"""Local Ollama embedding function for the distortions collection.

Wraps `ollama.embed` so it satisfies Chroma's `EmbeddingFunction` protocol. The
function is intentionally tiny: it batches by calling Ollama once per document,
which is fine for the ~150-doc seed corpus and avoids depending on Ollama's
batch behavior across versions.

There is no cloud fallback. If Ollama isn't running or the model isn't pulled,
the call raises and the seeder fails loudly.
"""

from __future__ import annotations

from typing import Any, Dict, List

import ollama
from chromadb import Documents, EmbeddingFunction, Embeddings

DEFAULT_EMBED_MODEL = "nomic-embed-text"


class OllamaEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self, model: str = DEFAULT_EMBED_MODEL) -> None:
        self._model = model

    def __call__(self, input: Documents) -> Embeddings:
        vectors: List[List[float]] = []
        for doc in input:
            resp = ollama.embed(model=self._model, input=doc)
            vectors.append(list(resp["embeddings"][0]))
        return vectors

    @staticmethod
    def name() -> str:
        return "ollama"

    def get_config(self) -> Dict[str, Any]:
        return {"model": self._model}

    @staticmethod
    def build_from_config(config: Dict[str, Any]) -> "OllamaEmbeddingFunction":
        return OllamaEmbeddingFunction(model=config.get("model", DEFAULT_EMBED_MODEL))

    def default_space(self) -> str:
        return "cosine"
