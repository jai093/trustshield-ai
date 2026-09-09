"""
Debug Gmail Analysis Service
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.core.config import get_settings
from app.services.analysis_service import EmailAnalysisService
import traceback

settings = get_settings()
service = EmailAnalysisService()

# Try a simple test
test_email = {
    "sender": "test@gmail.com",
    "senderName": "Test User",
    "subject": "Test Email",
    "body": "This is a test email",
    "links": [],
    "attachments": [],
}

print("[DEBUG] Testing analysis service...")
print(f"Settings configured:")
print(f"  MongoDB URI: {settings.mongodb_uri[:50]}...")
print(f"  Ollama URL: {settings.ollama_base_url}")
print(f"  Model path: {settings.phishing_model_path}")

try:
    result = service.analyze(test_email)
    print(f"\n[RESULT] Analysis returned:")
    print(f"  Type: {type(result)}")
    print(f"  Keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
    print(f"  Full result: {result}")
except Exception as e:
    print(f"\n[ERROR] Analysis failed:")
    print(f"  {type(e).__name__}: {e}")
    traceback.print_exc()
