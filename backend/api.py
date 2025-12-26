# FastAPI application
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from backend.scraper import fetch_wikipedia_article
from backend.summarizer import summarize_article
from backend.chat import answer_question
from backend.config import settings
from backend.logger import logger
from backend.exceptions import ArticleNotFoundError, SummarizationError, RateLimitError
from backend.cache import cache
from backend.rate_limiter import rate_limiter


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="API for summarizing Wikipedia articles using OpenAI GPT models"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Check configuration on startup."""
    if not settings.openai_api_key:
        logger.warning("=" * 60)
        logger.warning("WARNING: OpenAI API key is not set!")
        logger.warning("Please create a .env file with: OPENAI_API_KEY=your_key_here")
        logger.warning("Summarization and chat features will not work without an API key.")
        logger.warning("=" * 60)
    else:
        logger.info("OpenAI API key configured successfully")


def get_client_id(request: Request) -> str:
    if request.client:
        return request.client.host
    return "unknown"


def check_rate_limit(request: Request) -> None:
    client_id = get_client_id(request)
    allowed, retry_after = rate_limiter.is_allowed(client_id)
    if not allowed:
        raise RateLimitError(retry_after=retry_after or 60)


class SummarizeRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)


class SummarizeResponse(BaseModel):
    query: str
    summary: str
    source_url: str


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    question: str = Field(..., min_length=1, max_length=500)


class ChatResponse(BaseModel):
    question: str
    answer: str
    article_query: str


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": settings.api_version,
        "cache_enabled": settings.cache_enabled,
        "cache_size": cache.size(),
        "api_key_configured": bool(settings.openai_api_key)
    }


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_wikipedia(
    request: SummarizeRequest,
    client_id: str = Depends(get_client_id),
    _: None = Depends(check_rate_limit)
):
    query = request.query.strip()
    logger.info(f"Summarization request: {query}")
    
    cached_summary = cache.get(query)
    if cached_summary:
        article_text, article_url = fetch_wikipedia_article(query)
        if article_url:
            if not cache.get_article(query):
                cache.set_article(query, article_text)
            return SummarizeResponse(
                query=query,
                summary=cached_summary,
                source_url=article_url
            )
    
    article_text, article_url = fetch_wikipedia_article(query)
    
    if not article_text or not article_url:
        raise ArticleNotFoundError(query)
    
    cache.set_article(query, article_text)
    summary = summarize_article(article_text)
    
    if not summary:
        raise SummarizationError("Failed to generate summary. Please check your OpenAI API key.")
    
    cache.set(query, summary)
    
    return SummarizeResponse(
        query=query,
        summary=summary,
        source_url=article_url
    )


@app.get("/cache/stats")
async def cache_stats():
    return {
        "enabled": settings.cache_enabled,
        "size": cache.size(),
        "ttl_seconds": settings.cache_ttl_seconds
    }


@app.delete("/cache/clear")
async def clear_cache():
    cache.clear()
    return {"message": "Cache cleared successfully"}


@app.post("/chat", response_model=ChatResponse)
async def chat_about_article(
    request: ChatRequest,
    client_id: str = Depends(get_client_id),
    _: None = Depends(check_rate_limit)
):
    query = request.query.strip()
    question = request.question.strip()
    
    article_text = cache.get_article(query)
    
    if not article_text:
        article_text, article_url = fetch_wikipedia_article(query)
        if not article_text:
            raise ArticleNotFoundError(query)
        cache.set_article(query, article_text)
    
    answer = answer_question(article_text, question, query)
    
    if not answer:
        raise SummarizationError("Failed to generate answer. Please check your OpenAI API key.")
    
    return ChatResponse(
        question=question,
        answer=answer,
        article_query=query
    )


@app.exception_handler(ArticleNotFoundError)
@app.exception_handler(SummarizationError)
@app.exception_handler(RateLimitError)
async def custom_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

