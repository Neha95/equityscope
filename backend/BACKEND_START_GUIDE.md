# Qualitative Edge Backend - Quick Start Guide

## 🚀 Starting the Backend Server

### Method 1: Using the Start Script (Recommended)
```bash
cd backend
python start_server.py
```

### Method 2: Using uvicorn directly
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Method 3: Using Python module
```bash
cd backend
python -m uvicorn app.main:app --reload
```

## 📋 Prerequisites

1. **Python 3.8+** (Currently using Python 3.13)
2. **Dependencies installed**:
   ```bash
   pip install -r requirements.txt
   ```

## 🔧 Configuration

### Required Dependencies
The system needs these key packages:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `anthropic` - Claude AI integration
- `beautifulsoup4` - Web scraping
- `aiohttp` - Async HTTP client
- `yfinance` - Financial data

### Environment Variables (Optional)
```bash
# For AI agentic workflow (optional - can be set via UI)
export ANTHROPIC_API_KEY="sk-ant-..."

# For enhanced features (optional)
export KITE_API_KEY="your_kite_key"
export KITE_API_SECRET="your_kite_secret"
```

## 🎯 Verification

Once started, you should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
```

### Test the server:
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **Agentic Health**: http://localhost:8000/api/agentic/health

## 🔍 Troubleshooting

### Common Issues:

1. **Port 8000 already in use**
   ```bash
   # Find what's using port 8000
   lsof -i :8000
   # Kill the process or use a different port
   uvicorn app.main:app --reload --port 8001
   ```

2. **Import errors**
   ```bash
   # Make sure you're in the backend directory
   cd backend
   # Install missing dependencies
   pip install -r requirements.txt
   ```

3. **Claude API key missing**
   - The server will start but AI features will be disabled
   - Add your Claude API key via the frontend Settings panel
   - Or set the ANTHROPIC_API_KEY environment variable

4. **Module not found errors**
   ```bash
   # Make sure Python can find the app module
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

## 📊 Backend Features

When running, the backend provides:

### Standard Features (Always Available):
- Company analysis via yfinance
- DCF valuation modeling
- Basic market data

### AI Features (Requires Claude API Key):
- 4-agent agentic workflow
- News scraping with source attribution
- SWOT analysis with detailed insights
- Investment committee validation

### Enhanced Features (Requires Kite Connect):
- Real-time Indian market data
- Intraday charts
- Portfolio tracking

## 🏁 Success Indicators

✅ **Server Started**: See uvicorn startup messages
✅ **Health Check**: http://localhost:8000/health returns 200
✅ **Frontend Connected**: Frontend shows no "Backend server not running" errors
✅ **AI Ready**: http://localhost:8000/api/agentic/health shows claude_available: true

## 📞 Need Help?

If you're still having issues:
1. Check that you're in the `backend` directory
2. Verify Python version with `python --version`
3. Check dependencies with `pip list | grep fastapi`
4. Look at server logs for specific error messages