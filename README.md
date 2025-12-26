# Wiki Summary Application

A web application that fetches and summarizes Wikipedia articles using OpenAI's GPT-4o-mini model. Built with FastAPI backend and Streamlit frontend.

## Features

- Wikipedia article fetching with search fallback
- AI-powered summarization (up to 300 words)
- Interactive chat to ask questions about articles
- In-memory caching to reduce API calls
- Rate limiting to prevent abuse
- Clean, intuitive UI

## Prerequisites

- Python 3.10+ (preferably 3.11)
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <repository_url>
cd wiki_summerize
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
BACKEND_URL=http://localhost:8000
```

Optional configuration:
```env
OPENAI_MODEL=gpt-4o-mini
MAX_SUMMARY_WORDS=300
MAX_INPUT_TOKENS=6000
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=10
CACHE_ENABLED=true
CACHE_TTL_SECONDS=3600
LOG_LEVEL=INFO
```

## Usage

### Running the Backend

Start the FastAPI server:
```bash
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Running the Frontend

In a new terminal, launch the Streamlit app:
```bash
streamlit run frontend/main.py
```

Navigate to http://localhost:8501

## API Endpoints

### GET /health
Health check endpoint.

### POST /summarize
Summarize a Wikipedia article.

Request:
```json
{
  "query": "Machine Learning"
}
```

Response:
```json
{
  "query": "Machine Learning",
  "summary": "Machine learning is a subset of artificial intelligence...",
  "source_url": "https://en.wikipedia.org/wiki/Machine_learning"
}
```

### POST /chat
Ask questions about a Wikipedia article.

Request:
```json
{
  "query": "Machine Learning",
  "question": "What are the main types of machine learning?"
}
```

### GET /cache/stats
Get cache statistics.

### DELETE /cache/clear
Clear all cached summaries.

## Project Structure

```
wiki_summerize/
├── backend/
│   ├── api.py              # FastAPI application
│   ├── scraper.py          # Wikipedia scraping
│   ├── summarizer.py       # OpenAI summarization
│   ├── chat.py             # Q&A functionality
│   ├── config.py           # Configuration
│   ├── logger.py           # Logging
│   ├── exceptions.py       # Custom exceptions
│   ├── cache.py            # Caching
│   └── rate_limiter.py     # Rate limiting
├── frontend/
│   └── main.py             # Streamlit UI
├── requirements.txt
└── README.md
```

## Model

Uses GPT-4o-mini for summarization - chosen for its balance of performance, cost-efficiency, and quality. Articles are truncated to 6000 tokens to fit the context window, and summaries are limited to 300 words.

