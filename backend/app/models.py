"""
Database Models
SQLAlchemy ORM models for PostgreSQL
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(255), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)  # For local auth
    google_id = Column(String(255), unique=True, nullable=True)  # For OAuth
    profile_picture = Column(String(500), nullable=True)
    
    # Privacy settings
    privacy_mode = Column(Boolean, default=True)
    enable_backend_analysis = Column(Boolean, default=False)
    risk_threshold = Column(Integer, default=50)
    
    # Profile data
    trusted_contacts = Column(JSON, default=list)
    frequent_domains = Column(JSON, default=list)
    trusted_organizations = Column(JSON, default=list)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_email', 'email'),
        Index('idx_google_id', 'google_id'),
    )


class AnalysisRecord(Base):
    """Email analysis record"""
    __tablename__ = "analysis_records"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # Email metadata
    sender = Column(String(255), nullable=False)
    sender_domain = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=False)
    message_id = Column(String(255), nullable=True, unique=True)
    
    # Analysis results
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(50), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    threat_category = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Detailed analysis (JSON)
    analysis_details = Column(JSON, nullable=False)
    agent_scores = Column(JSON, nullable=False)
    prevention_actions = Column(JSON, default=list)
    
    # Email content hash (for deduplication)
    content_hash = Column(String(64), index=True, nullable=True)
    
    # Status
    was_blocked = Column(Boolean, default=False)
    was_reported = Column(Boolean, default=False)
    is_false_positive = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    analysis_time_ms = Column(Integer, nullable=False)
    local_analysis_only = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_risk_level', 'risk_level'),
        Index('idx_threat_category', 'threat_category'),
    )


class BlockedEmail(Base):
    """Blocked/flagged email record"""
    __tablename__ = "blocked_emails"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    analysis_id = Column(String(36), ForeignKey('analysis_records.id'), nullable=False)
    
    sender = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    reason = Column(String(500), nullable=False)
    action_taken = Column(String(50), nullable=False)  # BLOCKED, WARNED, REWRITTEN
    
    # User feedback
    user_feedback = Column(String(20), nullable=True)  # CORRECT, FALSE_POSITIVE, SKIP
    feedback_at = Column(DateTime, nullable=True)
    user_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_user_blocked', 'user_id', 'created_at'),
    )


class PhishingReport(Base):
    """User-submitted phishing reports"""
    __tablename__ = "phishing_reports"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    analysis_id = Column(String(36), ForeignKey('analysis_records.id'), nullable=True)
    
    report_type = Column(String(50), nullable=False)  # PHISHING, SPAM, FALSE_POSITIVE
    sender = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    
    # Email content (anonymized)
    email_hash = Column(String(64), nullable=False, index=True)
    email_data = Column(JSON, nullable=True)  # Partial data if user consents
    
    # Report details
    user_description = Column(Text, nullable=True)
    urls_identified = Column(JSON, default=list)
    attachments_identified = Column(JSON, default=list)
    
    # Intelligence
    threat_intelligence_processed = Column(Boolean, default=False)
    shared_with_community = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_user_reports', 'user_id', 'created_at'),
        Index('idx_report_type', 'report_type'),
    )


class ThreatIntelligence(Base):
    """Known phishing indicators (IPs, domains, email addresses)"""
    __tablename__ = "threat_intelligence"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    indicator_type = Column(String(50), nullable=False)  # DOMAIN, IP, EMAIL, HASH
    indicator_value = Column(String(500), nullable=False, index=True, unique=True)
    
    threat_category = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)  # 0-1
    source = Column(String(255), nullable=False)  # User reports, external feeds, etc.
    
    details = Column(JSON, nullable=True)
    evidence = Column(JSON, default=list)
    
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    report_count = Column(Integer, default=1)
    
    is_active = Column(Boolean, default=True, index=True)
    
    __table_args__ = (
        Index('idx_indicator', 'indicator_type', 'indicator_value'),
    )


class ExtensionSession(Base):
    """Chrome Extension session tracking"""
    __tablename__ = "extension_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    extension_version = Column(String(20), nullable=False)
    chrome_version = Column(String(20), nullable=True)
    os_type = Column(String(50), nullable=True)
    
    session_token = Column(String(500), unique=True, nullable=False)
    token_expires_at = Column(DateTime, nullable=False)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_user_sessions', 'user_id', 'is_active'),
    )


class DashboardMetrics(Base):
    """Aggregated metrics for dashboard (updated daily)"""
    __tablename__ = "dashboard_metrics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, unique=True)
    
    total_emails_analyzed = Column(Integer, default=0)
    total_phishing_detected = Column(Integer, default=0)
    total_blocked = Column(Integer, default=0)
    
    # By threat category
    threat_distribution = Column(JSON, default=dict)
    # { "credential_theft": 10, "financial_fraud": 5, ... }
    
    # By brand
    brand_impersonation_stats = Column(JSON, default=dict)
    # { "Microsoft": 5, "Google": 3, ... }
    
    # Trend data
    daily_detections = Column(JSON, default=list)
    # [ { "date": "2026-07-26", "count": 5 }, ... ]
    
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Create indexes
__all__ = [
    'Base',
    'User',
    'AnalysisRecord',
    'BlockedEmail',
    'PhishingReport',
    'ThreatIntelligence',
    'ExtensionSession',
    'DashboardMetrics',
]
