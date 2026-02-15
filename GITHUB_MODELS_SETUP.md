# GitHub Models Setup Guide (FREE LLM)

## Overview

Insightor now supports **GitHub Models** as a free fallback for LLM summarization when Google Gemini API is unavailable due to location restrictions.

### LLM Priority (Fallback Chain)
1. **Google Gemini** (primary)
2. **GitHub Models** (free tier) ← **RECOMMENDED**
3. **Claude** (optional, paid)
4. **Text Extraction** (fallback)

---

## GitHub Models - Free Tier Benefits

✅ **Completely Free** - No credit card required  
✅ **Uses Your GitHub Account** - Existing account only  
✅ **Multiple Models** - gpt-4o, Llama 3.1 405B, Phi-4  
✅ **OpenAI Compatible API** - Standard `openai` library  

### Free Tier Rate Limits (2026)

| Metric | Limit |
|--------|-------|
| **Requests Per Minute (RPM)** | 10-15 |
| **Requests Per Day (RPD)** | 50-150 |
| **Input Tokens** | ~8,000 |
| **Output Tokens** | ~4,000 |
| **Concurrent Requests** | 2 |

*Suitable for prototyping and development*

---

## Step 1: Generate GitHub Personal Access Token (PAT)

1. Go to GitHub Settings:
   ```
   https://github.com/settings/tokens?type=beta
   ```

2. Click **"Generate new token"** → **"Fine-grained token"**

3. **Token Details:**
   - **Token name:** `Insightor-Models`
   - **Expiration:** 90 days (or custom)
   - **Account permissions:** Search for "Models"
   - **Grant:** ✅ **"Model inference"** (Read-only)

4. Click **"Generate token"** and **copy immediately**

5. Token will look like:
   ```
   github_pat_11A...something...xyz
   ```

---

## Step 2: Configure Environment Variables

### Development (Local)

1. Create/update `backend/.env`:

```env
GITHUB_TOKEN=github_pat_your_copied_token_here
GOOGLE_API_KEY=your_gemini_key_here
TAVILY_API_KEY=your_tavily_key_here
FIREBASE_ENABLED=true
FIREBASE_CREDENTIALS_PATH=service-keys/serviceAccountKey.json
FIREBASE_PROJECT_ID=your_firebase_project_id
```

2. Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

3. Start backend:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production (Render)

1. Go to **Render Dashboard** → Select **Insightor** service

2. Navigate to **Environment**

3. Add/Update these variables:
   ```
   GITHUB_TOKEN=github_pat_your_token_here
   GOOGLE_API_KEY=your_gemini_key
   TAVILY_API_KEY=your_tavily_key
   USE_PINECONE=true
   PINECONE_API_KEY=your_pinecone_key
   FIREBASE_ENABLED=true
   FIREBASE_PROJECT_ID=your_firebase_project_id
   ```

4. Click **"Save"** → Render will auto-redeploy (1-2 minutes)

---

## Step 3: How It Works (Automatic)

When a user makes a research query:

1. **Gemini API is attempted first**
   - If successful → Returns full AI summary ✅
   - If fails with location error → Falls back to GitHub Models

2. **GitHub Models is used as fallback**
   - Generates professional summary with gpt-4o
   - Same quality as Gemini but free tier
   - If rate-limited → Falls back to Claude (if available)

3. **Text extraction fallback**
   - If all LLM services fail
   - Extracts snippets and titles directly
   - User still gets results ✅

### Log Output Example

```
⚠️ Google Gemini API location restriction detected.
🔄 Attempting summarization with GitHub Models (free)...
✅ GitHub Models summary generated successfully
```

---

## Testing the Setup

### Test GitHub Models Directly

```bash
# Install openai client
pip install openai

# Create test_github_models.py
```

```python
import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def test():
    client = AsyncOpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.getenv("GITHUB_TOKEN"),
    )
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are helpful assistant"},
            {"role": "user", "content": "What is machine learning in 2 sentences?"}
        ],
        max_tokens=100,
    )
    
    print(response.choices[0].message.content)

asyncio.run(test())
```

```bash
python test_github_models.py
```

### Test Insightor with GitHub Models

1. Search for anything on your Insightor app
2. Check Render logs:
   ```
   🔄 Attempting summarization with GitHub Models...
   ✅ GitHub Models summary generated successfully
   ```

3. Verify summaries are displayed correctly ✅

---

## Troubleshooting

### "GitHub token is invalid"
- ✅ Make sure token starts with `github_pat_`
- ✅ Check token has "Model inference" permission
- ✅ Token not expired

### "Rate limit exceeded"
- GitHub free tier: 10-15 requests/minute
- Solution: Wait 1-2 minutes or upgrade to paid tier
- Or use Claude as backup

### "GitHub Models API error"
- ✅ Check GITHUB_TOKEN is set in `.env`
- ✅ Verify network connectivity
- ✅ Check Render logs for detailed error
- Falls back to text extraction automatically

### Gemini still showing errors
- ✅ Verify GITHUB_TOKEN is properly set in Render
- ✅ Check that Render has redeployed after env update
- ✅ Do a hard refresh of frontend (Ctrl+Shift+R)

---

## Comparison: Gemini vs GitHub Models

| Feature | Gemini | GitHub Models |
|---------|--------|---------------|
| **Cost** | $0.075/1M input tokens | Free (rate-limited) |
| **Quality** | Excellent | Excellent (gpt-4o) |
| **Speed** | Fast | Fast |
| **Rate Limits** | Generous (free tier) | Limited (10-15/min) |
| **Location** | US-restricted | ✅ Worldwide |
| **Setup** | API key from Google | GitHub account |

**Best Practice:** Use Gemini as primary, GitHub Models as free fallback

---

## Next Steps

1. ✅ Generate GitHub PAT (5 minutes)
2. ✅ Add GITHUB_TOKEN to `.env` (local) and Render (production)
3. ✅ Test with a search query
4. ✅ Check logs to confirm GitHub Models is being used
5. ✅ Results should show with proper summaries

---

## Support

- GitHub Models Docs: https://github.com/marketplace/models
- Insightor Issues: https://github.com/MohamedImran10/Insightor/issues
- GitHub Support: https://github.com/support
