from __future__ import annotations

from typing import Any, Dict, Optional

import requests


class OllamaAnalyticsService:
    """Optional LLM enrichment layer for better explanations and summaries."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None, api_key: Optional[str] = None, timeout: int = 8) -> None:
        self.base_url = (base_url or "").rstrip("/")
        self.model = model or "gpt-oss:120b"
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

    def enrich_analysis(self, risk_label: str, evidence_text: str, risk_level: str) -> Dict[str, Any]:
        if not self.base_url:
            return self._fallback_summary(risk_level, evidence_text)

        prompt = (
            "You are a concise phishing analyst. Summarize the following security signal into a short executive summary. "
            f"Risk label: {risk_label}. Evidence: {evidence_text}. Risk level: {risk_level}."
        )
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = self.session.post(f"{self.base_url}/api/chat", json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            message = data.get("message", {}).get("content") or data.get("response") or ""
            if message.strip():
                return {"summary": message.strip(), "provider": "ollama"}
        except Exception:
            pass

        return self._fallback_summary(risk_level, evidence_text)

    def _fallback_summary(self, risk_level: str, evidence_text: str) -> Dict[str, Any]:
        summary = f"{risk_level.title()} risk detected with behavioral indicators: {evidence_text[:160]}"
        return {"summary": summary, "provider": "fallback"}
