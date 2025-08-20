# EquityScope User Management API Documentation

## Overview

The EquityScope User Management API provides comprehensive authentication, authorization, and user management capabilities for the EquityScope DCF analysis platform. This document covers all authentication endpoints, protected analysis endpoints, and user management features.

## Base URL

- **Development**: `http://localhost:8000/api/v2`
- **Production**: `https://api.equityscope.com/api/v2`

## Authentication Methods

### 1. JWT Bearer Tokens
Standard JWT tokens for web applications:
```
Authorization: Bearer <jwt_token>
```

### 2. API Keys
Programmatic access for integrations:
```
Authorization: Bearer eq_<api_key>
```

## Authentication Endpoints

### User Registration

**POST** `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "company": "Example Corp"
}
```

**Response:**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "company": "Example Corp",
  "status": "pending_verification",
  "email_verified": false,
  "tier": "free",
  "subscription_status": {
    "is_active": true,
    "expires_at": null,
    "days_remaining": null
  },
  "total_analyses": 0,
  "monthly_analyses": 0,
  "rate_limits": {
    "analyses_per_hour": 5,
    "analyses_per_day": 20,
    "analyses_per_month": 100
  },
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": null
}
```

### User Login

**POST** `/auth/login`

Authenticate user and receive access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "tier": "professional",
    "subscription_status": {
      "is_active": true,
      "expires_at": "2024-07-15T10:30:00Z",
      "days_remaining": 180
    }
  }
}
```

### Get Current User

**GET** `/auth/me`

Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "company": "Example Corp",
  "status": "active",
  "email_verified": true,
  "tier": "professional",
  "subscription_status": {
    "is_active": true,
    "expires_at": "2024-07-15T10:30:00Z",
    "days_remaining": 180
  },
  "total_analyses": 1250,
  "monthly_analyses": 85,
  "rate_limits": {
    "analyses_per_hour": 50,
    "analyses_per_day": 200,
    "analyses_per_month": 2000
  },
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-03-15T09:15:00Z"
}
```

### Update User Profile

**PUT** `/auth/me`

Update user profile information.

**Request Body:**
```json
{
  "full_name": "John Smith",
  "company": "New Company Inc"
}
```

### Email Verification

**POST** `/auth/verify-email?token=<verification_token>`

Verify user email address.

**Response:**
```json
{
  "message": "Email verified successfully"
}
```

### Password Management

**POST** `/auth/forgot-password`

Request password reset token.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**POST** `/auth/reset-password?token=<reset_token>`

Reset password with token.

**Request Body:**
```json
{
  "new_password": "newsecurepassword123"
}
```

**POST** `/auth/change-password`

Change password (authenticated).

**Request Body:**
```json
{
  "current_password": "currentpassword123",
  "new_password": "newpassword123"
}
```

### API Key Management

**POST** `/auth/api-keys`

Create new API key.

**Request Body:**
```json
{
  "name": "Production Integration",
  "expires_days": 90
}
```

**Response:**
```json
{
  "api_key_id": "key-uuid",
  "name": "Production Integration",
  "key": "eq_1234567890abcdef...",
  "expires_at": "2024-06-15T10:30:00Z",
  "created_at": "2024-03-15T10:30:00Z",
  "warning": "Store this key securely. It will not be shown again."
}
```

### Session Management

**GET** `/auth/sessions`

Get active user sessions.

**DELETE** `/auth/sessions/{session_id}`

Invalidate specific session.

**POST** `/auth/logout`

Logout current session.

## Protected Analysis Endpoints

### Comprehensive Company Analysis

**POST** `/analyze`

Perform comprehensive DCF analysis with authentication and rate limiting.

**Request Body:**
```json
{
  "ticker": "TCS.NS",
  "user_assumptions": {
    "revenue_growth_rate": 15.0,
    "terminal_growth_rate": 3.0,
    "discount_rate": 12.0
  }
}
```

**Response:**
```json
{
  "companyName": "Tata Consultancy Services",
  "ticker": "TCS.NS",
  "analysis": {
    "financial_analysis": {...},
    "dcf_valuation": {...},
    "scenario_analysis": {...},
    "risk_assessment": {...}
  },
  "metadata": {
    "cached": false,
    "user_tier": "professional",
    "user_id": "user-uuid",
    "analysis_timestamp": "2024-03-15T10:30:00Z",
    "rate_limit_status": {
      "is_rate_limited": false,
      "current_usage": 15,
      "hourly_limit": 50,
      "monthly_usage": 85,
      "monthly_limit": 2000
    }
  }
}
```

### Multi-Stage DCF Analysis

**POST** `/multi-stage-dcf`

10-year multi-stage DCF analysis.

**Request Parameters:**
- `ticker` (required): Company ticker symbol
- `mode` (optional): "simple" or "agentic"
- `user_level` (optional): "beginner", "intermediate", "advanced"
- `user_assumptions` (optional): Custom financial assumptions

### User Dashboard

**GET** `/user-dashboard`

Get personalized user dashboard with usage statistics.

**Response:**
```json
{
  "user_info": {
    "name": "John Doe",
    "tier": "professional",
    "member_since": "2024-01-15T10:30:00Z"
  },
  "usage_statistics": {
    "total_analyses": 1250,
    "monthly_analyses": 85,
    "current_streak": 7,
    "favorite_sectors": ["Technology", "Financial Services"],
    "most_analyzed_companies": ["TCS.NS", "RELIANCE.NS", "HDFCBANK.NS"]
  },
  "cache_performance": {
    "total_cost_saved": 15.75,
    "hit_rate": 68.5
  },
  "recent_analyses": [...],
  "recommendations": {
    "suggested_companies": ["INFY.NS", "WIPRO.NS"],
    "educational_content": [...],
    "subscription_suggestions": []
  }
}
```

### Subscription Plans

**GET** `/subscription-plans`

Get available subscription tiers and features.

## Rate Limiting

### Rate Limit Structure by Tier

| Tier | Hourly Limit | Daily Limit | Monthly Limit | Price |
|------|--------------|-------------|---------------|-------|
| **Free** | 5 analyses | 20 analyses | 100 analyses | $0 |
| **Professional** | 50 analyses | 200 analyses | 2,000 analyses | $29/month |
| **Enterprise** | 500 analyses | 2,000 analyses | 20,000 analyses | $99/month |

### Rate Limit Headers

All API responses include rate limiting headers:

```
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 35
X-RateLimit-Reset: 1647345600
X-RateLimit-Type: hourly
```

### Rate Limit Exceeded Response

**HTTP 429 Too Many Requests**

```json
{
  "detail": {
    "message": "Rate limit exceeded",
    "rate_limit_status": {
      "is_rate_limited": true,
      "current_usage": 50,
      "hourly_limit": 50,
      "reset_time": "2024-03-15T11:00:00Z",
      "monthly_usage": 150,
      "monthly_limit": 2000,
      "suggested_action": "Wait 15 minutes or upgrade to Professional tier"
    }
  }
}
```

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message",
  "error_code": "AUTHENTICATION_FAILED",
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req-uuid"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTHENTICATION_FAILED` | 401 | Invalid or expired token |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required permissions |
| `RATE_LIMIT_EXCEEDED` | 429 | API rate limit exceeded |
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource not found |
| `INTERNAL_ERROR` | 500 | Server-side error |

## Usage Examples

### Python SDK Example

```python
import requests

# Initialize client
class EquityScopeClient:
    def __init__(self, api_key=None, base_url="https://api.equityscope.com/api/v2"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_company(self, ticker, user_assumptions=None):
        """Perform comprehensive company analysis"""
        response = requests.post(
            f"{self.base_url}/analyze",
            json={
                "ticker": ticker,
                "user_assumptions": user_assumptions
            },
            headers=self.headers
        )
        return response.json()
    
    def get_dashboard(self):
        """Get user dashboard"""
        response = requests.get(
            f"{self.base_url}/user-dashboard",
            headers=self.headers
        )
        return response.json()

# Usage
client = EquityScopeClient(api_key="eq_your_api_key_here")
analysis = client.analyze_company("TCS.NS")
dashboard = client.get_dashboard()
```

### JavaScript/Node.js Example

```javascript
class EquityScopeClient {
    constructor(apiKey, baseUrl = 'https://api.equityscope.com/api/v2') {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }
    
    async analyzeCompany(ticker, userAssumptions = null) {
        const response = await fetch(`${this.baseUrl}/analyze`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({
                ticker,
                user_assumptions: userAssumptions
            })
        });
        return response.json();
    }
    
    async getDashboard() {
        const response = await fetch(`${this.baseUrl}/user-dashboard`, {
            headers: this.headers
        });
        return response.json();
    }
}

// Usage
const client = new EquityScopeClient('eq_your_api_key_here');
const analysis = await client.analyzeCompany('TCS.NS');
const dashboard = await client.getDashboard();
```

### cURL Examples

```bash
# Login
curl -X POST https://api.equityscope.com/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Analyze company
curl -X POST https://api.equityscope.com/api/v2/analyze \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "TCS.NS",
    "user_assumptions": {
      "revenue_growth_rate": 15.0,
      "terminal_growth_rate": 3.0
    }
  }'

# Get user dashboard
curl -X GET https://api.equityscope.com/api/v2/user-dashboard \
  -H "Authorization: Bearer your_jwt_token"
```

## Security Considerations

### Authentication Security
- JWT tokens expire after 60 minutes by default
- API keys can be set to expire and should be rotated regularly
- All passwords are hashed using bcrypt with salt
- Session management tracks IP addresses and user agents

### Rate Limiting Security
- Rate limits prevent abuse and ensure fair usage
- IP-based rate limiting for anonymous users
- User-based rate limiting for authenticated users
- Graduated rate limits based on subscription tier

### Data Security
- All API endpoints use HTTPS in production
- Sensitive data is never logged or cached
- Email enumeration protection on registration/login
- Password reset tokens expire after 24 hours

## Support and Resources

### API Status
- **Status Page**: https://status.equityscope.com
- **Health Check**: `/health`

### Support Channels
- **Email**: api-support@equityscope.com
- **Documentation**: https://docs.equityscope.com
- **Community**: https://community.equityscope.com

### Rate Limit Monitoring
Monitor your API usage through:
- User Dashboard: Real-time usage statistics
- API Headers: Rate limit information in response headers
- Webhooks: Notifications when approaching limits (Enterprise tier)