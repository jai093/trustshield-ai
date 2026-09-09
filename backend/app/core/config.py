import os
from dataclasses import dataclass, field
from typing import Tuple

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True), override=False)


@dataclass(frozen=True)
class Settings:
    app_name: str = "TrustShield AI API"
    app_version: str = "1.0.0"
    debug: bool = False
    cors_origins: Tuple[str, ...] = field(default_factory=lambda: ("http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"))
    allowed_hosts: Tuple[str, ...] = field(default_factory=lambda: ("localhost", "127.0.0.1"))
    api_rate_limit: int = 60
    api_rate_window_seconds: int = 60
    allowed_extension_id: str | None = None
    enable_backend_analysis: bool = False
    mongodb_uri: str | None = None
    mongodb_database: str = "trustshield_ai"
    mongodb_collection: str = "analyses"
    ollama_base_url: str | None = None
    ollama_model: str = "gpt-oss:120b"
    ollama_api_key_1: str | None = None
    phishing_model_path: str | None = None
    spam_dataset_path: str | None = None


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "TrustShield AI API"),
        app_version=os.getenv("APP_VERSION", "1.0.0"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        cors_origins=tuple(filter(None, os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","))),
        allowed_hosts=tuple(filter(None, os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(","))),
        api_rate_limit=int(os.getenv("API_RATE_LIMIT", "60")),
        api_rate_window_seconds=int(os.getenv("API_RATE_WINDOW_SECONDS", "60")),
        allowed_extension_id=os.getenv("ALLOWED_EXTENSION_ID") or None,
        enable_backend_analysis=os.getenv("ENABLE_BACKEND_ANALYSIS", "false").lower() == "true",
        mongodb_uri=os.getenv("MONGODB_URI") or None,
        mongodb_database=os.getenv("MONGODB_DATABASE", "trustshield_ai"),
        mongodb_collection=os.getenv("MONGODB_COLLECTION", "analyses"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL") or None,
        ollama_model=os.getenv("OLLAMA_MODEL", "gpt-oss:120b"),
        ollama_api_key_1=os.getenv("OLLAMA_API_KEY_1") or None,
        phishing_model_path=os.getenv("PHISHING_MODEL_PATH") or None,
        spam_dataset_path=os.getenv("SPAM_DATASET_PATH") or None,
    )
