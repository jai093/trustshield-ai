"""
Brand Verification Agent
Responsibilities:
- Detect brand impersonation
- Compare sender domain with known brands
- Analyze logo and visual similarity
- Generate Brand Similarity Score
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from difflib import SequenceMatcher


class KnownBrand(Enum):
    """Known brands that are frequently impersonated"""
    MICROSOFT = "microsoft"
    GOOGLE = "google"
    AMAZON = "amazon"
    PAYPAL = "paypal"
    APPLE = "apple"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    BANK = "bank"
    IRS = "irs"
    FEDEX = "fedex"
    UPS = "ups"
    DHL = "dhl"


@dataclass
class BrandMatch:
    brand: str
    impersonation_probability: float  # 0-1
    indicators: Dict[str, float]
    evidence: List[str]
    risk_score: int  # 0-100


KNOWN_BRANDS = {
    "microsoft": {
        "official_domains": ["microsoft.com", "outlook.com", "office.com"],
        "official_colors": ["#00A4EF", "#FFB900", "#7FBA00"],
        "keywords": ["microsoft", "office", "outlook", "teams"],
        "logos": ["microsoft.png", "outlook.png"],
    },
    "google": {
        "official_domains": ["google.com", "gmail.com", "drive.google.com"],
        "official_colors": ["#4285F4", "#EA4335", "#FBBC04", "#34A853"],
        "keywords": ["google", "gmail", "drive", "accounts.google"],
        "logos": ["google.png", "gmail.png"],
    },
    "amazon": {
        "official_domains": ["amazon.com", "amazon.com", "aws.amazon.com"],
        "official_colors": ["#FF9900", "#146EB4"],
        "keywords": ["amazon", "aws", "your account"],
        "logos": ["amazon.png", "aws.png"],
    },
    "paypal": {
        "official_domains": ["paypal.com", "accounts.paypal.com"],
        "official_colors": ["#003087", "#009cde"],
        "keywords": ["paypal", "payment", "account"],
        "logos": ["paypal.png"],
    },
    "apple": {
        "official_domains": ["apple.com", "icloud.com", "support.apple.com"],
        "official_colors": ["#555555", "#FFFFFF"],
        "keywords": ["apple", "icloud", "itunes", "appid"],
        "logos": ["apple.png"],
    },
    "linkedin": {
        "official_domains": ["linkedin.com", "em.linkedin.com", "e.linkedin.com"],
        "official_colors": ["#0A66C2", "#FFFFFF"],
        "keywords": ["linkedin", "profile", "connection", "premium"],
        "logos": ["linkedin.png"],
    },
}

TYPOSQUAT_PATTERNS = [
    # Common typos and homoglyphs
    (r"micros[o0]ft", "microsoft"),
    (r"g[0o]ogle", "google"),
    (r"amaz[o0]n", "amazon"),
    (r"paypa1", "paypal"),
    (r"app1e", "apple"),
    (r"l1nked1n", "linkedin"),
]

SUSPICIOUS_SUBDOMAINS = [
    "verify", "confirm", "update", "login", "secure", "auth",
    "account", "payment", "billing", "urgent", "alert", "warning",
]


class BrandVerificationAgent:
    """Verify if email impersonates known brands"""
    
    def __init__(self):
        self.known_brands = KNOWN_BRANDS
    
    def extract_domain_from_email(self, email: str) -> str:
        """Extract domain from email address"""
        if "@" in email:
            return email.split("@")[1].lower()
        return ""
    
    def similarity_ratio(self, a: str, b: str) -> float:
        """Calculate similarity between two strings (0-1)"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def check_typosquatting(self, domain: str) -> Optional[Tuple[str, float]]:
        """Check if domain is a typosquat of known brand"""
        domain_lower = domain.lower()
        
        for pattern, brand in TYPOSQUAT_PATTERNS:
            if re.search(pattern, domain_lower):
                return brand, 0.85
        
        # Check similarity to known domains
        for brand_name, brand_info in self.known_brands.items():
            for official_domain in brand_info["official_domains"]:
                similarity = self.similarity_ratio(domain_lower, official_domain)
                if 0.70 <= similarity < 1.0:  # Similar but not exact
                    return brand_name, similarity
        
        return None
    
    def check_domain_impersonation(self, sender_email: str) -> Optional[BrandMatch]:
        """Check if sender domain impersonates known brand"""
        domain = self.extract_domain_from_email(sender_email)
        
        if not domain:
            return None
        
        evidence = []
        
        # Check for exact match or subdomain match with known brand domains
        for brand_name, brand_info in self.known_brands.items():
            for official_domain in brand_info["official_domains"]:
                if domain == official_domain or domain.endswith("." + official_domain):
                    return None  # Legitimate domain or legitimate subdomain
        
        # Check for typosquatting
        typosquat_match = self.check_typosquatting(domain)
        if typosquat_match:
            brand, similarity = typosquat_match
            evidence.append(f"Domain '{domain}' is similar to official domain '{self.known_brands[brand]['official_domains'][0]}'")
            
            return BrandMatch(
                brand=brand.upper(),
                impersonation_probability=similarity,
                indicators={
                    "domain_similarity": similarity,
                    "suspicious_subdomain": 0,
                    "logo_match": 0,
                    "content_match": 0,
                },
                evidence=evidence,
                risk_score=int(similarity * 100)
            )
        
        return None
    
    def check_content_impersonation(self, 
                                   subject: str,
                                   body: str,
                                   sender_email: str) -> List[BrandMatch]:
        """Check if email content impersonates known brands"""
        matches = []
        evidence_list = []
        
        combined_text = f"{subject} {body}".lower()
        
        for brand_name, brand_info in self.known_brands.items():
            keyword_matches = 0
            
            for keyword in brand_info["keywords"]:
                if keyword.lower() in combined_text:
                    keyword_matches += 1
            
            if keyword_matches > 0:
                # Calculate score based on keyword density
                density = keyword_matches / len(brand_info["keywords"])
                
                # Check if sender is from a suspicious domain
                sender_domain = self.extract_domain_from_email(sender_email)
                is_suspicious = not any(
                    sender_domain == official or sender_domain.endswith("." + official)
                    for official in brand_info["official_domains"]
                )
                
                if is_suspicious:
                    evidence = [
                        f"Email mentions {brand_name} keywords {keyword_matches} times",
                        f"Sender domain '{sender_domain}' is not official {brand_name} domain",
                    ]
                    
                    matches.append(BrandMatch(
                        brand=brand_name.upper(),
                        impersonation_probability=min(density, 1.0),
                        indicators={
                            "keyword_density": density,
                            "suspicious_sender": 1.0 if is_suspicious else 0,
                            "logo_match": 0,
                            "domain_match": 0,
                        },
                        evidence=evidence,
                        risk_score=int(min(density, 1.0) * 100)
                    ))
        
        return matches
    
    def check_suspicious_subdomains(self, sender_email: str) -> Optional[str]:
        """Check for suspicious subdomains in sender"""
        domain = self.extract_domain_from_email(sender_email)
        domain_parts = domain.split(".")
        
        if len(domain_parts) > 2:
            subdomain = domain_parts[0].lower()
            if subdomain in SUSPICIOUS_SUBDOMAINS:
                return subdomain
        
        return None
    
    def analyze_brand_impersonation(self, 
                                   sender_email: str,
                                   subject: str,
                                   body: str,
                                   sender_name: Optional[str] = None) -> Dict:
        """
        Comprehensive brand impersonation analysis
        
        Returns:
            {
                "impersonation_detected": bool,
                "brand_matches": List[BrandMatch],
                "primary_brand": Optional[str],
                "impersonation_score": 0-100,
                "confidence": 0-1,
                "evidence": List[str],
            }
        """
        evidence = []
        all_matches = []
        
        # Check domain impersonation
        domain_match = self.check_domain_impersonation(sender_email)
        if domain_match:
            all_matches.append(domain_match)
            evidence.extend(domain_match.evidence)
        
        # Check content impersonation
        content_matches = self.check_content_impersonation(subject, body, sender_email)
        all_matches.extend(content_matches)
        for match in content_matches:
            evidence.extend(match.evidence)
        
        # Check suspicious subdomains
        suspicious_subdomain = self.check_suspicious_subdomains(sender_email)
        if suspicious_subdomain:
            evidence.append(f"Suspicious subdomain detected: '{suspicious_subdomain}'")
        
        # Sort by risk score
        all_matches.sort(key=lambda x: x.risk_score, reverse=True)
        
        # Calculate overall impersonation score
        overall_score = all_matches[0].risk_score if all_matches else 0
        confidence = all_matches[0].impersonation_probability if all_matches else 0
        
        return {
            "impersonation_detected": len(all_matches) > 0,
            "brand_matches": all_matches,
            "primary_brand": all_matches[0].brand if all_matches else None,
            "impersonation_score": overall_score,
            "confidence": confidence,
            "evidence": evidence,
        }


# Export
__all__ = [
    "BrandVerificationAgent",
    "BrandMatch",
    "KnownBrand",
]
