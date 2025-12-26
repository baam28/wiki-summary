# OpenAI summarization logic
from typing import Optional
from openai import OpenAI
import tiktoken
from backend.config import settings
from backend.logger import logger


def _get_encoding(model: str = "gpt-4o-mini"):
    try:
        # Try to get encoding for the model directly
        return tiktoken.encoding_for_model(model)
    except (KeyError, ValueError):
        # If model-specific encoding fails, try common encodings
        # GPT-4o-mini and GPT-4o can use cl100k_base encoding
        # (cl100k_base works for GPT-3.5, GPT-4, and GPT-4o variants)
        try:
            return tiktoken.get_encoding("cl100k_base")
        except ValueError:
            # Last resort: try p50k_base (older GPT models)
            try:
                return tiktoken.get_encoding("p50k_base")
            except ValueError:
                # If all else fails, raise a clear error
                raise ValueError(
                    f"Could not find a suitable encoding for model '{model}'. "
                    "Please ensure tiktoken is properly installed and up to date."
                )


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    try:
        encoding = _get_encoding(model)
        return len(encoding.encode(text))
    except Exception:
        return len(text) // 4


def truncate_to_tokens(text: str, max_tokens: int = 6000, model: str = "gpt-4o-mini") -> str:
    encoding = _get_encoding(model)
    tokens = encoding.encode(text)
    
    if len(tokens) <= max_tokens:
        return text
    
    truncated_tokens = tokens[:max_tokens]
    return encoding.decode(truncated_tokens)


def summarize_article(article_text: str, max_words: Optional[int] = None) -> Optional[str]:
    if max_words is None:
        max_words = settings.max_summary_words
    
    truncated_text = truncate_to_tokens(article_text, max_tokens=settings.max_input_tokens)
    
    client = OpenAI(api_key=settings.openai_api_key)
    
    prompt = f"""Please provide a concise summary of the following Wikipedia article in approximately {max_words} words or less. 
Focus on the main points, key facts, and important information. Write in clear, readable prose.

Article content:
{truncated_text}

Summary:"""
    
    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates clear, concise summaries of Wikipedia articles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=settings.max_output_tokens,
            temperature=settings.temperature
        )
        
        summary = response.choices[0].message.content.strip()
        return summary
        
    except Exception as e:
        logger.error(f"Error summarizing article: {e}", exc_info=True)
        return None

