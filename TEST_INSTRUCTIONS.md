# Testing Instructions for GeminiTrader

## Quick Start

### 1. Start the Backend API

```bash
# Make sure you're in the GeminiTrader directory
cd /home/user/GeminiTrader

# Set your API key (required)
export GOOGLE_API_KEY="your-google-api-key-here"

# Start the backend server
uvicorn app:app --reload --host localhost --port 8000
```

The API should start at: http://localhost:8000

### 2. Open the Frontend

Simply open the frontend in your browser:

```bash
# Option 1: Open directly in browser
open frontend/index.html

# Option 2: Use a simple HTTP server (recommended)
cd frontend
python -m http.server 8080
# Then open: http://localhost:8080
```

## Testing All Features

### Feature 1: API Health Check
- The status indicator at the top should turn **green** and say "API Connected"
- If it's red, check that the backend is running

### Feature 2: Available Agents
1. Click **"Load Available Agents"**
2. You should see all agent categories:
   - Analysts (market, fundamentals, news, social)
   - Researchers (bull, bear)
   - Managers (research, risk)
   - Risk Analysts (risky, safe, neutral)
   - Trader

### Feature 3: Session Management
1. Click **"List Active Sessions"**
2. Initially should show "No active sessions"
3. After initializing agents, you'll see your session listed

### Feature 4: Debug Controls
1. Click **"Enable Debug Mode"**
2. Check the backend console - you should see detailed debug logs
3. Click **"Disable Debug Mode"** to turn it off

### Feature 5: Initialize Agents
1. Select at least one analyst (all are checked by default)
2. Click **"Initialize Agents"**
3. You should see a success message
4. The "Run Analysis" button should now be enabled

### Feature 6: Run Stock Analysis
1. Enter a ticker symbol (e.g., **AAPL**, **MSFT**, **TSLA**)
2. Enter a date (defaults to today)
3. Enter your question (e.g., "Should I invest in this stock?")
4. Click **"Run Analysis"**
5. Wait 30-60 seconds for the analysis to complete
6. View results in 4 tabs:
   - **Classification**: Shows query analysis and agent selection
   - **Analysts**: Individual analyst reports
   - **Debate**: Bull vs Bear debate rounds
   - **Final Verdict**: Overall recommendation

### Feature 7: View History
1. After running an analysis, click **"View History"**
2. You should see your recent queries with:
   - Ticker symbol
   - Timestamp
   - Query text
   - Recommendation

### Feature 8: Clear History
1. Click **"Clear History"**
2. Confirm the action
3. History should be cleared

### Feature 9: Delete Session
1. Click **"Delete Current Session"**
2. Confirm the action
3. Session is deleted, and you'll need to re-initialize agents

## API Endpoints Test

You can also test endpoints directly using curl:

```bash
# Health check
curl http://localhost:8000/api/health

# Get available agents
curl http://localhost:8000/api/agents

# Initialize pool
curl -X POST http://localhost:8000/api/initialize-pool \
  -H "Content-Type: application/json" \
  -d '{"selected_agents": ["market_analyst", "fundamentals_analyst"]}'

# Run analysis (after initializing)
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Should I invest in this stock?",
    "ticker": "AAPL",
    "date": "2024-01-15"
  }'

# View history
curl http://localhost:8000/api/history

# List sessions
curl http://localhost:8000/api/sessions

# Enable debug
curl -X POST http://localhost:8000/api/debug/enable

# Disable debug
curl -X POST http://localhost:8000/api/debug/disable
```

## Expected Behavior

### Success Indicators
- ✅ Green "API Connected" status
- ✅ All buttons work without errors
- ✅ Analysis completes and shows results
- ✅ All tabs display content
- ✅ History shows previous queries
- ✅ Sessions list shows active sessions

### Common Issues

**Issue: API Offline**
- Solution: Make sure backend is running with `uvicorn app:app --reload --host localhost --port 8000`

**Issue: Agents not initializing**
- Solution: Check that at least one analyst is selected
- Solution: Check backend console for error messages

**Issue: Analysis fails**
- Solution: Ensure GOOGLE_API_KEY is set
- Solution: Check ticker symbol is valid (e.g., AAPL, MSFT)
- Solution: Check backend console for detailed errors

**Issue: CORS errors in browser**
- Solution: Use a proper HTTP server instead of file:// protocol
- Solution: Run `python -m http.server 8080` in the frontend directory

**Issue: Analysis takes too long**
- Expected: 30-60 seconds for full analysis
- Check: Backend console should show progress logs
- Note: First run may take longer due to cache misses

## Interactive API Documentation

FastAPI provides interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly from the Swagger UI interface.

## Troubleshooting

### Backend Logs
Check the backend console for detailed logs:
- INFO: High-level workflow events
- DEBUG: Detailed execution (enable with debug mode)
- WARNING: Recoverable issues
- ERROR: Failures

### Browser Console
Open browser developer tools (F12) and check the Console tab for:
- API call responses
- JavaScript errors
- Network requests

### Network Tab
In browser developer tools, check the Network tab to see:
- API request/response details
- HTTP status codes
- Response bodies

## Success Criteria

All features are working if:
1. ✅ API health check shows green status
2. ✅ Can load and view all available agents
3. ✅ Can initialize agent pool successfully
4. ✅ Can run stock analysis and get results
5. ✅ Can view results in all 4 tabs (classification, analysts, debate, verdict)
6. ✅ Can view query history
7. ✅ Can clear history
8. ✅ Can list active sessions
9. ✅ Can delete sessions
10. ✅ Can enable/disable debug mode

## Next Steps

If all tests pass:
- The frontend and backend are fully functional
- All API endpoints are working correctly
- The multi-agent system is operational
- Ready for production testing with real stock tickers

If any tests fail:
- Check the backend console for error messages
- Check browser console for JavaScript errors
- Verify environment variables are set
- Check API keys are valid
- Review the logs for specific error details
