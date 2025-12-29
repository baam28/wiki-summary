# Tests for summarizer
import pytest
from unittest.mock import patch, Mock
from backend.summarizer import count_tokens, truncate_to_tokens


def test_count_tokens():
    text = "This is a test sentence."
    tokens = count_tokens(text)
    assert tokens > 0
    assert isinstance(tokens, int)


def test_truncate_to_tokens():
    long_text = "This is a test. " * 1000
    
    truncated = truncate_to_tokens(long_text, max_tokens=100)
    tokens = count_tokens(truncated)
    
    assert tokens <= 100
    assert len(truncated) < len(long_text)


def test_truncate_short_text():
    short_text = "This is short."
    truncated = truncate_to_tokens(short_text, max_tokens=1000)
    
    assert truncated == short_text


@patch('backend.summarizer.OpenAI')
def test_summarize_article(mock_openai):
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "This is a test summary."
    mock_response.usage = Mock()
    mock_response.usage.completion_tokens = 50
    
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    from backend.summarizer import summarize_article
    
    result = summarize_article("Test article content here")
    assert result is not None
    assert "test summary" in result.lower()

