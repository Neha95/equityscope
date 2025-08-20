# Qualitative Edge - Kite Connect Pilot Test Setup

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.9+
- Node.js 16+
- Zerodha Kite Connect account (for enhanced features)

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

#### Environment Configuration
Create `.env` file in backend directory:

```env
# Kite Connect Configuration (Optional - app works without these)
KITE_API_KEY=your_kite_api_key
KITE_API_SECRET=your_kite_api_secret
KITE_ACCESS_TOKEN=your_access_token
KITE_REQUEST_TOKEN=your_request_token

# Optional: API Configuration
PYTHONUNBUFFERED=1
```

#### Start Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

#### Environment Configuration
Create `.env` file in frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

#### Start Frontend Server
```bash
npm start
```

### 3. Docker Setup (Alternative)

```bash
docker-compose up --build
```

## 🧪 Pilot Test Scenarios

### Scenario 1: Standard Mode (No Kite Authentication)
**Objective**: Test basic functionality with yfinance fallback

1. **Access Application**: http://localhost:3000
2. **Search Company**: Enter "RELIANCE" or "TCS"
3. **Verify Features**:
   - ✅ Company information loads
   - ✅ Stock price data appears
   - ✅ Qualitative analysis cards display
   - ✅ DCF valuation calculates
   - ⚠️ "Standard Mode" indicator shows
   - ❌ Real-time features unavailable

### Scenario 2: Enhanced Mode (With Kite Authentication)
**Objective**: Test real-time features with Kite Connect

#### Step 1: Get Kite API Credentials
1. Visit [Kite Connect Console](https://kite.trade)
2. Create developer app
3. Note down API Key and API Secret

#### Step 2: Authenticate
1. **Get Login URL**: 
   ```bash
   curl http://localhost:8000/api/v2/company/kite/login-url
   ```
2. **Visit Login URL**: Complete authentication
3. **Extract Request Token**: From redirect URL
4. **Set Tokens**:
   ```bash
   curl -X POST http://localhost:8000/api/v2/company/kite/set-tokens \
     -H "Content-Type: application/json" \
     -d '{"request_token": "your_request_token"}'
   ```

#### Step 3: Test Enhanced Features
1. **Check Status**: Verify "Real-time Mode" indicator
2. **Test Features**:
   - ✅ Live stock prices
   - ✅ Intraday charts (1min, 5min intervals)
   - ✅ Market depth data
   - ✅ Enhanced DCF with real-time pricing
   - ✅ Symbol search functionality
   - ✅ Market status information

### Scenario 3: API Testing
**Objective**: Direct API testing without frontend

#### V1 API (Standard)
```bash
# Company Analysis
curl http://localhost:8000/api/company/RELIANCE.NS

# DCF Valuation
curl -X POST http://localhost:8000/api/valuation/dcf \
  -H "Content-Type: application/json" \
  -d '{
    "revenue_growth_rate": 10.0,
    "ebitda_margin": 15.0,
    "tax_rate": 25.0,
    "wacc": 12.0,
    "terminal_growth_rate": 4.0
  }' \
  --get --data-urlencode "ticker=RELIANCE.NS"
```

#### V2 API (Enhanced)
```bash
# Enhanced Company Analysis
curl http://localhost:8000/api/v2/company/RELIANCE.NS

# Real-time Quote
curl http://localhost:8000/api/v2/company/RELIANCE.NS/price

# Intraday Data
curl "http://localhost:8000/api/v2/company/RELIANCE.NS/intraday?interval=5minute"

# Market Depth
curl http://localhost:8000/api/v2/company/RELIANCE.NS/market-depth

# Symbol Search
curl http://localhost:8000/api/v2/company/search/RELIANCE

# Data Source Status
curl http://localhost:8000/api/v2/company/status
```

## 📊 Test Data & Validation

### Test Tickers
- **Large Cap**: RELIANCE.NS, TCS.NS, HDFCBANK.NS
- **Mid Cap**: ZOMATO.NS, NYKAA.NS, PAYTM.NS
- **IT Sector**: INFY.NS, WIPRO.NS, HCLTECH.NS
- **Banking**: ICICIBANK.NS, KOTAKBANK.NS, AXISBANK.NS

### Expected Results

#### Standard Mode (yfinance)
- **Response Time**: 2-5 seconds
- **Data Freshness**: Previous day close
- **Features Available**: Basic analysis, DCF modeling
- **Rate Limits**: Moderate (100 requests/hour)

#### Enhanced Mode (Kite Connect)
- **Response Time**: 0.5-2 seconds
- **Data Freshness**: Real-time (15-second delay)
- **Features Available**: Full suite including intraday, depth
- **Rate Limits**: Higher (3 requests/second)

### Validation Checklist

#### Functional Tests
- [ ] Company search and analysis
- [ ] Real-time price updates
- [ ] DCF calculation accuracy
- [ ] Intraday chart rendering
- [ ] Market depth display
- [ ] Error handling (invalid tickers)
- [ ] Fallback mechanism (Kite → yfinance)

#### Performance Tests
- [ ] Page load time < 3 seconds
- [ ] API response time < 2 seconds
- [ ] Real-time updates without lag
- [ ] Memory usage stable over time
- [ ] No memory leaks in frontend

#### UI/UX Tests
- [ ] Responsive design (mobile/desktop)
- [ ] Dark theme consistency
- [ ] Smooth animations
- [ ] Loading states clear
- [ ] Error messages helpful

## 🔧 Troubleshooting

### Common Issues

#### "Kite session not initialized"
**Cause**: Missing or invalid Kite authentication
**Solution**: 
1. Check API credentials in `.env`
2. Re-authenticate using login URL
3. Verify request token extraction

#### "Financial data not found"
**Cause**: Invalid ticker or data unavailable
**Solution**:
1. Verify ticker format (add .NS for NSE)
2. Try alternative tickers
3. Check yfinance fallback

#### "CORS errors in browser"
**Cause**: Frontend/backend URL mismatch
**Solution**:
1. Check `REACT_APP_API_URL` in frontend `.env`
2. Verify backend CORS settings
3. Ensure both servers running

#### Slow API responses
**Cause**: Rate limiting or network issues
**Solution**:
1. Implement request caching
2. Use batch API calls
3. Check network connectivity

### Debug Mode
Enable detailed logging:

```bash
# Backend
export PYTHONPATH=. && python -m uvicorn app.main:app --reload --log-level debug

# Frontend
REACT_APP_DEBUG=true npm start
```

## 📈 Performance Monitoring

### Key Metrics
- **API Response Time**: < 2s for 95th percentile
- **Frontend Load Time**: < 3s for initial load
- **Error Rate**: < 1% for valid requests
- **Data Accuracy**: ±0.1% vs official sources

### Monitoring Tools
- Backend: FastAPI built-in metrics at `/metrics`
- Frontend: Browser dev tools performance tab
- API: Use Postman or curl for response time testing

## 🚦 Go-Live Checklist

### Technical Requirements
- [ ] All test scenarios pass
- [ ] Performance metrics met
- [ ] Error handling comprehensive
- [ ] Security review completed
- [ ] Documentation updated

### Business Requirements
- [ ] Kite Connect terms accepted
- [ ] Data usage limits understood
- [ ] User authentication flow tested
- [ ] Backup/fallback mechanisms verified

### Production Configuration
- [ ] Environment variables secured
- [ ] API rate limits configured
- [ ] Monitoring/alerting setup
- [ ] SSL/HTTPS enabled
- [ ] Domain and hosting configured

## 📞 Support

### Resources
- **API Documentation**: http://localhost:8000/docs
- **Kite Connect Docs**: https://kite.trade/docs/connect/v3/
- **yfinance Docs**: https://github.com/ranaroussi/yfinance

### Contact
- Technical Issues: Check GitHub issues
- API Questions: Refer to FastAPI docs
- Kite Connect: Zerodha support portal

---

**Happy Testing! 🎉**