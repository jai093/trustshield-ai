"""
TrustShield AI - Backend package initialization
"""

__version__ = "1.0.0"
__author__ = "TrustShield AI Team"
__description__ = "Enterprise Phishing Detection System Backend"

from fastapi import FastAPI

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    from app.main import app
    return app
