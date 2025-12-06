# How to Get Firebase Configuration Values

This guide shows you **exactly where to find** each Firebase configuration value needed for the frontend.

## Prerequisites

✅ You already have a Firebase project created
✅ You have Email/Password authentication enabled

If not, follow **Step 1-2** in [FIREBASE_AUTH_SETUP.md](./FIREBASE_AUTH_SETUP.md) first.

---

## Complete Step-by-Step Guide

### Step 1: Go to Firebase Project Settings

1. Open [Firebase Console](https://console.firebase.google.com/)
2. Select your Insightor project
3. Click the **⚙️ gear icon** (Project Settings) in the top left
4. You'll see the project overview page

![Screenshot would show: gear icon → Project Settings]

---

### Step 2: Find Your Web App Configuration

In Project Settings, you need to scroll down to find **"Your apps"** section.

**Method A: If you already have a web app registered**

1. Look for **"Your apps"** section at the bottom of Project Settings
2. You should see an app listed (might say something like "Insightor" or "Web App")
3. If it exists, click on it and proceed to **Step 3**

**Method B: If you don't see a web app registered**

1. In the **"Your apps"** section, click the **"</>"** icon (Web icon)
2. Enter app nickname: "Insightor Frontend"
3. Check "Also set up Firebase Hosting for this app" (optional)
4. Click "Register app"
5. Copy the config object (you'll need it)
6. You can skip "Add Firebase SDK" and "Deploy to Firebase Hosting"
7. Click "Continue to console"

---

### Step 3: Get Your Firebase Web Config

Now you should be in Project Settings with your web app visible.

**Look for the Firebase SDK snippet (appears in two formats):**

#### Option 1: If you see the config object directly

You might see code like:
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyC_1234567890...",
  authDomain: "insightor-project.firebaseapp.com",
  projectId: "insightor-project",
  storageBucket: "insightor-project.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abc123def456"
};
```

**Extract each value for your .env.local:**

```
VITE_FIREBASE_API_KEY=AIzaSyC_1234567890...
VITE_FIREBASE_AUTH_DOMAIN=insightor-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=insightor-project
VITE_FIREBASE_STORAGE_BUCKET=insightor-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789012
VITE_FIREBASE_APP_ID=1:123456789012:web:abc123def456
```

#### Option 2: If config is not visible

1. Click on your app in "Your apps" section
2. Look for **"SDK setup and configuration"** or a **"Config"** button
3. Select **"Config"** from the dropdown
4. You'll see the configuration object
5. Copy each value as shown in Option 1

---

## Individual Values Explained

Here's what each value means and where to find it in Firebase Console:

### 1️⃣ VITE_FIREBASE_API_KEY

**What it is:** Your public API key for the Firebase project

**Where to find it:**
- Project Settings → "Your apps" → Web app → Config
- Starts with `AIzaSy...` or similar
- Safe to expose (it's public)

**Example:**
```
VITE_FIREBASE_API_KEY=AIzaSyC_1234567890abcdefghijklmnopqrstuvwxyz
```

---

### 2️⃣ VITE_FIREBASE_AUTH_DOMAIN

**What it is:** The domain used for Firebase authentication (OAuth redirects)

**Where to find it:**
- Project Settings → "Your apps" → Web app → Config
- Format: `{project-name}.firebaseapp.com`
- Always contains `.firebaseapp.com`

**Example:**
```
VITE_FIREBASE_AUTH_DOMAIN=insightor-project.firebaseapp.com
```

**Note:** Your project name is visible in the Firebase Console URL bar
- URL: `https://console.firebase.google.com/project/insightor-project/overview`
- Project: `insightor-project`
- Auth Domain: `insightor-project.firebaseapp.com`

---

### 3️⃣ VITE_FIREBASE_PROJECT_ID

**What it is:** Your Firebase project's unique identifier

**Where to find it:**
- Project Settings → "Your apps" → Web app → Config
- Also visible in Project Settings → General tab
- Also in the Firebase Console URL: `...project/YOUR_PROJECT_ID/...`

**Example:**
```
VITE_FIREBASE_PROJECT_ID=insightor-project
```

---

### 4️⃣ VITE_FIREBASE_STORAGE_BUCKET

**What it is:** Your Cloud Storage bucket (even if you don't use it yet)

**Where to find it:**
- Project Settings → "Your apps" → Web app → Config
- Format: `{project-name}.appspot.com`
- Always contains `.appspot.com`

**Example:**
```
VITE_FIREBASE_STORAGE_BUCKET=insightor-project.appspot.com
```

---

### 5️⃣ VITE_FIREBASE_MESSAGING_SENDER_ID

**What it is:** Your Cloud Messaging sender ID

**Where to find it:**
- Project Settings → "Your apps" → Web app → Config
- Format: A 12-digit number like `123456789012`
- Also visible in: Project Settings → General tab → "Project number"

**Example:**
```
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789012
```

---

### 6️⃣ VITE_FIREBASE_APP_ID

**What it is:** Your app's unique identifier within the Firebase project

**Where to find it:**
- Project Settings → "Your apps" → Web app → Config
- Format: `1:123456789012:web:abc123def456`
- Starts with `1:` followed by the project number

**Example:**
```
VITE_FIREBASE_APP_ID=1:123456789012:web:abc123def456
```

---

## Visual Walkthrough

### Firebase Console - Project Settings

```
Firebase Console
    ↓
Select Project: "Insightor"
    ↓
Click ⚙️ (Project Settings)
    ↓
You are now in: Project Settings
    ↓
Scroll down to: "Your apps"
    ↓
See: "Insightor Frontend" (or your app name)
    ↓
Click on the app
    ↓
See: Firebase SDK snippet/Config
    ↓
Copy all values
```

### Project Settings Page Layout

```
┌─ Firebase Console ─────────────────────────────┐
│                                                 │
│  Project Settings for: insightor-project       │
│                                                 │
│  Tabs:                                          │
│  ├─ General (Project ID visible here)          │
│  ├─ Service Accounts                           │
│  ├─ Cloud Messaging                            │
│  └─ Integrations                               │
│                                                 │
│  ─────────────────────────────────────────     │
│  Your apps:                                     │
│  ├─ Insightor Frontend                         │
│  │  └─ Config Button ← CLICK HERE              │
│  └─ [+ Add app]                                │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Quick Copy-Paste Guide

1. **Open Firebase Console:**
   ```
   https://console.firebase.google.com/
   ```

2. **Go to Project Settings:**
   - Click your project
   - Click ⚙️ gear icon
   - Scroll to "Your apps"

3. **View your app config:**
   - Click on your web app
   - Look for the config object

4. **Copy these exact fields:**

   | Frontend Variable | Firebase Field |
   |---|---|
   | VITE_FIREBASE_API_KEY | apiKey |
   | VITE_FIREBASE_AUTH_DOMAIN | authDomain |
   | VITE_FIREBASE_PROJECT_ID | projectId |
   | VITE_FIREBASE_STORAGE_BUCKET | storageBucket |
   | VITE_FIREBASE_MESSAGING_SENDER_ID | messagingSenderId |
   | VITE_FIREBASE_APP_ID | appId |

5. **Paste into `frontend/.env.local`:**
   ```env
   VITE_FIREBASE_API_KEY=<value from Firebase>
   VITE_FIREBASE_AUTH_DOMAIN=<value from Firebase>
   VITE_FIREBASE_PROJECT_ID=<value from Firebase>
   VITE_FIREBASE_STORAGE_BUCKET=<value from Firebase>
   VITE_FIREBASE_MESSAGING_SENDER_ID=<value from Firebase>
   VITE_FIREBASE_APP_ID=<value from Firebase>
   VITE_API_BASE_URL=http://localhost:8000
   ```

---

## Common Issues

### ❌ "I can't find the config object"

**Solution:**
1. Make sure you're in Project Settings (⚙️ gear icon)
2. Scroll ALL the way down to "Your apps" section
3. If no apps listed, create one by clicking the web icon (</>) in "Your apps"

### ❌ "The values look different from the examples"

**That's OK!** Each Firebase project has unique values:
- `AIzaSyC_` prefix is standard
- Your project name replaces `insightor-project`
- Your project number replaces `123456789012`

### ❌ "I see a service account key instead"

**You're in the wrong place!** 
- Service account key is for backend (backend/service-keys/)
- Web config is what you need for frontend
- Make sure you're looking at "Your apps" section, not "Service Accounts"

### ❌ "The config shows different field names"

**Old Firebase SDK uses different format:**
- Old: Uses `databaseURL`, `measurementId`
- New: Uses the 6 fields shown above

**If you see extra fields:**
- `databaseURL` - Optional, ignore it
- `measurementId` - Optional, but can add it if present

---

## Verification Checklist

After copying all values, verify:

- [ ] `VITE_FIREBASE_API_KEY` starts with `AIzaSy`
- [ ] `VITE_FIREBASE_AUTH_DOMAIN` ends with `.firebaseapp.com`
- [ ] `VITE_FIREBASE_PROJECT_ID` doesn't have spaces
- [ ] `VITE_FIREBASE_STORAGE_BUCKET` ends with `.appspot.com`
- [ ] `VITE_FIREBASE_MESSAGING_SENDER_ID` is 12 digits
- [ ] `VITE_FIREBASE_APP_ID` starts with `1:`
- [ ] All values are in `frontend/.env.local`
- [ ] File is in `frontend/` directory (not `frontend/src/`)

---

## What To Do Next

1. ✅ Copy all 6 values from Firebase Console
2. ✅ Create/edit `frontend/.env.local`
3. ✅ Paste all values
4. ✅ Add `VITE_API_BASE_URL=http://localhost:8000`
5. ✅ Restart frontend: `npm run dev`
6. ✅ Test signup at http://localhost:5173/

---

## Still Need Help?

Check these resources:

1. **Firebase Official Docs:**
   https://firebase.google.com/docs/web/setup

2. **See it in Firebase Console:**
   https://console.firebase.google.com/

3. **Back to Setup Guide:**
   [FIREBASE_AUTH_SETUP.md](./FIREBASE_AUTH_SETUP.md)

4. **Setup Checklist:**
   [SETUP_CHECKLIST.md](./SETUP_CHECKLIST.md)

---

## Real Example

Here's what a real complete configuration looks like:

**In Firebase Console, you see:**
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyD8_zJxnV-pqR4wT9u-klMnOpQr-sTuVwXyZ",
  authDomain: "my-research-app.firebaseapp.com",
  projectId: "my-research-app",
  storageBucket: "my-research-app.appspot.com",
  messagingSenderId: "987654321098",
  appId: "1:987654321098:web:zyxwvutsrqponmlkjih"
};
```

**In `frontend/.env.local`, you paste:**
```env
VITE_FIREBASE_API_KEY=AIzaSyD8_zJxnV-pqR4wT9u-klMnOpQr-sTuVwXyZ
VITE_FIREBASE_AUTH_DOMAIN=my-research-app.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=my-research-app
VITE_FIREBASE_STORAGE_BUCKET=my-research-app.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=987654321098
VITE_FIREBASE_APP_ID=1:987654321098:web:zyxwvutsrqponmlkjih
VITE_API_BASE_URL=http://localhost:8000
```

**Then:**
```bash
cd frontend
npm run dev
```

**Open browser:**
```
http://localhost:5173/signup
```

---

**You're all set! 🎉**

