"""Custom exceptions for the application."""
from fastapi import HTTPException, status


class WikiSummaryException(HTTPException):
    """Base exception for Wiki Summary application."""
    pass


class ArticleNotFoundError(WikiSummaryException):
    """Raised when Wikipedia article is not found."""
    def __init__(self, query: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find Wikipedia article for query: {query}"
        )


class SummarizationError(WikiSummaryException):
    """Raised when summarization fails."""
    def __init__(self, message: str = "Failed to generate summary"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )


class ConfigurationError(WikiSummaryException):
    """Raised when configuration is invalid."""
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {message}"
        )


class RateLimitError(WikiSummaryException):
    """Raised when rate limit is exceeded."""
    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(retry_after)}
        )

