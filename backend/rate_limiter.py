"""Rate limiting utilities."""
import time
from collections import defaultdict
from typing import Optional
from backend.config import settings
from backend.exceptions import RateLimitError
from backend.logger import logger


class RateLimiter:
    """Simple rate limiter using sliding window."""
    
    def __init__(self, requests_per_minute: int = 10):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[float]] = defaultdict(list)
    
    def _clean_old_requests(self, client_id: str, current_time: float) -> None:
        """Remove requests older than 1 minute."""
        minute_ago = current_time - 60
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
    
    def is_allowed(self, client_id: str = "default") -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed.
        
        Args:
            client_id: Client identifier (can use IP address in production)
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        if not settings.rate_limit_enabled:
            return True, None
        
        current_time = time.time()
        self._clean_old_requests(client_id, current_time)
        
        if len(self.requests[client_id]) >= self.requests_per_minute:
            # Calculate retry after
            oldest_request = min(self.requests[client_id])
            retry_after = int(60 - (current_time - oldest_request)) + 1
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return False, retry_after
        
        self.requests[client_id].append(current_time)
        return True, None
    
    def reset(self, client_id: str) -> None:
        """Reset rate limit for a client."""
        if client_id in self.requests:
            del self.requests[client_id]


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=settings.rate_limit_per_minute)

