# Streamlit frontend
import streamlit as st
import requests
import os
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Initialize session state
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = {}


def check_backend_health() -> bool:
    """Check if backend is available."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def get_backend_health() -> Optional[dict]:
    """Get backend health status."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def get_backend_health() -> Optional[dict]:
    """Get backend health status."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def get_summary(query: str) -> Optional[dict]:
    """Fetch summary from backend API."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/summarize",
            json={"query": query},
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        # Try to get error detail from JSON response
        error_detail = "Unknown error"
        if e.response is not None:
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e))
            except (ValueError, requests.exceptions.JSONDecodeError):
                # If response is not JSON, use status text or response text
                error_detail = e.response.text or e.response.reason or str(e)
        
        if e.response and e.response.status_code == 429:
            st.error("Rate limit exceeded. Please wait a moment and try again.")
            retry_after = e.response.headers.get("Retry-After", "60")
            st.info(f"Retry after {retry_after} seconds")
        elif e.response and e.response.status_code == 404:
            st.error(f"{error_detail}")
        else:
            st.error(f"Error: {error_detail}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None


def get_cache_stats() -> Optional[dict]:
    """Get cache statistics from backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/cache/stats", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def ask_question(article_query: str, question: str) -> Optional[dict]:
    """Ask a question about the Wikipedia article."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"query": article_query, "question": question},
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        # Try to get error detail from JSON response
        error_detail = "Unknown error"
        if e.response is not None:
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e))
            except (ValueError, requests.exceptions.JSONDecodeError):
                # If response is not JSON, use status text or response text
                error_detail = e.response.text or e.response.reason or str(e)
        
        if e.response and e.response.status_code == 429:
            st.error("Rate limit exceeded. Please wait a moment and try again.")
            retry_after = e.response.headers.get("Retry-After", "60")
            st.info(f"Retry after {retry_after} seconds")
        elif e.response and e.response.status_code == 404:
            st.error(f"{error_detail}")
        else:
            st.error(f"Error: {error_detail}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None


# Page configuration
st.set_page_config(
    page_title="Wiki Summary",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        .stApp > header {
            background-color: transparent;
        }
        .stApp {
            margin-top: -80px;
        }
    </style>
""", unsafe_allow_html=True)

# Check backend connection
if not check_backend_health():
    st.error("Backend API is not available. Please make sure the FastAPI server is running.")
    st.info(f"Expected backend URL: {BACKEND_URL}")
    st.code("uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000", language="bash")
    st.stop()

# Check API key configuration
health_data = get_backend_health()
if health_data and not health_data.get("api_key_configured", False):
    st.warning("OpenAI API key is not configured. Please create a `.env` file with your API key.")
    with st.expander("How to configure API key"):
        st.markdown("""
        1. Create a `.env` file in the project root directory
        2. Add the following line:
        ```
        OPENAI_API_KEY=sk-your-api-key-here
        ```
        3. Restart the backend server
        
        Get your API key from: https://platform.openai.com/api-keys
        """)
    st.info("The application will start, but summarization and chat features will not work without an API key.")

# Main title
st.title("Wiki Summary")
st.markdown("Enter a Wikipedia search query to get an AI-generated summary (up to 300 words).")

# Search section
with st.container():
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input(
            "Search Query",
            placeholder="e.g., Python programming, Machine Learning, Quantum Computing",
            help="Enter a topic or article name to search on Wikipedia",
            label_visibility="collapsed"
        )
    with col2:
        search_button = st.button("Get Summary", use_container_width=True, type="primary")

# Process search
if search_button:
    if not search_query or not search_query.strip():
        st.warning("Please enter a search query.")
    else:
        query = search_query.strip()
        with st.spinner("Fetching and summarizing article... This may take a few seconds."):
            result = get_summary(query)
            
            if result:
                # Add to history
                search_entry = {
                    "query": result["query"],
                    "summary": result["summary"],
                    "source_url": result["source_url"],
                    "timestamp": datetime.now().isoformat()
                }
                # Avoid duplicates
                if search_entry not in st.session_state.search_history:
                    st.session_state.search_history.append(search_entry)
                
                st.session_state.current_result = result
                st.rerun()

# Main content area - split into two columns
if st.session_state.current_result:
    result = st.session_state.current_result
    article_query = result['query']
    
    # Initialize chat messages for this article if not exists
    if article_query not in st.session_state.chat_messages:
        st.session_state.chat_messages[article_query] = []
    
    # Create two columns: Summary on left, Chat on right
    left_col, right_col = st.columns([1.2, 1])
    
    # Left column: Summary
    with left_col:
        st.markdown("---")
        st.subheader(f"Summary: {result['query']}")
        
        # Summary text
        st.write(result["summary"])
        
        # Metadata
        col1, col2 = st.columns(2)
        with col1:
            word_count = len(result["summary"].split())
            st.metric("Words", word_count)
        with col2:
            st.markdown(f"[View Source Article]({result['source_url']})")
        
        # Clear/New search button
        if st.button("New Search", use_container_width=True):
            st.session_state.current_result = None
            st.rerun()
    
    # Right column: Chat
    with right_col:
        st.markdown("---")
        st.subheader("Ask Questions")
        st.caption("Ask questions about this article. Answers are based only on the article content.")
        
        # Chat container with scrollable area
        chat_container = st.container()
        with chat_container:
            # Display chat history
            if st.session_state.chat_messages[article_query]:
                for msg in st.session_state.chat_messages[article_query]:
                    if msg["role"] == "user":
                        with st.chat_message("user"):
                            st.write(msg["content"])
                    else:
                        with st.chat_message("assistant"):
                            st.write(msg["content"])
            else:
                st.info("No questions yet. Ask a question about the article above.")
        
        # Chat input
        user_question = st.chat_input("Ask a question about this article...")
        
        if user_question:
            # Add user message to chat
            st.session_state.chat_messages[article_query].append({
                "role": "user",
                "content": user_question
            })
            
            # Get answer from backend
            with st.spinner("Thinking..."):
                chat_response = ask_question(article_query, user_question)
                
                if chat_response:
                    answer = chat_response.get("answer", "Sorry, I couldn't generate an answer.")
                    # Add assistant message to chat
                    st.session_state.chat_messages[article_query].append({
                        "role": "assistant",
                        "content": answer
                    })
                    st.rerun()
        
        # Clear chat button
        if st.session_state.chat_messages[article_query]:
            if st.button("Clear Chat", use_container_width=True, key="clear_chat"):
                st.session_state.chat_messages[article_query] = []
                st.rerun()

else:
    # No result yet - show search history if available
    if st.session_state.search_history:
        st.markdown("---")
        st.subheader("Recent Searches")
        cols = st.columns(min(3, len(st.session_state.search_history)))
        for idx, item in enumerate(reversed(st.session_state.search_history[-6:])):
            with cols[idx % 3]:
                if st.button(item['query'], use_container_width=True, key=f"history_{idx}"):
                    st.session_state.current_result = {
                        "query": item['query'],
                        "summary": item['summary'],
                        "source_url": item['source_url']
                    }
                    st.rerun()

# Footer
st.markdown("---")
st.caption("Powered by FastAPI, Streamlit, and OpenAI GPT-4o-mini")
