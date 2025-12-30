#!/bin/bash
# GeminiTrader Startup Script

echo "=================================="
echo "GeminiTrader - Starting Backend"
echo "=================================="
echo ""

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "ERROR: GOOGLE_API_KEY environment variable is not set!"
    echo ""
    echo "Please set it with:"
    echo "  export GOOGLE_API_KEY=\"your-google-api-key-here\""
    echo ""
    exit 1
fi

echo "✓ GOOGLE_API_KEY is set"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "ERROR: app.py not found!"
    echo "Please run this script from the GeminiTrader directory"
    exit 1
fi

echo "✓ Found app.py"
echo ""

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "ERROR: frontend directory not found!"
    exit 1
fi

echo "✓ Found frontend directory"
echo ""

echo "Starting server on http://localhost:8000"
echo ""
echo "Available URLs:"
echo "  - Frontend:  http://localhost:8000"
echo "  - API Docs:  http://localhost:8000/docs"
echo "  - API Info:  http://localhost:8000/api/info"
echo "  - Health:    http://localhost:8000/api/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="
echo ""

# Start the server
uvicorn app:app --reload --host localhost --port 8000
