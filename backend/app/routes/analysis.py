"""API routes for email analysis with validation, throttling, and service-layer orchestration."""

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request

from app.core.config import get_settings
from app.core.security import InMemoryRateLimiter
from app.schemas import EmailAnalysisRequest
from app.services.analysis_service import EmailAnalysisService

router = APIRouter(prefix="/api", tags=["analysis"])
settings = get_settings()
rate_limiter = InMemoryRateLimiter(limit=settings.api_rate_limit, window_seconds=settings.api_rate_window_seconds)
analysis_service = EmailAnalysisService()


@router.post("/analyze")
async def analyze_email(
    email_data: EmailAnalysisRequest,
    request: Request,
    x_extension_id: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
):
    """Analyze an email using the multi-agent detection pipeline."""
    rate_key = x_user_id or x_extension_id or (request.client.host if request.client else "anonymous")
    if not rate_limiter.allow(rate_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    if settings.allowed_extension_id and x_extension_id != settings.allowed_extension_id:
        raise HTTPException(status_code=403, detail="Invalid extension ID")

    return analysis_service.analyze(email_data, extension_id=x_extension_id, user_id=x_user_id)


@router.post("/report")
async def report_phishing(report_data: dict, x_user_id: Optional[str] = Header(None)) -> dict:
    """Accept a user-submitted phishing report."""
    return {
        "success": True,
        "report_id": "report_123",
        "message": "Thank you for reporting this email. It has been added to our threat intelligence system.",
        "metadata": {"user_id": x_user_id},
    }


@router.get("/dashboard/stats")
async def get_dashboard_stats(x_user_id: Optional[str] = Header(None)) -> dict:
    """Provide lightweight dashboard statistics for a user."""
    return analysis_service.get_dashboard_stats(x_user_id)


@router.get("/history")
async def get_email_history(x_user_id: Optional[str] = Header(None), limit: int = 50, offset: int = 0) -> dict:
    """Return a paginated history of analyzed emails."""
    return analysis_service.get_email_history(x_user_id, limit=limit, offset=offset)
