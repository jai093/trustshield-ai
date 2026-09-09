from typing import List, Optional

from pydantic import BaseModel, Field


class EmailLink(BaseModel):
    text: Optional[str] = None
    href: Optional[str] = None
    visible: bool = True


class EmailImage(BaseModel):
    src: Optional[str] = None
    alt: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class EmailAttachment(BaseModel):
    name: Optional[str] = None
    size: Optional[int] = None
    mimeType: Optional[str] = None


class EmailAnalysisRequest(BaseModel):
    sender: Optional[str] = None
    senderName: Optional[str] = None
    subject: Optional[str] = ""
    body: Optional[str] = ""
    htmlBody: Optional[str] = None
    links: List[EmailLink] = Field(default_factory=list)
    images: List[EmailImage] = Field(default_factory=list)
    attachments: List[EmailAttachment] = Field(default_factory=list)
    replyTo: Optional[str] = None
    extractedAt: Optional[str] = None
    isSpamFolder: Optional[bool] = False

    def summary_text(self) -> str:
        return " ".join(filter(None, [self.subject, self.body]))
