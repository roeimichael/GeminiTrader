# GeminiTrader - AI Stock Analysis

Simple stock analysis tool using Google's Gemini AI.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with your Gemini API key:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

3. Run the application:
```bash
python main.py
```

## Features

- Analyzes 50 stocks across 5 sectors
- Uses Gemini AI for fundamental, technical, and sentiment analysis
- Dark theme GUI with live progress updates
- Export results to CSV

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key to your `.env` file

## Usage

1. Click "Test API" to verify your connection
2. Click "Run Analysis" to analyze all stocks
3. Click "Export CSV" to save results

## Customizing Prompts

Edit `prompts.json` to customize the analysis prompts. Use `{ticker}` as a placeholder for the stock symbol.
