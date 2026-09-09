"""
Architecture Documentation
High-level system design and component overview
"""

# TrustShield AI - System Architecture

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Chrome Extension (MV3)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Content Script (Gmail/Outlook)                       │  │
│  │ - Email DOM Extraction (MutationObserver)            │  │
│  │ - Real-time Detection                                │  │
│  │ - Prevention Actions (Block/Warn/Rewrite)            │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Background Service Worker                            │  │
│  │ - Communication with Backend                         │  │
│  │ - Cache Management (IndexedDB)                       │  │
│  │ - Authentication                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Popup & Options UI                                   │  │
│  │ - Settings & Configuration                          │  │
│  │ - Quick Analysis View                                │  │
│  │ - Reporting Interface                                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ API
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Backend (Python)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ API Layer (REST, WebSocket)                         │  │
│  │ - /api/analyze        (Email analysis)              │  │
│  │ - /api/report         (Phishing reporting)          │  │
│  │ - /api/dashboard      (Analytics)                   │  │
│  │ - /api/auth           (OAuth, JWT)                  │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ AI Multi-Agent Engine                                │  │
│  │ 1. Email Extraction Agent                            │  │
│  │ 2. Brand Verification Agent                          │  │
│  │ 3. Intent Detection Agent                            │  │
│  │ 4. URL Intelligence Agent                            │  │
│  │ 5. Psychology Manipulation Agent                     │  │
│  │ 6. QR Detection Agent                                │  │
│  │ 7. Attachment Analysis Agent                         │  │
│  │ 8. Decision Fusion Agent                             │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Services Layer                                        │  │
│  │ - ML Model Inference                                 │  │
│  │ - Threat Intelligence                                │  │
│  │ - User Profile Management                            │  │
│  │ - Cache Service                                      │  │
│  │ - Email Storage & Retrieval                          │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Database Layer (PostgreSQL)                          │  │
│  │ - Users, Sessions                                    │  │
│  │ - Analysis Records                                   │  │
│  │ - Blocked Emails                                     │  │
│  │ - Threat Intelligence                                │  │
│  │ - Dashboard Metrics                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Cache Layer (Redis)                                  │  │
│  │ - Session Cache                                      │  │
│  │ - URL Reputation Cache                               │  │
│  │ - Model Cache                                        │  │
│  │ - Rate Limiting                                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ API
┌─────────────────────────────────────────────────────────────┐
│            React Dashboard (Analytics & Admin)              │
│  - User Dashboard                                           │
│  - Threat Analytics                                         │
│  - Blocked Email History                                    │
│  - User Reports                                             │
│  - Settings Management                                      │
└─────────────────────────────────────────────────────────────┘
```

## 2. Component Descriptions

### Chrome Extension
- **Manifest V3**: Modern Chrome extension manifest
- **Content Scripts**: Inject DOM monitoring into Gmail/Outlook
- **Service Worker**: Background processing and API communication
- **Storage**: IndexedDB for local cache, localStorage for settings
- **Security**: CSP headers, message validation

### Backend Services
- **FastAPI**: Async REST API with automatic OpenAPI docs
- **AI Agents**: 8 specialized agents for multi-dimensional analysis
- **Database**: PostgreSQL with optimized indexes
- **Cache**: Redis for performance and rate limiting
- **Authentication**: Google OAuth + JWT tokens

### Frontend Dashboard
- **React 18**: Modern UI with hooks
- **TypeScript**: Type safety across the app
- **TailwindCSS**: Responsive design
- **Vite**: Fast development and build

## 3. Data Flow

### Email Analysis Flow
```
User opens email in Gmail
    ↓
Content Script detects via MutationObserver
    ↓
Extract email content (DOM parsing)
    ↓
Send to Backend via API
    ↓
Run 8 AI Agents in parallel
    ↓
Email Extraction Agent → Structured JSON
    ↓
Brand Verification Agent → Impersonation Score
Intent Detection Agent → Intent Type & Score
URL Intelligence Agent → URL Risk Scores
Psychology Agent → Manipulation Detection
QR Detection Agent → QR Analysis
Attachment Agent → File Risk Analysis
    ↓
Decision Fusion Agent combines all scores
    ↓
Generate Overall Risk Score (0-100)
    ↓
Determine Action (Allow/Warn/Block)
    ↓
Return Analysis to Extension
    ↓
Apply Prevention Actions to DOM
    ↓
Show Warning/Block UI if needed
    ↓
Store Analysis in Database
    ↓
Update Dashboard Metrics
```

## 4. Threat Detection Models

### Multi-Agent Scoring
Each agent produces a score (0-100) with confidence:

1. **Email Extraction (10% weight)**
   - Validates email structure
   - Extracts all components
   
2. **Brand Verification (20% weight)**
   - Detects impersonation
   - Analyzes domain similarity
   
3. **Intent Detection (25% weight)**
   - Identifies attack type
   - Analyzes urgency/fear tactics
   
4. **URL Intelligence (20% weight)**
   - Checks URL reputation
   - Detects typosquatting
   
5. **Psychology (15% weight)**
   - Manipulation tactics
   - Social engineering patterns
   
6. **QR Detection (5% weight)**
   - Decodes QR codes
   - Analyzes destinations
   
7. **Attachment Analysis (5% weight)**
   - File type analysis
   - Executable detection
   
8. **Decision Fusion**
   - Combines all scores
   - Generates final risk and action

### Risk Levels
- **LOW (0-25)**: Normal email, no action needed
- **MEDIUM (25-50)**: Warning shown, user can interact
- **HIGH (50-75)**: Warning shown, risky elements disabled
- **CRITICAL (75-100)**: Email blocked, minimal interaction

## 5. Privacy & Security

### Local Processing
- Email parsing happens locally in extension
- OCR done locally
- Initial risk scoring done locally
- Minimal data sent to backend

### Backend Processing
- Only if user enables
- Anonymized/hashed data
- No full email storage by default
- Encrypted in transit (HTTPS/TLS)

### Data Encryption
- Passwords: bcrypt + salt
- Sensitive data: AES-256-GCM
- Database: TLS connection
- API: JWT tokens with expiration

## 6. Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Redis session store
- Database connection pooling
- Load balancing ready

### Performance Optimization
- Caching layer (Redis)
- Database indexes
- Async processing
- Response compression
- CDN for static assets

### Rate Limiting
- Per-user per-minute limits
- Redis-backed counters
- Graceful degradation

## 7. Monitoring & Logging

### Metrics
- Analysis latency
- Detection accuracy
- False positive rate
- API response times
- Database query times

### Logging
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Audit trail for sensitive operations
- Error tracking integration

## 8. Deployment Architecture

### Development
- Docker Compose local stack
- Hot reloading
- Shared volumes

### Production
- Kubernetes ready
- Docker multi-stage builds
- Environment-based configuration
- Health checks & auto-restart

## 9. Future Enhancements

- [ ] Machine learning model fine-tuning
- [ ] Advanced threat intelligence feeds
- [ ] Graph-based phishing network detection
- [ ] Community reporting system
- [ ] Browser-wide protection (Safari, Firefox)
- [ ] Mobile app companion
- [ ] Integration with corporate email gateways
