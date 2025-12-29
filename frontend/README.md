# GeminiTrader Frontend

Modern web-based interface for the GeminiTrader multi-agent stock analysis system.

## Features

- Clean, responsive design that works on desktop and mobile
- Real-time API connection status indicator
- Agent selection with descriptions
- Tabbed results view (Classification, Analysts, Debate, Final Verdict)
- Loading states with progress indicators
- Modern UI with smooth animations

## Quick Start

### Option 1: Using Python's Built-in Server (Recommended)

```bash
cd frontend
python -m http.server 8080
```

Then open your browser to: http://localhost:8080

### Option 2: Using Node.js http-server

```bash
npm install -g http-server
cd frontend
http-server -p 8080
```

### Option 3: Using Live Server (VS Code Extension)

1. Install "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

## Prerequisites

1. **Backend API must be running**:
   ```bash
   # In the project root directory
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Environment variables configured**:
   - Make sure your `.env` file has `GOOGLE_API_KEY` set

## Usage

### 1. Initialize Agents

1. Select which analysts you want to use (Market, Fundamentals, News, Social)
2. Click "Initialize Agents" button
3. Wait for confirmation (button will show "Re-initialize Agents" when ready)

### 2. Run Analysis

1. Enter a stock ticker symbol (e.g., AAPL, MSFT, TSLA)
2. Select or adjust the analysis date
3. Enter your question (e.g., "Should I invest in this stock?")
4. Click "Run Analysis"
5. Wait 30-60 seconds for the multi-agent analysis to complete

### 3. View Results

Results are organized in tabs:
- **Classification**: Shows how the query was classified and which agents were selected
- **Analysts**: Individual responses from each analyst
- **Debate**: Bull vs Bear debate rounds
- **Final Verdict**: The final recommendation and decision

## API Endpoints Used

The frontend communicates with these FastAPI endpoints:

- `GET /api/health` - Check API status
- `POST /api/initialize-pool` - Initialize selected agents
- `POST /api/query` - Run stock analysis

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── style.css       # All styling and responsive design
├── app.js          # JavaScript for API communication
└── README.md       # This file
```

## Customization

### Change API URL

Edit `app.js` line 1:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### Modify Styling

All styles are in `style.css`. Key CSS variables:
```css
:root {
    --primary-color: #2563eb;    /* Main blue */
    --success-color: #16a34a;    /* Green for success */
    --danger-color: #dc2626;     /* Red for errors */
}
```

## Troubleshooting

### "API Offline" Status

- Make sure FastAPI backend is running: `uvicorn app:app --reload`
- Check that the API is accessible at http://localhost:8000
- Verify CORS is enabled in `app.py` (already configured)

### Analysis Fails

- Ensure agents are initialized first
- Check that you have entered a valid ticker symbol
- Verify your `GOOGLE_API_KEY` is set in `.env`
- Check browser console (F12) for detailed error messages

### Styling Issues

- Clear browser cache (Ctrl+Shift+R)
- Ensure all three files are in the same directory
- Check browser console for missing file errors

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Responsive design works on all major mobile browsers

## Development

### Recommended Tools

- Browser DevTools (F12) for debugging
- Live Server for auto-reload during development
- VS Code with extensions: Live Server, Prettier

### Adding New Features

1. Update HTML structure in `index.html`
2. Add styles to `style.css`
3. Implement functionality in `app.js`

## Security Notes

- This is a frontend-only application (HTML/CSS/JS)
- No sensitive data is stored in the frontend
- All API calls go through the FastAPI backend
- API keys are stored server-side only
- CORS is configured to allow frontend access

## Performance

- Initial load: < 100KB (no external dependencies)
- No third-party libraries (vanilla JavaScript)
- Optimized for fast loading and smooth animations
- Responsive images and adaptive layouts

## Future Enhancements

- [ ] Add conversation history viewer
- [ ] Export results to PDF
- [ ] Real-time analysis progress updates
- [ ] Dark mode toggle
- [ ] Save favorite tickers
- [ ] Comparison view for multiple stocks
