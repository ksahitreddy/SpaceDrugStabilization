import chromadb
import os
import google.generativeai as genai # For Google Gemini LLM

# --- Configuration ---
# Path to your Chroma DB data.
CHROMA_DB_PATH = "./chroma_db_data"

# Google Gemini API Key
# IMPORTANT: Load this from an environment variable for security in production!
# For testing, you can place it directly here, but remember to remove it later.
GEMINI_API_KEY = "AIzaSyD5eTn0XkIR6ui7f0L8PZUJ6bbfPrqs30Y" # <--- REPLACE WITH YOUR ACTUAL GEMINI API KEY

# Configure the Google Generative AI client
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY is not set. LLM recommendations will not function.")

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
                    "full_content": doc_content, # Pass full content to LLM
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

# --- 3. Function to Generate Recommendation with LLM ---
def generate_recommendation_with_llm(user_query, retrieved_papers_content):
    """
    Uses an LLM (Gemini) to generate a recommendation based on the user's query
    and the content of retrieved relevant papers.
    """
    if not GEMINI_API_KEY:
        return "LLM API key not configured. Cannot generate recommendation."

    # Join the content of retrieved papers to provide as context
    context = "\n\n".join([paper['full_content'] for paper in retrieved_papers_content])

    # Construct a detailed prompt for the LLM
    # This prompt is CRUCIAL for getting good results. Be specific!
    prompt = f"""
    You are an AI assistant specializing in medical countermeasures for astronauts in space missions.
    Your task is to provide an AI-based recommendation for over-the-counter drugs, appropriate dosage forms,
    and suitable packaging materials, based on the user's symptoms/mission parameters and the provided medical research.

    User's Symptoms/Mission Parameters:
    "{user_query}"

    Relevant Medical Research from Chroma DB:
    {context}

    Based PRIMARILY on the provided internal medical research and the optional online search results,
    and the user's symptoms, please provide a concise recommendation.
    If direct and specific information is not available for a particular aspect (e.g., packaging materials),
    you may provide widely accepted general considerations or best practices relevant to space environments,
    clearly stating when you are inferring or using general knowledge rather than direct textual evidence.

    Your recommendation should be structured as follows:

    1. **Recommended Over-the-Counter Drug(s):** [List specific drugs and mention if not found in context]
    2. **Recommended Dosage Form(s):** [e.g., tablet, liquid, transdermal patch, or mention if not found]
    3. **Recommended Packaging Material(s) and Considerations:** [e.g., blister pack, vacuum-sealed, light-protective, radiation-resistant, or mention if not found]

    Ensure your recommendation is grounded in the provided research and directly addresses the user's query.
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash') # Or 'gemini-1.5-pro' if preferred and access available
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating recommendation with LLM: {e}")
        return "An error occurred while generating the recommendation."

# --- Main execution for testing this module ---
if __name__ == "__main__":
    client = get_chroma_client()
    collection_name = "medical_research_papers"

    if client:
        print("\n--- AI-Based Medical Recommendation System ---")
        user_query = input("Enter the astronaut's symptoms or mission parameters: ")

        if user_query:
            # Step 1: Retrieve relevant papers from Chroma DB
            retrieved_papers = search_papers(client, collection_name, user_query, n_results=3)

            if retrieved_papers:
                print("\n--- Generating Recommendation with LLM ---")
                # Step 2: Pass retrieved content and query to the LLM
                recommendation = generate_recommendation_with_llm(user_query, retrieved_papers)
                print("\n--- AI-Generated Recommendation ---")
                print(recommendation)
            else:
                print("No relevant papers found to base a recommendation on.")
        else:
            print("No query entered. Exiting.")
    else:
        print("Failed to connect to Chroma DB. Exiting.")