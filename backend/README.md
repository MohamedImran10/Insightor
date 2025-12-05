# Insightor Backend

FastAPI-based backend for the AI Research Assistant with multi-agent orchestration.

## Architecture

### Agents

1. **Search Agent** (`search_agent.py`)
   - Handles Tavily Search API integration
   - Retrieves top N search results
   - Validates URLs for accessibility

2. **Reader Agent** (`reader_agent.py`)
   - Fetches content from URLs asynchronously
   - Cleans HTML using trafilatura
   - Extracts key sentences from content

3. **Gemini Summarizer** (`gemini_summarizer.py`)
   - Uses Google Gemini 2.5 Flash for summarization
   - Extracts insights and recommendations
   - Generates follow-up questions

### Orchestrator

`orchestrator.py` coordinates the complete workflow:
1. Search → Fetch relevant URLs
2. Read → Clean and extract content
3. Summarize → Generate AI-powered summary

## Setup

### 1. Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configuration

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```env
GOOGLE_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

### 4. Run Server

```bash
python run.py
```

Server will start on `http://localhost:8000`

## API Endpoints

### GET /
Welcome message and endpoint information

### GET /health
Health check with agent status

### GET /status
Application status and available endpoints

### POST /research
Main research endpoint

**Request:**
```json
{
  "query": "Your research question"
}
```

**Response:**
```json
{
  "query": "...",
  "status": "success",
  "final_summary": "...",
  "top_insights": [...],
  "search_results": [...]
}
```

## API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Gemini API key | `abc123...` |
| `TAVILY_API_KEY` | Tavily Search API key | `xyz789...` |
| `BACKEND_HOST` | Server host | `0.0.0.0` |
| `BACKEND_PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `True` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |

## Error Handling

The backend provides comprehensive error handling:

- **400 Bad Request**: Invalid input (empty query)
- **500 Internal Server Error**: API failures with details in response

Example error response:
```json
{
  "query": "...",
  "status": "error",
  "error": "Search failed: API error",
  "timestamp": "2024-12-04T10:30:00"
}
```

## Logging

All operations are logged with emoji indicators:
- 🔍 Search operations
- 📥 Content fetching
- 📖 Content reading
- 🧠 Summarization
- ✅ Success
- ❌ Errors
- ⚠️ Warnings

## Performance

Typical execution times:
- Search: 2-3s
- Reading: 3-5s
- Summarization: 3-5s
- **Total**: 8-13s

## Testing

To test the API:

```bash
# Using curl
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'

# Using Python
import requests
response = requests.post(
    "http://localhost:8000/research",
    json={"query": "What is machine learning?"}
)
print(response.json())
```

## Production Deployment

Using Gunicorn:

```bash
pip install gunicorn
gunicorn app.main:app --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## Troubleshooting

### Missing API Keys
Error: `KeyError: 'GOOGLE_API_KEY'`
**Solution**: Create `.env` file with API keys

### Connection Refused
Error: `Connection refused` when accessing backend
**Solution**: Ensure backend is running on correct port

### Tavily API Errors
Error: `Search API error`
**Solution**: Check Tavily API key validity and rate limits

## Dependencies

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **httpx**: Async HTTP client
- **trafilatura**: Content extraction
- **google-generativeai**: Gemini API client
- **tavily-python**: Tavily Search client
- **pydantic**: Data validation
- **beautifulsoup4**: HTML parsing

## Code Structure

```
app/
├── main.py           # FastAPI app & routes
├── config.py         # Configuration management
├── models.py         # Pydantic models
└── agents/
    ├── search_agent.py      # Search functionality
    ├── reader_agent.py      # Content reading
    ├── gemini_summarizer.py # Summarization
    └── orchestrator.py      # Workflow coordination
```

## API Rate Limits

- **Tavily**: Check your plan limits
- **Gemini**: Check your plan limits
- **Backend**: No rate limiting in Phase-1

---

**Ready for Phase-1 production use!**
