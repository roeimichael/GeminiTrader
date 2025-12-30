# START HERE - 3 Easy Steps

## Step 1: Create Your .env File

You already have your API keys in a `.env` file, which is **perfect**!

Your `.env` file should look like this:

```bash
GOOGLE_API_KEY="your-actual-key-here"
OPENAI_API_KEY="your-actual-key-here"
ALPHA_VANTAGE_API_KEY="your-actual-key-here"
```

✅ **Your `.env` file is already protected** - it's in `.gitignore` and will NEVER be committed to GitHub!

If you don't have a `.env` file yet:

```bash
cp .env.example .env
nano .env  # Add your real API keys
```

## Step 2: Start the Server

```bash
cd /home/user/GeminiTrader
./start.sh
```

That's it! The script will:
- Load your API keys from `.env` automatically
- Verify everything is configured
- Start the server

## Step 3: Open the Frontend

Open your browser and go to:

**http://localhost:8000**

You should see the **GeminiTrader interface** (not JSON)!

## Quick Test

1. Click **"Load Available Agents"** ✓
2. Click **"Initialize Agents"** ✓
3. Enter ticker: **AAPL**
4. Enter question: **"Should I invest?"**
5. Click **"Run Analysis"** ✓

## Security Check

Verify your `.env` file is protected:

```bash
git check-ignore .env
```

Should output: `.env` ✅

## Troubleshooting

**"GOOGLE_API_KEY not set" error?**
- Make sure `.env` file exists in `/home/user/GeminiTrader/`
- Make sure it has `GOOGLE_API_KEY="your-key"` (with quotes)
- No spaces around the `=` sign

**Still seeing JSON?**
- Restart the server
- Clear browser cache (Ctrl+Shift+R)

**API not working?**
- Check your GOOGLE_API_KEY is valid
- Check the backend console for error messages

## Important Files

| File | What It Is | Commit to Git? |
|------|------------|----------------|
| `.env` | Your real API keys | ❌ **NO** (protected) |
| `.env.example` | Template with placeholders | ✅ YES (safe) |
| `start.sh` | Startup script | ✅ YES (safe) |

## You're All Set!

Your API keys are secure and the application is ready to use.

For more details:
- **QUICKSTART.md** - Full quick start guide
- **SECURITY.md** - Security best practices
- **TEST_INSTRUCTIONS.md** - Complete testing guide
- **README.md** - Full project documentation
