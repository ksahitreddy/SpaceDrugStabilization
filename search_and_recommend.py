import chromadb
import os

# --- Configuration ---
# Path to your Chroma DB data. Ensure this matches where you ingested your papers.
CHROMA_DB_PATH = "./chroma_db_data"

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
    """
    collection = client.get_or_create_collection(name=collection_name)
    print(f"\nSearching '{collection_name}' for: '{query_text}'...")

    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances'] # Request full document text, metadata, and distance
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
                    "content_snippet": doc_content[:500] + "...", # Snippet for display
                    "full_content": doc_content, # Keep full content for potential RAG later
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

# --- Main execution for testing this module ---
if __name__ == "__main__":
    client = get_chroma_client()
    collection_name = "medical_research_papers" # Ensure this matches your ingested collection name

    if client:
        print("\n--- Testing Chroma DB Search ---")
        user_query = input("Enter your search query (e.g., 'drug metabolism in microgravity' or 'radiation shielding'): ")

        if user_query:
            chroma_results = search_papers(client, collection_name, user_query, n_results=2)
            if chroma_results:
                print("\nChroma DB Search Results:")
                for i, paper in enumerate(chroma_results):
                    print(f"  Result {i+1}:")
                    print(f"    Title: {paper['title']}")
                    print(f"    Filename: {paper['filename']}")
                    print(f"    Relevance: {paper['relevance_distance']:.4f}")
                    print(f"    Content Preview: {paper['content_snippet']}")
                    print("-" * 30)
            else:
                print("No relevant papers found in Chroma DB for the query.")
        else:
            print("Chroma DB client not available. Cannot perform search.")
    else:
        print("Failed to connect to Chroma DB. Exiting.")