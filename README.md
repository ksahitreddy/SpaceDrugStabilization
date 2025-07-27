# AI-Powered Drug Discovery and Research Platform

This project is an advanced document search and retrieval system designed for drug discovery and molecular research. It combines semantic search capabilities with large language models to provide intelligent insights from research papers and molecular data.

## Features

- **Semantic Document Search**: Find relevant research papers and documents using natural language queries
- **Molecular Data Integration**: Work with 3D molecular structures and CHARMM force field parameters
- **Vector Database**: Utilizes Chroma DB for efficient similarity search and retrieval
- **Web Interface**: User-friendly interface built with Flask for easy interaction
- **Advanced Search**: Integrated search capabilities combining semantic and traditional keyword search

## Project Structure

```
SpaceDrugStabilization/
├── Acetaminophen/           # GROMACS files for Acetaminophen simulation
├── Ibuprofen/           # GROMACS files for Ibuprofen simulation
└── src/                    # Source code
    ├── app.py              # Main Flask application
    ├── search_integrated.py # Integrated search functionality
    ├── requirements.txt    # Python dependencies
    ├── static/             # Static files (CSS, JS, images)
    └── templates/          # HTML templates
```

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Access to Google API (for web search functionality)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd IDP
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r src/requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key
   GROQ_API_KEY=your_groq_api_key
   GOOGLE_CSE_ID=your_google_cse_id
   # Add other environment variables as needed
   ```

## Usage

1. Start the web application:
   ```bash
   cd src
   python app.py
   ```

2. Open your web browser and navigate to `http://localhost:5000`

3. Use the search interface to query the document database or analyze molecular data

## Documentation

For detailed documentation on specific features, please refer to the following:

- [User Guide](docs/USER_GUIDE.md) - How to use the application
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Setup and contribution guidelines
- [API Documentation](docs/API.md) - API endpoints and usage

## Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Chroma DB](https://www.trychroma.com/) for vector similarity search
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [CHARMM](https://www.charmm.org/) for molecular dynamics simulations
- [Google Gemini](https://ai.google.dev/) for LLM capabilities
