"""
Database Schema Documentation
PostgreSQL schema design and relationships
"""

# TrustShield AI Database Schema

## 1. Database Overview

PostgreSQL database with 8 main tables:
- Users
- AnalysisRecords
- BlockedEmails
- PhishingReports
- ThreatIntelligence
- ExtensionSessions
- DashboardMetrics

## 2. ER Diagram

```
┌─────────────────┐
│     USERS       │
├─────────────────┤
│ id (PK)         │
│ email           │◄──────────────┐
│ username        │                │
│ hashed_password │                │
│ google_id       │                │
│ profile_picture │                │
│ privacy_mode    │                │
│ enable_backend  │                │
│ risk_threshold  │                │
│ created_at      │                │
│ is_active       │                │
└─────────────────┘                │
         ▲                         │
         │ (1)                     │ (1)
         │                         │
    (M)  │                         │
┌────────┼──────────────────────┐  │
│        │                      │  │
│   ANALYSIS_RECORDS      BLOCKED_EMAILS
├────────────────────────────────────┤
│ id (PK)                       │ id │
│ user_id (FK)───────────┐      │ user_id (FK)
│ sender                 │      │ analysis_id (FK)───┐
│ subject                │      │ sender            │
│ risk_score             │      │ reason            │
│ threat_category        │      │ action_taken      │
│ analysis_details (JSON)│      │ user_feedback     │
│ agent_scores (JSON)    │      │ created_at        │
│ prevention_actions     │      └───────────────────┘
│ content_hash           │                │
│ created_at             │◄───────────────┘
│ local_analysis_only    │
└────────────────────────┘
         │
         │ (1) ──────────────────┐
         │                       │ (M)
         │                       │
┌────────┴──────────────────────────────┐
│   PHISHING_REPORTS                   │
├──────────────────────────────────────┤
│ id (PK)                              │
│ user_id (FK)                         │
│ analysis_id (FK)                     │
│ report_type                          │
│ sender                               │
│ email_hash                           │
│ user_description                     │
│ threat_intelligence_processed        │
│ shared_with_community                │
│ created_at                           │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│   THREAT_INTELLIGENCE                │
├──────────────────────────────────────┤
│ id (PK)                              │
│ indicator_type                       │
│ indicator_value                      │
│ threat_category                      │
│ confidence                           │
│ source                               │
│ details (JSON)                       │
│ first_seen                           │
│ last_seen                            │
│ report_count                         │
│ is_active                            │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│   EXTENSION_SESSIONS                 │
├──────────────────────────────────────┤
│ id (PK)                              │
│ user_id (FK)                         │
│ extension_version                    │
│ session_token                        │
│ token_expires_at                     │
│ created_at                           │
│ last_activity_at                     │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│   DASHBOARD_METRICS                  │
├──────────────────────────────────────┤
│ id (PK)                              │
│ user_id (FK, UNIQUE)                 │
│ total_emails_analyzed                │
│ total_phishing_detected              │
│ threat_distribution (JSON)           │
│ brand_impersonation_stats (JSON)     │
│ daily_detections (JSON)              │
│ last_updated                         │
└──────────────────────────────────────┘
```

## 3. Table Specifications

### USERS
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE,
    hashed_password VARCHAR(255),
    google_id VARCHAR(255) UNIQUE,
    profile_picture VARCHAR(500),
    privacy_mode BOOLEAN DEFAULT TRUE,
    enable_backend_analysis BOOLEAN DEFAULT FALSE,
    risk_threshold INTEGER DEFAULT 50,
    trusted_contacts JSONB DEFAULT '[]'::jsonb,
    frequent_domains JSONB DEFAULT '[]'::jsonb,
    trusted_organizations JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);
```

### ANALYSIS_RECORDS
```sql
CREATE TABLE analysis_records (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    sender VARCHAR(255) NOT NULL,
    sender_domain VARCHAR(255),
    subject VARCHAR(500) NOT NULL,
    message_id VARCHAR(255) UNIQUE,
    risk_score INTEGER NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    threat_category VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    analysis_details JSONB NOT NULL,
    agent_scores JSONB NOT NULL,
    prevention_actions JSONB DEFAULT '[]'::jsonb,
    content_hash VARCHAR(64),
    was_blocked BOOLEAN DEFAULT FALSE,
    was_reported BOOLEAN DEFAULT FALSE,
    is_false_positive BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    analysis_time_ms INTEGER NOT NULL,
    local_analysis_only BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_analysis_user_created ON analysis_records(user_id, created_at DESC);
CREATE INDEX idx_analysis_risk_level ON analysis_records(risk_level);
CREATE INDEX idx_analysis_threat_category ON analysis_records(threat_category);
CREATE INDEX idx_analysis_content_hash ON analysis_records(content_hash);
```

### BLOCKED_EMAILS
```sql
CREATE TABLE blocked_emails (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    analysis_id VARCHAR(36) REFERENCES analysis_records(id) ON DELETE CASCADE,
    sender VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    reason VARCHAR(500) NOT NULL,
    action_taken VARCHAR(50) NOT NULL,
    user_feedback VARCHAR(20),
    feedback_at TIMESTAMP,
    user_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_blocked_user_created ON blocked_emails(user_id, created_at DESC);
```

### PHISHING_REPORTS
```sql
CREATE TABLE phishing_reports (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    analysis_id VARCHAR(36) REFERENCES analysis_records(id),
    report_type VARCHAR(50) NOT NULL,
    sender VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    email_hash VARCHAR(64) NOT NULL UNIQUE,
    email_data JSONB,
    user_description TEXT,
    urls_identified JSONB DEFAULT '[]'::jsonb,
    attachments_identified JSONB DEFAULT '[]'::jsonb,
    threat_intelligence_processed BOOLEAN DEFAULT FALSE,
    shared_with_community BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reports_user_type ON phishing_reports(user_id, report_type, created_at DESC);
CREATE INDEX idx_reports_email_hash ON phishing_reports(email_hash);
```

### THREAT_INTELLIGENCE
```sql
CREATE TABLE threat_intelligence (
    id VARCHAR(36) PRIMARY KEY,
    indicator_type VARCHAR(50) NOT NULL,
    indicator_value VARCHAR(500) NOT NULL UNIQUE,
    threat_category VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    source VARCHAR(255) NOT NULL,
    details JSONB,
    evidence JSONB DEFAULT '[]'::jsonb,
    first_seen TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    report_count INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_threat_indicator ON threat_intelligence(indicator_type, indicator_value);
CREATE INDEX idx_threat_active ON threat_intelligence(is_active);
```

### EXTENSION_SESSIONS
```sql
CREATE TABLE extension_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    extension_version VARCHAR(20) NOT NULL,
    chrome_version VARCHAR(20),
    os_type VARCHAR(50),
    session_token VARCHAR(500) UNIQUE NOT NULL,
    token_expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_active ON extension_sessions(user_id, is_active);
```

### DASHBOARD_METRICS
```sql
CREATE TABLE dashboard_metrics (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    total_emails_analyzed INTEGER DEFAULT 0,
    total_phishing_detected INTEGER DEFAULT 0,
    total_blocked INTEGER DEFAULT 0,
    threat_distribution JSONB DEFAULT '{}'::jsonb,
    brand_impersonation_stats JSONB DEFAULT '{}'::jsonb,
    daily_detections JSONB DEFAULT '[]'::jsonb,
    last_updated TIMESTAMP DEFAULT NOW()
);
```

## 4. Key Design Decisions

- **UUID for IDs**: Distributed system friendly, privacy-preserving
- **JSONB for flexible data**: Stores complex agent outputs, easy querying
- **Indexes on foreign keys**: Fast joins
- **Indexes on created_at**: Timeline queries
- **Content hash**: Email deduplication
- **Cascade deletes**: User deletion cleans related data

## 5. Performance Considerations

- Partition ANALYSIS_RECORDS by created_at for large datasets
- Archive old records to separate schema
- Materialized views for dashboard metrics
- Read replicas for reporting queries
- Connection pooling (max 20 connections)

## 6. Security Considerations

- All user IDs are opaque UUIDs
- Never log full emails
- Hash sensitive indicators
- Encrypt at rest (PGCRYPTO extension)
- Row-level security for multi-tenant isolation
