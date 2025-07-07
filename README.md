# AI-Powered Astronaut Medical Advisor

This project is an interactive web application that provides medical recommendations for astronauts based on research papers. It leverages [Chroma DB](https://www.trychroma.com/) for semantic search, Google Gemini for LLM-powered recommendations, Google Search API for web search capabilities and [Streamlit](https://streamlit.io/) for the user interface.

## Features

- **Semantic Search:** Retrieves the most relevant medical research papers from a local Chroma DB vector database based on user queries.
- **LLM Recommendations:** Uses Google Gemini to generate tailored medical advice using the retrieved research context.
- **Web Search Integration:** Uses Google's Search API for enhanced recommendations with web search
- **User-Friendly UI:** Built with Streamlit for easy interaction and visualization.

## Usage

1. **Install Requirements**
   ```sh
   pip install -r requirements.txt
   ```

2. **Set Up Chroma DB**
   - Ensure your research papers are ingested into Chroma DB. Use `ingest_papers.py` if needed.

3. **Configure Gemini API Key**
   - Set your Google Gemini API key in `llm_integration.py` as `GEMINI_API_KEY`.

4. **Run the App**
   ```sh
   streamlit run app.py
   ```

5. **Interact**
   - Enter astronaut symptoms or mission parameters in the text area.
   - Click "Get Recommendation" to view relevant research and an AI-generated recommendation.

## File Structure
The project has been built in increments, with each increment integrated with a new feature.

- `app.py` — Main Streamlit app for querying research papers and generating recommendations.
- `llm_integration.py` — Handles Chroma DB connection, semantic search, and Gemini LLM integration.
- `ingest_papers.py` — Script to ingest research papers into Chroma DB.
- `chroma_client.py` — Chroma DB client utilities.
- `search_and_recommend.py`, `search_integrated.py`, `improved_frontend.py`, `app2.py` — Additional/experimental modules.
- `chroma_db_data/` — Chroma DB data directory.

## Requirements

- Python 3.8+
- Streamlit
- Chroma DB
- Google Gemini API access

## Acknowledgements

- Built with [Chroma DB](https://www.trychroma.com/), [Google Gemini](https://ai.google.dev/gemini-api), and [Streamlit](https://streamlit.io/).

---

*For research and educational purposes only. Not for clinical use.*

