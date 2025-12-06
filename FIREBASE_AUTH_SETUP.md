# Firebase Authentication Setup Guide

This guide walks you through setting up Firebase Authentication for the Insightor application.

## Table of Contents

1. [Firebase Project Setup](#firebase-project-setup)
2. [Backend Configuration](#backend-configuration)
3. [Frontend Configuration](#frontend-configuration)
4. [Testing the Authentication Flow](#testing-the-authentication-flow)
5. [Troubleshooting](#troubleshooting)

---

## Firebase Project Setup

### Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Create a project"**
3. Enter your project name (e.g., "Insightor")
4. Follow the setup wizard and create the project
5. Once created, you'll be redirected to the project dashboard

### Step 2: Enable Authentication

1. In the left sidebar, click **"Authentication"**
2. Click **"Get Started"**
3. Select **"Email/Password"** as the sign-in method
4. Enable it and save

### Step 3: Get Your Backend Credentials (Service Account Key)

1. In the left sidebar, click **"Project Settings"** (gear icon)
2. Go to the **"Service Accounts"** tab
3. Click **"Generate New Private Key"**
4. Save the JSON file as `serviceAccountKey.json`
5. Place it in `backend/service-keys/` directory
6. **IMPORTANT:** Never commit this file to git (it's already in .gitignore)

### Step 4: Get Your Frontend Credentials

1. In the left sidebar, click **"Project Settings"** (gear icon)
2. Scroll down to **"Your apps"** section
3. Click on your web app (or create one if not exists)
4. Copy the Firebase config object containing:
   - `apiKey`
   - `authDomain`
   - `projectId`
   - `storageBucket`
   - `messagingSenderId`
   - `appId`

---

## Backend Configuration

### Step 1: Update Backend .env

Edit `backend/.env` and set:

```env
# Firebase Configuration
FIREBASE_ENABLED=true
FIREBASE_CREDENTIALS_PATH=backend/service-keys/serviceAccountKey.json
FIREBASE_PROJECT_ID=your_firebase_project_id_here

# Other existing configurations...
GOOGLE_API_KEY=your_key
TAVILY_API_KEY=your_key
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_key
```

### Step 2: Verify Backend Setup

The backend will automatically:
- Load Firebase credentials from the path specified in `FIREBASE_CREDENTIALS_PATH`
- Initialize the Firebase Admin SDK on startup
- Set up auth middleware for verifying tokens
- Protect the `/research` endpoint with authentication

Test the backend is running:

```bash
cd backend
python run.py
```

You should see:
```
INFO: Uvicorn running on http://0.0.0.0:8000
```

Test auth endpoint:

```bash
curl -X POST http://localhost:8000/auth/verify \
  -H "Authorization: Bearer invalid_token"
```

Expected response: `{"detail": "Invalid or expired token"}`

---

## Frontend Configuration

### Step 1: Create .env.local File

Copy the example file and fill in your Firebase credentials:

```bash
cp frontend/.env.example frontend/.env.local
```

### Step 2: Edit frontend/.env.local

Add your Firebase credentials from Step 4 of Firebase Project Setup:

```env
VITE_FIREBASE_API_KEY=AIzaSyC_your_actual_key_here
VITE_FIREBASE_AUTH_DOMAIN=insightor-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=insightor-project
VITE_FIREBASE_STORAGE_BUCKET=insightor-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789012
VITE_FIREBASE_APP_ID=1:123456789012:web:abc123def456

VITE_API_BASE_URL=http://localhost:8000
```

### Step 3: Install Dependencies

```bash
cd frontend
npm install
```

This will install `react-router-dom`, `firebase`, and other required packages.

### Step 4: Start Frontend Development Server

```bash
npm run dev
```

You should see:
```
VITE v5.0.0  ready in 123 ms

➜  Local:   http://localhost:5173/
```

---

## Testing the Authentication Flow

### Test 1: Sign Up

1. Open http://localhost:5173/ in your browser
2. You should be redirected to http://localhost:5173/login
3. Click **"Don't have an account? Sign up"**
4. Enter:
   - Full Name: "Test User"
   - Email: "testuser@example.com"
   - Password: "testpass123"
   - Confirm Password: "testpass123"
5. Click **"Sign Up"**

**Expected Result:**
- User created in Firebase
- Redirected to home page (/)
- Header shows "Welcome Test User"
- Logout button visible

### Test 2: Research Query

1. With logged-in user, you should see the research interface
2. Enter a search query: "artificial intelligence trends"
3. Click search

**Expected Result:**
- Query sent with Authorization header
- Results displayed from backend
- Check browser DevTools → Network to verify Authorization header is included

### Test 3: Logout

1. Click **"Logout"** button in header
2. Should be redirected to /login
3. localStorage should be cleared (token removed)

**Expected Result:**
- Redirected to login page
- Cannot access / without logging in again

### Test 4: Login

1. Click **"Already have an account? Log in"**
2. Enter:
   - Email: "testuser@example.com"
   - Password: "testpass123"
3. Click **"Log In"**

**Expected Result:**
- Same user object loaded
- Redirected to home page
- Same as after signup

---

## Troubleshooting

### Issue: "Missing Authorization header" Error

**Cause:** Frontend not sending token in API requests

**Solution:**
1. Check browser DevTools → Application → Storage → localStorage
2. Verify `id_token`, `user_id`, and `user_email` are stored
3. Check browser console for errors in `api/client.js`

### Issue: "Invalid or expired token" Error

**Cause:** Token is invalid or has expired

**Solution:**
1. Logout and login again (gets new token)
2. Check token expiration: Tokens expire after 1 hour by default
3. Firebase SDK should auto-refresh before expiration

### Issue: 401 Unauthorized on /research Endpoint

**Cause:** 
- Token not being sent
- Backend not receiving Authorization header correctly
- Token verification failed

**Solution:**
1. Check backend logs for detailed error message
2. Verify backend .env has correct FIREBASE_CREDENTIALS_PATH
3. Test with curl:
```bash
# Get a token (after signing up in UI)
TOKEN=$(cat your_firebase_token.txt)

curl -X POST http://localhost:8000/research \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

### Issue: "Cannot find module 'firebase'"

**Cause:** Dependencies not installed

**Solution:**
```bash
cd frontend
npm install
npm run dev
```

### Issue: React Router Not Working

**Cause:** Missing react-router-dom package

**Solution:**
```bash
cd frontend
npm install react-router-dom
npm run dev
```

### Issue: VITE_* Environment Variables Not Loading

**Cause:** 
- .env.local file in wrong location
- Server not restarted after creating .env.local
- Variable names don't start with VITE_

**Solution:**
1. Ensure .env.local is in `frontend/` directory (not `frontend/src/`)
2. Restart dev server: Ctrl+C then `npm run dev`
3. Verify variable names start with `VITE_`
4. Check browser DevTools Console for import.meta.env values

### Issue: Firebase Initialization Error

**Cause:**
- Invalid API key in environment
- Firebase project not created
- Authentication not enabled

**Solution:**
1. Double-check all VITE_FIREBASE_* values from Firebase Console
2. Verify Authentication is enabled in Firebase Console
3. Check browser console for specific Firebase error

### Issue: Backend Not Accepting Requests from Frontend

**Cause:** CORS issue

**Solution:**
1. Verify backend is running on http://localhost:8000
2. Check browser Network tab for CORS errors
3. Backend should have CORS enabled for localhost:5173

---

## Architecture Overview

### Authentication Flow

```
User Sign Up/Login
        ↓
Firebase Client SDK (firebase.js)
        ↓
Get ID Token from Firebase
        ↓
Store in localStorage
        ↓
Include in API Requests (api/client.js)
        ↓
Backend Receives Token (auth_middleware.py)
        ↓
Verify with Firebase Admin SDK
        ↓
Extract User Info (uid, email, name)
        ↓
Inject into Request Dependencies
        ↓
Endpoint Receives Authenticated User
```

### File Structure

```
frontend/src/
├── App.jsx                          # Main app with routing
├── pages/
│   ├── Login.jsx                   # Login page
│   ├── Signup.jsx                  # Signup page
│   └── ResearchApp.jsx             # Research interface
├── components/
│   ├── ProtectedRoute.jsx          # Auth-required route wrapper
│   ├── SearchInput.jsx
│   └── ResearchContainer.jsx
├── hooks/
│   └── useAuth.js                  # Auth state management
├── api/
│   └── client.js                   # API client with token headers
├── firebase.js                     # Firebase SDK config
└── ...

backend/app/
├── main.py                         # FastAPI app with auth endpoints
├── auth_middleware.py              # Token verification
├── dependencies.py                 # Route protection dependencies
├── models.py
├── config.py
├── agents/
└── ...
```

### Key Components

**Frontend:**
- **Login.jsx / Signup.jsx:** User authentication UI
- **useAuth.js:** React hook tracking login state
- **api/client.js:** Fetches with automatic token header
- **ProtectedRoute.jsx:** Wraps routes requiring auth

**Backend:**
- **auth_middleware.py:** Verifies Firebase JWT tokens
- **dependencies.py:** FastAPI dependencies for protected routes
- **main.py:** `/auth/verify` and `/auth/logout` endpoints

---

## Security Notes

### What's Protected?

- ✅ User passwords stored securely by Firebase
- ✅ JWT tokens verified on every protected request
- ✅ Service account key never exposed to frontend
- ✅ Tokens stored in localStorage (consider httpOnly cookies for production)
- ✅ Single-user fallback available if Firebase disabled

### What to Remember

- 🔐 Never commit `serviceAccountKey.json` to git
- 🔐 Never expose Firebase API key in backend code (frontend only)
- 🔐 Tokens expire after 1 hour (Firebase SDK auto-refreshes)
- 🔐 Always use HTTPS in production
- 🔐 Consider using httpOnly cookies for token storage instead of localStorage

---

## Production Deployment

### Before Deploying

1. ✅ Remove localhost URLs from environment variables
2. ✅ Update VITE_API_BASE_URL to production backend URL
3. ✅ Ensure Firebase rules are properly configured
4. ✅ Use environment-specific Firebase projects (dev vs prod)
5. ✅ Enable HTTPS for all endpoints
6. ✅ Consider using secure httpOnly cookies for token storage

### Deployment Platforms

**Frontend:** Vercel, Netlify, Firebase Hosting
**Backend:** AWS, GCP, DigitalOcean, Heroku

---

## Additional Resources

- [Firebase Authentication Documentation](https://firebase.google.com/docs/auth)
- [Firebase Admin SDK for Python](https://firebase.google.com/docs/admin/setup)
- [React Router Documentation](https://reactrouter.com/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)

