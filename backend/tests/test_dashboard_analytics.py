from app.services.analytics_store import InMemoryAnalyticsStore


def test_dashboard_stats_fall_back_to_global_records_for_dashboard_user():
    store = InMemoryAnalyticsStore()
    store.records.clear()
    store.store_analysis({
        "user_id": None,
        "sender": "alerts@contoso.com",
        "subject": "Urgent verification required",
        "risk_level": "HIGH",
        "risk_score": 82,
        "threat_category": "credential_theft",
        "prevention_actions": ["block"],
        "timestamp": "2026-07-26T00:00:00Z",
    })

    stats = store.get_stats("dashboard-user")

    assert stats["success"] is True
    assert stats["data"]["total_emails_analyzed"] == 1
    assert stats["data"]["total_phishing_detected"] == 1
    assert stats["data"]["total_blocked"] == 1
