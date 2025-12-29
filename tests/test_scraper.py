# Tests for Wikipedia scraper
import pytest
from unittest.mock import patch, Mock
from backend.scraper import fetch_wikipedia_article


@patch('backend.scraper.requests.get')
def test_fetch_wikipedia_article_success(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '<html><body><p>Test article content</p></body></html>'
    mock_get.return_value = mock_response
    
    text, url = fetch_wikipedia_article("Python")
    
    assert text is not None
    assert url is not None
    assert "Python" in url or "python" in url.lower()
    assert len(text) > 0


@patch('backend.scraper.requests.get')
def test_fetch_wikipedia_article_not_found(mock_get):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    
    # Mock search that returns no results
    with patch('backend.scraper.requests.get') as mock_search:
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {"query": {"search": []}}
        mock_search.return_value = search_response
        
        text, url = fetch_wikipedia_article("NonExistentArticle12345")
        assert text is None or url is None


@patch('backend.scraper.requests.get')
def test_fetch_wikipedia_article_search_fallback(mock_get):
    # First request returns 404
    mock_404 = Mock()
    mock_404.status_code = 404
    
    # Search returns a result
    mock_search = Mock()
    mock_search.status_code = 200
    mock_search.json.return_value = {
        "query": {
            "search": [{"title": "Machine Learning"}]
        }
    }
    
    # Second request (with found title) returns 200
    mock_200 = Mock()
    mock_200.status_code = 200
    mock_200.text = '<html><body><p>Machine learning content</p></body></html>'
    
    mock_get.side_effect = [mock_404, mock_search, mock_200]
    
    text, url = fetch_wikipedia_article("machine learning")
    assert text is not None
    assert url is not None

