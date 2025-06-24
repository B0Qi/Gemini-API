# Gemini API Deployment Guide

## Quick Start

### 1. Local Deployment

Run the server directly:
```bash
python server.py
```

The API will be available at `http://localhost:8080`

### 2. Docker Deployment

Build and run with Docker Compose:
```bash
docker-compose up -d
```

### 3. Test the API

Use the provided client example:
```bash
python client_example.py
```

Or use curl:
```bash
# Health check
curl http://localhost:8080/health

# Chat request
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

## API Endpoints

- `GET /health` - Health check
- `POST /chat` - Send a message to Gemini
  - Request body: `{"message": "your message", "model": "optional-model-name", "files": ["optional-file-paths"]}`
  - Response: `{"text": "response text", "images": [], "thoughts": null}`
- `POST /chat/session` - Create a chat session (demo endpoint)

## Configuration

The cookies are hardcoded in `server.py`. To update them:
1. Get new cookies from https://gemini.google.com
2. Update `Secure_1PSID` and `Secure_1PSIDTS` in `server.py`

## Notes

- The API automatically refreshes cookies in the background
- For production, consider using environment variables for cookies
- The Docker setup includes a volume for persisting cookies