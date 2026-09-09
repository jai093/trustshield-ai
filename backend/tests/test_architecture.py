import pytest

from app.core.config import get_settings
from app.core.security import InMemoryRateLimiter
from app.services.analysis_service import EmailAnalysisService


def test_settings_load_defaults():
    settings = get_settings()
    assert settings.app_name == "TrustShield AI API"
    assert settings.allowed_hosts


def test_rate_limiter_blocks_after_limit():
    limiter = InMemoryRateLimiter(limit=2, window_seconds=60)
    assert limiter.allow("client-1") is True
    assert limiter.allow("client-1") is True
    assert limiter.allow("client-1") is False


def test_analysis_service_returns_structured_result():
    service = EmailAnalysisService()

    payload = {
        "sender": "alerts@contoso.com",
        "subject": "Urgent: Verify Your Account",
        "body": "Please click the link to verify your credentials immediately.",
        "htmlBody": "<html><body><a href='https://evil.example.com'>Verify</a></body></html>",
        "links": [{"text": "Verify", "href": "https://evil.example.com", "visible": True}],
        "images": [],
        "attachments": [],
        "extractedAt": "2026-07-26T00:00:00Z"
    }

    result = service.analyze(payload, extension_id="test-extension")
    assert result["success"] is True
    assert result["data"]["risk_level"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    assert result["data"]["risk_score"] >= 0
    assert result["data"]["prevention_actions"]
