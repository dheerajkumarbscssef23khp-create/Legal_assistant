import os
import json 
from pathlib import Path

# --- Gemini / LLM client (safely handles import) ---
try:
    from google import genai
except ImportError:
    genai = None
    
# --- Load system prompt ---
try:
    from prompt import SYSTEM_PROMPT
except ImportError:
    SYSTEM_PROMPT = "You are an AI legal assistant. Adhere strictly to the provided CONTEXT if available."

# =========================================================================
# NOTE: Ensure GEMINI_API_KEY environment variable is set.
# =========================================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCSUDmVCw_xKDeSS2w18vKrKIUjmkmAFsc") 

# --- Gemini Client Setup ---
client = None
if genai and GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        client = None
        print(f"[WARN] Could not init Gemini client: {e}")
else:
    if not genai:
        print("[WARN] google.genai library not available in this environment.")
    if not GEMINI_API_KEY:
        print("[WARN] GEMINI_API_KEY environment variable not set.")


# --- JSON loader for data (pre-extracted from PDFs) ---
# This path points to the data derived from your PDFs.
DATA_JSON = Path(__file__).resolve().parents[1] / "data" / "pak_constitution" / "constitution.json"

def load_constitution_data():
    """Load the JSON dataset (list of dictionaries) into memory."""
    items = []
    if DATA_JSON.exists(): 
        try:
            with open(DATA_JSON, 'r', encoding='utf-8') as f:
                items = json.load(f)
            print(f"[INFO] Loaded {len(items)} documents from {DATA_JSON}.")
        except json.JSONDecodeError as e:
            print(f"[ERROR] Could not decode JSON from {DATA_JSON}: {e}")
            items = []
    else:
        print(f"[WARN] Constitution JSON file not found at {DATA_JSON}.")
    return items

# Load the data once when the module starts
constitution_data = load_constitution_data()


def search_constitution(query, top_k=5):
    """Retrieval: Searches the local, pre-extracted PDF content."""
    q = query.lower().strip()
    scored = []
    for item in constitution_data:
        # Search combines the 'file_name' and the 'text' content
        text = (item.get('file_name','') + ' ' + item.get('text','')).lower()
        score = text.count(q)
        
        # Simple scoring logic
        if score > 0 or (len(q) < 6 and q in text):
            scored.append((score, item))
            
    # Sort by score in descending order
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in scored[:top_k]]


# --- Main response generation function: RAG implementation ---
def generate_response(user_input):
    # Step 1: Attempt local search (Retrieval from 'PDF' content)
    local_results = search_constitution(user_input)
    
    context_text = ""
    source = "gemini_fallback" 
    
    if local_results:
        # If context is found locally, we prepare it for the LLM
        source = "constitution_RAG" 
        
        # Format the retrieved data into a CONTEXT block for the LLM
        context_text = "--- CONTEXT (Retrieved from Local Documents) ---\n"
        for i, item in enumerate(local_results):
            context_text += f"[{i+1}] Source Document: {item.get('file_name', 'No File Name')}\n"
            context_text += f"Content: {item.get('text', 'No text content available.')}\n---\n"
        context_text += "\n" 

    # Step 2: Fallback Check (if LLM is unavailable)
    if client is None:
        if local_results:
            raw_answer = context_text + "\n\n[ERROR: AI is offline. Above is raw context from the data.]"
        else:
            raw_answer = 'AI is unavailable. Gemini client is not configured, and no local documents were found.'
        
        return raw_answer


    # Step 3: Augment the prompt and Call Gemini (Generation)
    
    if context_text:
        # RAG Prompt: Uses local context to augment the LLM's answer
        full_prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"{context_text}"
            f"USER REQUEST: {user_input}\n\n"
            f"Based on the CONTEXT provided above, generate a concise, synthesized answer. If the context is insufficient, state that you could not find a full answer in the provided documents."
        )
    else:
        # Fallback Prompt: Asks the question to the LLM's general knowledge (API)
        full_prompt = f"{SYSTEM_PROMPT}\n\nUSER REQUEST: {user_input}"
        
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        text = getattr(response, 'text', None) or str(response)
        
    except Exception as e:
        text = f'Error: Failed to get response from Gemini. Details: {e}'
    
    # Return only the clean answer string
    return text.strip()