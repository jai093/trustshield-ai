import os

from app.core.config import Settings, get_settings
from app.services.ollama_service import OllamaAnalyticsService


def test_settings_expose_mongodb_and_ollama_values(monkeypatch):
    monkeypatch.setenv("MONGODB_URI", "mongodb://example")
    monkeypatch.setenv("OLLAMA_BASE_URL", "https://ollama.example")
    monkeypatch.setenv("OLLAMA_MODEL", "gpt-oss:120b")
    monkeypatch.setenv("OLLAMA_API_KEY_1", "secret-key")

    settings = get_settings()

    assert settings.mongodb_uri == "mongodb://example"
    assert settings.ollama_base_url == "https://ollama.example"
    assert settings.ollama_model == "gpt-oss:120b"
    assert settings.ollama_api_key_1 == "secret-key"


def test_ollama_service_falls_back_when_unavailable(monkeypatch):
    service = OllamaAnalyticsService(base_url="https://ollama.example", model="gpt-oss:120b", api_key="secret-key")

    class DummyResponse:
        def raise_for_status(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(service.session, "post", lambda *args, **kwargs: DummyResponse())

    result = service.enrich_analysis("risk", "urgent login", "high")

    assert "high" in result["summary"].lower()
    assert result["provider"] == "fallback"
