"""
Installation and Deployment Guide
Step-by-step setup for development and production
"""

# TrustShield AI Installation Guide

## Prerequisites

- Node.js 18+ (LTS)
- Python 3.10+
- Docker & Docker Compose (optional)
- PostgreSQL 14+ (if not using Docker)
- Redis (if not using Docker)
- Chrome/Chromium browser
- Google OAuth credentials (optional, for OAuth login)

## Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd trustshield-ai
```

### 2. Environment Configuration

Copy environment template and fill in values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
DATABASE_URL=postgresql://trustshield:password@localhost:5432/trustshield_ai
REDIS_URL=redis://localhost:6379/0
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
SECRET_KEY=your-secret-key-here
```

### 3. Option A: Docker Compose (Recommended for Development)

```bash
# Build and start all services
docker-compose up -d

# Watch logs
docker-compose logs -f

# Access services:
# Backend API: http://localhost:8000
# Dashboard: http://localhost:3000
# PostgreSQL: localhost:5432
# Redis: localhost:6379
```

### 4. Option B: Manual Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create database (make sure PostgreSQL is running)
python scripts/init_db.py

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload

# Server runs at http://localhost:8000
```

#### Chrome Extension Setup

```bash
# Navigate to extension directory
cd chrome-extension

# Install dependencies
npm install

# Build extension
npm run build

# Load unpacked extension in Chrome:
# 1. Open chrome://extensions
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select the 'build' directory
```

#### Dashboard Setup

```bash
# Navigate to dashboard directory
cd dashboard

# Install dependencies
npm install

# Start development server
npm run dev

# Dashboard runs at http://localhost:5173
```

### 5. Verify Installation

```bash
# Check backend health
curl http://localhost:8000/health

# Check dashboard (in browser)
open http://localhost:3000

# Verify extension is loaded in chrome://extensions
```

## Production Deployment

### 1. Build Docker Images

```bash
# Build all services
docker-compose -f docker-compose.prod.yml build

# Push to registry (optional)
docker tag trustshield-backend:latest <registry>/trustshield-backend:latest
docker push <registry>/trustshield-backend:latest
```

### 2. Kubernetes Deployment

Create deployment files:

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trustshield-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: trustshield-backend
  template:
    metadata:
      labels:
        app: trustshield-backend
    spec:
      containers:
      - name: backend
        image: <registry>/trustshield-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: trustshield-secrets
              key: database_url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: trustshield-backend
spec:
  selector:
    app: trustshield-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy to Kubernetes:

```bash
# Apply secrets
kubectl create secret generic trustshield-secrets \
  --from-literal=database_url=$DATABASE_URL \
  --from-literal=google_client_id=$GOOGLE_CLIENT_ID

# Apply deployment
kubectl apply -f backend-deployment.yaml

# Check status
kubectl get pods
kubectl get svc trustshield-backend
```

### 3. Database Setup for Production

```bash
# Create production database
createdb -U postgres trustshield_ai_prod

# Run migrations
DATABASE_URL=postgresql://user:password@prod-db:5432/trustshield_ai_prod \
alembic upgrade head

# Create backups
pg_dump -U postgres trustshield_ai_prod > backup.sql
```

### 4. Chrome Extension Publication

For Chrome Web Store:

1. Prepare extension package:
```bash
cd chrome-extension
npm run build
zip -r extension.zip build/
```

2. Upload to Chrome Web Store:
   - Go to https://chrome.google.com/webstore/developer/dashboard
   - Upload extension.zip
   - Fill metadata and submit for review

3. Set API endpoints for production:
```bash
# Update API endpoint in extension config
# chrome-extension/src/config.ts
export const API_ENDPOINT = 'https://api.trustshield.io';
```

### 5. SSL/TLS Setup

For production API:

```bash
# Use Let's Encrypt with Certbot
certbot certonly --standalone -d api.trustshield.io

# Configure HTTPS in FastAPI
# Update nginx/reverse proxy configuration
```

### 6. Monitoring & Logging

Setup ELK Stack or similar:

```bash
# Docker Compose with logging
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose logs -f backend

# Or use centralized logging
# - Datadog
# - New Relic
# - CloudWatch
```

### 7. Backup Strategy

```bash
# Automated daily backups
0 2 * * * pg_dump trustshield_ai_prod | gzip > /backups/db_$(date +%Y%m%d).sql.gz

# Backup Redis
redis-cli BGSAVE
redis-cli --rdb /backups/redis_dump.rdb
```

### 8. Performance Tuning

#### PostgreSQL

```sql
-- Connection pooling
max_connections = 100
shared_buffers = 256MB
work_mem = 4MB

-- Query optimization
random_page_cost = 1.1
effective_cache_size = 1GB
```

#### Redis

```conf
# redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
```

#### FastAPI

```python
# In production, use Gunicorn with multiple workers
# gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## Common Issues & Troubleshooting

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -h localhost -U trustshield -d trustshield_ai

# Check Redis connection
redis-cli ping
```

### Extension Not Loading

1. Clear cache: chrome://settings/clearBrowserData
2. Reload extension: chrome://extensions (refresh)
3. Check browser console: chrome://extensions -> Details -> Errors

### API Connection Issues

```bash
# Test API endpoint
curl -X GET http://localhost:8000/health

# Check CORS settings in .env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Database Migration Issues

```bash
# Check current revision
alembic current

# Rollback one revision
alembic downgrade -1

# View migration history
alembic history

# Create new migration after schema change
alembic revision --autogenerate -m "description"
```

## Maintenance

### Regular Tasks

- Daily: Monitor logs and alerts
- Weekly: Review blocked emails, false positives
- Monthly: Update threat intelligence feeds
- Quarterly: Database optimization, backups verification
- Annually: Security audit, dependency updates

### Updates

```bash
# Update dependencies
pip install --upgrade -r requirements.txt
npm update

# Update Chrome extension
npm run build
# Test in staging, then publish to Web Store

# Update Docker images
docker-compose pull
docker-compose up -d
```

## Security Hardening

1. **Network Security**
   - Use VPN for admin access
   - Firewall rules (only allow necessary ports)
   - DDoS protection

2. **Data Security**
   - Enable encryption at rest
   - Use encrypted connections (TLS 1.3+)
   - Regular security updates

3. **Access Control**
   - Strong passwords (20+ characters)
   - MFA for admin access
   - Rotate API keys regularly

4. **Monitoring**
   - Set up alerts for anomalies
   - Regular security scans
   - Audit logs retention (90 days minimum)

## Support

For issues and questions:
- GitHub Issues: https://github.com/trustshield-ai/issues
- Documentation: https://docs.trustshield.io
- Email: support@trustshield.io
