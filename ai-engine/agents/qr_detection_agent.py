"""
QR Code Detection Agent
Detects, decodes, and analyzes QR codes in emails
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class QRCodeAnalysis:
    url: str
    risk_score: int  # 0-100
    is_suspicious: bool
    indicators: List[str]
    domain_info: Dict
    evidence: List[str]


class QRDetectionAgent:
    """Detect and analyze QR codes"""
    
    def __init__(self):
        self.suspicious_schemes = [
            "ftp://", "file://", "gopher://", "telnet://",
            "ldap://", "javascript:", "vbscript:"
        ]
        
        self.suspicious_domains = [
            "bit.ly", "tinyurl.com", "goo.gl", "short.link",
            "rebrand.ly", "is.gd", "adf.ly"
        ]
    
    def decode_qr_destination(self, qr_data: str) -> Optional[str]:
        """
        Decode QR code to get destination URL
        In production, would use pyzbar or OpenCV
        """
        # For now, return the data as-is
        # Real implementation would use:
        # from pyzbar.pyzbar import decode
        # decoded_objects = decode(img)
        return qr_data if qr_data.startswith('http') else None
    
    def extract_domain_from_url(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return None
    
    def check_url_scheme(self, url: str) -> Tuple[bool, Optional[str]]:
        """Check if URL uses suspicious scheme"""
        for scheme in self.suspicious_schemes:
            if url.lower().startswith(scheme):
                return True, scheme
        return False, None
    
    def check_url_shortener(self, domain: str) -> bool:
        """Check if domain is URL shortener"""
        return any(shortener in domain for shortener in self.suspicious_domains)
    
    def check_ip_address(self, domain: str) -> bool:
        """Check if domain is IP address"""
        import re
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        return bool(re.match(ip_pattern, domain))
    
    def check_homoglyph(self, domain: str) -> bool:
        """Check for homoglyph attacks"""
        # Common homoglyphs
        homoglyphs = [
            ("0", "o"), ("1", "i"), ("l", "1"),
            ("rn", "m"), ("nn", "m")
        ]
        
        suspicious_domains = [
            "gооgle.com",  # o with Cyrillic
            "facebook.com",
            "microsoft.com",
            "amazon.com",
            "apple.com"
        ]
        
        for suspicious in suspicious_domains:
            if domain.lower() == suspicious:
                return False  # Exact match is not homoglyph
            
            # Check similarity
            similarity = self.string_similarity(domain.lower(), suspicious)
            if 0.8 < similarity < 1.0:
                return True
        
        return False
    
    def string_similarity(self, a: str, b: str) -> float:
        """Calculate string similarity"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, a, b).ratio()
    
    def analyze_qr_destination(self, qr_image_data: str) -> QRCodeAnalysis:
        """
        Analyze QR code destination
        
        Args:
            qr_image_data: QR code image data or decoded URL
        
        Returns:
            QRCodeAnalysis with risk assessment
        """
        risk_score = 0
        indicators = []
        evidence = []
        
        # Decode QR (in production would use pyzbar)
        destination_url = self.decode_qr_destination(qr_image_data)
        
        if not destination_url:
            return QRCodeAnalysis(
                url="",
                risk_score=100,
                is_suspicious=True,
                indicators=["Could not decode QR code"],
                domain_info={},
                evidence=["QR code is invalid or corrupted"]
            )
        
        domain = self.extract_domain_from_url(destination_url)
        
        # Check 1: Suspicious scheme
        has_suspicious_scheme, scheme = self.check_url_scheme(destination_url)
        if has_suspicious_scheme:
            risk_score += 40
            indicators.append(f"Suspicious URL scheme: {scheme}")
            evidence.append(f"QR code points to {scheme} URL")
        
        # Check 2: URL shortener
        if domain and self.check_url_shortener(domain):
            risk_score += 25
            indicators.append("URL shortener (destination hidden)")
            evidence.append("QR code uses URL shortening service")
        
        # Check 3: IP address
        if domain and self.check_ip_address(domain):
            risk_score += 35
            indicators.append("Direct IP address (no domain)")
            evidence.append("QR code points to IP address instead of domain")
        
        # Check 4: Homoglyph attack
        if domain and self.check_homoglyph(domain):
            risk_score += 30
            indicators.append("Possible homoglyph attack")
            evidence.append("QR code domain resembles known brand")
        
        # Cap risk score
        risk_score = min(risk_score, 100)
        
        return QRCodeAnalysis(
            url=destination_url,
            risk_score=risk_score,
            is_suspicious=risk_score > 50,
            indicators=indicators,
            domain_info={"domain": domain or "unknown"},
            evidence=evidence
        )
    
    def analyze_qr_codes(self, qr_list: List[Dict]) -> List[Dict]:
        """Analyze multiple QR codes"""
        analyses = []
        
        for qr in qr_list:
            image_data = qr.get("image_data", "")
            analysis = self.analyze_qr_destination(image_data)
            
            analyses.append({
                "url": analysis.url,
                "risk_score": analysis.risk_score,
                "is_suspicious": analysis.is_suspicious,
                "indicators": analysis.indicators,
                "evidence": analysis.evidence,
            })
        
        return analyses


# Export
__all__ = [
    "QRDetectionAgent",
    "QRCodeAnalysis",
]
