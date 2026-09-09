"""
Psychology Manipulation Agent
Detects social engineering and manipulation tactics
"""

from typing import Dict, List, Tuple
from enum import Enum
import re


class ManipulationTactic(Enum):
    FEAR = "fear"
    URGENCY = "urgency"
    AUTHORITY = "authority"
    SCARCITY = "scarcity"
    CURIOSITY = "curiosity"
    REWARD = "reward"
    SOCIAL_PROOF = "social_proof"
    RECIPROCITY = "reciprocity"


# Manipulation detection patterns
MANIPULATION_PATTERNS = {
    ManipulationTactic.FEAR: {
        "keywords": [
            "compromised", "unauthorized", "suspicious",
            "problem", "error", "issue", "trouble",
            "security", "warning", "alert", "danger",
            "urgent action", "act now"
        ],
        "weight": 1.0
    },
    ManipulationTactic.URGENCY: {
        "keywords": [
            "urgent", "immediately", "asap", "right now",
            "now", "within 24 hours", "limited time",
            "expires", "deadline", "hurry", "act fast",
            "before", "today", "tonight", "tomorrow"
        ],
        "weight": 1.0
    },
    ManipulationTactic.AUTHORITY: {
        "keywords": [
            "administrator", "ceo", "director", "manager",
            "official", "authorized", "verify", "confirm",
            "compliance", "required", "must", "need to",
            "important notice", "official notice"
        ],
        "weight": 0.9
    },
    ManipulationTactic.SCARCITY: {
        "keywords": [
            "limited", "limited time", "limited offer",
            "exclusive", "only", "few", "last", "final",
            "ends soon", "sold out", "running out",
            "don't miss", "last chance"
        ],
        "weight": 0.8
    },
    ManipulationTactic.CURIOSITY: {
        "keywords": [
            "click here", "learn more", "find out",
            "discover", "see what", "read more",
            "unknown", "mystery", "surprise",
            "shocking", "unbelievable", "you won't believe"
        ],
        "weight": 0.7
    },
    ManipulationTactic.REWARD: {
        "keywords": [
            "prize", "winner", "won", "reward", "bonus",
            "free", "claim", "congratulations",
            "lucky", "selected", "chosen",
            "gift", "offer", "benefit"
        ],
        "weight": 0.8
    },
    ManipulationTactic.SOCIAL_PROOF: {
        "keywords": [
            "everyone", "most people", "popular",
            "trending", "verified", "top rated",
            "trusted", "recommended", "majority",
            "millions", "thousands"
        ],
        "weight": 0.7
    },
    ManipulationTactic.RECIPROCITY: {
        "keywords": [
            "free gift", "free service", "help you",
            "assist you", "special offer", "for you",
            "exclusive access", "invitation", "special"
        ],
        "weight": 0.7
    }
}


class PsychologyManipulationAgent:
    """Detect manipulation and social engineering tactics"""
    
    def __init__(self):
        self.patterns = MANIPULATION_PATTERNS
    
    def detect_tactic(self, 
                     text: str,
                     tactic: ManipulationTactic) -> Tuple[float, List[str]]:
        """
        Detect specific manipulation tactic
        
        Returns:
            (score: 0-1, found_keywords: List[str])
        """
        tactic_data = self.patterns[tactic]
        keywords = tactic_data["keywords"]
        weight = tactic_data["weight"]
        
        found = []
        text_lower = text.lower()
        
        for keyword in keywords:
            # Use word boundary for more accurate matching
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                found.append(keyword)
        
        # Calculate score based on keyword density
        score = min(len(found) / max(len(keywords), 1), 1.0)
        score *= weight  # Apply tactic-specific weight
        
        return score, found
    
    def count_calls_to_action(self, text: str) -> int:
        """Count number of CTAs in text"""
        cta_patterns = [
            r"\bclick\b", r"\btap\b", r"\bbutton\b",
            r"\bverify\b", r"\bconfirm\b", r"\bupdate\b",
            r"\bsign in\b", r"\blogin\b", r"\bsubmit\b",
            r"\bdownload\b", r"\bopen\b"
        ]
        
        count = 0
        for pattern in cta_patterns:
            count += len(re.findall(pattern, text.lower()))
        
        return count
    
    def analyze_emotional_language(self, text: str) -> Tuple[float, str]:
        """
        Analyze emotional intensity of text
        Returns (score: 0-1, dominant_emotion: str)
        """
        emotions = {
            "fear": ["afraid", "scared", "danger", "risk", "threat", "compromised"],
            "anger": ["angry", "furious", "infuriated", "outrageous"],
            "sadness": ["sad", "depressed", "unfortunate", "regret"],
            "joy": ["happy", "excited", "thrilled", "delighted"],
            "surprise": ["shocked", "surprised", "astonished", "unexpected"],
        }
        
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in emotions.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            emotion_scores[emotion] = count
        
        # Find dominant emotion
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        max_score = emotion_scores[dominant_emotion]
        
        # Calculate overall emotional intensity (0-1)
        total_words = len(text.split())
        emotional_intensity = min(max_score / max(total_words / 20, 1), 1.0)
        
        return emotional_intensity, dominant_emotion
    
    def analyze_language_complexity(self, text: str) -> float:
        """
        Analyze text complexity
        Phishing emails often use simpler language
        Returns score 0-1 (lower = simpler)
        """
        words = text.split()
        if not words:
            return 0
        
        # Count complex words (longer than 10 chars)
        complex_words = sum(1 for w in words if len(w) > 10)
        
        # Complexity ratio
        complexity = complex_words / len(words)
        
        # Normalize (phishing typically < 0.1)
        return min(complexity, 1.0)
    
    def detect_urgency_indicators(self, text: str) -> Dict:
        """Detailed urgency analysis"""
        urgency_keywords = [
            "urgent", "asap", "immediately", "right now",
            "now", "today", "tonight", "tomorrow"
        ]
        
        time_pressure = [
            "24 hours", "48 hours", "within hours", "within days",
            "before", "after", "deadline", "expires"
        ]
        
        action_pressure = [
            "must", "need to", "have to", "required",
            "necessary", "essential", "important"
        ]
        
        text_lower = text.lower()
        
        return {
            "has_urgency": any(kw in text_lower for kw in urgency_keywords),
            "has_time_pressure": any(kw in text_lower for kw in time_pressure),
            "has_action_pressure": any(kw in text_lower for kw in action_pressure),
            "urgency_count": sum(1 for kw in urgency_keywords if kw in text_lower),
        }
    
    def analyze_manipulation(self,
                            subject: str,
                            body: str,
                            sender: str = "") -> Dict:
        """
        Comprehensive manipulation analysis
        
        Returns:
            {
                "manipulation_score": 0-100,
                "detected_tactics": List[Dict],
                "dominant_tactic": str,
                "emotional_intensity": 0-1,
                "cta_count": int,
                "urgency_indicators": Dict,
                "language_complexity": 0-1,
                "confidence": 0-1,
                "evidence": List[str],
            }
        """
        text = f"{subject} {body}".lower()
        
        # Detect all tactics
        detected_tactics = []
        tactic_scores = {}
        
        for tactic in ManipulationTactic:
            score, found = self.detect_tactic(text, tactic)
            tactic_scores[tactic.value] = score
            
            if score > 0.1:  # If detected
                detected_tactics.append({
                    "tactic": tactic.value,
                    "score": score,
                    "keywords_found": found[:3]  # Top 3 keywords
                })
        
        # Sort by score
        detected_tactics.sort(key=lambda x: x["score"], reverse=True)
        
        # Overall manipulation score
        avg_score = sum(tactic_scores.values()) / len(tactic_scores)
        manipulation_score = int(avg_score * 100)
        
        # Emotional analysis
        emotional_intensity, dominant_emotion = self.analyze_emotional_language(text)
        
        # CTAs
        cta_count = self.count_calls_to_action(text)
        
        # Urgency
        urgency = self.detect_urgency_indicators(text)
        
        # Language complexity
        complexity = self.analyze_language_complexity(text)
        
        # Evidence
        evidence = []
        if detected_tactics:
            evidence.append(f"Detected {len(detected_tactics)} manipulation tactics")
        if urgency["urgency_count"] > 2:
            evidence.append("High urgency language detected")
        if emotional_intensity > 0.5:
            evidence.append(f"Strong {dominant_emotion} language detected")
        if cta_count > 3:
            evidence.append(f"Multiple calls-to-action ({cta_count})")
        if complexity < 0.1:
            evidence.append("Simplified language (typical of phishing)")
        
        # Confidence based on number of indicators
        confidence = min(len(detected_tactics) / 5.0, 1.0)
        
        return {
            "manipulation_score": manipulation_score,
            "manipulation_level": "LOW" if manipulation_score < 30 else 
                                 "MEDIUM" if manipulation_score < 60 else 
                                 "HIGH" if manipulation_score < 80 else "CRITICAL",
            "detected_tactics": detected_tactics,
            "dominant_tactic": detected_tactics[0]["tactic"] if detected_tactics else None,
            "emotional_intensity": emotional_intensity,
            "dominant_emotion": dominant_emotion,
            "cta_count": cta_count,
            "urgency_indicators": urgency,
            "language_complexity": complexity,
            "confidence": confidence,
            "evidence": evidence,
        }


# Export
__all__ = [
    "PsychologyManipulationAgent",
    "ManipulationTactic",
]
