import chromadb
import os
import google.generativeai as genai
from googleapiclient.discovery import build

# --- Configuration ---
CHROMA_DB_PATH = "./chroma_db_data"

# Google Gemini API Key
GEMINI_API_KEY = "AIzaSyBPtUpfMu9S-nAgPS1SpnFYwnL1Ni0K7dE"

# Google Custom Search API Credentials
GOOGLE_API_KEY = "AIzaSyDhQRS0tccUHDoGMlxl7OUccsvDVcKqkkQ"
GOOGLE_CSE_ID = "336fd9d8ab2a34781" # Keep your actual CX ID here

# Configure the Google Generative AI client
if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY":
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY is not set or is default. LLM recommendations will not function.")

if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY" or \
   not GOOGLE_CSE_ID or GOOGLE_CSE_ID == "YOUR_GOOGLE_CSE_ID": # Corrected the typo here!
    print("WARNING: Google Search API keys not fully configured. Google Search integration will not function without them.")


# --- 1. Connect to Chroma DB ---
def get_chroma_client():
    """Establishes and returns a Chroma DB client connection."""
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        print(f"Successfully connected to Chroma DB. Data loaded from: {CHROMA_DB_PATH}")
        return client
    except Exception as e:
        print(f"Error connecting to Chroma DB: {e}")
        return None

# --- 2. Function to Search Research Papers in Chroma DB ---
def search_papers(client, collection_name, query_text, n_results=3):
    """
    Searches the Chroma DB collection for research papers relevant to the query.
    Returns a list of dictionaries with paper details, including full_content.
    """
    collection = client.get_or_create_collection(name=collection_name)
    print(f"\nSearching '{collection_name}' for: '{query_text}'...")

    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )

        relevant_papers = []
        if results and results['documents']:
            for i in range(len(results['documents'][0])):
                doc_content = results['documents'][0][i]
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]

                relevant_papers.append({
                    "title": metadata.get('title', 'N/A'),
                    "filename": metadata.get('filename', 'N/A'),
                    "full_content": doc_content,
                    "relevance_distance": distance
                })
            print(f"Found {len(relevant_papers)} relevant papers in Chroma DB.")
            return relevant_papers
        else:
            print("No relevant papers found in Chroma DB for this query.")
            return []
    except Exception as e:
        print(f"Error during Chroma DB search: {e}")
        return []

# --- 3. Google Custom Search API Integration Function ---
def google_search(query, num_results=3):
    """
    Performs a Google Custom Search for a given query.
    Requires GOOGLE_API_KEY and GOOGLE_CSE_ID to be set.
    """
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY" or \
       not GOOGLE_CSE_ID or GOOGLE_CSE_ID == "YOUR_GOOGLE_CSE_ID": # Corrected here!
        print("Google Search API keys are not configured or are default. Skipping Google search.")
        return []

    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        res = service.cse().list(q=query, cx=GOOGLE_CSE_ID, num=num_results).execute()

        search_results = []
        if 'items' in res:
            for item in res['items']:
                search_results.append({
                    "title": item.get('title'),
                    "link": item.get('link'),
                    "snippet": item.get('snippet')
                })
        print(f"Found {len(search_results)} results from Google Search.")
        return search_results
    except Exception as e:
        print(f"Error during Google Search: {e}")
        return []

# --- 4. Function to Generate Recommendation with LLM ---
def generate_recommendation_with_llm(user_query, retrieved_papers_content, google_search_results=None):
    """
    Uses an LLM (Gemini) to generate a recommendation based on the user's query,
    the content of retrieved relevant papers, and optionally Google search results.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        return "LLM API key not configured. Cannot generate recommendation."

    context_papers = "\n\n".join([paper['full_content'] for paper in retrieved_papers_content])

    context_google_search = ""
    if google_search_results:
        context_google_search = "\n\n--- Online Search Results ---\n"
        for i, result in enumerate(google_search_results):
            context_google_search += f"Result {i+1}:\n"
            context_google_search += f"Title: {result.get('title', 'N/A')}\n"
            context_google_search += f"Link: {result.get('link', 'N/A')}\n"
            context_google_search += f"Snippet: {result.get('snippet', 'N/A')}\n\n"


    prompt = f"""
You are an AI assistant specializing in medical countermeasures for astronauts in space missions.
Your task is to provide an AI-based recommendation for over-the-counter drugs, appropriate dosage forms,
and suitable packaging materials, based on the user's symptoms/mission parameters and the provided medical research.

User's Symptoms/Mission Parameters:
"{user_query}"

--- Internal Medical Research from Chroma DB ---
{context_papers}

{context_google_search}

Based PRIMARILY on the provided internal medical research and the optional online search results,
    and the user's symptoms, please provide a concise recommendation.
    If direct and specific information is not available for a particular aspect (e.g., packaging materials),
    you may provide widely accepted general considerations or best practices relevant to space environments,
    clearly stating when you are inferring or using general knowledge rather than direct textual evidence.

    If no information at all can be found for a recommendation, state that.

Your recommendation should be structured as follows:

1. **Recommended Over-the-Counter Drug(s):** [List specific drugs and mention if not found in context]
2. **Recommended Dosage Form(s):** [e.g., tablet, liquid, transdermal patch, or mention if not found]
3. **Recommended Packaging Material(s) and Considerations:** [e.g., blister pack, vacuum-sealed, light-protective, radiation-resistant, or mention if not found]

Ensure your recommendation is grounded in the provided context and directly addresses the user's query.
"""

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating recommendation with LLM: {e}")
        return "An error occurred while generating the recommendation."

# --- Main execution for testing this module (can be removed when using app.py) ---
if __name__ == "__main__":
    client = get_chroma_client()
    collection_name = "medical_research_papers"

    if client:
        print("\n--- AI-Based Medical Recommendation System ---")
        user_query = input("Enter the astronaut's symptoms or mission parameters: ")

        if user_query:
            retrieved_papers = search_papers(client, collection_name, user_query, n_results=3)

            google_results = google_search(user_query, num_results=5) # Perform Google search here

            if retrieved_papers or google_results:
                print("\n--- Generating Recommendation with LLM ---")
                recommendation = generate_recommendation_with_llm(user_query, retrieved_papers, google_search_results=google_results)
                print("\n--- AI-Generated Recommendation ---")
                print(recommendation)
            else:
                print("No relevant papers or online search results found to base a recommendation on.")
        else:
            print("No query entered. Exiting.")
    else:
        print("Failed to connect to Chroma DB. Exiting.")
