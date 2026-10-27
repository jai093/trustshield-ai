from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "phishing_model.pkl"
DEFAULT_DATASET_PATH = PROJECT_ROOT / "spam.csv"


class LocalPhishingModelService:
    """Use the locally trained phishing model and spam dataset as a fast inference layer."""

    def __init__(self, model_path: Optional[Path | str] = None, dataset_path: Optional[Path | str] = None) -> None:
        self.model_path = Path(model_path or DEFAULT_MODEL_PATH)
        self.dataset_path = Path(dataset_path or DEFAULT_DATASET_PATH)
        self.model: Any = None
        self.vectorizer: Any = None
        self._load()

    def _load(self) -> None:
        if self.model_path.exists():
            try:
                with self.model_path.open("rb") as handle:
                    data = pickle.load(handle)
                    if isinstance(data, dict):
                        self.model = data.get("model")
                        self.vectorizer = data.get("vectorizer")
                    else:
                        self.model = data
                        self.vectorizer = getattr(data, "vectorizer", None)
            except Exception as e:
                print(f"[LocalPhishingModelService] Failed to load model: {e}")
                self.model = None
                self.vectorizer = None

    def score_text(self, text: str, sender: Optional[str] = None) -> Dict[str, Any]:
        # If sender is trusted, immediately return safe
        if sender:
            try:
                from app.services.whitelist_service import whitelist_service
                is_trusted, reason, _ = whitelist_service.is_trusted_sender(sender)
                if is_trusted:
                    return {
                        "risk_score": 0,
                        "decision": "safe",
                        "source": "whitelist",
                        "trusted_reason": reason,
                    }
            except Exception:
                pass

        normalized = (text or "").strip()
        if not normalized:
            return {"risk_score": 0, "decision": "safe", "source": "empty"}

        model_score = self._infer_with_model(normalized)
        heuristic_score = self._infer_with_keywords(normalized)

        # Use model score primarily when model is available; combine carefully with heuristics
        if self.model is not None and self.vectorizer is not None:
            # If model predicts low risk (< 25%), don't let mild heuristics falsely inflate it
            if model_score < 25 and heuristic_score < 50:
                combined = model_score
            else:
                combined = int(round(max(model_score, min(heuristic_score, 80))))
        else:
            combined = heuristic_score

        combined = int(round(min(100, max(0, combined))))
        return {
            "risk_score": combined,
            "decision": "suspicious" if combined >= 50 else "safe",
            "source": "model" if (self.model is not None and self.vectorizer is not None) else "heuristics",
        }

    def _infer_with_model(self, text: str) -> int:
        if self.model is None:
            return 0
        try:
            if self.vectorizer is not None:
                features = self.vectorizer.transform([text])
            else:
                features = [text]

            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(features)[0]
                phish_idx = 1
                if hasattr(self.model, "classes_"):
                    for idx, c in enumerate(self.model.classes_):
                        if str(c).lower() in {"1", "spam", "phishing"}:
                            phish_idx = idx
                            break
                        elif str(c).lower() in {"0", "ham", "legitimate"}:
                            # Phishing is the other class
                            phish_idx = 1 if idx == 0 else 0
                return int(round(float(probs[phish_idx]) * 100))

            if hasattr(self.model, "predict"):
                prediction = self.model.predict(features)[0]
                if str(prediction).lower() in {"spam", "phishing", "1", "true", "yes"}:
                    return 85
                return 10
        except Exception as e:
            print(f"[LocalPhishingModelService] Inference error: {e}")
            return 0
        return 0

    def _infer_with_keywords(self, text: str) -> int:
        tokens = self._tokenize(text)
        if not tokens:
            return 0

        # Highly specific phishing indicators (not ordinary English words)
        credential_terms = {"password", "login", "credentials", "account suspended", "unauthorized access"}
        financial_scam_terms = {"crypto", "bitcoin", "lottery", "won $", "wire transfer", "western union"}
        urgency_terms = {"verify immediately", "act now or account deleted", "suspended within 24 hours"}

        score = 0
        text_lower = text.lower()
        if any(term in text_lower for term in credential_terms):
            score += 35
        if any(term in text_lower for term in financial_scam_terms):
            score += 45
        if any(term in text_lower for term in urgency_terms):
            score += 25

        return min(100, score)

    def _tokenize(self, text: str) -> set[str]:
        return {token.lower() for token in text.replace("/", " ").replace("-", " ").split() if len(token) > 2}
