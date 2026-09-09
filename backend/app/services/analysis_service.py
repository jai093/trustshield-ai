from __future__ import annotations

import hashlib
import json
import sys
import traceback
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import get_settings
from app.schemas import EmailAnalysisRequest
from app.services.analytics_store import InMemoryAnalyticsStore
from app.services.local_model_service import LocalPhishingModelService
from app.services.mongo_store import MongoAnalyticsStore
from app.services.ollama_service import OllamaAnalyticsService

PROJECT_ROOT = Path(__file__).resolve().parents[3]
AGENT_ROOT = PROJECT_ROOT / "ai-engine" / "agents"
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

try:
    from email_extraction_agent import EmailExtractionAgent
    from brand_verification_agent import BrandVerificationAgent
    from intent_detection_agent import IntentDetectionAgent
    from url_intelligence_agent import URLIntelligenceAgent
    from psychology_manipulation_agent import PsychologyManipulationAgent
    from qr_detection_agent import QRDetectionAgent
    from attachment_analysis_agent import AttachmentAnalysisAgent
    from decision_fusion_agent import DecisionFusionAgent
except ImportError as exc:  # pragma: no cover - runtime fallback
    raise RuntimeError(f"Unable to import AI agents: {exc}") from exc


class EmailAnalysisService:
    """Facade for orchestrating phishing analysis with caching and resilience."""

    def __init__(self, cache_size: int = 256) -> None:
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._cache_size = cache_size
        self.settings = get_settings()
        self.email_extractor = EmailExtractionAgent()
        self.brand_verifier = BrandVerificationAgent()
        self.intent_detector = IntentDetectionAgent()
        self.url_analyzer = URLIntelligenceAgent()
        self.psychology_agent = PsychologyManipulationAgent()
        self.qr_agent = QRDetectionAgent()
        self.attachment_agent = AttachmentAnalysisAgent()
        self.decision_fusion = DecisionFusionAgent()
        self.model_service = LocalPhishingModelService(
            model_path=self.settings.phishing_model_path,
            dataset_path=self.settings.spam_dataset_path,
        )
        self.mongo_store = MongoAnalyticsStore(self.settings.mongodb_uri, self.settings.mongodb_database, self.settings.mongodb_collection)
        self.analytics_store = InMemoryAnalyticsStore()
        self.ollama_service = OllamaAnalyticsService(
            base_url=self.settings.ollama_base_url,
            model=self.settings.ollama_model,
            api_key=self.settings.ollama_api_key_1,
        )

    def analyze(self, email_data: Any, extension_id: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        payload = self._normalize_payload(email_data)
        self._validate_payload(payload)

        cache_key = self._build_cache_key(payload)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        start_time = datetime.now(timezone.utc)
        try:
            extracted_email = self.email_extractor.extract_email_from_json(payload.model_dump())

            brand_analysis = self.brand_verifier.analyze_brand_impersonation(
                sender_email=extracted_email.metadata.sender,
                subject=extracted_email.metadata.subject,
                body=extracted_email.content.body,
                sender_name=extracted_email.metadata.sender,
            )

            intent_analysis = self.intent_detector.analyze_intent(
                subject=extracted_email.metadata.subject,
                body=extracted_email.content.body,
                sender=extracted_email.metadata.sender,
            )

            url_results = []
            for link in extracted_email.links:
                if not getattr(link, "href", None):
                    continue
                url_risk = self.url_analyzer.analyze_url(link.href)
                if hasattr(url_risk, "to_dict"):
                    url_results.append(url_risk.to_dict())
                else:
                    url_results.append({
                        "url": getattr(url_risk, "url", link.href),
                        "risk_score": getattr(url_risk, "risk_score", 0),
                        "indicators": getattr(url_risk, "indicators", {}),
                        "evidence": getattr(url_risk, "evidence", []),
                    })
            psychology_analysis = self.psychology_agent.analyze_manipulation(
                subject=extracted_email.metadata.subject,
                body=extracted_email.content.body,
                sender=extracted_email.metadata.sender,
            )
            qr_analysis = self.qr_agent.analyze_qr_destination("", "") if False else {"qr_codes": []}
            normalized_attachments = []
            for attachment in extracted_email.attachments:
                if isinstance(attachment, dict):
                    normalized_attachments.append({
                        "name": attachment.get("name") or attachment.get("filename") or "",
                        "mimeType": attachment.get("mime_type") or attachment.get("mimeType") or "",
                        "size": attachment.get("size", 0),
                    })
                else:
                    normalized_attachments.append({
                        "name": getattr(attachment, "name", "") or getattr(attachment, "filename", ""),
                        "mimeType": getattr(attachment, "mime_type", "") or getattr(attachment, "mimeType", ""),
                        "size": getattr(attachment, "size", 0),
                    })
            attachment_analyses = self.attachment_agent.analyze_attachments(normalized_attachments)
            attachment_analysis = {
                "risk_score": max((item.get("risk_score", 0) for item in attachment_analyses), default=0),
                "attachments": attachment_analyses,
            }

            decision_result = self.decision_fusion.fuse_analysis(
                email_extraction={},
                brand_analysis=brand_analysis,
                intent_analysis=intent_analysis,
                url_analysis={"urls": url_results},
                psychology_analysis=psychology_analysis,
                qr_analysis=qr_analysis,
                attachment_analysis=attachment_analysis,
            )

            processing_time = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            ml_signal = self.model_service.score_text(
                " | ".join(filter(None, [extracted_email.metadata.subject, extracted_email.content.body]))
            )
            
            # STRICT FUSION: Take the maximum of AI reasoning and ML detection so NOTHING slips through
            fused_risk_score = max(decision_result.overall_risk_score, ml_signal["risk_score"])
            fused_risk_score = max(0, min(100, fused_risk_score))
            
            # Strict mode: Override category if ML says it's bad but agents didn't catch it
            threat_category_val = decision_result.threat_category.value
            
            # If the user is scanning an email already in the Gmail spam folder, unequivocally flag it
            if getattr(payload, "isSpamFolder", False):
                fused_risk_score = max(fused_risk_score, 100)
                threat_category_val = "spam"
            elif ml_signal["risk_score"] >= 60 and threat_category_val in ["none", "unknown"]:
                threat_category_val = "spam" if ml_signal["risk_score"] < 80 else "scam"
                
            risk_level = self._risk_level_from_score(fused_risk_score)
            
            # Update suggested action to block/warn if strict score is high
            suggested_action_val = decision_result.suggested_action.value
            if fused_risk_score >= 75:
                suggested_action_val = "block"
                if not decision_result.prevention_actions:
                    decision_result.prevention_actions.append({
                        "type": "DISABLE_BUTTONS",
                        "reason": "High risk detected - interactive elements disabled"
                    })
            elif fused_risk_score >= 50:
                suggested_action_val = "warn"
                if not decision_result.prevention_actions:
                    decision_result.prevention_actions.append({
                        "type": "WARN_BANNER",
                        "reason": "Suspicious email detected"
                    })
                
            enrichment = self.ollama_service.enrich_analysis(
                risk_label=str(threat_category_val),
                evidence_text=" | ".join(decision_result.detailed_reasons or []),
                risk_level=risk_level,
            )
            explanation = enrichment.get("summary") or decision_result.explanation
            result = {
                "success": True,
                "data": {
                    "risk_score": fused_risk_score,
                    "overall_risk_score": fused_risk_score,
                    "risk_level": risk_level,
                    "threat_category": threat_category_val,
                    "suggested_action": suggested_action_val,
                    "confidence": decision_result.confidence,
                    "explanation": explanation,
                    "detailed_reasons": decision_result.detailed_reasons,
                    "prevention_actions": decision_result.prevention_actions,
                    "agent_scores": {
                        "brand_verification": brand_analysis.get("impersonation_score", 0),
                        "intent_detection": intent_analysis.get("intent_score", 0),
                        "url_intelligence": max((item.get("risk_score", 0) for item in url_results), default=0),
                        "psychology_manipulation": psychology_analysis.get("manipulation_score", 0),
                        "attachment_analysis": attachment_analysis.get("risk_score", 0),
                        "local_model": ml_signal["risk_score"],
                    },
                    "timestamp": decision_result.timestamp,
                    "processing_time_ms": processing_time,
                    "metadata": {
                        "extension_id": extension_id,
                        "user_id": user_id,
                        "content_hash": cache_key,
                        "ai_provider": enrichment.get("provider", "fallback"),
                    },
                },
            }
        except Exception as exc:  # pragma: no cover - defensive fallback
            traceback.print_exc()
            result = {
                "success": False,
                "error": str(exc),
                "data": {
                    "risk_score": 0,
                    "overall_risk_score": 0,
                    "risk_level": "LOW",
                    "threat_category": "UNKNOWN",
                    "suggested_action": "allow",
                    "confidence": 0.0,
                    "explanation": "Analysis failed; falling back to low risk.",
                    "detailed_reasons": ["Fallback triggered because analysis encountered an unexpected error."],
                    "prevention_actions": [],
                    "agent_scores": {},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "processing_time_ms": 0,
                    "metadata": {
                        "extension_id": extension_id,
                        "user_id": user_id,
                        "content_hash": cache_key,
                    },
                },
            }

        self._cache[cache_key] = result
        self._trim_cache()
        self._persist_result(payload, cache_key, result)
        return result

    def _persist_result(self, payload: EmailAnalysisRequest, cache_key: str, result: Dict[str, Any]) -> None:
        record_payload = {
            "id": cache_key,
            "user_id": result.get("data", {}).get("metadata", {}).get("user_id"),
            "sender": payload.sender,
            "subject": payload.subject,
            "risk_level": result.get("data", {}).get("risk_level"),
            "risk_score": result.get("data", {}).get("overall_risk_score"),
            "threat_category": result.get("data", {}).get("threat_category"),
            "prevention_actions": result.get("data", {}).get("prevention_actions", []),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            self.analytics_store.store_analysis(record_payload)
        except Exception:
            pass

        try:
            self.mongo_store.store_analysis(record_payload)
        except Exception:
            pass

    def get_dashboard_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        if self.mongo_store.is_available():
            return self.mongo_store.get_stats(user_id)
        return self.analytics_store.get_stats(user_id)

    def get_email_history(self, user_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        if self.mongo_store.is_available():
            return self.mongo_store.get_history(user_id, limit, offset)
        return self.analytics_store.get_history(user_id, limit, offset)

    def _normalize_payload(self, payload: Any) -> EmailAnalysisRequest:
        if isinstance(payload, EmailAnalysisRequest):
            return payload
        if isinstance(payload, dict):
            return EmailAnalysisRequest(**payload)
        raise TypeError("Email analysis payload must be a dictionary or EmailAnalysisRequest")

    def _validate_payload(self, payload: EmailAnalysisRequest) -> None:
        if not payload.summary_text().strip():
            raise ValueError("Email body or subject must be provided")

    def _build_cache_key(self, payload: EmailAnalysisRequest) -> str:
        text = json.dumps(
            {
                "sender": payload.sender,
                "subject": payload.subject,
                "body": payload.body,
                "links": [link.model_dump() for link in payload.links],
                "attachments": [attachment.model_dump() for attachment in payload.attachments],
                "isSpamFolder": getattr(payload, "isSpamFolder", False),
            },
            sort_keys=True,
        )
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _trim_cache(self) -> None:
        while len(self._cache) > self._cache_size:
            self._cache.popitem(last=False)

    def _risk_level_from_score(self, score: int) -> str:
        if score >= 75:
            return "CRITICAL"
        if score >= 50:
            return "HIGH"
        if score >= 25:
            return "MEDIUM"
        return "LOW"
