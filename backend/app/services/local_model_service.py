from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "phishing_model.pkl"
DEFAULT_DATASET_PATH = PROJECT_ROOT / "spam.csv"


class LocalPhishingModelService:
    """Use the locally trained phishing model and spam.csv as a fast inference layer."""

    def __init__(self, model_path: Optional[Path | str] = None, dataset_path: Optional[Path | str] = None) -> None:
        self.model_path = Path(model_path or DEFAULT_MODEL_PATH)
        self.dataset_path = Path(dataset_path or DEFAULT_DATASET_PATH)
        self.model: Any = None
        self.dataset_keywords: set[str] = set()
        self._load()

    def _load(self) -> None:
        if self.model_path.exists():
            try:
                with self.model_path.open("rb") as handle:
                    self.model = pickle.load(handle)
            except Exception:
                self.model = None

        if self.dataset_path.exists():
            try:
                frame = pd.read_csv(self.dataset_path, encoding="latin-1")
                text_series = frame.get("Message") or frame.get("message") or frame.get("Text")
                if text_series is not None:
                    tokens = set()
                    for value in text_series.dropna().astype(str):
                        for token in self._tokenize(value):
                            if len(token) > 2:
                                tokens.add(token)
                    self.dataset_keywords = tokens
            except Exception:
                self.dataset_keywords = set()

    def score_text(self, text: str) -> Dict[str, Any]:
        normalized = (text or "").strip()
        if not normalized:
            return {"risk_score": 0, "decision": "safe", "source": "empty"}

        model_score = self._infer_with_model(normalized)
        heuristic_score = self._infer_with_keywords(normalized)
        combined = int(round(min(100, max(model_score, heuristic_score))))
        if combined < 20 and self.model is None and not self.dataset_keywords:
            combined = 0
        return {
            "risk_score": combined,
            "decision": "suspicious" if combined >= 60 else "safe",
            "source": "model" if self.model is not None else "heuristics",
        }

    def _infer_with_model(self, text: str) -> int:
        if self.model is None:
            return 0
        try:
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba([text])[0]
                positive_class = max(probs)
                return int(round(positive_class * 100))
            if hasattr(self.model, "predict"):
                prediction = self.model.predict([text])[0]
                if str(prediction).lower() in {"spam", "phishing", "1", "true", "yes"}:
                    return 85
                return 15
        except Exception:
            return 0
        return 0

    def _infer_with_keywords(self, text: str) -> int:
        tokens = self._tokenize(text)
        if not tokens:
            return 0

        keyword_hits = 0
        suspicious_terms = {
            "urgent", "verify", "password", "login", "click", "account", "bank", "invoice", "update",
            "suspicious", "immediately", "security", "confirm", "free", "won", "prize", "gift", "card",
            "reset", "claim", "limited", "official", "alert"
        }
        keyword_hits += sum(1 for term in suspicious_terms if term in tokens)
        keyword_hits += sum(1 for term in self.dataset_keywords if term in tokens)

        score = min(100, keyword_hits * 6)
        if any(term in tokens for term in {"urgent", "verify", "password", "click", "reset"}):
            score = min(100, score + 15)
        return int(round(score))

    def _tokenize(self, text: str) -> set[str]:
        return {token.lower() for token in text.replace("/", " ").replace("-", " ").split() if len(token) > 2}
