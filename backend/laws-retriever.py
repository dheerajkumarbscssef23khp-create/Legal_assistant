# laws_retriever.py

import pandas as pd
import os

# Define the dataset path
LAWS_DATASET_FILE = 'pakistan_laws_dataset.csv'
laws_df = pd.DataFrame()

def load_laws_dataset():
    """Load the CSV dataset into a pandas DataFrame."""
    global laws_df
    try:
        # Assumes the CSV is in the same directory as the script
        laws_df = pd.read_csv(LAWS_DATASET_FILE)
        # Convert columns to string for robust searching
        laws_df['Title'] = laws_df['Title'].astype(str)
        laws_df['Content'] = laws_df['Content'].astype(str)
        print(f"Successfully loaded {len(laws_df)} laws from {LAWS_DATASET_FILE}.")
    except FileNotFoundError:
        print(f"ERROR: Dataset file '{LAWS_DATASET_FILE}' not found. Local retrieval will be disabled.")
        laws_df = pd.DataFrame()
    except Exception as e:
        print(f"ERROR loading dataset: {e}")
        laws_df = pd.DataFrame()

# Load the data when the module is imported
# NOTE: Ensure you have 'pandas' installed (pip install pandas)
load_laws_dataset()


def retrieve_local_context(query: str) -> str:
    """
    Searches the local Pakistan Laws dataset (loaded from CSV).
    This simulates a vector search by performing a simple keyword/phrase search.
    """
    if laws_df.empty:
        return ""

    # Create a case-insensitive search pattern
    query_pattern = f"(?i){query}"
    
    # 1. Search for matches in Title first for high relevance
    title_match = laws_df[laws_df['Title'].str.contains(query_pattern, na=False)]
    
    # 2. If no title match, check for matches in Content
    if title_match.empty:
        content_match = laws_df[laws_df['Content'].str.contains(query_pattern, na=False)]
        top_matches = content_match.head(1)
    else:
        top_matches = title_match.head(1)
    
    if not top_matches.empty:
        law = top_matches.iloc[0]
        context = (
            f"LOCAL DATASET ENTRY: {law['Title']} (Year: {law['Year']})\n"
            f"---\n"
            f"Relevant Snippet:\n{law['Content']}\n"
            f"---\n"
        )
        return context

    # If no local match is found
    return ""


def fetch_external_law(query: str) -> str:
    """
    Simulates the external API/Search fallback.
    In your final project, you would integrate a real API here (e.g., Google Search or a legal database API).
    """
    
    print(f"--- Triggering External API Search for: {query} ---")
    
    # Simulate a successful search for a topic likely not in the simple CSV
    if "artificial intelligence" in query.lower() or "ai regulation" in query.lower():
        search_context = f"""
        EXTERNAL API SEARCH RESULT (Web Snippet for Fallback):
        The 'Regulation of Artificial Intelligence Act, 2024' is a proposed or recent legislation in Pakistan aimed at governing the use of AI, promoting an ethical AI ecosystem, and ensuring data privacy and transparency in algorithmic decision-making. The Senate of Pakistan has published drafts of this Act, indicating the country's move towards comprehensive AI regulation. (Source: Web Search/Latest News)
        """
        return search_context

    return "No relevant external search result found."


def retrieve_relevant_context(query: str) -> str:
    """
    Implements the two-step RAG logic: Local Dataset first, then API fallback.
    """
    # 1. Try the local dataset first
    local_context = retrieve_local_context(query)
    
    if local_context:
        return local_context
    
    # 2. If local dataset fails, use the external API/Search fallback
    external_context = fetch_external_law(query)
    
    if "No relevant external search result found" not in external_context:
        return external_context
    
    # 3. Final fallback: nothing found
    return "No relevant law found in the local dataset or external API for this query."