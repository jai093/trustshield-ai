"""FastAPI application entry point with centralized configuration and error handling."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.routes.analysis import router as analysis_router

load_dotenv()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Enterprise phishing detection system API",
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_origin_regex=r"^(https?://localhost(:[0-9]+)?|https?://127\.0\.0\.1(:[0-9]+)?|chrome-extension://.*)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=list(settings.allowed_hosts),
)

app.include_router(analysis_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"success": False, "error": exc.detail, "code": "HTTP_ERROR"})


@app.exception_handler(ValueError)
async def value_error_handler(_request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"success": False, "error": str(exc), "code": "VALIDATION_ERROR"})


@app.get("/")
async def root() -> dict:
    return {"status": "ok", "service": settings.app_name, "version": settings.app_version}


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "service": settings.app_name}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "8000")))
