# Tests for cache
import time
from backend.cache import SimpleCache


def test_cache_set_and_get():
    cache = SimpleCache(ttl_seconds=3600)
    cache.set("test_query", "test_summary")
    
    result = cache.get("test_query")
    assert result == "test_summary"


def test_cache_expiration():
    cache = SimpleCache(ttl_seconds=1)
    cache.set("test_query", "test_summary")
    
    time.sleep(2)
    
    result = cache.get("test_query")
    assert result is None


def test_cache_article():
    cache = SimpleCache(ttl_seconds=3600)
    cache.set_article("test_query", "full article text")
    
    result = cache.get_article("test_query")
    assert result == "full article text"


def test_cache_clear():
    cache = SimpleCache(ttl_seconds=3600)
    cache.set("query1", "summary1")
    cache.set_article("query1", "article1")
    
    cache.clear()
    
    assert cache.get("query1") is None
    assert cache.get_article("query1") is None
    assert cache.size() == 0


def test_cache_size():
    cache = SimpleCache(ttl_seconds=3600)
    assert cache.size() == 0
    
    cache.set("query1", "summary1")
    assert cache.size() == 1
    
    cache.set("query2", "summary2")
    assert cache.size() == 2

