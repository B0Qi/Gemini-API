# Docker Deployment Guide for Gemini OpenAI-Compatible API

## Prerequisites

- Docker and Docker Compose installed
- Valid Gemini cookies from https://gemini.google.com

## Quick Start

1. **Update cookies in `config.env`**:
   ```bash
   # Edit config.env and add your cookies
   nano config.env
   ```

2. **Build and start the container**:
   ```bash
   docker-compose up -d
   ```

3. **Check if it's running**:
   ```bash
   docker-compose ps
   docker-compose logs gemini-openai-api
   ```

4. **Test the API**:
   ```bash
   # Health check
   curl http://localhost:8080/health

   # List models
   curl http://localhost:8080/v1/models

   # Chat completion
   curl -X POST http://localhost:8080/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [{"role": "user", "content": "Hello!"}]
     }'
   ```

## Features

### Cookie Persistence
- Cookies are automatically saved to `./gemini_cookies/` directory
- The container will reload saved cookies on restart
- No need to update cookies frequently due to auto-refresh

### Health Monitoring
- Built-in health checks every 30 seconds
- Automatic restart on failure
- Check status: `docker-compose ps`

### Configuration
- All settings in `config.env` (not tracked by git)
- Copy `config.env.example` to create your own
- Environment variables:
  - `SECURE_1PSID` - Required Gemini cookie
  - `SECURE_1PSIDTS` - Required Gemini cookie
  - `PORT` - API port (default: 8080)
  - `HOST` - API host (default: 0.0.0.0)

## Usage with OpenAI Clients

### Python OpenAI SDK
```python
from openai import OpenAI

client = OpenAI(
    api_key="dummy",  # Any value works
    base_url="http://localhost:8080/v1"
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### LangChain
```python
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(
    openai_api_key="dummy",
    openai_api_base="http://localhost:8080/v1",
    model_name="gpt-3.5-turbo"
)
```

### Continue.dev, Cursor, etc.
Set the API base URL to: `http://localhost:8080/v1`

## Management Commands

```bash
# Start containers
docker-compose up -d

# View logs
docker-compose logs -f gemini-openai-api

# Stop containers
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Clean everything (including volumes)
docker-compose down -v

# Start with both APIs (OpenAI + original)
docker-compose --profile full up -d
```

## Troubleshooting

### Cookie Expired Error
1. Get new cookies from https://gemini.google.com
2. Update `config.env`
3. Restart: `docker-compose restart`

### Container Won't Start
1. Check logs: `docker-compose logs gemini-openai-api`
2. Verify cookies are correct in `config.env`
3. Ensure port 8080 is not in use

### Permission Issues
```bash
# Fix cookie directory permissions
sudo chown -R $USER:$USER gemini_cookies/
```

## Production Deployment

For production use:

1. Use a reverse proxy (nginx/traefik)
2. Enable HTTPS
3. Set up proper authentication
4. Monitor with Prometheus/Grafana
5. Use Docker secrets for cookies instead of env file

Example nginx config:
```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```