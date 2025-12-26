# Wikipedia scraping utilities
import requests
from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import quote
from backend.logger import logger


def fetch_wikipedia_article(query: str) -> tuple[Optional[str], Optional[str]]:
    try:
        # Normalize query for URL (replace spaces with underscores)
        page_title = query.replace(" ", "_")
        
        # URL encode the page title for the API
        encoded_title = quote(page_title, safe='')
        
        # First, try to get the page directly using REST API
        content_url = f"https://en.wikipedia.org/api/rest_v1/page/html/{encoded_title}"
        headers = {
            'User-Agent': 'WikiSummaryApp/1.0 (https://github.com/yourusername/wiki_summerize)'
        }
        content_response = requests.get(content_url, headers=headers, timeout=10)
        
        # If not found, try searching
        if content_response.status_code == 404:
            logger.debug(f"Direct page not found for '{query}', trying search...")
            search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'format': 'json',
                'srlimit': 1
            }
            search_response = requests.get(search_url, params=search_params, headers=headers, timeout=10)
            search_response.raise_for_status()
            search_data = search_response.json()
            
            if search_data.get("query", {}).get("search"):
                # Get the first result
                found_title = search_data["query"]["search"][0]["title"]
                page_title = found_title.replace(" ", "_")
                encoded_title = quote(page_title, safe='')
                logger.info(f"Found article via search: '{found_title}'")
                
                # Try fetching the found page
                content_url = f"https://en.wikipedia.org/api/rest_v1/page/html/{encoded_title}"
                content_response = requests.get(content_url, headers=headers, timeout=10)
            else:
                logger.warning(f"No search results found for query: {query}")
                return None, None
        
        if content_response.status_code != 200:
            logger.error(f"Failed to fetch article. Status code: {content_response.status_code}")
            return None, None
        
        # Parse HTML content
        soup = BeautifulSoup(content_response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Extract text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Get the article URL (use the actual page title found)
        # Decode if needed, but Wikipedia URLs use underscores
        article_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
        
        logger.info(f"Successfully fetched Wikipedia article: {query} -> {page_title}")
        return text, article_url
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching Wikipedia article '{query}': {e}")
        return None, None
    except Exception as e:
        logger.error(f"Error fetching Wikipedia article '{query}': {e}", exc_info=True)
        return None, None

