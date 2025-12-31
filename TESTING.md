# GeminiTrader API Testing

This document describes how to test the GeminiTrader API to ensure all endpoints are working correctly.

## Test Scripts

### 1. Comprehensive Test Suite (`test_api.py`)

**Purpose:** Full end-to-end testing of all API endpoints with multiple scenarios.

**What it tests:**
- ✅ Health check endpoint
- ✅ Get available agents
- ✅ Initialize agent pool (minimal and full configurations)
- ✅ Run stock analysis queries (AAPL, MSFT)
- ✅ Session management (list, delete)
- ✅ Query history (get, clear)
- ✅ Debug controls (enable/disable)

**Run:**
```bash
python test_api.py
```

**Expected time:** 3-5 minutes (includes 2 full stock analyses)

**Output:** Colored terminal output with detailed test results and summary.

---

### 2. Quick Smoke Test (`test_api_quick.py`)

**Purpose:** Fast validation of critical endpoints during development.

**What it tests:**
- ✅ Health check
- ✅ Get agents
- ✅ Initialize pool
- ✅ List sessions
- ✅ Delete session

**Run:**
```bash
python test_api_quick.py
```

**Expected time:** 5-10 seconds

**Output:** Simple pass/fail indicators.

---

## Prerequisites

1. **Backend server must be running:**
   ```bash
   uvicorn app:app --reload --host localhost --port 8000
   ```

2. **Environment variables must be set:**
   - Ensure `.env` file exists with `GOOGLE_API_KEY`
   - API keys for yfinance/alpha_vantage (optional)

3. **Python dependencies:**
   ```bash
   pip install requests
   ```

---

## Test Scenarios

### Scenario 1: Minimal Agent Setup
- **Agents:** Market Analyst, Fundamentals Analyst (2 agents)
- **Ticker:** AAPL
- **Query:** "What is your analysis of this stock? Should I buy or sell?"
- **Purpose:** Test basic functionality with minimal agents

### Scenario 2: Full Agent Setup
- **Agents:** Market, Fundamentals, News, Bull Researcher, Bear Researcher (5 agents)
- **Ticker:** MSFT
- **Query:** "Should I invest in this company for long-term growth?"
- **Purpose:** Test full multi-agent analysis with debate

---

## Understanding Test Results

### Success Indicators (✓)
- Green checkmarks indicate passed tests
- All critical endpoints working correctly

### Failure Indicators (✗)
- Red X marks indicate failed tests
- Error details printed below the test name
- Check backend logs for more details

### Warning Indicators (⚠)
- Yellow warnings for non-critical issues
- Tests that failed but don't block other tests

---

## Common Issues and Solutions

### Issue: "Connection refused"
**Solution:** Backend server is not running. Start it with:
```bash
uvicorn app:app --reload --host localhost --port 8000
```

### Issue: "GOOGLE_API_KEY not found"
**Solution:** Create `.env` file with your API key:
```bash
GOOGLE_API_KEY="your-key-here"
```

### Issue: "Ticker validation failed"
**Solution:** Check that:
- yfinance is installed: `pip install yfinance`
- Internet connection is available
- Ticker symbol is valid (e.g., AAPL, MSFT, GOOGL)

### Issue: "Collection already exists"
**Solution:** This is now fixed, but if it occurs:
- Restart the backend server
- Delete ChromaDB data folder (if needed)

### Issue: Analysis times out
**Solution:**
- Check backend logs for errors
- Ensure Google API key is valid and has quota
- Try with fewer agents first

---

## Manual Testing with curl

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Get Agents
```bash
curl http://localhost:8000/api/agents
```

### Initialize Pool
```bash
curl -X POST http://localhost:8000/api/initialize-pool \
  -H "Content-Type: application/json" \
  -d '{
    "selected_agents": ["market_analyst", "fundamentals_analyst"],
    "session_id": "test_session"
  }'
```

### Run Analysis
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Should I buy this stock?",
    "ticker": "AAPL",
    "session_id": "test_session"
  }'
```

---

## CI/CD Integration

To use in automated testing:

```bash
# Run quick tests (for CI)
python test_api_quick.py
if [ $? -eq 0 ]; then
  echo "✅ Quick tests passed"
else
  echo "❌ Quick tests failed"
  exit 1
fi

# Run comprehensive tests (for release validation)
python test_api.py
```

---

## Performance Benchmarks

Expected response times on a typical setup:

| Endpoint | Expected Time |
|----------|--------------|
| `/api/health` | < 50ms |
| `/api/agents` | < 200ms |
| `/api/initialize-pool` | 1-3s (2 agents) |
| `/api/initialize-pool` | 3-8s (5+ agents) |
| `/api/query` | 30-90s (depends on agents) |
| `/api/sessions` | < 100ms |
| `/api/history` | < 200ms |

---

## Next Steps

After running tests successfully:

1. ✅ All endpoints working → Ready for frontend integration
2. ⚠️ Some warnings → Review non-critical issues
3. ✗ Critical failures → Check backend logs and fix issues

For production deployment, ensure all tests pass consistently.
