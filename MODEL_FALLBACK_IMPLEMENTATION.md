# Model Fallback Mechanism - Implementation Complete

## Overview
Implemented a robust automatic fallback system that tries multiple Gemini model versions in order until one works. This solves the 404 NOT_FOUND errors and provides resilience against model deprecation and quota issues.

## What Was Changed

### 1. New File: `tradingagents/llm_utils.py`
**Safe Model Factory** with intelligent fallback logic:

```python
create_gemini_model_with_fallback(model_candidates, api_key, temperature, max_retries)
```

**How It Works:**
1. Takes an ordered list of model names (e.g., `["gemini-1.5-flash-002", "gemini-1.5-flash-001", "gemini-1.5-flash"]`)
2. For each model:
   - Initializes `ChatGoogleGenerativeAI` with `max_retries=6`
   - Tests with a minimal "Hello" invocation
   - If successful → returns the model immediately
   - If 404 (Not Found) or 429 (Quota Exhausted) → tries next model
   - Logs all attempts and results
3. If all models fail → raises clear error with diagnostic info

**Convenience Functions:**
- `get_quick_thinking_llm(config)` - For analyst agents
- `get_deep_thinking_llm(config)` - For planner/supervisor agents

### 2. Updated: `tradingagents/config.py`

**Before:**
```python
"quick_think_llm": "gemini-1.5-flash",
"deep_think_llm": "gemini-1.5-pro",
```

**After:**
```python
"quick_think_llm_candidates": [
    "gemini-1.5-flash-002",  # Primary: Latest, fastest, smartest
    "gemini-1.5-flash-001",  # Secondary: Previous stable version
    "gemini-1.5-flash",      # Fallback: Generic alias
],
"deep_think_llm_candidates": [
    "gemini-1.5-pro-002",    # Primary: Latest stable Pro
    "gemini-1.5-pro-001",    # Secondary: Previous stable Pro
    "gemini-1.5-pro",        # Fallback: Generic alias
],
```

Legacy single-model config still present for backward compatibility.

### 3. Updated: `tradingagents/agent_pool.py`

**Before:**
```python
self.llm_quick = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=api_key
)
```

**After:**
```python
self.llm_quick = get_quick_thinking_llm(config)
self.llm_deep = get_deep_thinking_llm(config)
```

### 4. Updated: `tradingagents/query_classifier.py`

**Before:**
```python
self.llm = ChatGoogleGenerativeAI(
    model=self.config.get("quick_think_llm", "gemini-1.5-flash"),
    temperature=0.0
)
```

**After:**
```python
self.llm = get_quick_thinking_llm(self.config, temperature=0.0)
```

### 5. Updated: `tradingagents/graph/trading_graph.py`

**Before:**
```python
elif self.config["llm_provider"].lower() == "google":
    self.deep_thinking_llm = ChatGoogleGenerativeAI(model=self.config["deep_think_llm"])
    self.quick_thinking_llm = ChatGoogleGenerativeAI(model=self.config["quick_think_llm"])
```

**After:**
```python
elif self.config["llm_provider"].lower() == "google":
    self.deep_thinking_llm = get_deep_thinking_llm(self.config)
    self.quick_thinking_llm = get_quick_thinking_llm(self.config)
```

## How to Test

### 1. Restart Your Backend Server
```bash
# Stop current server (Ctrl+C)
uvicorn app:app --reload
```

### 2. Watch the Logs
When the server starts, you should see log messages like:
```
INFO | tradingagents.llm_utils | Attempting to initialize model: gemini-1.5-flash-002
INFO | tradingagents.llm_utils | Testing model gemini-1.5-flash-002 with minimal invocation...
INFO | tradingagents.llm_utils | ✓ Successfully initialized and tested model: gemini-1.5-flash-002
```

Or if the first model fails:
```
WARNING | tradingagents.llm_utils | ✗ Model gemini-1.5-flash-002 not found (404), trying next candidate...
INFO | tradingagents.llm_utils | Attempting to initialize model: gemini-1.5-flash-001
INFO | tradingagents.llm_utils | ✓ Successfully initialized and tested model: gemini-1.5-flash-001
```

### 3. Test the API
Try initializing a pool and running a query:

```bash
# Initialize pool
curl -X POST http://localhost:8000/api/initialize-pool \
  -H "Content-Type: application/json" \
  -d '{"selected_agents": ["market_analyst", "fundamentals_analyst"]}'

# Run analysis
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Should I invest in AAPL?",
    "context": {"ticker": "AAPL"}
  }'
```

## Expected Behavior

### Success Scenario
- **Primary model works:** Uses `gemini-1.5-flash-002` immediately
- **Fast startup:** Single test invocation per LLM type
- **No errors:** Analysis runs smoothly

### Fallback Scenario
- **Primary model 404:** Automatically tries `gemini-1.5-flash-001`
- **Secondary works:** Continues with that model
- **Clear logging:** Shows which model was selected
- **No user impact:** System works transparently

### Complete Failure Scenario (All Models Fail)
- **Clear error message:** Lists all attempted models
- **Last error details:** Shows why the final attempt failed
- **Diagnostic info:** Helps determine if it's an API key issue, network problem, or model availability

## Benefits

1. **Automatic Recovery:** No manual intervention needed when models are deprecated
2. **Zero Downtime:** Seamlessly switches to working models
3. **Quota Handling:** Tries alternative models when quota is exhausted
4. **Clear Diagnostics:** Detailed logging for troubleshooting
5. **Backward Compatible:** Still works with legacy single-model config
6. **Production Ready:** Configured with `max_retries=6` for rate limiting

## Troubleshooting

### If All Models Fail
Check the error message for:
- **404 errors on all models:** Your API key might not have access to these models
- **Authentication errors:** Check `GOOGLE_API_KEY` in `.env`
- **Network errors:** Check internet connectivity

### Run the Diagnostic Script
```bash
python list_gemini_models.py
```
This shows all models available in your account.

### Adjust Model Candidates
If certain models aren't available in your account, edit `tradingagents/config.py`:
```python
"quick_think_llm_candidates": [
    "gemini-pro",  # Use models that work for your account
    "gemini-1.0-pro",
],
```

## Files Modified
- ✅ `tradingagents/llm_utils.py` (NEW - 140 lines)
- ✅ `tradingagents/config.py` (Added model candidate lists)
- ✅ `tradingagents/agent_pool.py` (Uses factory functions)
- ✅ `tradingagents/query_classifier.py` (Uses factory functions)
- ✅ `tradingagents/graph/trading_graph.py` (Uses factory functions)

All changes committed and pushed to: `claude/refactor-api-backend-O96OJ`
