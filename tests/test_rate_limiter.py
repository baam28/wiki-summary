# Tests for rate limiter
import time
from backend.rate_limiter import RateLimiter


def test_rate_limiter_allows_requests():
    limiter = RateLimiter(requests_per_minute=10)
    
    for i in range(10):
        allowed, _ = limiter.is_allowed("test_client")
        assert allowed is True


def test_rate_limiter_blocks_excess():
    limiter = RateLimiter(requests_per_minute=2)
    
    allowed1, _ = limiter.is_allowed("test_client")
    allowed2, _ = limiter.is_allowed("test_client")
    allowed3, retry_after = limiter.is_allowed("test_client")
    
    assert allowed1 is True
    assert allowed2 is True
    assert allowed3 is False
    assert retry_after is not None


def test_rate_limiter_resets():
    limiter = RateLimiter(requests_per_minute=1)
    
    allowed1, _ = limiter.is_allowed("test_client")
    allowed2, _ = limiter.is_allowed("test_client")
    
    assert allowed1 is True
    assert allowed2 is False
    
    limiter.reset("test_client")
    allowed3, _ = limiter.is_allowed("test_client")
    assert allowed3 is True

