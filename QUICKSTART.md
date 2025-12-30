# Quick Start Guide

## The Problem You Had

You were seeing JSON output instead of the frontend because:
- You navigated to `http://localhost:8000` which was the API root
- The frontend wasn't being served, only the API

## The Solution

I've configured FastAPI to serve the frontend directly! Now everything works from one URL.

## Setup Your API Keys (IMPORTANT)

### 1. Create your .env file

```bash
cd /home/user/GeminiTrader

# Copy the example file
cp .env.example .env

# Edit with your actual API keys
nano .env
```

### 2. Add your actual API keys

Your `.env` file should look like this:

```bash
GOOGLE_API_KEY="your-actual-google-api-key-here"
OPENAI_API_KEY="your-actual-openai-key-here"
ALPHA_VANTAGE_API_KEY="your-actual-alpha-vantage-key-here"
```

**Important:**
- Replace the placeholder text with your real API keys
- At minimum, you need `GOOGLE_API_KEY` for Gemini
- Your `.env` file is protected by `.gitignore` - it won't be committed to GitHub ✅

## How to Start

### Method 1: Use the startup script (Recommended)

```bash
cd /home/user/GeminiTrader

# The script automatically loads .env file
./start.sh
```

The script will:
- ✓ Load API keys from `.env` file
- ✓ Verify all requirements
- ✓ Start the server
- ✓ Show you all available URLs

### Method 2: Manual start

```bash
cd /home/user/GeminiTrader

# Load environment variables from .env
export $(cat .env | grep -v '^#' | xargs)

# Start the server
uvicorn app:app --reload --host localhost --port 8000
```

## Access the Application

Once the server is running, open your browser and go to:

**http://localhost:8000**

You should now see the **actual frontend UI** instead of JSON.

## What Changed

1. **Backend (`app.py`)**:
   - Root URL `/` now serves the frontend HTML
   - Static files (CSS, JS) are served from `/static/*`
   - API endpoints remain at `/api/*`
   - New endpoint `/api/info` for JSON API information

2. **Frontend (`frontend/app.js`)**:
   - API base URL now uses `window.location.origin` (auto-detects the server URL)
   - Works seamlessly with the backend

3. **Frontend (`frontend/index.html`)**:
   - CSS and JS paths updated to use `/static/` prefix

4. **Environment Variables**:
   - API keys are now loaded from `.env` file
   - `.env` is protected by `.gitignore` (never committed to GitHub)
   - Use `.env.example` as a template

## URL Structure

| URL | What You Get |
|-----|--------------|
| http://localhost:8000 | Frontend UI |
| http://localhost:8000/docs | API Documentation (Swagger) |
| http://localhost:8000/redoc | API Documentation (ReDoc) |
| http://localhost:8000/api/info | API Information (JSON) |
| http://localhost:8000/api/health | Health Check |
| http://localhost:8000/api/agents | List Available Agents |
| http://localhost:8000/static/* | Static Files (CSS, JS) |

## Testing the Frontend

Once you open http://localhost:8000, you should see:

1. **Green status indicator** at the top showing "API Connected"
2. **Multiple cards** for different features:
   - Available Agents
   - Session Management
   - Debug Controls
   - Query History
   - Stock Analysis Configuration

3. **No more black screen with JSON!**

## Quick Test

1. Start the server: `./start.sh`
2. Open browser: http://localhost:8000
3. Click **"Load Available Agents"** - should show all agents
4. Select analysts and click **"Initialize Agents"**
5. Enter ticker (e.g., AAPL), question, and click **"Run Analysis"**

## Troubleshooting

**Still seeing JSON?**
- Make sure you restart the server after the changes
- Clear your browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Try incognito/private browsing mode

**Static files not loading (no styling)?**
- Check the browser console (F12) for errors
- Verify files exist in `frontend/` directory
- Make sure the server restarted properly

**API not connecting?**
- Check the backend console for errors
- Verify GOOGLE_API_KEY is set in `.env` file
- Check if port 8000 is already in use

**"GOOGLE_API_KEY not set" error?**
- Make sure `.env` file exists
- Check that `.env` has your API key (no quotes or spaces around =)
- Run the startup script which loads `.env` automatically

## Security

✅ Your API keys are safe:
- `.env` file is listed in `.gitignore`
- Git will never commit your `.env` file
- Only `.env.example` (with placeholders) is committed

See `SECURITY.md` for more security information.

## Success Indicators

✅ You should see a styled webpage (not plain text/JSON)
✅ Status indicator shows green "API Connected"
✅ All buttons are clickable and styled
✅ CSS is loaded (colors, layout, styling visible)

## Need Help?

- Security guide: `SECURITY.md`
- Full testing guide: `TEST_INSTRUCTIONS.md`
- Project documentation: `README.md`
