# Caching utilities
import hashlib
import time
from typing import Optional
from backend.config import settings
from backend.logger import logger


class SimpleCache:
    """Simple in-memory cache with TTL."""
    
    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize cache.
        
        Args:
            ttl_seconds: Time to live in seconds
        """
        self.cache: dict[str, tuple[any, float]] = {}
        self.article_cache: dict[str, tuple[str, float]] = {}  # Cache for full article text
        self.ttl = ttl_seconds
    
    def _generate_key(self, query: str) -> str:
        """Generate cache key from query."""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def get(self, query: str) -> Optional[str]:
        """
        Get cached summary.
        
        Args:
            query: Search query
            
        Returns:
            Cached summary or None
        """
        if not settings.cache_enabled:
            return None
        
        key = self._generate_key(query)
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                logger.debug(f"Cache hit for query: {query}")
                return value
            else:
                # Expired, remove it
                del self.cache[key]
                logger.debug(f"Cache expired for query: {query}")
        
        return None
    
    def set(self, query: str, summary: str) -> None:
        """
        Cache a summary.
        
        Args:
            query: Search query
            summary: Summary to cache
        """
        if not settings.cache_enabled:
            return
        
        key = self._generate_key(query)
        self.cache[key] = (summary, time.time())
        logger.debug(f"Cached summary for query: {query}")
    
    def get_article(self, query: str) -> Optional[str]:
        """
        Get cached article text.
        
        Args:
            query: Search query
            
        Returns:
            Cached article text or None
        """
        if not settings.cache_enabled:
            return None
        
        key = self._generate_key(query)
        if key in self.article_cache:
            value, timestamp = self.article_cache[key]
            if time.time() - timestamp < self.ttl:
                logger.debug(f"Article cache hit for query: {query}")
                return value
            else:
                del self.article_cache[key]
        
        return None
    
    def set_article(self, query: str, article_text: str) -> None:
        """
        Cache article text.
        
        Args:
            query: Search query
            article_text: Full article text to cache
        """
        if not settings.cache_enabled:
            return
        
        key = self._generate_key(query)
        self.article_cache[key] = (article_text, time.time())
        logger.debug(f"Cached article text for query: {query}")
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()
        self.article_cache.clear()
        logger.info("Cache cleared")
    
    def size(self) -> int:
        """Get number of cached entries."""
        return len(self.cache)


# Global cache instance
cache = SimpleCache(ttl_seconds=settings.cache_ttl_seconds)

