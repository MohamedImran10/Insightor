# Insightor - AI-Powered Research Assistant

An intelligent web research application that combines web search, content analysis, and AI-powered summarization with **multi-user authentication** and persistent vector memory using **Pinecone**.

## 🌟 Features

- **🔐 Multi-User Authentication** - Secure Firebase email/password + Google OAuth authentication
- **🔍 Intelligent Web Search** - Find relevant information across the web using Tavily API
- **📖 Content Analysis** - Extract and clean content from web sources with citation tracking
- **🧠 AI Summarization** - Generate intelligent summaries using Google Gemini 2.5 Flash
- **💾 Advanced Memory System** - Store and retrieve past research with Pinecone vector database
- **⚡ Production Vector Storage** - Pinecone cloud-native vector database for scalable memory
- **🎨 Modern UI** - Beautiful, responsive React interface with Framer Motion animations
- **🌙 Dark Mode** - Comprehensive dark/light theme support
- **📱 Responsive Design** - Mobile-first design with Tailwind CSS
- **🚀 Production Ready** - Comprehensive error handling, graceful degradation, and deployment-ready

## 🏗️ Architecture

### Tech Stack

**Backend (Python FastAPI):**
- **FastAPI** - Async Python web framework with automatic OpenAPI documentation
- **Pinecone** - Production-grade vector database for memory storage and similarity search
- **Firebase Admin SDK** - Server-side authentication and user management
- **Google Gemini 2.5 Flash** - Latest LLM for intelligent content summarization
- **Tavily API** - Advanced web search with content extraction
- **SentenceTransformers** - Local embeddings generation (all-MiniLM-L6-v2)
- **Pydantic** - Data validation and settings management
- **Uvicorn** - ASGI server for production deployment

**Frontend (React + Vite):**
- **React 18** - Latest React with hooks and concurrent features
- **Vite** - Lightning-fast build tool and development server
- **React Router DOM** - Client-side routing for single-page application
- **Firebase SDK** - Client-side authentication with Google OAuth
- **Framer Motion** - Professional animations and micro-interactions
- **Tailwind CSS** - Utility-first CSS framework with custom design system
- **Lucide React** - Beautiful, consistent icon library
- **Axios** - HTTP client for API communication

**Authentication & Security:**
- **Firebase Authentication** - Email/password + Google OAuth with secure token management
- **JWT Verification** - Server-side token validation with Firebase Admin SDK
- **CORS Protection** - Configurable cross-origin resource sharing
- **Input Validation** - Comprehensive request validation with Pydantic

**Vector Database & Memory:**
- **Pinecone** - Cloud-native vector database with auto-scaling
- **Embedding Generation** - Local SentenceTransformers for privacy and speed
- **Semantic Search** - Advanced similarity search across research history
- **Memory Persistence** - Long-term storage of research contexts and insights

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (Backend development and deployment)
- **Node.js 18+** (Frontend development)
- **Firebase Project** (Authentication - free tier available)
- **Pinecone Account** (Vector database - free tier available)

### Required API Keys

- **Google Gemini API** - AI summarization ([Get key](https://aistudio.google.com/app/apikey))
- **Tavily Search API** - Web search ([Get key](https://tavily.com))
- **Pinecone API** - Vector database ([Get key](https://pinecone.io))
- **Firebase Config** - Authentication ([Setup guide](https://firebase.google.com/docs/web/setup))

### Backend Setup

```bash
# Clone repository
git clone <repository-url>
cd Insightor/backend

# Install Python dependencies
pip install -r requirements.txt

# Create .env file with your credentials
cp .env.example .env
# Edit .env and add:
# - FIREBASE credentials
# - GOOGLE_API_KEY=your_gemini_api_key
# - TAVILY_API_KEY=your_tavily_key
# - PINECONE_API_KEY=your_pinecone_key
# - PINECONE_ENVIRONMENT=us-east-1-aws

# Start the backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend runs on `http://localhost:8000` with automatic API docs at `/docs`

### Frontend Setup (Next.js)

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start the development server
npm run dev
```

Frontend runs on `http://localhost:3000`

## 🚀 Production Deployment

### Backend Deployment (Render)

1. **Create Render Account** at [render.com](https://render.com)
2. **Connect GitHub Repository**
3. **Create Web Service** with these settings:
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`

4. **Set Environment Variables** in Render dashboard:
```env
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=us-east-1-aws
USE_PINECONE=true
FIREBASE_ENABLED=true
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_CREDENTIALS_PATH=/app/service-keys/serviceAccountKey.json
```

5. **Upload Firebase Service Account** key to your repository in `backend/service-keys/`

### Frontend Deployment (Vercel)

1. **Create Vercel Account** at [vercel.com](https://vercel.com)
2. **Connect GitHub Repository**
3. **Import Project** with these settings:
   - **Framework**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Install Command**: `npm install`

4. **Set Environment Variables** in Vercel dashboard:
```env
NEXT_PUBLIC_API_URL=https://your-render-backend-url.onrender.com
```

5. **Deploy** - Automatic deployment on every push to main branch

### Alternative: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or individually:
docker build -t insightor-backend ./backend
docker build -t insightor-frontend ./frontend
```

## 🔐 Authentication Setup

Complete Firebase authentication setup:

### 1. Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" and follow the setup wizard
3. Enable Google Analytics (optional)

### 2. Enable Authentication Methods
1. Navigate to "Authentication" → "Sign-in method"
2. Enable **Email/Password** provider
3. Enable **Google** provider (add your domain to authorized domains)

### 3. Get Configuration Keys

**For Backend (Service Account):**
1. Go to "Project Settings" → "Service accounts"
2. Click "Generate new private key"
3. Save as `backend/service-keys/serviceAccountKey.json`

**For Frontend (Web Config):**
1. Go to "Project Settings" → "Your apps" → "Web app"
2. Copy the configuration object
3. Update `frontend/lib/config.js` with your values

### 4. Configure Environment Variables
Update your `.env` files with the Firebase credentials from steps above.

## 📖 Usage Guide

### Getting Started
1. **Sign Up**: Create account with email/password or Google OAuth
2. **Research**: Enter any query in natural language
3. **Explore Results**: View AI summary, sources, and insights
4. **Memory**: System automatically remembers past research for context
5. **History**: Access previous research sessions (coming soon)

### Research Examples

**Academic Research:**
- "Latest breakthroughs in quantum computing 2024"
- "CRISPR gene editing recent developments"
- "Climate change mitigation strategies"

**Business Intelligence:**
- "AI startup funding trends 2024"
- "Remote work productivity studies"
- "Cryptocurrency regulatory updates"

**Technology Analysis:**
- "Comparison of React vs Vue.js frameworks"
- "Best practices for API security"
- "Machine learning deployment strategies"

## 🗂️ Project Structure

```
Insightor/
├── backend/                        # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py                 # FastAPI app with routes
│   │   ├── config.py               # Settings & environment variables
│   │   ├── models.py               # Pydantic data models
│   │   ├── auth.py                 # Firebase authentication
│   │   ├── auth_middleware.py      # JWT token verification
│   │   ├── dependencies.py         # Route dependencies
│   │   └── agents/
│   │       ├── orchestrator.py     # Main research coordinator
│   │       ├── search_agent.py     # Tavily web search
│   │       ├── reader_agent.py     # Content extraction
│   │       ├── memory_agent.py     # Memory management
│   │       ├── gemini_summarizer.py # AI summarization
│   │       ├── pinecone_memory.py  # Pinecone vector storage
│   │       └── embeddings.py       # SentenceTransformers
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                 # Docker container config
│   ├── migrate_to_pinecone.py     # Data migration script
│   └── service-keys/               # Firebase credentials
│
├── frontend/                       # Next.js 14 Frontend
│   ├── app/
│   │   ├── layout.js               # Root layout with providers
│   │   ├── page.js                 # Home page (redirect to research)
│   │   ├── login/page.js           # Authentication login
│   │   ├── signup/page.js          # User registration
│   │   ├── research/page.js        # Main research interface
│   │   ├── history/page.js         # Research history
│   │   ├── profile/page.js         # User profile
│   │   └── globals.css             # Global styles & CSS variables
│   ├── components/
│   │   ├── ProtectedRoute.jsx      # Authentication guard
│   │   ├── ResearchApp.jsx         # Main research component
│   │   ├── SearchInput.jsx         # Query input with animations
│   │   ├── ResearchContainer.jsx   # Results display
│   │   └── Toast.jsx               # Notification system
│   ├── hooks/
│   │   ├── useAuth.js              # Firebase authentication
│   │   ├── useToast.jsx            # Toast notifications
│   │   └── useTheme.jsx            # Dark/light mode
│   ├── lib/
│   │   ├── config.js               # Environment configuration
│   │   ├── firebase.js             # Firebase client setup
│   │   └── api/
│   │       └── client.js           # API client with auth
│   ├── package.json                # Node.js dependencies
│   ├── next.config.js              # Next.js configuration
│   ├── tailwind.config.js          # Tailwind CSS config
│   └── .env.local                  # Environment variables
│
├── docker-compose.yml              # Multi-container setup
├── .gitignore                      # Git ignore patterns
└── README.md                       # This documentation
```

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
# ============================================
# API KEYS (Required)
# ============================================
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key

# ============================================
# VECTOR DATABASE - PINECONE (Production)
# ============================================
USE_PINECONE=true
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-east-1-aws

# ============================================
# FIREBASE AUTHENTICATION
# ============================================
FIREBASE_ENABLED=true
FIREBASE_CREDENTIALS_PATH=/path/to/serviceAccountKey.json
FIREBASE_PROJECT_ID=your_firebase_project_id

# ============================================
# SERVER CONFIGURATION
# ============================================
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=True
FRONTEND_URL=http://localhost:3000
```

**Frontend (.env.local):**
```env
# ============================================
# API CONFIGURATION
# ============================================
NEXT_PUBLIC_API_URL=http://localhost:8000

# ============================================
# FIREBASE WEB CONFIG (from Firebase Console)
# ============================================
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```
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

## 🔄 System Architecture & Workflow

### Request Flow
```
1. User Authentication (Firebase) 
   ↓
2. Query Input (Next.js Frontend)
   ↓ 
3. JWT Token Verification (FastAPI Backend)
   ↓
4. Web Search (Tavily API)
   ↓
5. Content Extraction (Reader Agent)
   ↓
6. Memory Retrieval (Pinecone Vector Search)
   ↓
7. AI Summarization (Google Gemini 2.5 Flash)
   ↓
8. Memory Storage (Pinecone Vector Database)
   ↓
9. Response with Results (JSON)
   ↓
10. UI Rendering (Next.js with Framer Motion)
```

### Agent System

**🔍 Search Agent**
- Performs intelligent web search using Tavily API
- Retrieves top relevant sources with metadata
- Handles rate limiting and error recovery

**📖 Reader Agent**  
- Fetches full article content from URLs
- Cleans HTML and extracts relevant text
- Removes advertisements, navigation, and noise
- Maintains source attribution for citations

**🧠 Memory Agent**
- Manages vector embeddings with SentenceTransformers
- Stores research chunks in Pinecone with metadata
- Performs semantic similarity search for context
- Maintains topic-based memory organization

**🎯 Orchestrator**
- Coordinates all agents in research pipeline  
- Manages parallel processing and error handling
- Optimizes memory usage and response times
- Provides comprehensive logging and metrics

**✨ Summarizer Agent**
- Generates intelligent summaries with Google Gemini
- Extracts key insights and actionable information  
- Maintains context from previous research sessions
- Provides cited sources for fact verification

## 🎨 UI/UX Features

### Design System
- **Modern Interface** - Clean, professional design with consistent spacing
- **Dark/Light Mode** - Comprehensive theming with smooth transitions
- **Responsive Design** - Mobile-first approach with adaptive layouts
- **Micro-interactions** - Smooth animations with Framer Motion
- **Loading States** - Progressive loading with skeleton screens
- **Error Handling** - Graceful error messages with recovery options

### Accessibility  
- **Keyboard Navigation** - Full keyboard support for all interactions
- **Screen Reader Support** - Semantic HTML with proper ARIA labels
- **Color Contrast** - WCAG AA compliant color schemes
- **Focus Management** - Clear focus indicators and logical tab order
- **Reduced Motion** - Respects user preferences for animations

### Performance
- **Code Splitting** - Dynamic imports for optimal bundle sizes
- **Image Optimization** - Next.js automatic image optimization
- **Caching Strategy** - Intelligent caching for API responses
- **Lazy Loading** - Components and content loaded on demand
- **Bundle Analysis** - Webpack bundle analyzer integration

## 🛡️ Security & Privacy

### Authentication Security
- **JWT Tokens** - Secure token-based authentication with expiration
- **Firebase Integration** - Enterprise-grade authentication infrastructure  
- **CORS Protection** - Configurable cross-origin resource sharing
- **Input Validation** - Comprehensive request validation with Pydantic
- **Rate Limiting** - API rate limiting to prevent abuse

### Data Privacy
- **Local Embeddings** - SentenceTransformers run locally for privacy
- **Secure API Keys** - Environment-based key management
- **No Data Logging** - User queries and results are not logged
- **GDPR Compliant** - User data handling follows privacy regulations

### Production Security
- **HTTPS Only** - Secure communication in production
- **Environment Isolation** - Separate development and production configs
- **Secret Management** - Secure handling of API keys and credentials
- **Error Sanitization** - No sensitive data in error responses

## 📈 Performance & Scaling

### Backend Performance
- **Async Processing** - FastAPI with async/await for concurrent requests
- **Connection Pooling** - Optimized database connections
- **Caching Layer** - In-memory caching for frequent queries
- **Background Tasks** - Non-blocking background processing
- **Health Monitoring** - Comprehensive health checks and metrics

### Frontend Performance  
- **Server Components** - Next.js 14 Server Components for faster loading
- **Static Generation** - Pre-built pages where possible
- **Optimistic Updates** - Immediate UI feedback for better UX
- **Request Deduplication** - Automatic deduplication of identical requests
- **Progressive Enhancement** - Works without JavaScript enabled

### Scaling Strategy
- **Pinecone Auto-scaling** - Vector database scales automatically
- **Render Auto-scaling** - Backend scales with demand
- **Vercel Edge Network** - Global CDN for frontend delivery  
- **Microservice Ready** - Architecture supports service separation
- **Database Partitioning** - User-based data partitioning support

## 🔧 Development & Testing

### Local Development
```bash
# Backend development with hot reload
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development with fast refresh
cd frontend  
npm run dev

# Full stack development
docker-compose up --build
```

### API Testing
- **Interactive Docs** - Automatic OpenAPI documentation at `/docs`
- **Health Endpoints** - System health monitoring at `/health`
- **Authentication Testing** - Token validation endpoints
- **Error Simulation** - Test error handling and recovery

### Code Quality
- **Type Safety** - TypeScript support for frontend
- **Linting** - ESLint and Prettier for code consistency
- **Git Hooks** - Pre-commit hooks for quality checks
- **Documentation** - Comprehensive inline documentation

## 🚀 Deployment Options

### Recommended: Vercel + Render
- **Frontend**: Vercel (Next.js optimized)
- **Backend**: Render (Python support)
- **Database**: Pinecone (managed vector DB)
- **Auth**: Firebase (managed authentication)

### Alternative: Railway
- **Full Stack**: Railway supports both Python and Node.js
- **One Platform**: Single dashboard for entire application
- **Auto-scaling**: Automatic scaling based on usage

### Enterprise: AWS/GCP/Azure
- **Frontend**: CloudFront + S3 or Azure Static Web Apps
- **Backend**: ECS/Kubernetes or App Engine  
- **Database**: Managed vector databases or self-hosted
- **CDN**: Global content delivery networks

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/login` - User login with email/password
- `POST /auth/register` - User registration  
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user profile

### Research Endpoints
- `POST /research` - Perform research query
- `GET /research/history` - Get user research history
- `GET /research/{id}` - Get specific research session
- `DELETE /research/{id}` - Delete research session

### System Endpoints
- `GET /health` - System health check
- `GET /health/detailed` - Detailed system status
- `GET /metrics` - System metrics (admin only)

## 🤝 Contributing

### Development Setup
1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create feature branch** from main
4. **Set up development environment** following setup guide
5. **Make changes** with comprehensive tests
6. **Submit pull request** with detailed description

### Code Style
- **Python**: Follow PEP 8 with Black formatter
- **JavaScript/TypeScript**: Follow Airbnb style guide
- **Documentation**: Update README for any new features
- **Testing**: Include tests for all new functionality

### Pull Request Process
1. **Update documentation** if needed
2. **Add tests** for new features  
3. **Ensure all tests pass** locally
4. **Update version numbers** if applicable
5. **Request review** from maintainers

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- **Next.js**: MIT License
- **FastAPI**: MIT License  
- **Firebase**: Apache License 2.0
- **Pinecone**: Commercial License
- **Framer Motion**: MIT License

## 🙋‍♂️ Support & Community

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides in `/docs`
- **Examples**: Sample implementations in `/examples`
- **API Reference**: Interactive docs at `/docs`

### Contributing
- **Bug Reports**: Use GitHub issue templates
- **Feature Requests**: Propose enhancements via issues
- **Code Contributions**: Submit pull requests
- **Documentation**: Help improve documentation

### Roadmap
- [ ] **Advanced Analytics** - Research session analytics and insights
- [ ] **Collaboration** - Team workspaces and sharing
- [ ] **Export Options** - PDF, Word, and citation exports  
- [ ] **Custom Models** - Support for additional LLM providers
- [ ] **Plugin System** - Extensible agent architecture
- [ ] **Mobile App** - Native mobile applications

---

**Built with ❤️ for researchers, students, and knowledge seekers worldwide.**

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

- [x] Google OAuth login
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
