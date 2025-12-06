# Insightor - AI-Powered Research Assistant

An intelligent web research application that combines web search, content analysis, and AI-powered summarization with **multi-user authentication** and persistent memory.

## 🌟 Features

- **🔐 Multi-User Authentication** - Secure Firebase email/password authentication
- **🔍 Intelligent Web Search** - Find relevant information across the web using Tavily API
- **📖 Content Analysis** - Extract and clean content from web sources
- **🧠 AI Summarization** - Generate intelligent summaries using Google Gemini 2.5 Flash
- **💾 Memory System** - Store and retrieve past research with ChromaDB
- **☁️ Distributed Vector Database** - Optional Qdrant Cloud integration for scalability
- **📱 Responsive UI** - Beautiful, animated interface with Framer Motion
- **🚀 Production Ready** - Comprehensive error handling and graceful degradation

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI (async Python web framework)
- Firebase Admin SDK (authentication)
- ChromaDB (local vector memory)
- Qdrant (optional remote vector database)
- Google Gemini 2.5 Flash (LLM)
- Tavily API (web search)

**Frontend:**
- React 18 + Vite
- React Router (client-side routing)
- Firebase SDK (authentication)
- Framer Motion (animations)
- TailwindCSS (styling)

**Authentication:**
- Firebase Authentication (email/password)
- JWT-based token verification
- Secure token storage and refresh

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Firebase project (free tier available)
- API keys:
  - Google Gemini API key
  - Tavily Search API key
  - Qdrant API key (optional)

### Backend Setup

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Create .env file with your credentials
cp .env.example .env
# Edit .env and add:
# - FIREBASE credentials
# - GOOGLE_API_KEY
# - TAVILY_API_KEY
# - Qdrant credentials (optional)

# Start the backend server
python run.py
```

Backend runs on `http://localhost:8000`

### Frontend Setup

```bash
# Install Node dependencies
cd frontend
npm install

# Create .env.local file with Firebase config
cp .env.example .env.local
# Edit .env.local and add:
# - VITE_FIREBASE_API_KEY
# - VITE_FIREBASE_AUTH_DOMAIN
# - VITE_FIREBASE_PROJECT_ID
# - Other Firebase config values

# Start the development server
npm run dev
```

Frontend runs on `http://localhost:5173`

## 🔐 Authentication Setup

Complete step-by-step Firebase authentication setup:

📖 **[See FIREBASE_AUTH_SETUP.md](./FIREBASE_AUTH_SETUP.md)**

Quick summary:
1. Create Firebase project at https://console.firebase.google.com/
2. Enable Email/Password authentication
3. Get service account key for backend
4. Get web config for frontend
5. Fill in environment variables
6. Sign up and start researching!

## 📖 Usage

### Sign Up

1. Navigate to http://localhost:5173/
2. Click "Sign up"
3. Enter name, email, password
4. Verify email (optional, can use test account)
5. Redirected to research interface

### Research

1. Enter a query (e.g., "latest AI trends")
2. Click search or press Enter
3. System will:
   - Search the web for information
   - Extract relevant content
   - Store chunks in memory
   - Generate AI summary
   - Display results

### View Results

- **Summary** - AI-generated comprehensive summary
- **Top Insights** - Key points extracted
- **Search Results** - Original web sources
- **Memory** - Relevant past research
- **New Search** - Start a new query

### Logout

Click the "Logout" button in the header to sign out.

## 🗂️ Project Structure

```
Insightor/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app & routes
│   │   ├── auth_middleware.py      # Firebase token verification
│   │   ├── dependencies.py         # Route protection
│   │   ├── models.py               # Data models
│   │   ├── config.py               # Configuration
│   │   └── agents/
│   │       ├── search_agent.py     # Web search agent
│   │       ├── reader_agent.py     # Content extraction
│   │       ├── orchestrator.py     # Agent coordination
│   │       └── gemini_summarizer.py # AI summarization
│   ├── requirements.txt
│   ├── run.py
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Main app with routing
│   │   ├── firebase.js             # Firebase config
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Signup.jsx
│   │   │   └── ResearchApp.jsx
│   │   ├── components/
│   │   │   ├── ProtectedRoute.jsx
│   │   │   ├── SearchInput.jsx
│   │   │   └── ResearchContainer.jsx
│   │   ├── hooks/
│   │   │   └── useAuth.js
│   │   ├── api/
│   │   │   └── client.js
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── .env.local
│
└── README.md (this file)
```

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
# Firebase
FIREBASE_ENABLED=true
FIREBASE_CREDENTIALS_PATH=backend/service-keys/serviceAccountKey.json
FIREBASE_PROJECT_ID=your_project_id

# APIs
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key

# Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_key
```

**Frontend (.env.local):**
```env
# Firebase Web Config
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_domain.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_bucket.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id

# API Base URL
VITE_API_BASE_URL=http://localhost:8000
```

## 🔄 System Workflow

```
User Query
    ↓
[Frontend] Sends request with auth token
    ↓
[Backend] Verifies token & user
    ↓
[Search Agent] Searches web (Tavily API)
    ↓
[Reader Agent] Extracts content
    ↓
[Orchestrator] Processes results
    ↓
[Vector Memory] Stores chunks (ChromaDB/Qdrant)
    ↓
[Summarizer] Generates AI summary (Gemini)
    ↓
[Frontend] Displays results
```

## 📊 Components

### Search Agent
- Performs web search using Tavily API
- Retrieves top relevant sources
- Extracts metadata (title, URL, snippet)

### Reader Agent
- Fetches full article content
- Cleans and extracts relevant text
- Removes HTML, ads, and noise

### Memory System
- Stores content chunks in ChromaDB (local)
- Optionally uses Qdrant (cloud)
- Retrieves relevant past research
- Uses semantic similarity (all-MiniLM-L6-v2 embeddings)

### Summarizer Agent
- Takes extracted content
- Generates comprehensive summary using Gemini 2.5 Flash
- Extracts top insights
- Structures output for clarity

### Orchestrator
- Coordinates all agents
- Manages request flow
- Handles errors gracefully

## 🧪 Testing

### Test Backend

```bash
# Check if backend is running
curl http://localhost:8000/docs  # Swagger UI
curl http://localhost:8000/health

# Test with auth
curl -X POST http://localhost:8000/auth/verify \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Frontend

```bash
# Sign up → Make query → Check Network tab for Authorization header
# DevTools → Network → research request → Headers
# Should see: Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 🚨 Troubleshooting

### Backend Won't Start

```bash
# Check Python version
python --version  # Should be 3.9+

# Check if port 8000 is in use
lsof -i :8000

# Verify environment variables
cat backend/.env
```

### Frontend Dependencies Error

```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Firebase Errors

See **[FIREBASE_AUTH_SETUP.md](./FIREBASE_AUTH_SETUP.md)** Troubleshooting section

### API Key Invalid

1. Verify key is correct in .env / .env.local
2. Check API key quota hasn't been exceeded
3. Verify API is enabled in respective console

## 📈 Performance

- **Search Speed:** < 5 seconds for typical queries
- **Memory Retrieval:** Instant (local ChromaDB)
- **UI Response:** < 100ms for all interactions
- **Concurrent Users:** Limited only by backend resources

## 🔒 Security

✅ Firebase JWT token verification on every request
✅ Service account key excluded from source control
✅ Environment variables for all secrets
✅ CORS configured for frontend origin
✅ Graceful degradation when services unavailable
✅ User data scoped by authentication

## 📝 Documentation

- **[FIREBASE_AUTH_SETUP.md](./FIREBASE_AUTH_SETUP.md)** - Complete authentication setup
- **[AUTH_IMPLEMENTATION_COMPLETE.md](./AUTH_IMPLEMENTATION_COMPLETE.md)** - Architecture details
- **[VERIFICATION_REPORT.md](./VERIFICATION_REPORT.md)** - System verification results
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Detailed system architecture

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## 🚀 Deployment

### Production Checklist

- [ ] Firebase project created and configured
- [ ] All environment variables set (no hardcoded secrets)
- [ ] Frontend built: `npm run build`
- [ ] Backend tested with production URLs
- [ ] CORS properly configured
- [ ] API keys rotated and secured
- [ ] Database backed up
- [ ] SSL/TLS certificates configured
- [ ] Monitoring and logging enabled

### Recommended Platforms

**Frontend:** Vercel, Netlify, Firebase Hosting
**Backend:** AWS EC2, Google Cloud Run, DigitalOcean

## 📊 API Documentation

Backend Swagger UI: http://localhost:8000/docs

### Key Endpoints

- `POST /research` - Main research endpoint (requires auth)
- `POST /auth/verify` - Verify current user (requires auth)
- `POST /auth/logout` - Logout confirmation (requires auth)
- `GET /health` - Health check

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test
3. Commit: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open Pull Request

## 📄 License

[Add your license here]

## 🆘 Support

For issues or questions:
1. Check troubleshooting section
2. Review documentation
3. Check GitHub issues
4. Open a new issue with:
   - What you were doing
   - Error message
   - Steps to reproduce
   - Environment info

## 🎯 Roadmap

- [ ] Google OAuth login
- [ ] Password reset functionality
- [ ] Email verification
- [ ] Advanced search filters
- [ ] Research history/favorites
- [ ] Team collaboration
- [ ] Export/share research
- [ ] Mobile app

## 💡 Ideas

Have an idea to improve Insightor? Open an issue or discussion!

---

**Made with ❤️ using FastAPI, React, and Firebase**
