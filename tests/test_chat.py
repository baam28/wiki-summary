# Tests for chat functionality
import pytest
from unittest.mock import patch, Mock
from backend.chat import answer_question


@patch('backend.chat.OpenAI')
def test_answer_question_success(mock_openai):
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "This is the answer to your question."
    mock_response.usage = Mock()
    mock_response.usage.completion_tokens = 30
    
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    result = answer_question("Article content here", "What is this about?", "Test Article")
    
    assert result is not None
    assert "answer" in result.lower()


@patch('backend.chat.OpenAI')
def test_answer_question_error(mock_openai):
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_openai.return_value = mock_client
    
    result = answer_question("Article content", "Question?", "Test")
    
    assert result is None

