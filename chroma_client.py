import chromadb
import os

# --- Configuration ---
# Define the path where Chroma DB will store its data.
# This creates a folder named 'chroma_db_data' in your current working directory.
CHROMA_DB_PATH = "./chroma_db_data"

# You might still need an OpenAI API Key later for embeddings if you use an OpenAI embedding model.
# For now, we'll use a local embedding model.
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- 1. Connect to Chroma DB ---
def get_chroma_client():
    """Establishes and returns a Chroma DB client connection."""
    try:
        # This creates a persistent client that stores data in the specified path.
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        print(f"Successfully connected to Chroma DB. Data will be stored in: {CHROMA_DB_PATH}")
        return client
    except Exception as e:
        print(f"Error connecting to Chroma DB: {e}")
        return None

# --- Main execution (for testing connection and creating a collection) ---
if __name__ == "__main__":
    client = get_chroma_client()

    if client:
        # Create a collection. This is similar to a 'table' or 'class' in other databases.
        # If it already exists, it will be retrieved.
        collection_name = "medical_research_papers"
        try:
            collection = client.get_or_create_collection(name=collection_name)
            print(f"\nSuccessfully got/created collection: '{collection_name}'")

            # You can check the number of items in the collection
            print(f"Number of items in '{collection_name}': {collection.count()}")

        except Exception as e:
            print(f"Error with Chroma DB collection: {e}")
    else:
        print("Failed to get Chroma DB client. Exiting.")