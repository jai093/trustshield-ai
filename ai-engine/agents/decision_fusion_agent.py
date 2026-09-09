"""
Decision Fusion Agent
Responsibilities:
- Collect all agent outputs
- Generate Overall Risk Score
- Determine threat category
- Suggest prevention actions
- Generate explanations
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone


class ActionType(Enum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    REWRITE = "rewrite"
    REPORT = "report"


class ThreatCategory(Enum):
    NONE = "none"
    CREDENTIAL_THEFT = "credential_theft"
    FINANCIAL_FRAUD = "financial_fraud"
    MALWARE = "malware"
    IMPERSONATION = "impersonation"
    SCAM = "scam"
    UNKNOWN = "unknown"


@dataclass
class DecisionResult:
    overall_risk_score: int  # 0-100
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    threat_category: ThreatCategory
    suggested_action: ActionType
    confidence: float  # 0-1
    prevention_actions: List[Dict[str, str]]
    explanation: str
    detailed_reasons: List[str]
    timestamp: str


class DecisionFusionAgent:
    """Fuse all agent outputs into final decision"""
    
    RISK_THRESHOLDS = {
        "low": (0, 25),
        "medium": (25, 50),
        "high": (50, 75),
        "critical": (75, 100)
    }
    
    AGENT_WEIGHTS = {
        "email_extraction": 0.1,
        "brand_verification": 0.2,
        "intent_detection": 0.25,
        "url_intelligence": 0.2,
        "psychology_manipulation": 0.15,
        "qr_detection": 0.05,
        "attachment_analysis": 0.05,
    }
    
    def __init__(self):
        self.weights = self.AGENT_WEIGHTS
    
    def calculate_weighted_score(self, agent_scores: Dict[str, int]) -> int:
        """Calculate weighted risk score from all agents"""
        weighted_sum = 0.0
        weight_sum = 0.0
        
        for agent_name, score in agent_scores.items():
            weight = self.weights.get(agent_name, 0.1)
            weighted_sum += score * weight
            weight_sum += weight
        
        if weight_sum == 0:
            return 0
        
        final_score = int(weighted_sum / weight_sum)
        return min(final_score, 100)
    
    def determine_risk_level(self, score: int) -> str:
        """Determine risk level from score"""
        for level, (min_val, max_val) in self.RISK_THRESHOLDS.items():
            if min_val <= score <= max_val:
                return level.upper()
        return "UNKNOWN"
    
    def determine_threat_category(self, 
                                 intent_analysis: Dict,
                                 brand_analysis: Dict,
                                 attachment_risks: List) -> ThreatCategory:
        """Determine threat category from analyses"""
        
        # If high brand impersonation, it's impersonation threat
        if brand_analysis.get("impersonation_score", 0) > 50:
            return ThreatCategory.IMPERSONATION
        
        # If malware/executable attachments, it's malware
        if any(att.get("is_executable") for att in attachment_risks):
            return ThreatCategory.MALWARE
        
        # Get intent type - convert enum to string if needed
        primary_intent = intent_analysis.get("primary_intent", "unknown")
        if hasattr(primary_intent, 'value'):
            primary_intent = primary_intent.value
        primary_intent = str(primary_intent).lower()
        
        if "credential" in primary_intent:
            return ThreatCategory.CREDENTIAL_THEFT
        elif "financial" in primary_intent or "fraud" in primary_intent:
            return ThreatCategory.FINANCIAL_FRAUD
        elif "scam" in primary_intent or "lottery" in primary_intent:
            return ThreatCategory.SCAM
        
        return ThreatCategory.UNKNOWN
    
    def suggest_prevention_actions(self, 
                                  risk_score: int,
                                  url_risks: List,
                                  attachment_risks: List,
                                  qr_codes: List) -> List[Dict[str, str]]:
        """Suggest prevention actions based on findings"""
        actions = []
        
        if risk_score > 75:
            # CRITICAL - Block everything
            for url in url_risks:
                if url.get("risk_score", 0) > 50:
                    actions.append({
                        "type": "DISABLE_LINK",
                        "target": url.get("url", ""),
                        "reason": f"High-risk URL detected (score: {url.get('risk_score')})"
                    })
            
            # Block all buttons
            actions.append({
                "type": "DISABLE_BUTTONS",
                "reason": "High phishing risk - all interactive elements disabled"
            })
            
            # Block downloads
            actions.append({
                "type": "BLOCK_DOWNLOADS",
                "reason": "Potential malware detected"
            })
        
        elif risk_score > 50:
            # HIGH - Warn and disable risky elements
            for url in url_risks:
                if url.get("risk_score", 0) > 40:
                    actions.append({
                        "type": "WARN_ON_LINK",
                        "target": url.get("url", ""),
                        "reason": "Suspicious URL detected"
                    })
            
            for att in attachment_risks:
                if att.get("is_executable"):
                    actions.append({
                        "type": "DISABLE_DOWNLOAD",
                        "target": att.get("name", ""),
                        "reason": "Executable file detected"
                    })
        
        elif risk_score > 25:
            # MEDIUM - Show warning banner
            actions.append({
                "type": "WARN_BANNER",
                "reason": "This email has phishing indicators"
            })
        
        # Always blur risky QR codes
        for qr in qr_codes:
            if qr.get("risk_score", 0) > 50:
                actions.append({
                    "type": "BLUR_QR",
                    "reason": "Suspicious QR code detected"
                })
        
        return actions
    
    def generate_explanation(self,
                            risk_score: int,
                            threat_category: ThreatCategory,
                            detailed_reasons: List[str]) -> str:
        """Generate human-readable explanation"""
        
        risk_level = self.determine_risk_level(risk_score)
        
        explanation_templates = {
            ThreatCategory.CREDENTIAL_THEFT: "This email appears to be attempting credential theft. It requests you to verify or confirm your credentials.",
            ThreatCategory.FINANCIAL_FRAUD: "This email appears to be a financial fraud attempt, possibly requesting payment or fund transfer.",
            ThreatCategory.MALWARE: "This email contains suspicious attachments that may contain malware.",
            ThreatCategory.IMPERSONATION: "This email impersonates a known brand or service you trust.",
            ThreatCategory.SCAM: "This email appears to be a scam, potentially offering false prizes or rewards.",
            ThreatCategory.UNKNOWN: "This email has phishing characteristics but the specific threat type is unclear.",
        }
        
        base_explanation = explanation_templates.get(
            threat_category,
            "This email has been flagged as potentially suspicious."
        )
        
        if len(detailed_reasons) > 0:
            base_explanation += f" Specific concerns: {', '.join(detailed_reasons[:2])}"
        
        return base_explanation
    
    def fuse_analysis(self, 
                     email_extraction: Dict,
                     brand_analysis: Dict,
                     intent_analysis: Dict,
                     url_analysis: Dict,
                     psychology_analysis: Dict,
                     qr_analysis: Dict,
                     attachment_analysis: Dict,
                     override_score: Optional[int] = None) -> DecisionResult:
        """
        Fuse all agent analyses into final decision
        """
        
        # Extract scores from each agent
        agent_scores = {
            "brand_verification": brand_analysis.get("impersonation_score", 0),
            "intent_detection": intent_analysis.get("intent_score", 0),
            "url_intelligence": max([u.get("risk_score", 0) for u in url_analysis.get("urls", [])], default=0),
            "psychology_manipulation": int(psychology_analysis.get("manipulation_score", 0) * 100),
            "qr_detection": max([q.get("risk_score", 0) for q in qr_analysis.get("qr_codes", [])], default=0),
            "attachment_analysis": max([a.get("risk_score", 0) for a in attachment_analysis.get("attachments", [])], default=0),
        }
        
        # Calculate final score
        if override_score is not None:
            overall_score = override_score
        else:
            overall_score = self.calculate_weighted_score(agent_scores)
        
        # Determine risk level
        risk_level = self.determine_risk_level(overall_score)
        
        # Determine threat category
        threat_category = self.determine_threat_category(
            intent_analysis,
            brand_analysis,
            attachment_analysis.get("attachments", [])
        )
        
        # Suggest action
        if overall_score >= 75:
            suggested_action = ActionType.BLOCK
        elif overall_score >= 50:
            suggested_action = ActionType.WARN
        elif overall_score >= 25:
            suggested_action = ActionType.WARN
        else:
            suggested_action = ActionType.ALLOW
        
        # Calculate confidence
        avg_score = sum(agent_scores.values()) / len(agent_scores) if agent_scores else 0
        confidence = min(1.0, abs(overall_score - avg_score) / 50 + 0.5)  # Higher confidence if scores agree
        
        # Gather reasons
        detailed_reasons = []
        if brand_analysis.get("impersonation_detected"):
            detailed_reasons.append(f"Brand impersonation: {brand_analysis.get('primary_brand')}")
        if intent_analysis.get("evidence"):
            detailed_reasons.extend(intent_analysis.get("evidence", [])[:2])
        if psychology_analysis.get("evidence"):
            detailed_reasons.extend(psychology_analysis.get("evidence", [])[:1])
        
        # Suggest prevention actions
        prevention_actions = self.suggest_prevention_actions(
            overall_score,
            url_analysis.get("urls", []),
            attachment_analysis.get("attachments", []),
            qr_analysis.get("qr_codes", [])
        )
        
        # Generate explanation
        explanation = self.generate_explanation(overall_score, threat_category, detailed_reasons)
        
        return DecisionResult(
            overall_risk_score=overall_score,
            risk_level=risk_level,
            threat_category=threat_category,
            suggested_action=suggested_action,
            confidence=confidence,
            prevention_actions=prevention_actions,
            explanation=explanation,
            detailed_reasons=detailed_reasons,
            timestamp=datetime.now(timezone.utc).isoformat()
        )


# Export
__all__ = [
    "DecisionFusionAgent",
    "DecisionResult",
    "ActionType",
    "ThreatCategory",
]
