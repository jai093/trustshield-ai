import pytest
from app.services.analysis_service import EmailAnalysisService
from app.services.whitelist_service import whitelist_service


def test_whitelist_service_recognizes_college_senders():
    is_trusted, reason, domain = whitelist_service.is_trusted_sender("placement@sairamce.edu.in")
    assert is_trusted is True
    assert domain == "sairamce.edu.in"
    assert "Sri Sairam College of Engineering" in reason

    # Test another faculty/student from sairamce
    is_trusted, reason, domain = whitelist_service.is_trusted_sender("hod.cse@sairamce.edu.in")
    assert is_trusted is True
    assert domain == "sairamce.edu.in"

    # Test general accredited Indian university
    is_trusted, reason, domain = whitelist_service.is_trusted_sender("dean@annauniv.edu")
    assert is_trusted is True

    # Test phishing address
    is_trusted, reason, domain = whitelist_service.is_trusted_sender("support@paypa1-security.com")
    assert is_trusted is False


def test_college_placement_email_analyzed_as_safe():
    service = EmailAnalysisService()
    payload = {
        "sender": "placement@sairamce.edu.in",
        "subject": "Campus Placement Drive 2026 - Registration Mandatory",
        "body": "Dear Students, please register on the portal immediately for the upcoming Zoho campus drive. Google Form link attached.",
        "links": [{"text": "Register", "href": "https://forms.gle/xyz123"}],
        "attachments": [],
    }

    result = service.analyze(payload, extension_id="test-extension")
    assert result["success"] is True
    data = result["data"]
    assert data["risk_score"] == 0
    assert data["risk_level"] == "LOW"
    assert data["threat_category"] == "none"
    assert data["suggested_action"] == "allow"
    assert len(data["prevention_actions"]) == 0
    assert any("Trusted Sender" in r for r in data["detailed_reasons"])
