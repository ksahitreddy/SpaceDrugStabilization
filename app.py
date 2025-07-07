import streamlit as st
import os
import sys

# Add the directory containing recommendation_system.py to the Python path
# This allows us to import functions from that file.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your core logic functions from llm_integration.py
# Make sure llm_integration.py is in the same directory as app.py
from llm_integration import get_chroma_client, search_papers, generate_recommendation_with_llm, GEMINI_API_KEY

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="Astronaut Medical Advisor",
    page_icon="👨‍🚀",
    layout="centered"
)

st.title("👨‍🚀 AI-Powered Astronaut Medical Advisor")
st.write("Enter astronaut's symptoms or mission parameters to get medical recommendations based on research.")

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

# --- Check for LLM API Key ---
if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
    st.warning("Please set your `GEMINI_API_KEY` in `recommendation_system.py` for LLM recommendations to work.")

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
    elif not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        st.error("Gemini API Key is not configured. Cannot generate recommendation. Please check `recommendation_system.py`.")
    else:
        with st.spinner("Searching relevant papers and generating recommendation..."):
            # Step 1: Retrieve relevant papers from Chroma DB
            retrieved_papers = search_papers(chroma_client, collection_name, user_query, n_results=3)

            if retrieved_papers:
                st.subheader("Relevant Research Found:")
                for i, paper in enumerate(retrieved_papers):
                    st.markdown(f"**{i+1}. {paper['title']}** (Filename: `{paper['filename']}`, Relevance: `{paper['relevance_distance']:.4f}`)")
                    st.write(f"*{paper['full_content'][:300]}...*") # Show a snippet of content
                    st.divider() # Visual separator

                # Step 2: Pass retrieved content and query to the LLM
                st.subheader("AI-Generated Recommendation:")
                recommendation = generate_recommendation_with_llm(user_query, retrieved_papers)
                st.markdown(recommendation) # Use markdown to render formatted text

            else:
                st.info("No highly relevant papers found in the internal database for this query. Consider broadening your search or providing more context.")

st.markdown("---")
st.info("Built with Chroma DB, Google Gemini, and Streamlit.")