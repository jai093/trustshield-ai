"""
Intent Detection Agent
Responsibilities:
- Determine what the attacker is trying to achieve
- Classify email intent
- Generate Intent Score
"""

from typing import Dict, List, Tuple
from enum import Enum
import re
from dataclasses import dataclass


class IntentType(Enum):
    """Possible phishing intents"""
    CREDENTIAL_THEFT = "credential_theft"
    FINANCIAL_FRAUD = "financial_fraud"
    INVOICE_SCAM = "invoice_scam"
    GIFT_CARD_SCAM = "gift_card_scam"
    BANK_SCAM = "bank_scam"
    CRYPTO_SCAM = "crypto_scam"
    MALWARE_DELIVERY = "malware_delivery"
    FAKE_VERIFICATION = "fake_verification"
    PASSWORD_RESET_SCAM = "password_reset_scam"
    PRIZE_LOTTERY = "prize_lottery"
    TECH_SUPPORT_SCAM = "tech_support_scam"
    BUSINESS_EMAIL_COMPROMISE = "business_email_compromise"
    UNKNOWN = "unknown"


@dataclass
class IntentMatch:
    intent_type: IntentType
    probability: float  # 0-1
    keywords_found: List[str]
    evidence: List[str]
    risk_score: int  # 0-100


# Intent-specific keywords
INTENT_KEYWORDS = {
    IntentType.CREDENTIAL_THEFT: {
        "keywords": [
            "verify account", "confirm identity", "verify password", "login",
            "account access", "security check", "click here", "verify now",
            "update information", "confirm credentials"
        ],
        "patterns": [
            r"verify.*account",
            r"confirm.*password",
            r"update.*information",
            r"security.*check",
        ]
    },
    IntentType.FINANCIAL_FRAUD: {
        "keywords": [
            "payment", "invoice", "billing", "refund", "charge", "transaction",
            "fund transfer", "wire transfer", "bank account", "credit card"
        ],
        "patterns": [
            r"payment.*required",
            r"pending.*payment",
            r"invoice.*action",
            r"fund.*transfer",
        ]
    },
    IntentType.INVOICE_SCAM: {
        "keywords": [
            "invoice", "receipt", "payment due", "overdue", "urgent payment",
            "bill", "statement", "account payable", "amount due"
        ],
        "patterns": [
            r"invoice.*paid",
            r"payment.*overdue",
            r"urgent.*invoice",
            r"confirm.*payment",
        ]
    },
    IntentType.GIFT_CARD_SCAM: {
        "keywords": [
            "gift card", "itunes card", "amazon card", "google play",
            "code", "redeem", "purchase cards", "target card"
        ],
        "patterns": [
            r"buy.*gift.*card",
            r"purchase.*card",
            r"redeem.*card",
        ]
    },
    IntentType.BANK_SCAM: {
        "keywords": [
            "bank", "account suspended", "verify banking", "confirm account",
            "update banking info", "security alert", "unusual activity"
        ],
        "patterns": [
            r"account.*suspended",
            r"unusual.*activity",
            r"verify.*banking",
        ]
    },
    IntentType.CRYPTO_SCAM: {
        "keywords": [
            "bitcoin", "ethereum", "crypto", "wallet", "private key",
            "seed phrase", "exchange", "blockchain", "digital currency"
        ],
        "patterns": [
            r"verify.*wallet",
            r"confirm.*crypto",
            r"update.*exchange",
        ]
    },
    IntentType.MALWARE_DELIVERY: {
        "keywords": [
            "download", "attachment", "document", "receipt", "invoice",
            "report", "file", "zip", "executable"
        ],
        "patterns": [
            r"download.*attachment",
            r"open.*document",
            r"view.*receipt",
        ]
    },
    IntentType.FAKE_VERIFICATION: {
        "keywords": [
            "verify", "confirm", "validate", "authenticate", "check",
            "approval", "authorized", "2fa", "two-factor"
        ],
        "patterns": [
            r"verify.*identity",
            r"confirm.*verification",
            r"two-factor.*required",
        ]
    },
    IntentType.PASSWORD_RESET_SCAM: {
        "keywords": [
            "password reset", "reset password", "change password",
            "update password", "confirm password", "new password"
        ],
        "patterns": [
            r"reset.*password",
            r"change.*password",
            r"password.*expired",
        ]
    },
    IntentType.PRIZE_LOTTERY: {
        "keywords": [
            "congratulations", "winner", "prize", "lottery", "claim",
            "reward", "bonus", "free", "won", "selected"
        ],
        "patterns": [
            r"you.*won",
            r"claim.*prize",
            r"congratulations.*winner",
        ]
    },
    IntentType.TECH_SUPPORT_SCAM: {
        "keywords": [
            "error", "virus", "malware", "infected", "tech support",
            "call us", "urgent fix", "your computer", "system warning"
        ],
        "patterns": [
            r"system.*infected",
            r"call.*support",
            r"urgent.*fix",
        ]
    },
    IntentType.BUSINESS_EMAIL_COMPROMISE: {
        "keywords": [
            "urgent", "wire transfer", "payment", "invoice", "request",
            "ceo", "boss", "confidential", "immediate action"
        ],
        "patterns": [
            r"urgent.*transfer",
            r"wire.*immediately",
            r"confidential.*action",
        ]
    },
}


class IntentDetectionAgent:
    """Detect attacker intent from email content"""
    
    def __init__(self):
        self.intent_keywords = INTENT_KEYWORDS
    
    def extract_text_features(self, 
                             subject: str,
                             body: str,
                             sender: str) -> str:
        """Combine all text for analysis"""
        return f"{subject} {body}".lower()
    
    def count_keyword_matches(self, 
                             text: str,
                             keywords: List[str]) -> Tuple[int, List[str]]:
        """Count how many keywords appear in text"""
        matches = 0
        found_keywords = []
        
        for keyword in keywords:
            if keyword.lower() in text.lower():
                matches += 1
                found_keywords.append(keyword)
        
        return matches, found_keywords
    
    def check_pattern_matches(self, 
                             text: str,
                             patterns: List[str]) -> Tuple[int, List[str]]:
        """Check regex patterns"""
        matches = 0
        found_patterns = []
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
                found_patterns.append(pattern)
        
        return matches, found_patterns
    
    def detect_urgency_language(self, text: str) -> Tuple[float, List[str]]:
        """Detect urgency and pressure tactics"""
        urgency_keywords = [
            "urgent", "immediately", "asap", "right now", "act now",
            "confirm now", "verify now", "update now", "expires", "expired",
            "limited time", "within 24 hours", "within 48 hours"
        ]
        
        count, found = self.count_keyword_matches(text, urgency_keywords)
        urgency_score = min(count / len(urgency_keywords), 1.0)
        
        return urgency_score, found
    
    def detect_fear_language(self, text: str) -> Tuple[float, List[str]]:
        """Detect fear-based tactics"""
        fear_keywords = [
            "suspended", "locked", "disabled", "blocked", "compromised",
            "unauthorized", "unusual activity", "suspicious",
            "problem", "issue", "warning", "alert", "danger"
        ]
        
        count, found = self.count_keyword_matches(text, fear_keywords)
        fear_score = min(count / len(fear_keywords), 1.0)
        
        return fear_score, found
    
    def detect_call_to_action(self, text: str) -> Tuple[float, List[str]]:
        """Detect strong calls to action"""
        cta_keywords = [
            "click", "click here", "click below", "tap here",
            "download", "open", "view", "submit", "confirm",
            "verify", "update", "sign in", "login"
        ]
        
        count, found = self.count_keyword_matches(text, cta_keywords)
        cta_score = min(count / len(cta_keywords), 1.0)
        
        return cta_score, found
    
    def analyze_intent(self, 
                      subject: str,
                      body: str,
                      sender: str = "") -> Dict:
        """
        Analyze email intent
        
        Returns:
            {
                "detected_intents": List[IntentMatch],
                "primary_intent": IntentType,
                "intent_score": 0-100,
                "urgency_score": 0-1,
                "fear_tactics": 0-1,
                "evidence": List[str],
            }
        """
        text = self.extract_text_features(subject, body, sender)
        detected_intents = []
        evidence = []
        
        # Check each intent type
        for intent_type, keywords_data in self.intent_keywords.items():
            keyword_count, found_keywords = self.count_keyword_matches(
                text,
                keywords_data["keywords"]
            )
            
            pattern_count, _ = self.check_pattern_matches(
                text,
                keywords_data["patterns"]
            )
            
            # Calculate probability
            total_matches = keyword_count + pattern_count
            max_possible = len(keywords_data["keywords"]) + len(keywords_data["patterns"])
            probability = min(total_matches / max(max_possible, 1), 1.0)
            
            if probability > 0.1:  # If at least 10% match
                risk_score = int(probability * 100)
                
                match = IntentMatch(
                    intent_type=intent_type,
                    probability=probability,
                    keywords_found=found_keywords,
                    evidence=[
                        f"Found {len(found_keywords)} intent-specific keywords",
                        f"Matched {pattern_count} intent patterns"
                    ],
                    risk_score=risk_score
                )
                detected_intents.append(match)
        
        # Sort by probability
        detected_intents.sort(key=lambda x: x.probability, reverse=True)
        
        # Get auxiliary scores
        urgency_score, urgency_keywords = self.detect_urgency_language(text)
        fear_score, fear_keywords = self.detect_fear_language(text)
        cta_score, cta_keywords = self.detect_call_to_action(text)
        
        # Build evidence
        if urgency_keywords:
            evidence.append(f"Urgency language detected: {', '.join(urgency_keywords[:3])}")
        if fear_keywords:
            evidence.append(f"Fear-based tactics: {', '.join(fear_keywords[:3])}")
        if cta_keywords:
            evidence.append(f"Strong CTAs: {', '.join(cta_keywords[:3])}")
        
        return {
            "detected_intents": detected_intents,
            "primary_intent": detected_intents[0].intent_type if detected_intents else IntentType.UNKNOWN,
            "intent_score": detected_intents[0].risk_score if detected_intents else 0,
            "confidence": detected_intents[0].probability if detected_intents else 0,
            "urgency_score": urgency_score,
            "fear_score": fear_score,
            "cta_score": cta_score,
            "evidence": evidence,
        }


# Export
__all__ = [
    "IntentDetectionAgent",
    "IntentType",
    "IntentMatch",
]
