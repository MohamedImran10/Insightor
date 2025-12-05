# Architecture Diagram

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React)                       │
│                     Port 3000 - Browser UI                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • SearchInput Component - Get user query              │   │
│  │  • ResearchContainer - Display results                 │   │
│  │  • Framer Motion Animations                            │   │
│  │  • Responsive Design (Mobile/Desktop)                  │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP POST /research
                             │ { "query": "..." }
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│                   Port 8000 - REST API                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Research Orchestrator                      │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  PHASE 1: Search Agent                           │  │   │
│  │  │  ├─ Tavily Search API                            │  │   │
│  │  │  ├─ Query: "user question"                       │  │   │
│  │  │  └─ Output: [SearchResult{title, url, snippet}] │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │                                                         │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  PHASE 2: Reader Agent                           │  │   │
│  │  │  ├─ Fetch URLs (async httpx)                    │  │   │
│  │  │  ├─ Extract content (trafilatura)               │  │   │
│  │  │  ├─ Clean HTML (BeautifulSoup fallback)         │  │   │
│  │  │  └─ Output: {url, cleaned_text}                 │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │                                                         │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  PHASE 3: Gemini Summarizer                      │  │   │
│  │  │  ├─ Google Gemini 2.5 Flash API                 │  │   │
│  │  │  ├─ Input: Combined content from phase 2        │  │   │
│  │  │  ├─ Process: Summarization & insights           │  │   │
│  │  │  └─ Output: {summary, insights, key_findings}  │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP 200 OK
                             │ {
                             │  "query": "...",
                             │  "status": "success",
                             │  "final_summary": "...",
                             │  "top_insights": [...],
                             │  "search_results": [...]
                             │ }
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND                               │
│                   Display Results with Animations               │
└─────────────────────────────────────────────────────────────────┘
```

## Component Interaction Diagram

```
Frontend                          Backend                    External APIs
─────────────────────────────────────────────────────────────────────────

User Input ──────────────┐
                         │
                    Query ▼
                         │
SearchInput.jsx ─────────┼──────────► main.py (/research)
                         │               │
                         │               │
                         │          ┌────▼────────┐
                         │          │ Orchestrator│
                         │          └────┬────────┘
                         │               │
                         │               ├──────────► search_agent.py
                         │               │                 │
                         │               │            ┌────▼──────────┐
                         │               │            │ Tavily API    │
                         │               │            │ (Search)      │
                         │               │            └────┬──────────┘
                         │               │                 │
                         │               ├──────────► reader_agent.py
                         │               │                 │
                         │               │            ┌────▼──────────┐
                         │               │            │ Fetch URLs    │
                         │               │            │ Clean Content │
                         │               │            └────┬──────────┘
                         │               │                 │
                         │               ├──────────► gemini_summarizer.py
                         │               │                 │
                         │               │            ┌────▼──────────┐
                         │               │            │ Gemini API    │
                         │               │            │ (Summarize)   │
                         │               │            └────┬──────────┘
                         │               │                 │
                    Results ◄───────────┬─┘
                         │
ResearchContainer.jsx ◄──┴─────── Display Results
                         
Animations & UI ────────────────── Framer Motion
```

## Data Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│ Input: User Query                                              │
│ Example: "What is machine learning?"                           │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│ SEARCH PHASE - Search Agent                                    │
│ Tavily API Call                                                │
│ Input: query string                                            │
│ Output: List[SearchResult]                                     │
│   - title: "Machine Learning Basics"                           │
│   - url: "https://example.com/ml"                              │
│   - snippet: "ML is a subset of AI..."                         │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│ READ PHASE - Reader Agent                                      │
│ For each URL:                                                  │
│   1. Fetch raw HTML (httpx async)                              │
│   2. Extract content (trafilatura)                             │
│   3. Clean text (remove noise)                                 │
│   4. Limit to 5000 chars                                       │
│                                                                │
│ Output: List[ProcessedContent]                                │
│   - url: "https://example.com/ml"                              │
│   - cleaned_text: "Machine learning is... [cleaned]"           │
│   - status: "success"                                          │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│ SUMMARIZE PHASE - Gemini Summarizer                            │
│ Google Gemini API Call                                         │
│ Input: Combined cleaned content                               │
│ Prompt: Structured analysis request                            │
│                                                                │
│ Output: Summary Data                                           │
│   - executive_summary: "ML is a field of AI that..."           │
│   - key_findings: "1. ML powers recommendations..."            │
│   - top_insights: ["Insight 1", "Insight 2", ...]             │
│   - recommendations: "Consider learning Python..."             │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│ Final Response to Frontend                                      │
│ {                                                              │
│   "query": "What is machine learning?",                        │
│   "status": "success",                                         │
│   "timestamp": "2024-12-04T...",                               │
│   "execution_time_seconds": 12.5,                              │
│   "search_results": [...],                                     │
│   "final_summary": "...",                                      │
│   "top_insights": [...],                                       │
│   "sources_count": 5                                           │
│ }                                                              │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│ Frontend Display                                               │
│ - Executive Summary Card                                       │
│ - Top Insights (3 cards)                                       │
│ - Source Results (clickable)                                   │
│ - Loading animations during process                            │
└────────────────────────────────────────────────────────────────┘
```

## Technology Stack

```
Frontend Layer
├── React 18.2
├── Framer Motion (animations)
├── Axios (HTTP client)
├── Lucide React (icons)
└── Tailwind CSS (styles)
    via Tailwind CDN

Backend Layer
├── FastAPI 0.104
├── Uvicorn (ASGI server)
├── Python 3.8+
└── Pydantic (validation)

Agent Layer
├── Search Agent
│   └── Tavily Python SDK
├── Reader Agent
│   ├── httpx (async HTTP)
│   ├── trafilatura (extraction)
│   ├── BeautifulSoup 4 (parsing)
│   └── LXML (HTML)
└── Summarizer
    └── google-generativeai (Gemini)

Infrastructure
├── Vite (frontend bundler)
├── Docker (containerization)
└── Docker Compose (orchestration)
```

## Execution Timeline

Typical request lifecycle:

```
Time    Component           Action
────    ────────────────    ──────────────────────────────
0ms     Frontend           User submits query
        ↓
50ms    API Request        POST /research sent to backend
        ↓
100ms   Orchestrator       Initialize workflow
        ↓
150ms   Search Agent       Start Tavily API call
        ↓
2500ms  Search Agent       Receive results (2-3 sec)
        ↓
2600ms  Reader Agent       Start fetching URLs
        ↓
5600ms  Reader Agent       Finish cleaning content (3+ sec)
        ↓
5700ms  Gemini Summarizer  Start Gemini API call
        ↓
10000ms Gemini Summarizer  Receive summary (3-5 sec)
        ↓
10050ms Orchestrator       Compile final response
        ↓
10100ms Backend            Send response to frontend
        ↓
10200ms Frontend           Display results with animations
        ↓
14000ms User               Reads complete results
```

## Error Handling Flow

```
User Query
    │
    ▼
Validate Input
    │
    ├─ Empty? ──────────────────► 400 Bad Request
    │
    ▼
Search Agent
    │
    ├─ API Error? ───────────────► 500 Error
    ├─ No Results? ──────────────► Continue with empty
    │
    ▼
Reader Agent
    │
    ├─ Network Error? ──────────► Log & Continue
    │
    ▼
Gemini Summarizer
    │
    ├─ API Error? ───────────────► 500 Error
    │
    ▼
Success! ─────────────────────────► 200 OK
```

---

**This architecture ensures fast, reliable, and scalable AI-powered research!**
