# TrustShield AI - Enterprise Phishing Detection System

An AI-powered Chrome Extension that detects and prevents phishing attacks in real-time using advanced machine learning, multi-agent architecture, and explainable AI.

## 🎯 Project Vision

TrustShield AI protects users from phishing emails **before they interact with them** by:
- Automatically analyzing email content when opened
- Detecting malicious intent using 8 specialized AI agents
- Preventing clicks on phishing links, QR codes, and buttons
- Providing explainable AI insights about threats
- Maintaining privacy with local processing

## 🏗️ Architecture Overview

```
Chrome Extension (React + TypeScript)
           ↓
Content Extraction Agent
           ↓
Multi-Agent AI System (8 Specialized Agents)
           ↓
ML Risk Prediction Engine
           ↓
Decision Fusion Engine
           ↓
Prevention Actions (Block • Warn • Rewrite • Report)
           ↓
User Dashboard (Analytics & History)
```

## 📦 Project Structure

```
trustshield-ai/
├── chrome-extension/      # Manifest V3 Chrome Extension
├── backend/               # FastAPI REST API & Services
├── ai-engine/             # AI Agents & ML Models
├── dashboard/             # React Admin Dashboard
├── shared/                # Shared Types & Utilities
├── docs/                  # Architecture & API Documentation
├── docker-compose.yml
├── .github/
│   └── workflows/         # CI/CD Pipelines
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- Chrome Browser

### Local Development

```bash
# Clone the repository
git clone <repo-url>
cd trustshield-ai

# Install dependencies
npm install              # Chrome Extension
pip install -r requirements.txt  # Backend

# Start services
docker-compose up -d

# Run backend
cd backend && uvicorn app.main:app --reload

# Build Chrome Extension
cd chrome-extension && npm run build

# Run tests
npm run test && pytest
```

### Load Extension in Chrome

1. Open `chrome://extensions`
2. Enable Developer Mode
3. Click "Load unpacked"
4. Select `chrome-extension/build` directory

## 🤖 AI Multi-Agent System

### 1. **Email Extraction Agent**
- Parses DOM and HTML
- Extracts sender, subject, body, links, buttons, images, QR codes
- Creates structured JSON output

### 2. **Brand Verification Agent**
- Detects brand impersonation
- Compares sender, domain, logo, writing style
- Returns Brand Similarity Score

### 3. **Intent Detection Agent**
- Identifies attack type (credential theft, fraud, scam, malware, etc.)
- Analyzes email content for attack indicators
- Returns Intent Score

### 4. **URL Intelligence Agent**
- Checks domain age, typosquatting, redirects
- Validates SSL certificates and DNS
- Analyzes IP reputation
- Returns URL Risk Score

### 5. **Psychology Manipulation Agent**
- Detects fear, urgency, authority, scarcity, curiosity, reward tactics
- Analyzes manipulation patterns
- Returns Manipulation Score

### 6. **QR Detection Agent**
- Detects and decodes QR codes
- Analyzes destination URLs
- Returns QR Risk Score

### 7. **Attachment Agent**
- Analyzes file extensions, double extensions
- Detects macros and password-protected archives
- Returns Attachment Risk Score

### 8. **Decision Fusion Agent**
- Combines all agent outputs
- Generates Overall Risk Score (0-100)
- Provides confidence metrics
- Suggests actions: Block, Warn, Rewrite, Report

## 🔐 Privacy & Security

- ✅ **Local Processing First**: DOM parsing, OCR, risk scoring done locally
- ✅ **Optional Backend**: Only send anonymous metadata if enabled
- ✅ **No Email Upload**: Complete emails never uploaded without explicit consent
- ✅ **Encrypted Profile**: Personal security profile stored locally encrypted
- ✅ **OAuth**: Secure Google authentication for dashboard

## 💻 Tech Stack

### Frontend
- React 18 + TypeScript
- Tailwind CSS
- Chrome Extension Manifest V3
- MutationObserver for real-time detection

### Backend
- FastAPI (Python)
- PostgreSQL + Redis
- JWT Authentication
- REST API

### AI/ML
- TensorFlow / PyTorch
- Transformers (BERT, RoBERTa)
- Scikit-learn
- OpenAI, Gemini, Claude APIs
- Tesseract OCR
- OpenCV, Pyzbar (QR detection)

### DevOps
- Docker & Docker Compose
- GitHub Actions CI/CD
- Kubernetes (optional)

## 📊 Features

### Email Protection
- ✅ Real-time phishing detection
- ✅ Link disabling and QR code blurring
- ✅ Malicious image hiding
- ✅ Fake login form blocking
- ✅ Download prevention

### Explainable AI
- ✅ Reason for detection
- ✅ Evidence from analysis
- ✅ Suggested actions
- ✅ Trust score with confidence

### Dashboard Analytics
- ✅ Threat timeline
- ✅ Blocked emails history
- ✅ Attack type distribution
- ✅ Brand impersonation statistics
- ✅ Risk patterns

### Personalization
- ✅ Trusted contacts
- ✅ Frequent domains
- ✅ Personal security profile
- ✅ False positive learning

## 🔌 API Endpoints

```
POST /api/analyze           - Analyze email
POST /api/report            - Report phishing
GET  /api/dashboard         - Get analytics
GET  /api/history           - Get blocked emails
POST /api/auth/login        - OAuth login
GET  /api/config            - Get extension config
```

## 📈 ML Models

### Pre-trained Models
- BERT for content classification
- RoBERTa for intent detection
- Sentence Transformers for similarity matching
- Random Forest for risk scoring

### Custom Models
- Brand verification classifier
- URL risk assessor
- Manipulation detector
- Psychology analyzer

## 🧪 Testing

```bash
# Unit Tests
npm run test                 # Frontend tests
pytest                       # Backend tests

# Integration Tests
npm run test:integration

# E2E Tests
npm run test:e2e

# Load Testing
locust -f tests/load_test.py
```

## 📝 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Database Schema](docs/DATABASE.md)
- [Extension Development](docs/EXTENSION.md)
- [AI Agent Design](docs/AI_AGENTS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 👥 Team

Enterprise Cybersecurity Architecture & Development

## 🙏 Acknowledgments

- Kaggle datasets for training data
- MITRE ATT&CK framework for threat patterns
- OpenAI, Google, Anthropic for AI models

---

**Status**: Production Ready (v1.0)  
**Last Updated**: July 2026
