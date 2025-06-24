# OpenAI Compatible API Documentation

This server provides an OpenAI-compatible API interface for Gemini, allowing you to use Gemini with any application that supports OpenAI's API format.

## Quick Start

1. Start the server:
```bash
python openai_compatible_server.py
```

2. Configure your OpenAI client:
```python
from openai import OpenAI

client = OpenAI(
    api_key="dummy-key",  # Gemini doesn't need an API key
    base_url="http://localhost:8080/v1"
)
```

## Supported Endpoints

### 1. List Models
```
GET /v1/models
```

Returns available models in OpenAI format.

### 2. Chat Completions
```
POST /v1/chat/completions
```

Create a chat completion. Supports both regular and streaming responses.

**Request Body:**
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "stream": false
}
```

**Model Mappings:**
- `gpt-3.5-turbo` → `gemini-2.5-flash`
- `gpt-4` → `gemini-2.5-pro`
- `gpt-4-turbo` → `gemini-2.5-flash`

You can also use Gemini model names directly.

### 3. Legacy Completions
```
POST /v1/completions
```

Legacy endpoint that converts requests to chat format.

## Usage Examples

### With curl
```bash
# Chat completion
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# Streaming
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Tell me a story"}],
    "stream": true
  }'
```

### With Python OpenAI Client
```python
from openai import OpenAI

client = OpenAI(
    api_key="dummy-key",
    base_url="http://localhost:8080/v1"
)

# Regular completion
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)

# Streaming
stream = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")
```

### With LangChain
```python
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(
    openai_api_key="dummy-key",
    openai_api_base="http://localhost:8080/v1",
    model_name="gpt-3.5-turbo"
)

response = llm.invoke("Hello!")
print(response.content)
```

## Notes

- No API key is required (use any dummy value)
- Token counting is approximate
- Chat sessions are maintained per user (use the `user` field)
- System prompts are supported and formatted appropriately
- Streaming responses use Server-Sent Events (SSE) format