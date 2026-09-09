"""
Attachment Analysis Agent
Analyzes file attachments for malware indicators
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class AttachmentRisk:
    file_name: str
    risk_score: int  # 0-100
    file_type: str
    risks: Dict[str, bool]
    evidence: List[str]


class AttachmentAnalysisAgent:
    """Analyze email attachments for risk"""
    
    # Dangerous file types
    EXECUTABLE_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr',
        '.vbs', '.js', '.ps1', '.jar', '.msi', '.app',
        '.deb', '.rpm', '.apk', '.dmg'
    }
    
    # Macro-enabled office documents
    MACRO_EXTENSIONS = {
        '.doc', '.docm', '.xls', '.xlsm', '.xlsb',
        '.ppt', '.pptm', '.potm', '.pubm', '.ppsm'
    }
    
    # Archives that could contain executables
    ARCHIVE_EXTENSIONS = {
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
        '.iso', '.dmg', '.pkg'
    }
    
    # Double extension patterns (e.g., file.txt.exe)
    SUSPICIOUS_DOUBLE_EXTENSIONS = {
        ('txt', 'exe'),
        ('pdf', 'exe'),
        ('docx', 'exe'),
        ('jpg', 'exe'),
        ('png', 'exe'),
        ('doc', 'exe')
    }
    
    def __init__(self):
        self.executable_extensions = self.EXECUTABLE_EXTENSIONS
        self.macro_extensions = self.MACRO_EXTENSIONS
        self.archive_extensions = self.ARCHIVE_EXTENSIONS
    
    def get_file_extension(self, filename: str) -> str:
        """Extract file extension"""
        if '.' not in filename:
            return ""
        return '.' + filename.split('.')[-1].lower()
    
    def check_double_extension(self, filename: str) -> Tuple[bool, Tuple[str, str]]:
        """Check for double extension like file.txt.exe"""
        parts = filename.split('.')
        if len(parts) < 3:
            return False, ()
        
        ext1 = '.' + parts[-2].lower()
        ext2 = '.' + parts[-1].lower()
        
        # Check common suspicious combinations
        for suspicious_pair in self.SUSPICIOUS_DOUBLE_EXTENSIONS:
            if (ext1 == f'.{suspicious_pair[0]}' and 
                ext2 == f'.{suspicious_pair[1]}'):
                return True, (suspicious_pair[0], suspicious_pair[1])
        
        return False, ()
    
    def check_executable(self, filename: str) -> bool:
        """Check if file is executable"""
        ext = self.get_file_extension(filename)
        return ext in self.executable_extensions
    
    def check_macro_enabled(self, filename: str) -> bool:
        """Check if file is macro-enabled Office document"""
        ext = self.get_file_extension(filename)
        return ext in self.macro_extensions
    
    def check_password_protected(self, file_info: Dict) -> bool:
        """Check if archive is password protected"""
        # Check metadata flags if available
        is_encrypted = file_info.get("is_encrypted", False)
        is_password_protected = file_info.get("is_password_protected", False)
        
        return is_encrypted or is_password_protected
    
    def check_suspicious_filename(self, filename: str) -> List[str]:
        """Check for suspicious filename patterns"""
        indicators = []
        filename_lower = filename.lower()
        
        # Check for urgent/fake filenames
        urgent_keywords = [
            "invoice", "receipt", "payment", "urgent",
            "verify", "confirm", "update", "alert",
            "tax", "refund", "delivery", "shipment",
            "package", "claim", "contract", "statement"
        ]
        
        for keyword in urgent_keywords:
            if keyword in filename_lower:
                indicators.append(f"Filename contains urgent keyword: {keyword}")
        
        # Check for suspicious combinations
        if any(char in filename for char in ['<', '>', '|', '&', ';']):
            indicators.append("Filename contains shell metacharacters")
        
        return indicators
    
    def analyze_attachment(self, 
                          filename: str,
                          file_size: int = 0,
                          mime_type: str = "",
                          file_info: Dict = None) -> AttachmentRisk:
        """
        Analyze single attachment
        
        Args:
            filename: Attachment filename
            file_size: File size in bytes
            mime_type: MIME type
            file_info: Additional file metadata
        
        Returns:
            AttachmentRisk analysis
        """
        risk_score = 0
        risks = {}
        evidence = []
        file_info = file_info or {}
        
        # Initialize risk flags
        risks['executable'] = False
        risks['macro_enabled'] = False
        risks['double_extension'] = False
        risks['password_protected'] = False
        risks['archive'] = False
        risks['suspicious_filename'] = False
        
        # Check 1: Executable
        if self.check_executable(filename):
            risk_score += 50
            risks['executable'] = True
            evidence.append(f"Executable file: {self.get_file_extension(filename)}")
        
        # Check 2: Double extension
        is_double_ext, ext_pair = self.check_double_extension(filename)
        if is_double_ext:
            risk_score += 40
            risks['double_extension'] = True
            evidence.append(f"Double extension detected: {ext_pair[0]}.{ext_pair[1]}")
        
        # Check 3: Macro-enabled documents
        if self.check_macro_enabled(filename):
            risk_score += 25
            risks['macro_enabled'] = True
            evidence.append("Macro-enabled Office document")
        
        # Check 4: Password-protected archive
        if self.check_password_protected(file_info):
            risk_score += 30
            risks['password_protected'] = True
            evidence.append("Password-protected archive (to hide content)")
        
        # Check 5: Archive
        ext = self.get_file_extension(filename)
        if ext in self.archive_extensions:
            risk_score += 15
            risks['archive'] = True
            evidence.append(f"Archive file: {ext} (may contain executables)")
        
        # Check 6: Suspicious filename
        filename_indicators = self.check_suspicious_filename(filename)
        if filename_indicators:
            risk_score += 10
            risks['suspicious_filename'] = True
            evidence.extend(filename_indicators)
        
        # Check 7: File size anomalies
        if file_size > 50 * 1024 * 1024:  # > 50 MB
            risk_score += 5
            evidence.append("Large file (>50MB)")
        
        # Check 8: MIME type mismatch
        if mime_type and not mime_type.startswith('application'):
            expected_type = self.get_expected_mime_type(filename)
            if expected_type and mime_type != expected_type:
                risk_score += 10
                evidence.append(f"MIME type mismatch: {mime_type} vs {expected_type}")
        
        # Cap risk score
        risk_score = min(risk_score, 100)
        
        return AttachmentRisk(
            file_name=filename,
            risk_score=risk_score,
            file_type=self.get_file_extension(filename),
            risks=risks,
            evidence=evidence
        )
    
    def get_expected_mime_type(self, filename: str) -> str:
        """Get expected MIME type for file"""
        mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.zip': 'application/zip',
            '.txt': 'text/plain',
            '.jpg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
        }
        
        ext = self.get_file_extension(filename)
        return mime_types.get(ext, "")
    
    def analyze_attachments(self, attachments: List[Dict]) -> List[Dict]:
        """Analyze multiple attachments"""
        analyses = []
        
        for att in attachments:
            analysis = self.analyze_attachment(
                filename=att.get("name", ""),
                file_size=att.get("size", 0),
                mime_type=att.get("mimeType", ""),
                file_info=att
            )
            
            analyses.append({
                "file_name": analysis.file_name,
                "risk_score": analysis.risk_score,
                "file_type": analysis.file_type,
                "risks": analysis.risks,
                "evidence": analysis.evidence,
            })
        
        return analyses


# Export
__all__ = [
    "AttachmentAnalysisAgent",
    "AttachmentRisk",
]
