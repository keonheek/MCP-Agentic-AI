"""
Tests for draft generator (mocked GPT-4o).
"""
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def _mock_gpt(text: str):
    mock = MagicMock()
    mock.choices[0].message.content = text
    return mock


def test_generate_draft_returns_all_questions():
    with patch("draft_generator.client") as mock_client, \
         patch("draft_generator.search", return_value=[]):
        mock_client.chat.completions.create.return_value = _mock_gpt("테스트 답변입니다.")
        from draft_generator import generate_draft, STANDARD_QUESTIONS
        result = generate_draft("모두의창업", {"business_idea": "AI 자동화"})
        expected_questions = STANDARD_QUESTIONS["모두의창업"]
        assert len(result) == len(expected_questions)
        for q in expected_questions:
            assert q in result


def test_generate_draft_unknown_program():
    with patch("draft_generator.client") as mock_client, \
         patch("draft_generator.search", return_value=[]):
        mock_client.chat.completions.create.return_value = _mock_gpt("답변")
        from draft_generator import generate_draft
        result = generate_draft("미지의프로그램", {"business_idea": "테스트"})
        assert len(result) > 0
