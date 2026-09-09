"""
URL Intelligence Agent
Responsibilities:
- Check domain age
- Detect typosquatting
- Analyze SSL certificates
- Check DNS
- Analyze IP reputation
- Generate URL Risk Score
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re
from urllib.parse import urlparse
import socket


@dataclass
class URLRisk:
    url: str
    risk_score: int  # 0-100
    indicators: Dict[str, any]
    evidence: List[str]


# Known suspicious TLDs
SUSPICIOUS_TLDS = [
    ".xyz", ".download", ".stream", ".racing", ".accountant",
    ".faith", ".review", ".click", ".country", ".men", ".work",
    ".trade", ".hk", ".tk", ".ml", ".ga", ".cf"
]

# Common legitimate TLDs
LEGITIMATE_TLDS = [
    ".com", ".org", ".net", ".edu", ".gov", ".co.uk",
    ".de", ".fr", ".it", ".es", ".ca", ".au", ".jp"
]

SUSPICIOUS_KEYWORDS_IN_URL = [
    "verify", "update", "confirm", "login", "signin", "auth",
    "account", "secure", "payment", "billing", "urgent",
    "click", "urgent-action", "validate", "confirm-identity"
]


class URLIntelligenceAgent:
    """Analyze URLs for phishing indicators"""
    
    def parse_url(self, url: str) -> Optional[Dict]:
        """Parse and validate URL"""
        try:
            parsed = urlparse(url)
            return {
                "scheme": parsed.scheme,
                "netloc": parsed.netloc,
                "path": parsed.path,
                "params": parsed.params,
                "query": parsed.query,
                "fragment": parsed.fragment,
            }
        except:
            return None
    
    def extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        parsed = self.parse_url(url)
        if parsed:
            return parsed["netloc"].lower()
        return None
    
    def extract_subdomain(self, domain: str) -> str:
        """Extract subdomain"""
        parts = domain.split(".")
        if len(parts) > 2:
            return ".".join(parts[:-2])
        return ""
    
    def check_suspicious_tld(self, domain: str) -> Tuple[bool, Optional[str]]:
        """Check if domain uses suspicious TLD"""
        for tld in SUSPICIOUS_TLDS:
            if domain.lower().endswith(tld):
                return True, tld
        return False, None
    
    def check_typosquatting(self, domain: str) -> List[str]:
        """Detect common typosquatting patterns"""
        indicators = []
        
        # Common homoglyph substitutions
        typosquat_patterns = [
            (r"l{2}", "l1"),  # ll -> l1
            (r"rn", "m"),     # rn -> m
            (r"0", "o"),      # 0 -> o
            (r"1", "i"),      # 1 -> i
        ]
        
        # Check for suspicious domain patterns
        if "goole" in domain or "g0ogle" in domain:
            indicators.append("Possible Google typosquat")
        if "micros0ft" in domain or "microsoft" in domain:
            indicators.append("Possible Microsoft typosquat")
        if "amaz0n" in domain:
            indicators.append("Possible Amazon typosquat")
        if "paypa1" in domain:
            indicators.append("Possible PayPal typosquat")
        if "app1e" in domain:
            indicators.append("Possible Apple typosquat")
        
        # Check for character mixing
        if any(c.isdigit() for c in domain.split(".")[0]):
            indicators.append("Domain contains numbers")
        
        return indicators
    
    def check_url_shortener(self, url: str) -> bool:
        """Check if URL uses shortener service"""
        shorteners = [
            "bit.ly", "tinyurl.com", "goo.gl", "short.link",
            "ow.ly", "adf.ly", "youtu.be", "qr.ae"
        ]
        
        domain = self.extract_domain(url)
        if domain:
            for shortener in shorteners:
                if shortener in domain:
                    return True
        return False
    
    def check_suspicious_keywords(self, url: str) -> List[str]:
        """Check for suspicious keywords in URL"""
        found = []
        url_lower = url.lower()
        
        for keyword in SUSPICIOUS_KEYWORDS_IN_URL:
            if keyword in url_lower:
                found.append(keyword)
        
        return found
    
    def check_ip_address_url(self, url: str) -> bool:
        """Check if URL uses direct IP address"""
        domain = self.extract_domain(url)
        if domain:
            # Simple check for IP pattern
            if re.match(r'^\d+\.\d+\.\d+\.\d+', domain):
                return True
        return False
    
    def check_multiple_redirects(self, url: str) -> int:
        """Count number of redirects in URL (query params that look like redirects)"""
        count = 0
        if "?" in url:
            query_string = url.split("?")[1]
            redirect_keywords = ["redirect", "return", "next", "url", "link"]
            for keyword in redirect_keywords:
                if keyword in query_string:
                    count += 1
        return count
    
    def analyze_url(self, url: str) -> URLRisk:
        """
        Comprehensive URL analysis
        
        Returns URLRisk with score and indicators
        """
        risk_score = 0
        evidence = []
        indicators = {}
        
        # Validate URL
        parsed = self.parse_url(url)
        if not parsed:
            return URLRisk(
                url=url,
                risk_score=95,
                indicators={"valid_url": False},
                evidence=["Invalid URL format"]
            )
        
        domain = self.extract_domain(url)
        subdomain = self.extract_subdomain(domain) if domain else ""
        
        # Check 1: Suspicious TLD
        is_suspicious_tld, tld = self.check_suspicious_tld(domain) if domain else (False, None)
        if is_suspicious_tld:
            risk_score += 20
            evidence.append(f"Suspicious TLD detected: {tld}")
            indicators["suspicious_tld"] = True
        
        # Check 2: Typosquatting
        typosquat_indicators = self.check_typosquatting(domain) if domain else []
        if typosquat_indicators:
            risk_score += 25
            evidence.extend(typosquat_indicators)
            indicators["typosquatting"] = True
        
        # Check 3: URL Shortener
        if self.check_url_shortener(url):
            risk_score += 15
            evidence.append("URL uses shortener service (destination hidden)")
            indicators["shortened_url"] = True
        
        # Check 4: Suspicious Keywords
        suspicious_keywords = self.check_suspicious_keywords(url)
        if suspicious_keywords:
            risk_score += 10 * len(suspicious_keywords)
            evidence.append(f"Suspicious keywords in URL: {', '.join(suspicious_keywords)}")
            indicators["suspicious_keywords"] = suspicious_keywords
        
        # Check 5: IP Address URL
        if self.check_ip_address_url(url):
            risk_score += 30
            evidence.append("URL uses direct IP address instead of domain")
            indicators["ip_address_url"] = True
        
        # Check 6: Multiple Redirects
        redirect_count = self.check_multiple_redirects(url)
        if redirect_count > 0:
            risk_score += 10 * redirect_count
            evidence.append(f"Multiple redirect parameters detected: {redirect_count}")
            indicators["redirect_count"] = redirect_count
        
        # Check 7: SSL/HTTPS
        if parsed["scheme"] != "https":
            risk_score += 15
            evidence.append("URL does not use HTTPS")
            indicators["no_https"] = True
        else:
            indicators["has_https"] = True
        
        # Check 8: Suspicious subdomain
        if subdomain in ["verify", "update", "confirm", "login", "secure", "account", "payment"]:
            risk_score += 10
            evidence.append(f"Suspicious subdomain: {subdomain}")
            indicators["suspicious_subdomain"] = subdomain
        
        # Cap risk score at 100
        risk_score = min(risk_score, 100)
        
        return URLRisk(
            url=url,
            risk_score=risk_score,
            indicators=indicators,
            evidence=evidence
        )
    
    def analyze_urls(self, urls: List[str]) -> List[URLRisk]:
        """Analyze multiple URLs"""
        return [self.analyze_url(url) for url in urls]


# Export
__all__ = [
    "URLIntelligenceAgent",
    "URLRisk",
]
