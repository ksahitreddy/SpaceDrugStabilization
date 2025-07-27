from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sys
from search_integrated import get_chroma_client, search_papers, generate_recommendation_with_llm, google_search, GOOGLE_API_KEY, GOOGLE_CSE_ID, GROQ_API_KEY

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize Chroma DB client
chroma_client = None
try:
    chroma_client = get_chroma_client()
    if chroma_client:
        print("Successfully connected to Chroma DB!")
    else:
        print("Failed to connect to Chroma DB.")
except Exception as e:
    print(f"Error initializing Chroma DB: {e}")

collection_name = "medical_research_papers"

@app.route('/')
def index():
    return render_template('index.html', 
                         groq_api_key=bool(GROQ_API_KEY),
                         google_api_configured=bool(GOOGLE_API_KEY and GOOGLE_CSE_ID and 
                                                  GOOGLE_API_KEY != "YOUR_GOOGLE_API_KEY" and 
                                                  GOOGLE_CSE_ID != "YOUR_GOOGLE_CSE_ID"))

@app.route('/get_recommendation', methods=['POST'])
def get_recommendation():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    user_query = data.get('query', '').strip()
    
    if not user_query:
        return jsonify({"error": "Please enter a query"}), 400
    
    if not chroma_client:
        return jsonify({"error": "Chroma DB client not available. Cannot perform search."}), 500
    
    try:
        # Step 1: Retrieve relevant papers from Chroma DB
        retrieved_papers = search_papers(chroma_client, collection_name, user_query, n_results=3)
        
        # Step 2: Perform Google Search
        google_results = []
        if GOOGLE_API_KEY and GOOGLE_CSE_ID and \
           GOOGLE_API_KEY != "YOUR_GOOGLE_API_KEY" and \
           GOOGLE_CSE_ID != "YOUR_GOOGLE_CSE_ID":
            google_results = google_search(user_query, num_results=5)
        
        if not retrieved_papers and not google_results:
            return jsonify({"error": "No relevant information found for your query."}), 404
        
        # Step 3: Generate recommendation
        recommendation = generate_recommendation_with_llm(user_query, retrieved_papers, google_results)
        
        return jsonify({
            "recommendation": recommendation,
            "papers": retrieved_papers,
            "search_results": google_results
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Run the app
    app.run(debug=True, port=5000)
