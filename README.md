# Nha Trang Tourism Assistant

An AI-powered tourism assistant for Nha Trang, Vietnam, built with FastAPI, LangGraph, and various AI agents.

## Features

- 🤖 **AI-Powered Chat**: Intelligent conversation flow using LangGraph
- 🍽️ **Food Search**: Restaurant and food place recommendations using SerpAPI
- 📚 **Information Retrieval**: PDF-based knowledge retrieval using FAISS
- 🌐 **REST API**: FastAPI-based web API
- 💬 **CLI Interface**: Command-line chat interface
- 🔍 **Smart Routing**: Automatic query classification and routing

## Project Structure

```
src/
├── api/                    # FastAPI web interface
│   ├── routes/            # API route handlers
│   ├── schemas.py         # Pydantic models
│   └── main.py           # FastAPI application
├── core/                  # Core business logic
│   ├── config.py         # Configuration management
│   ├── graph.py          # LangGraph workflow
│   ├── nodes.py          # Graph nodes
│   └── states.py         # State definitions
├── agents/               # Specialized AI agents
│   ├── food_agent/       # Food search functionality
│   └── retrieval/        # Document retrieval
├── prompts/              # Prompt templates
├── param/                # Parameter models
├── utils/                # Utility functions
│   └── logger.py         # Logging configuration
└── cli.py                # Command-line interface
```

## Setup

### Prerequisites

- Python 3.12+
- OpenAI API key
- SerpAPI key (for food search)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd llm-flight-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file
OPENAI_API_KEY=your_openai_api_key
SERPAPI_API_KEY=your_serpapi_key
```

4. Ensure FAISS index exists:
```bash
# The FAISS index should be in faiss_index_openai_embeddings/
# Generate it from your PDF documents if needed
```

## Usage

### Web API

Start the FastAPI server:
```bash
# Using the new structure
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Or using python module
python -m src.api.main
```

API endpoints:
- `POST /api/v1/chat` - Chat with the assistant
- `GET /api/v1/health` - Health check

### Command Line Interface

```bash
python -m src.cli
```

### Example API Usage

```python
import requests

response = requests.post("http://localhost:8000/api/v1/chat", json={
    "message": "Tôi muốn tìm quán phở ngon ở Nha Trang",
    "session_id": "my_session"
})

print(response.json())
```

## Configuration

The application uses Pydantic Settings for configuration. Key settings include:

- **LLM Settings**: Model, temperature, embedding model
- **Search Settings**: Default location, language, country
- **API Keys**: OpenAI, SerpAPI
- **Paths**: Data directory, FAISS index path, logs directory

See `src/core/config.py` for all available settings.

## Development

### Running Tests

```bash
# Run tests (if you have them)
pytest tests/
```

### Code Structure Guidelines

- **Separation of Concerns**: API, business logic, and utilities are separated
- **Dependency Injection**: Configuration and services are injected where needed
- **Type Hints**: All functions and classes use proper type annotations
- **Logging**: Comprehensive logging throughout the application
- **Error Handling**: Proper exception handling and user-friendly error messages

### Adding New Agents

1. Create agent in `src/agents/`
2. Add node in `src/core/nodes.py`
3. Update graph in `src/core/graph.py`
4. Add routing logic in router prompt

## Environment Variables

Required:
- `OPENAI_API_KEY`: OpenAI API key for LLM and embeddings

Optional:
- `SERPAPI_API_KEY`: For food search functionality
- `DEBUG`: Enable debug mode
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

## Logging

Logs are stored in the `logs/` directory with rotation. Configure logging levels in the settings.

## Contributing

1. Follow the existing code structure
2. Add type hints to all functions
3. Include docstrings for classes and methods
4. Update tests for new features
5. Update this README if needed

## License

[Your License Here]