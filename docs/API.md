"""
API Reference Documentation
Complete REST API endpoints and examples
"""

# TrustShield AI - API Reference

## Base URL
```
http://localhost:8000/api
https://api.trustshield.io/api (production)
```

## Authentication

### OAuth Login
```
GET /auth/google
```

### JWT Token
All requests (except /auth/google) require JWT token in header:
```
Authorization: Bearer <access_token>
```

---

## Endpoints

### 1. Email Analysis

#### POST `/analyze`
Analyze email for phishing

**Request:**
```json
{
  "sender": "admin@example.com",
  "subject": "Urgent: Verify Your Account",
  "body": "Please click below to verify...",
  "htmlBody": "<html>...</html>",
  "links": [
    {
      "text": "Verify Account",
      "href": "http://malicious-site.com",
      "visible": true
    }
  ],
  "images": [],
  "attachments": [],
  "replyTo": "noreply@example.com",
  "extractedAt": "2024-01-15T10:30:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "overall_risk_score": 85,
    "risk_level": "CRITICAL",
    "threat_category": "CREDENTIAL_THEFT",
    "suggested_action": "block",
    "confidence": 0.92,
    "explanation": "This email attempts credential theft with impersonation.",
    "detailed_reasons": [
      "Brand impersonation: Microsoft",
      "Urgency language detected",
      "Suspicious link detected"
    ],
    "prevention_actions": [
      {
        "type": "DISABLE_LINK",
        "target": "http://malicious-site.com",
        "reason": "High-risk URL detected"
      }
    ],
    "agent_scores": {
      "brand_verification": 75,
      "intent_detection": 85,
      "url_intelligence": 90,
      "psychology_manipulation": 70
    },
    "processing_time_ms": 245
  }
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid request
- `401`: Unauthorized
- `429`: Rate limited

---

### 2. Report Phishing

#### POST `/report`
Report a phishing email

**Request:**
```json
{
  "report_type": "PHISHING",
  "sender": "admin@example.com",
  "subject": "Urgent: Verify Your Account",
  "email_hash": "sha256_hash_of_email_content",
  "urls_identified": [
    "http://malicious-site.com"
  ],
  "attachments_identified": [],
  "user_description": "Received suspicious email asking to verify account"
}
```

**Response:**
```json
{
  "success": true,
  "report_id": "rpt_7f8a9b2c",
  "message": "Thank you for reporting. This email has been added to threat intelligence."
}
```

**Status Codes:**
- `201`: Created
- `400`: Invalid request
- `401`: Unauthorized

---

### 3. Dashboard Analytics

#### GET `/dashboard/stats`
Get user dashboard statistics

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_emails_analyzed": 1250,
    "total_phishing_detected": 48,
    "total_blocked": 42,
    "detection_rate": 0.88,
    "top_threats": [
      {
        "threat": "credential_theft",
        "count": 15
      },
      {
        "threat": "financial_fraud",
        "count": 12
      }
    ],
    "top_brands": [
      {
        "brand": "Microsoft",
        "count": 20
      },
      {
        "brand": "Apple",
        "count": 15
      }
    ]
  }
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized

---

### 4. Email History

#### GET `/history?limit=50&offset=0`
Get analyzed emails history

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (int, default: 50): Number of records
- `offset` (int, default: 0): Pagination offset
- `risk_level` (string, optional): Filter by risk level (LOW, MEDIUM, HIGH, CRITICAL)
- `from_date` (string, optional): ISO 8601 date

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "analysis_123",
      "sender": "admin@example.com",
      "subject": "Urgent: Verify Your Account",
      "risk_score": 85,
      "risk_level": "CRITICAL",
      "threat_category": "CREDENTIAL_THEFT",
      "created_at": "2024-01-15T10:30:00Z",
      "action_taken": "BLOCKED"
    }
  ],
  "total": 1250,
  "offset": 0,
  "limit": 50
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized

---

### 5. User Profile

#### GET `/profile`
Get user profile and settings

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user_123",
    "email": "user@example.com",
    "privacy_mode": true,
    "enable_backend_analysis": false,
    "risk_threshold": 50,
    "trusted_contacts": ["trusted@example.com"],
    "frequent_domains": ["company.com"],
    "trusted_organizations": ["Microsoft", "Google"],
    "created_at": "2023-12-01T00:00:00Z"
  }
}
```

---

#### PUT `/profile`
Update user profile and settings

**Request:**
```json
{
  "privacy_mode": false,
  "enable_backend_analysis": true,
  "risk_threshold": 75,
  "trusted_contacts": ["trusted@example.com"],
  "frequent_domains": ["company.com"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Profile updated successfully"
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid request
- `401`: Unauthorized

---

### 6. Configuration

#### GET `/config`
Get extension configuration

**Response:**
```json
{
  "success": true,
  "data": {
    "api_version": "v1",
    "supported_email_providers": ["gmail", "outlook"],
    "features": {
      "qr_detection": true,
      "attachment_analysis": true,
      "threat_intelligence": true,
      "community_reporting": true
    },
    "models": {
      "brand_verification": "v2.1",
      "intent_detection": "v1.5",
      "url_intelligence": "v2.0"
    }
  }
}
```

---

### 7. Threat Intelligence

#### GET `/threat-intelligence?indicator=example.com`
Check if indicator is known malicious

**Query Parameters:**
- `indicator` (string): Domain, IP, email, or hash
- `type` (string, optional): Indicator type (domain, ip, email, hash)

**Response:**
```json
{
  "success": true,
  "data": {
    "indicator": "example.com",
    "type": "domain",
    "is_malicious": true,
    "threat_category": "phishing",
    "confidence": 0.95,
    "report_count": 127,
    "first_seen": "2023-01-15T00:00:00Z",
    "last_seen": "2024-01-15T10:30:00Z"
  }
}
```

---

## Error Responses

### 400 - Bad Request
```json
{
  "success": false,
  "error": "Invalid email format",
  "code": "INVALID_REQUEST"
}
```

### 401 - Unauthorized
```json
{
  "success": false,
  "error": "Invalid or expired token",
  "code": "UNAUTHORIZED"
}
```

### 429 - Rate Limited
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

### 500 - Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error",
  "code": "INTERNAL_ERROR"
}
```

---

## Rate Limiting

- **Per-user limit**: 60 requests/minute
- **Reset**: Rolling 60-second window
- **Headers returned**:
  - `X-RateLimit-Limit`: 60
  - `X-RateLimit-Remaining`: 45
  - `X-RateLimit-Reset`: 1705318260

---

## Examples

### cURL
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "admin@example.com",
    "subject": "Urgent: Verify Account",
    "body": "Click below to verify..."
  }'
```

### Python (requests)
```python
import requests

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

data = {
    "sender": "admin@example.com",
    "subject": "Urgent: Verify Account",
    "body": "Click below to verify..."
}

response = requests.post(
    "http://localhost:8000/api/analyze",
    headers=headers,
    json=data
)

print(response.json())
```

### JavaScript (fetch)
```javascript
const analyze = async (emailData) => {
  const response = await fetch('http://localhost:8000/api/analyze', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(emailData)
  });
  
  return response.json();
};
```

---

## WebSocket Endpoints

### Real-time Analysis Updates

**Connection:**
```
ws://localhost:8000/api/ws/analysis?token=TOKEN
```

**Messages:**
```json
{
  "type": "analysis_complete",
  "data": {
    "email_id": "msg_123",
    "risk_score": 85,
    "action_taken": "blocked"
  }
}
```

---

## Pagination

List endpoints support pagination via query parameters:
- `limit` (1-100, default: 50)
- `offset` (default: 0)
- `sort_by` (field name, default: created_at)
- `sort_order` (asc/desc, default: desc)

**Example:**
```
GET /history?limit=25&offset=50&sort_by=risk_score&sort_order=desc
```

---

## Filtering

List endpoints support filtering:

**Example:**
```
GET /history?risk_level=HIGH&from_date=2024-01-01&to_date=2024-01-31
```

---

## API Versioning

Current version: **v1**

Future changes will be made to `/api/v2` while maintaining `/api/v1` for backward compatibility.

---

## Support

- Documentation: https://docs.trustshield.io
- API Status: https://status.trustshield.io
- Issue Tracker: https://github.com/trustshield-ai/issues
