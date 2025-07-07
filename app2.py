import streamlit as st
import os
import sys

# Add the directory containing recommendation_system.py to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your core logic functions from search_integrated.py
from search_integrated import (
    get_chroma_client,
    search_papers,
    generate_recommendation_with_llm,
    google_search,
    GEMINI_API_KEY,
    GOOGLE_API_KEY,
    GOOGLE_CSE_ID
)

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="Astronaut Medical Advisor",
    page_icon="👨‍🚀",
    layout="centered"
)

st.title("👨‍🚀 AI-Powered Astronaut Medical Advisor")
st.write("Enter astronaut's symptoms or mission parameters to get medical recommendations based on research and web search.")

# --- Initialize Chroma Client (only once) ---
@st.cache_resource
def load_chroma_client():
    """Loads and caches the Chroma DB client."""
    client = get_chroma_client()
    if client:
        st.success("Connected to Chroma DB successfully!")
    else:
        st.error("Failed to connect to Chroma DB. Ensure data is ingested and path is correct.")
    return client

chroma_client = load_chroma_client()
collection_name = "medical_research_papers" # Match your collection name

# --- Check for API Keys ---
api_key_status = []
if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
    api_key_status.append("Gemini API Key (for LLM)")
if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY" or \
   not GOOGLE_CSE_ID or GOOGLE_CSE_ID == "YOUR_GOOGLE_CSE_ID":
    api_key_status.append("Google Search API Keys (for web search)")

if api_key_status:
    st.warning(f"Please set your {', '.join(api_key_status)} in `recommendation_system.py` for full functionality.")


# --- User Input ---
user_query = st.text_area(
    "Describe the astronaut's symptoms or mission parameters:",
    height=100,
    placeholder="E.g., 'Persistent nausea and mild headache after treadmill in microgravity. What OTC remedies are safe?'"
)

if st.button("Get Recommendation"):
    if not user_query:
        st.warning("Please enter a query to get a recommendation.")
    elif not chroma_client:
        st.error("Chroma DB client not available. Cannot perform search.")
    else:
        with st.spinner("Searching relevant papers and web, then generating recommendation..."):
            # Step 1: Retrieve relevant papers from Chroma DB
            retrieved_papers = search_papers(chroma_client, collection_name, user_query, n_results=3)

            # Step 2: Perform Google Search (num_results increased here!)
            google_results = google_search(user_query, num_results=5) # <--- UPDATED: Fetch 5 results from Google

            if retrieved_papers or google_results:
                st.subheader("Relevant Research Found:")
                if retrieved_papers:
                    for i, paper in enumerate(retrieved_papers):
                        st.markdown(f"**{i+1}. {paper['title']}** (Filename: `{paper['filename']}`, Relevance: `{paper['relevance_distance']:.4f}`)")
                        st.write(f"*{paper['full_content'][:300]}...*")
                        st.divider()
                else:
                    st.info("No highly relevant papers found in internal database.")

                st.subheader("Relevant Online Search Results:")
                if google_results:
                    for i, result in enumerate(google_results):
                        st.markdown(f"**{i+1}. [{result['title']}]({result['link']})**")
                        st.write(f"*{result['snippet']}*")
                        st.divider()
                else:
                    st.info("No relevant online search results found or Google Search API not configured.")

                # Step 3: Pass all relevant context to the LLM
                st.subheader("AI-Generated Recommendation:")
                recommendation = generate_recommendation_with_llm(user_query, retrieved_papers, google_search_results=google_results)
                st.markdown(recommendation)

            else:
                st.info("No relevant papers or online search results found to base a recommendation on.")

st.markdown("---")
st.info("Built with Chroma DB, Google Gemini, Google Custom Search, and Streamlit.")