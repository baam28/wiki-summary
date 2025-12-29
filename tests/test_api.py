# Tests for API endpoints
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.api import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "api_key_configured" in data


def test_summarize_endpoint_empty_query(client):
    response = client.post("/summarize", json={"query": ""})
    assert response.status_code == 422


def test_summarize_endpoint_invalid_query(client):
    with patch('backend.api.fetch_wikipedia_article') as mock_fetch:
        mock_fetch.return_value = (None, None)
        
        response = client.post(
            "/summarize",
            json={"query": "NonExistentArticle12345"}
        )
        assert response.status_code == 404


@patch('backend.api.summarize_article')
@patch('backend.api.fetch_wikipedia_article')
def test_summarize_endpoint_success(mock_fetch, mock_summarize):
    mock_fetch.return_value = ("Article text content", "https://en.wikipedia.org/wiki/Test")
    mock_summarize.return_value = "This is a test summary."
    
    client = TestClient(app)
    response = client.post("/summarize", json={"query": "Test"})
    
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "source_url" in data


def test_cache_stats_endpoint(client):
    response = client.get("/cache/stats")
    assert response.status_code == 200
    data = response.json()
    assert "enabled" in data
    assert "size" in data


def test_cache_clear_endpoint(client):
    response = client.delete("/cache/clear")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@patch('backend.api.cache.get_article')
@patch('backend.api.answer_question')
def test_chat_endpoint_success(mock_answer, mock_get_article):
    mock_get_article.return_value = "Article text content"
    mock_answer.return_value = "This is the answer."
    
    client = TestClient(app)
    response = client.post(
        "/chat",
        json={"query": "Test", "question": "What is this about?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "question" in data

