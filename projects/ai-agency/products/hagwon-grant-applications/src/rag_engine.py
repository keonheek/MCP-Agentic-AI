"""
RAG engine for government grant application drafting.
Uses custom cosine similarity VectorDB (no ChromaDB).
Pattern: OpenAI text-embedding-3-small + JSON persistence.
"""
import os
import json
import numpy as np
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

DATA_DIR = Path(__file__).parent.parent / "data"
VECTOR_DB_PATH = DATA_DIR / "grant_vectors.json"


def cosine_similarity(a: list, b: list) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def get_embedding(text: str) -> list:
    resp = client.embeddings.create(input=text, model="text-embedding-3-small")
    return resp.data[0].embedding


def _load_db() -> list:
    if VECTOR_DB_PATH.exists():
        return json.loads(VECTOR_DB_PATH.read_text(encoding="utf-8"))
    return []


def _save_db(db: list) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_DB_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")


def ingest_document(doc_id: str, text: str, metadata: dict) -> None:
    """Add a grant application document to the vector DB."""
    db = _load_db()
    existing_ids = {d["id"] for d in db}
    if doc_id in existing_ids:
        return  # idempotent

    embedding = get_embedding(text[:8000])  # truncate for embedding limit
    db.append({
        "id": doc_id,
        "text": text,
        "embedding": embedding,
        "metadata": metadata,
    })
    _save_db(db)


def search(query: str, top_k: int = 3) -> list:
    """Return top_k most similar grant documents."""
    db = _load_db()
    if not db:
        return []

    query_embedding = get_embedding(query)
    scored = [
        (cosine_similarity(query_embedding, doc["embedding"]), doc)
        for doc in db
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]
