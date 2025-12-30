# Security Guide - API Keys Protection

## ✅ Your API Keys Are Protected

Your `.env` file is **already protected** and will NOT be committed to GitHub!

### Protection Status

✓ `.env` is listed in `.gitignore` (line 1)
✓ Git will ignore this file automatically
✓ Your API keys are safe from accidental commits

## Setting Up Your .env File

### 1. Create the .env file

If you don't have a `.env` file yet, create one:

```bash
cd /home/user/GeminiTrader

# Copy the example file
cp .env.example .env

# Edit with your actual API keys
nano .env
```

### 2. Add Your API Keys

Your `.env` file should look like this:

```bash
# REQUIRED: Google API Key for Gemini
GOOGLE_API_KEY="your-actual-google-api-key-here"

# OPTIONAL: OpenAI API Key
OPENAI_API_KEY="your-actual-openai-key-here"

# OPTIONAL: Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY="your-actual-alpha-vantage-key-here"
```

**Important:** Replace the placeholder values with your actual API keys!

### 3. Verify Protection

Check that your `.env` file is ignored by git:

```bash
git check-ignore .env
```

If it outputs `.env`, you're protected! ✅

## Security Best Practices

### ✅ DO:
- Keep API keys in `.env` file
- Add `.env` to `.gitignore` (already done!)
- Use `.env.example` for documentation (committed to git)
- Rotate API keys if they're ever exposed

### ❌ DON'T:
- Never commit `.env` to git
- Never hardcode API keys in source files
- Never share `.env` file publicly
- Never add API keys to documentation

## Verifying Your Setup

### Check if .env is in .gitignore

```bash
grep "^\.env$" .gitignore
```

Should output: `.env` ✅

### Check git won't commit it

```bash
git status
```

Your `.env` file should NOT appear in the list of files to commit!

### Check for accidental exposure

```bash
# This should show nothing related to your API keys
git log -p | grep -i "api.*key"
```

## What Files Are Safe to Commit

| File | Commit to Git? | Contains Secrets? |
|------|----------------|-------------------|
| `.env` | ❌ **NO** | Yes - Your real API keys |
| `.env.example` | ✅ YES | No - Just placeholders |
| `.gitignore` | ✅ YES | No |
| `start.sh` | ✅ YES | No |
| All other code | ✅ YES | No |

## Starting the Application

The `start.sh` script automatically loads your `.env` file:

```bash
./start.sh
```

This is equivalent to:

```bash
export GOOGLE_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
uvicorn app:app --reload --host localhost --port 8000
```

But much safer because the keys never appear in your shell history!

## Troubleshooting

### "GOOGLE_API_KEY not set" error

1. Make sure `.env` file exists:
   ```bash
   ls -la .env
   ```

2. Make sure it has your API key:
   ```bash
   cat .env
   ```

3. Make sure the format is correct (no spaces around `=`):
   ```bash
   GOOGLE_API_KEY="your-key-here"  # ✅ Correct
   GOOGLE_API_KEY = "your-key"     # ❌ Wrong (spaces)
   ```

### Accidentally committed .env file?

If you accidentally committed your `.env` file:

1. **Remove it from git history immediately:**
   ```bash
   git rm --cached .env
   git commit -m "Remove .env from git"
   git push
   ```

2. **Rotate your API keys immediately!**
   - Go to your API provider's dashboard
   - Generate new API keys
   - Update your `.env` file with new keys
   - Invalidate the old keys

3. **For complete history removal** (if already pushed):
   - Consider using `git filter-branch` or BFG Repo-Cleaner
   - Contact GitHub support if needed
   - But **rotate keys first** - this is critical!

## Getting API Keys

### Google API Key (Gemini)
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key to your `.env` file

### OpenAI API Key (Optional)
1. Go to: https://platform.openai.com/api-keys
2. Create new secret key
3. Copy to your `.env` file

### Alpha Vantage API Key (Optional)
1. Go to: https://www.alphavantage.co/support/#api-key
2. Claim your free API key
3. Copy to your `.env` file

## Summary

✅ Your setup is secure if:
- `.env` is in `.gitignore` ✓
- `.env` file contains your real keys
- You use `./start.sh` to run the application
- You never commit `.env` to git

🚨 Red flags (contact security immediately if any of these happen):
- `.env` appears in `git status`
- API keys appear in code files
- API keys in commit history
- Unexpected API usage charges

Your API keys are safe! 🔒
