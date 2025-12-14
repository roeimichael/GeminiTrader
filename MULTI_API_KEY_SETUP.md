# Multi-API Key Setup Guide

## Overview

GeminiTrader now supports using **multiple Gemini API keys** to automatically cycle through them, helping you:
- **Process stocks faster** by avoiding rate limits
- **Maximize free tier usage** across multiple Google accounts
- **Ensure continuous operation** with automatic failover

## Quick Start

### Option 1: Single API Key (Simplest)

In your `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Option 2: Multiple Keys - Comma Separated (Recommended)

In your `.env` file:
```env
GEMINI_API_KEYS=key1,key2,key3
```

### Option 3: Multiple Keys - Numbered

In your `.env` file:
```env
GEMINI_API_KEY_1=first_key_here
GEMINI_API_KEY_2=second_key_here
GEMINI_API_KEY_3=third_key_here
```

## How It Works

1. **Automatic Rotation**: When a rate limit is detected (429 error), the system automatically switches to the next available API key
2. **Optimized Delays**: With multiple keys, rate limit delays are reduced (12s → 6s between calls)
3. **Smart Failover**: If all keys are rate-limited, the system falls back to exponential backoff retry logic
4. **Backward Compatible**: Old configurations with single `GEMINI_API_KEY` still work perfectly

## Benefits by Number of Keys

| Keys | Processing Speed | Free Tier Requests/Day | Estimated Time for 100 Stocks |
|------|-----------------|------------------------|------------------------------|
| 1    | Baseline        | 1,500                  | ~60 minutes                  |
| 2    | 2x faster       | 3,000                  | ~30 minutes                  |
| 3    | 3x faster       | 4,500                  | ~20 minutes                  |
| 5    | 5x faster       | 7,500                  | ~12 minutes                  |

## Getting Multiple API Keys

1. Create multiple Google accounts (or use existing ones)
2. For each account:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in
   - Click "Create API Key"
   - Copy the key
3. Add all keys to your `.env` file using one of the formats above

## Example Configurations

### For Daily Analysis (100 stocks)
**Recommended**: 2-3 API keys
```env
GEMINI_API_KEYS=AIzaSy...key1,AIzaSy...key2,AIzaSy...key3
```

### For Heavy Testing/Development
**Recommended**: 3-5 API keys
```env
GEMINI_API_KEY_1=AIzaSy...key1
GEMINI_API_KEY_2=AIzaSy...key2
GEMINI_API_KEY_3=AIzaSy...key3
GEMINI_API_KEY_4=AIzaSy...key4
GEMINI_API_KEY_5=AIzaSy...key5
```

### For Production with Paid Tier
**Note**: With paid tier, rate limits are much higher (1000-2000 RPM), so you might only need 1 key
```env
GEMINI_API_KEY=your_paid_tier_key_here
```

## Running the Overnight Analysis

```bash
python overnight_analysis.py
```

The script will:
- Automatically detect and load all your API keys
- Display the number of keys loaded
- Optimize delays based on key count
- Rotate through keys on rate limit errors

## Troubleshooting

### "No API keys found" Error
- Make sure your `.env` file exists in the project root
- Check that you've uncommented the correct option (remove the `#` at the start)
- Verify there are no spaces in comma-separated keys

### Rate Limits Still Occurring
- Free tier: 5 requests/minute per key
- If you're hitting limits with multiple keys, consider:
  - Adding more keys
  - Upgrading to paid tier
  - Increasing the `rate_limit_delay` in code

### Keys Not Rotating
- Check console output for "🔄 Rotated to API key X/Y" messages
- Ensure you're using the updated `overnight_analysis.py` script
- Verify all keys are valid and active

## Technical Details

The multi-key system is implemented in:
- `src/utils/api_key_manager.py` - Manages key loading and rotation
- `src/gemini_api/analysis_engine.py` - Handles automatic rotation on rate limits
- `overnight_analysis.py` - Main script using multi-key support

## Need Help?

If you encounter issues:
1. Check your `.env` file format
2. Verify all API keys are valid
3. Review console output for specific errors
4. Check the Gemini API quotas at [Google Cloud Console](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas)
