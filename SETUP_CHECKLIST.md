# Insightor Setup Completion Checklist

Follow this checklist to complete the Firebase authentication setup and get Insightor running.

## Phase 1: Firebase Project Setup ✅

- [ ] Go to https://console.firebase.google.com/
- [ ] Create a new Firebase project
- [ ] Wait for project creation to complete
- [ ] Go to **Authentication** → **Get Started**
- [ ] Enable **Email/Password** authentication method
- [ ] Go to **Project Settings** (gear icon)
- [ ] Copy **Project ID** (you'll need this)
- [ ] Go to **Service Accounts** tab
- [ ] Click **Generate New Private Key**
- [ ] Save as `backend/service-keys/serviceAccountKey.json`
- [ ] Verify file is NOT tracked in git: `git status backend/service-keys/`
- [ ] Go to Project Settings again
- [ ] Find your **Web API Configuration** (scroll down)
- [ ] Copy all Firebase config values for frontend

## Phase 2: Backend Configuration 🔧

- [ ] Open `backend/.env`
- [ ] Set `FIREBASE_ENABLED=true`
- [ ] Set `FIREBASE_CREDENTIALS_PATH=backend/service-keys/serviceAccountKey.json`
- [ ] Set `FIREBASE_PROJECT_ID=your_project_id_here` (from Firebase console)
- [ ] Verify `GOOGLE_API_KEY` is set (you should have this from earlier)
- [ ] Verify `TAVILY_API_KEY` is set (you should have this from earlier)
- [ ] Save the file

### Test Backend Setup

```bash
cd backend
python run.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ **Backend running successfully** - Keep it running

## Phase 3: Frontend Configuration 🎨

In a **new terminal window:**

- [ ] Navigate to frontend directory: `cd frontend`
- [ ] Create `.env.local` file: `cp .env.example .env.local`
- [ ] Edit `frontend/.env.local`
- [ ] Add your Firebase config values:
  - `VITE_FIREBASE_API_KEY=` (from Firebase console)
  - `VITE_FIREBASE_AUTH_DOMAIN=` (e.g., your-project.firebaseapp.com)
  - `VITE_FIREBASE_PROJECT_ID=` (same as backend)
  - `VITE_FIREBASE_STORAGE_BUCKET=` (from Firebase console)
  - `VITE_FIREBASE_MESSAGING_SENDER_ID=` (from Firebase console)
  - `VITE_FIREBASE_APP_ID=` (from Firebase console)
- [ ] Set `VITE_API_BASE_URL=http://localhost:8000`
- [ ] Save the file
- [ ] Install dependencies: `npm install`

### Test Frontend Installation

```bash
npm run dev
```

**Expected output:**
```
➜  Local:   http://localhost:5173/
```

✅ **Frontend running successfully** - Keep it running

## Phase 4: Test Authentication Flow 🧪

In your browser:

1. **Sign Up Test**
   - [ ] Open http://localhost:5173/
   - [ ] Click "Don't have an account? Sign up"
   - [ ] Enter test data:
     - Name: "Test User"
     - Email: "test@example.com"
     - Password: "testpass123"
   - [ ] Click "Sign Up"
   - [ ] Should be redirected to home page
   - [ ] Should see "Welcome Test User" in header

2. **Research Query Test**
   - [ ] Enter search query: "artificial intelligence"
   - [ ] Click search
   - [ ] Open DevTools → Network tab
   - [ ] Check the `research` request
   - [ ] Go to **Headers** tab
   - [ ] Verify **Authorization header** is present with Bearer token
   - [ ] Should see results displayed

3. **Logout Test**
   - [ ] Click "Logout" button in header
   - [ ] Should be redirected to /login
   - [ ] DevTools → Application → Storage → localStorage should be empty

4. **Login Test**
   - [ ] Click "Already have an account? Log in"
   - [ ] Enter email: "test@example.com"
   - [ ] Enter password: "testpass123"
   - [ ] Click "Log In"
   - [ ] Should be redirected to home page
   - [ ] Should see "Welcome Test User" again

✅ **Authentication working successfully**

## Phase 5: Verify Everything 📋

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173
- [ ] Can sign up new user
- [ ] Can make authenticated research queries
- [ ] Can logout and login again
- [ ] Token appears in API requests (Network tab)
- [ ] No errors in browser console (F12)
- [ ] No errors in backend terminal

## Phase 6: Clean Up Before Deployment 🧹

- [ ] Backend `.env` file is in `.gitignore`
- [ ] Frontend `.env.local` file is in `.gitignore`
- [ ] Service account key is in `.gitignore`
- [ ] No credentials appear in git history:
  ```bash
  git log --all -S "serviceAccountKey" --oneline
  # Should show no results
  ```
- [ ] Review `.gitignore` file to ensure all secrets are excluded

## Phase 7: Documentation Review 📚

- [ ] Read [README.md](./README.md) - Project overview
- [ ] Read [FIREBASE_AUTH_SETUP.md](./FIREBASE_AUTH_SETUP.md) - Detailed setup guide
- [ ] Read [AUTH_IMPLEMENTATION_COMPLETE.md](./AUTH_IMPLEMENTATION_COMPLETE.md) - Implementation details
- [ ] Bookmark [FIREBASE_AUTH_SETUP.md](./FIREBASE_AUTH_SETUP.md) for troubleshooting

## Optional: Advanced Features 🌟

### Enable Qdrant Cloud (Optional)

If you want to use Qdrant Cloud for distributed vector database:

- [ ] Go to https://cloud.qdrant.io/
- [ ] Create account and project
- [ ] Copy Qdrant API key and URL
- [ ] Add to `backend/.env`:
  ```env
  QDRANT_URL=https://your-instance-url.qdrant.io
  QDRANT_API_KEY=your_api_key
  ```
- [ ] Restart backend

### Enable Google Sign-In (Optional)

To add Google login as alternative to email/password:

1. Go to Firebase Console → Authentication → Sign-in methods
2. Enable "Google"
3. Configure OAuth consent screen
4. Update `frontend/src/pages/Login.jsx` to add Google button
5. Add logic to handle `signInWithPopup(auth, new GoogleAuthProvider())`

## Production Deployment Checklist 🚀

When ready to deploy:

- [ ] Create production Firebase project (separate from development)
- [ ] Update backend `.env` for production database/URLs
- [ ] Update frontend `.env.local` for production API endpoint
- [ ] Set `VITE_API_BASE_URL` to production backend URL
- [ ] Run `npm run build` in frontend to create optimized build
- [ ] Deploy frontend to Vercel/Netlify/Firebase Hosting
- [ ] Deploy backend to AWS/GCP/DigitalOcean/Heroku
- [ ] Enable SSL/TLS certificates
- [ ] Set up monitoring and error tracking
- [ ] Configure CORS for production domains
- [ ] Review Firebase security rules
- [ ] Enable Firebase rate limiting

## Troubleshooting Quick Links

If you encounter issues:

1. **Firebase Setup Problems** → See [FIREBASE_AUTH_SETUP.md Troubleshooting](./FIREBASE_AUTH_SETUP.md#troubleshooting)
2. **Backend Errors** → Check backend terminal for error messages
3. **Frontend Errors** → Check browser DevTools Console (F12)
4. **Network/API Issues** → Check Network tab in DevTools, look for request headers
5. **Token Issues** → Check localStorage in DevTools Application tab

## Success! 🎉

Once all checkboxes are complete:

✅ Insightor is fully set up with Firebase authentication
✅ Multi-user support is enabled
✅ System is production-ready
✅ You're ready to deploy

## Next Steps

1. **Create more test users** with different emails
2. **Test with real queries** to verify search quality
3. **Review logs** to understand system behavior
4. **Optimize performance** if needed
5. **Plan deployment** to production

## Support Resources

- [Firebase Docs](https://firebase.google.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [React Router Docs](https://reactrouter.com/)
- [Insightor GitHub](https://github.com/your-username/insightor)

---

**Version:** 1.0
**Last Updated:** 2024
**Status:** ✅ Ready for Production

