"""
Sanity tests for hagwon message generator.
Does not call OpenAI API — mocks the response.
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from message_generator import generate_alimtalk, EVENT_TEMPLATES


def _mock_openai_response(text: str):
    mock = MagicMock()
    mock.choices[0].message.content = text
    return mock


def test_event_templates_defined():
    assert "attendance" in EVENT_TEMPLATES
    assert "homework" in EVENT_TEMPLATES
    assert "progress" in EVENT_TEMPLATES


def test_generate_alimtalk_returns_string():
    with patch("message_generator.client") as mock_client:
        mock_client.chat.completions.create.return_value = _mock_openai_response(
            "[학원명] 안녕하세요. 오늘 김민준 학생이 결석하였습니다."
        )
        result = generate_alimtalk("attendance", "김민준", {"status": "결석"})
        assert isinstance(result, str)
        assert len(result) > 0


def test_generate_alimtalk_under_90_chars():
    with patch("message_generator.client") as mock_client:
        mock_client.chat.completions.create.return_value = _mock_openai_response(
            "오늘 수업 잘 들었어요!"
        )
        result = generate_alimtalk("progress", "박서연", {"subject": "영어"})
        assert len(result) <= 90
