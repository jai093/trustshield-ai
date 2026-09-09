"""
Email Extraction Agent
Responsibilities:
- Detect new emails in Gmail
- Extract DOM content
- Parse HTML structure
- Create structured JSON
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import re
import json
from html.parser import HTMLParser
from urllib.parse import urlparse


@dataclass
class ExtractedLink:
    text: str
    href: str
    visible: bool
    is_button: bool = False


@dataclass
class ExtractedImage:
    src: str
    alt: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    data_url: Optional[str] = None


@dataclass
class ExtractedAttachment:
    name: str
    mime_type: str
    size: int
    extension: str
    is_executable: bool = False
    has_macros: bool = False


@dataclass
class QRCode:
    position: Dict[str, int]
    decoded_value: Optional[str] = None
    destination_url: Optional[str] = None
    image_data: Optional[str] = None


@dataclass
class EmailContent:
    body: str
    html_body: Optional[str] = None
    plain_text: str = ""


@dataclass
class EmailMetadata:
    sender: str
    subject: str
    sender_domain: Optional[str] = None
    reply_to: Optional[str] = None
    timestamp: str = ""
    gmail_message_id: Optional[str] = None


@dataclass
class ExtractedEmail:
    metadata: EmailMetadata
    content: EmailContent
    links: List[ExtractedLink]
    images: List[ExtractedImage]
    attachments: List[ExtractedAttachment]
    qr_codes: List[QRCode]
    html_dom: Optional[str] = None
    extracted_at: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "metadata": asdict(self.metadata),
            "content": asdict(self.content),
            "links": [asdict(l) for l in self.links],
            "images": [asdict(i) for i in self.images],
            "attachments": [asdict(a) for a in self.attachments],
            "qr_codes": [asdict(q) for q in self.qr_codes],
            "html_dom": self.html_dom,
            "extracted_at": self.extracted_at,
        }


class URLExtractor:
    """Extract URLs from HTML and text"""
    
    @staticmethod
    def extract_urls_from_html(html: str) -> List[ExtractedLink]:
        """Extract all URLs from HTML"""
        links = []
        
        # Find <a> tags
        href_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>'
        for href, text in re.findall(href_pattern, html, re.IGNORECASE):
            if href and not href.startswith("javascript:"):
                links.append(ExtractedLink(
                    text=text.strip() or href,
                    href=href,
                    visible=bool(text.strip()),
                    is_button=False
                ))
        
        # Find buttons with onclick or data-url
        button_pattern = r'<button[^>]+(?:data-url|onclick)=["\']([^"\']+)["\'][^>]*>([^<]*)</button>'
        for url, text in re.findall(button_pattern, html, re.IGNORECASE):
            if url:
                links.append(ExtractedLink(
                    text=text.strip() or url,
                    href=url,
                    visible=True,
                    is_button=True
                ))
        
        return links

    @staticmethod
    def extract_hidden_urls(html: str) -> List[ExtractedLink]:
        """Extract hidden URLs from meta tags, iframes, etc."""
        hidden_links = []
        
        # Find iframe sources
        iframe_pattern = r'<iframe[^>]+src=["\']([^"\']+)["\']'
        for src in re.findall(iframe_pattern, html, re.IGNORECASE):
            hidden_links.append(ExtractedLink(
                text=f"[iframe] {src}",
                href=src,
                visible=False
            ))
        
        # Find img sources with click handlers
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'].*?(?:onclick|data-url)=["\']([^"\']+)["\']'
        for src, url in re.findall(img_pattern, html, re.IGNORECASE | re.DOTALL):
            hidden_links.append(ExtractedLink(
                text=f"[image] {url}",
                href=url,
                visible=False
            ))
        
        return hidden_links


class ImageExtractor:
    """Extract images from email"""
    
    @staticmethod
    def extract_images(html: str) -> List[ExtractedImage]:
        """Extract all images"""
        images = []
        
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'](?:[^>]*alt=["\']([^"\']+)["\'])?'
        for match in re.finditer(img_pattern, html, re.IGNORECASE):
            src = match.group(1)
            alt = match.group(2)
            
            # Extract width/height if present
            width_match = re.search(r'width=["\']?(\d+)', match.group(0))
            height_match = re.search(r'height=["\']?(\d+)', match.group(0))
            
            images.append(ExtractedImage(
                src=src,
                alt=alt,
                width=int(width_match.group(1)) if width_match else None,
                height=int(height_match.group(1)) if height_match else None
            ))
        
        return images


class AttachmentExtractor:
    """Extract attachment metadata"""
    
    EXECUTABLE_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr',
        '.vbs', '.js', '.jar', '.zip', '.rar', '.7z',
        '.sh', '.app', '.deb'
    }
    
    MACRO_EXTENSIONS = {'.doc', '.docm', '.xls', '.xlsm', '.ppt', '.pptm'}
    
    @staticmethod
    def extract_attachments(attachments_data: List[Dict]) -> List[ExtractedAttachment]:
        """Extract attachment information"""
        attachments = []
        
        for att in attachments_data:
            name = att.get("filename", "unknown")
            mime_type = att.get("mimeType", "")
            size = att.get("size", 0)
            
            # Get extension
            ext = "." + name.split(".")[-1].lower() if "." in name else ""
            
            # Check for double extensions
            parts = name.split(".")
            double_ext = len(parts) > 2 and parts[-2].lower() in {'exe', 'bat', 'cmd'}
            
            attachments.append(ExtractedAttachment(
                name=name,
                mime_type=mime_type,
                size=size,
                extension=ext,
                is_executable=ext in AttachmentExtractor.EXECUTABLE_EXTENSIONS or double_ext,
                has_macros=ext in AttachmentExtractor.MACRO_EXTENSIONS
            ))
        
        return attachments


class EmailExtractionAgent:
    """Main Email Extraction Agent"""
    
    def __init__(self):
        self.url_extractor = URLExtractor()
        self.image_extractor = ImageExtractor()
        self.attachment_extractor = AttachmentExtractor()
    
    def extract_sender_domain(self, sender: str) -> str:
        """Extract domain from email address"""
        if "@" in sender:
            return sender.split("@")[1].lower()
        return ""
    
    def extract_email(self, 
                     sender: str,
                     subject: str,
                     body: str,
                     html_body: Optional[str] = None,
                     reply_to: Optional[str] = None,
                     attachments_data: Optional[List[Dict]] = None,
                     gmail_message_id: Optional[str] = None,
                     timestamp: str = "") -> ExtractedEmail:
        """
        Extract structured email data
        
        Args:
            sender: Email sender address
            subject: Email subject
            body: Plain text body
            html_body: HTML body
            reply_to: Reply-to address
            attachments_data: List of attachment dictionaries
            gmail_message_id: Gmail message ID
            timestamp: Email timestamp
        
        Returns:
            ExtractedEmail object with all extracted data
        """
        
        # Extract metadata
        metadata = EmailMetadata(
            sender=sender,
            sender_domain=self.extract_sender_domain(sender),
            subject=subject,
            reply_to=reply_to,
            timestamp=timestamp,
            gmail_message_id=gmail_message_id
        )
        
        # Extract content
        content = EmailContent(
            body=body,
            html_body=html_body,
            plain_text=body
        )
        
        # Extract links
        links = []
        if html_body:
            links = self.url_extractor.extract_urls_from_html(html_body)
            links.extend(self.url_extractor.extract_hidden_urls(html_body))
        
        # Extract images
        images = []
        if html_body:
            images = self.image_extractor.extract_images(html_body)
        
        # Extract attachments
        attachments = []
        if attachments_data:
            attachments = self.attachment_extractor.extract_attachments(attachments_data)
        
        # QR code detection would require image processing
        # This is a placeholder for future implementation
        qr_codes = []
        
        # Create extracted email
        extracted = ExtractedEmail(
            metadata=metadata,
            content=content,
            links=links,
            images=images,
            attachments=attachments,
            qr_codes=qr_codes,
            html_dom=html_body,
            extracted_at=timestamp or ""
        )
        
        return extracted
    
    def extract_email_from_json(self, email_json: Dict[str, Any]) -> ExtractedEmail:
        """Extract from JSON representation"""
        return self.extract_email(
            sender=email_json.get("sender", ""),
            subject=email_json.get("subject", ""),
            body=email_json.get("body", ""),
            html_body=email_json.get("htmlBody"),
            reply_to=email_json.get("replyTo"),
            attachments_data=email_json.get("attachments", []),
            gmail_message_id=email_json.get("gmailMessageId"),
            timestamp=email_json.get("timestamp", "")
        )


# Export
__all__ = [
    "EmailExtractionAgent",
    "ExtractedEmail",
    "ExtractedLink",
    "ExtractedImage",
    "ExtractedAttachment",
    "QRCode",
    "EmailMetadata",
    "EmailContent",
]
