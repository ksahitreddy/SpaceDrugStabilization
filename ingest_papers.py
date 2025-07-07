import chromadb
import os
import fitz # PyMuPDF library for PDF processing
import hashlib # To generate unique IDs for documents

# --- Configuration ---
CHROMA_DB_PATH = "./chroma_db_data" # Ensure this matches your previous setup
PAPERS_FOLDER_PATH = r"D:\RV College of Engineering\6th Semester\Interdisciplinary Project\Research Papers"

# --- 1. Connect to Chroma DB (from previous step) ---
def get_chroma_client():
    """Establishes and returns a Chroma DB client connection."""
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        print(f"Successfully connected to Chroma DB. Data will be stored in: {CHROMA_DB_PATH}")
        return client
    except Exception as e:
        print(f"Error connecting to Chroma DB: {e}")
        return None

# --- 2. Function to Extract Text from PDF ---
def extract_text_from_pdf(pdf_path):
    """
    Extracts text content and attempts to find a title from a PDF file.
    Returns (text_content, title_guess).
    """
    text_content = ""
    title_guess = os.path.basename(pdf_path).replace(".pdf", "").replace("_", " ").title() # Default title from filename

    try:
        document = fitz.open(pdf_path)
        for page_num in range(document.page_count):
            page = document.load_page(page_num)
            text_content += page.get_text()

        # Attempt to find a more accurate title from the first few lines or metadata
        # This is a heuristic and might need fine-tuning for your specific papers
        if document.metadata and "title" in document.metadata and document.metadata["title"]:
            title_guess = document.metadata["title"]
        elif len(text_content) > 100: # Try to get title from first few lines if metadata is empty
            first_lines = text_content.split('\n')[:5]
            potential_title = next((line.strip() for line in first_lines if len(line.strip()) > 10), "")
            if potential_title:
                title_guess = potential_title

        document.close()
        return text_content, title_guess

    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        return "", title_guess # Return empty text if error

# --- 3. Ingest Research Papers ---
def ingest_research_papers(client, collection_name, papers_folder):
    """
    Reads PDF files from a folder, extracts text, and adds them to a Chroma collection.
    """
    collection = client.get_or_create_collection(name=collection_name)
    print(f"\nIngesting papers into collection: '{collection_name}'...")

    documents = []
    metadatas = []
    ids = []
    processed_count = 0

    for filename in os.listdir(papers_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(papers_folder, filename)
            print(f"Processing: {filename}")

            text_content, title = extract_text_from_pdf(pdf_path)

            if text_content:
                # Generate a unique ID for each document (e.g., hash of filename or content)
                doc_id = hashlib.sha256(filename.encode('utf-8')).hexdigest()

                documents.append(text_content)
                metadatas.append({
                    "filename": filename,
                    "title": title,
                    "source_path": pdf_path,
                    # Add more metadata if you can extract it (e.g., authors, year)
                })
                ids.append(doc_id)
                processed_count += 1
            else:
                print(f"Skipping {filename} due to empty content or processing error.")

    if documents:
        # Add all documents in a batch
        try:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"\nSuccessfully added {processed_count} documents to Chroma DB.")
        except Exception as e:
            print(f"Error adding documents to Chroma DB: {e}")
    else:
        print("No valid PDF documents found or processed from the specified folder.")

    print(f"Total items in '{collection_name}' after ingestion: {collection.count()}")


# --- Main execution ---
if __name__ == "__main__":
    client = get_chroma_client()

    if client:
        collection_name = "medical_research_papers"
        # Optional: Clear collection for fresh ingestion during testing
        # try:
        #     client.delete_collection(name=collection_name)
        #     print(f"Deleted existing collection: {collection_name}")
        # except Exception as e:
        #     print(f"Could not delete collection (may not exist): {e}")

        ingest_research_papers(client, collection_name, PAPERS_FOLDER_PATH)
    else:
        print("Failed to get Chroma DB client. Exiting.")