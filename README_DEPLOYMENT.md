# Gemini OpenAI-Compatible API Deployment

This project provides an OpenAI-compatible API interface for Google Gemini, allowing you to use Gemini with any OpenAI-compatible application.

## 🚀 Quick Start

### 1. Update Cookies

First, you need to get fresh cookies from Gemini:

```bash
./update_cookies.sh
```

Or manually edit `config.env` with your cookies.

### 2. Deploy with Docker

```bash
# Build and start the container
docker compose up -d

# Check logs
docker compose logs -f

# Test the API
curl http://localhost:8080/health
```

## 📁 Project Structure

```
gemini_api/
├── openai_server.py        # Main OpenAI-compatible server
├── config.env              # Cookie configuration (not in git)
├── config.env.example      # Example configuration
├── docker-compose.yml      # Docker deployment
├── Dockerfile.openai       # Docker image definition
├── requirements.txt        # Python dependencies
├── update_cookies.sh       # Cookie update helper
├── test_openai_api.py      # Test script
└── gemini_cookies/         # Persistent cookie storage (created automatically)
```

## 🔧 Features

- ✅ **Full OpenAI API Compatibility** - Works with any OpenAI client
- ✅ **Automatic Cookie Refresh** - Keeps sessions alive
- ✅ **Cookie Persistence** - Survives container restarts
- ✅ **Model Mapping** - Maps OpenAI models to Gemini equivalents
- ✅ **Streaming Support** - Real-time response streaming
- ✅ **Health Monitoring** - Built-in health checks

## 📖 API Usage

### With OpenAI Python Client

```python
from openai import OpenAI

client = OpenAI(
    api_key="any-value",  # Gemini doesn't need API key
    base_url="http://localhost:8080/v1"
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # Maps to gemini-2.5-flash
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### With curl

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## 🔑 Cookie Management

The system stores cookies in two places:
1. `config.env` - Initial cookies (update when expired)
2. `./gemini_cookies/` - Auto-saved working cookies

When cookies expire:
1. Run `./update_cookies.sh`
2. Or manually update `config.env`
3. Restart: `docker compose restart`

## 🛠️ Troubleshooting

### Common Issues

1. **Cookie Expired Error**
   - Get new cookies from https://gemini.google.com
   - Update using `./update_cookies.sh`

2. **Port Already in Use**
   - Change port in `config.env`
   - Or stop conflicting service

3. **Container Won't Start**
   - Check logs: `docker compose logs`
   - Verify cookies are valid

## 📝 Model Mappings

| OpenAI Model | Gemini Model |
|--------------|--------------|
| gpt-3.5-turbo | gemini-2.5-flash |
| gpt-4 | gemini-2.5-pro |
| gpt-4-turbo | gemini-2.5-flash |

## 🔒 Security Notes

- Never commit `config.env` to git
- Use Docker secrets in production
- Consider adding authentication
- Use HTTPS in production

## 📚 More Documentation

- [Detailed Docker deployment guide](DOCKER_DEPLOYMENT.md)
- [OpenAI API compatibility details](OPENAI_API.md)
- [Original Gemini API docs](README.md)