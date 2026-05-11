"""
Tests for DOCX exporter (file output check, no Word installed needed).
"""
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from docx_exporter import export_to_docx


def test_export_creates_file(tmp_path):
    draft = {"Q1. 동기": "AI로 학원 자동화를 돕고 싶습니다."}
    output = str(tmp_path / "test_output")
    result_path = export_to_docx("모두의창업", "테스트학원", draft, output)
    assert Path(result_path).exists()
    assert Path(result_path).stat().st_size > 0
