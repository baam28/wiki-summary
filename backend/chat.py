# Chat/Q&A functionality for Wikipedia articles
from typing import Optional
from openai import OpenAI
from backend.config import settings
from backend.logger import logger
from backend.summarizer import truncate_to_tokens, count_tokens


def answer_question(article_text: str, question: str, article_title: str = "") -> Optional[str]:
    # Truncate article to fit context window (leave room for question and response)
    truncated_text = truncate_to_tokens(article_text, max_tokens=settings.max_input_tokens - 500)
    
    input_tokens = count_tokens(truncated_text)
    logger.info(f"Answering question with {input_tokens} input tokens from article: {article_title}")
    
    client = OpenAI(api_key=settings.openai_api_key)
    
    system_prompt = """You are a helpful assistant that answers questions based ONLY on the provided Wikipedia article content. 
If the question cannot be answered from the article, politely state that the information is not available in this article.
Do not use any external knowledge - only use information from the article text provided."""
    
    user_prompt = f"""Based on the following Wikipedia article{' about ' + article_title if article_title else ''}, please answer this question:

Question: {question}

Article content:
{truncated_text}

Answer (based only on the article above):"""
    
    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=settings.max_output_tokens,
            temperature=0.3  # Lower temperature for more factual answers
        )
        
        answer = response.choices[0].message.content.strip()
        output_tokens = response.usage.completion_tokens if response.usage else 0
        logger.info(f"Generated answer with {output_tokens} tokens")
        return answer
        
    except Exception as e:
        logger.error(f"Error answering question: {e}", exc_info=True)
        return None

