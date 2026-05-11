"""
Tests for RAG engine (no OpenAI calls).
"""
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_engine import cosine_similarity, search, ingest_document


def test_cosine_similarity_identical():
    v = [1.0, 0.0, 0.0]
    assert abs(cosine_similarity(v, v) - 1.0) < 1e-6


def test_cosine_similarity_orthogonal():
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    assert abs(cosine_similarity(a, b)) < 1e-6


def test_search_empty_db(tmp_path):
    with patch("rag_engine.VECTOR_DB_PATH", tmp_path / "test_vectors.json"), \
         patch("rag_engine.get_embedding", return_value=[0.1, 0.2, 0.3]):
        results = search("테스트 쿼리")
        assert results == []
