# USCIS Policy Manual Chat Server

This is a Flask-based API server that provides a chat interface for querying the USCIS Policy Manual using Weaviate vector database and Ollama for LLM inference.

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Ollama installed locally with llama3.2 model

## Setup

1. Start the Weaviate database:
```bash
cd backend
docker-compose up -d
```

2. Install Python dependencies:
```bash
pip install flask flask-cors weaviate-client requests
```

3. Ensure Ollama is running locally with llama3.2 model:
```bash
ollama run llama3.2
```

## Starting the Server

1. Run the Flask server:
```bash
python api.py
```

The server will start on `http://localhost:5555` with the following endpoints:
- `POST /api/chat/ask` - Ask a question
- `GET /api/chat/history` - Get chat history
- `POST /api/chat/clear` - Clear chat history

## Environment

The server expects:
- Weaviate to be running on `http://localhost:8080`
- Ollama to be running on `http://localhost:11434`
- The USCIS Policy Manual data to be loaded in Weaviate under collection name "USCIS_Policy_Manual"

## Frontend Integration

The server is configured with CORS enabled and can be used with the frontend service running on `http://localhost:3000`.

## API Endpoints

### Ask a Question
```bash
POST /api/chat/ask
Content-Type: application/json

{
    "question": "What is the naturalization process?"
}
```

### Get Chat History
```bash
GET /api/chat/history
```

### Clear Chat History
```bash
POST /api/chat/clear
```
