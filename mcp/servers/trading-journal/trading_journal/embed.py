"""Optional Qdrant embedding layer for semantic journal search.

If QDRANT_URL is not set, all functions are no-ops and `enabled` is False.
Embeddings come from Ollama's `nomic-embed-text` model so we don't need an
extra paid embeddings provider.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any

import httpx

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qm
except ImportError:  # pragma: no cover
    QdrantClient = None  # type: ignore
    qm = None  # type: ignore


COLLECTION = "neurotrader_journal"
EMBED_DIM = 768  # nomic-embed-text output


class Embedder:
    def __init__(self, url: str | None, api_key: str | None) -> None:
        self.enabled = bool(url) and QdrantClient is not None
        if not self.enabled:
            self._client = None
            return
        self._client = QdrantClient(url=url, api_key=api_key)
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        cols = {c.name for c in self._client.get_collections().collections}
        if COLLECTION not in cols:
            self._client.create_collection(
                collection_name=COLLECTION,
                vectors_config=qm.VectorParams(size=EMBED_DIM, distance=qm.Distance.COSINE),
            )

    def _embed(self, text: str) -> list[float]:
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        r = httpx.post(
            f"{host}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text},
            timeout=30.0,
        )
        r.raise_for_status()
        return r.json()["embedding"]

    def upsert(self, doc_id: str, text: str, payload: dict[str, Any]) -> None:
        if not self.enabled:
            return
        vec = self._embed(text)
        # qdrant point ids must be int or uuid; hash to int.
        pid = int(hashlib.sha1(doc_id.encode()).hexdigest()[:15], 16)
        self._client.upsert(
            collection_name=COLLECTION,
            points=[qm.PointStruct(id=pid, vector=vec, payload={"doc_id": doc_id, **payload})],
        )

    def search(self, query: str, k: int = 5) -> list[dict]:
        if not self.enabled:
            return []
        vec = self._embed(query)
        hits = self._client.search(collection_name=COLLECTION, query_vector=vec, limit=k)
        return [{"score": h.score, **h.payload} for h in hits]
