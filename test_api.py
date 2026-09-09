import requests
import json

payload = {
    "sender": "support@apple-id-security-update.com",
    "subject": "Free online fake mailer with attachments...",
    "body": "URGENT: Your Apple ID is locked. Verify your identity within 24 hours.",
    "links": [],
    "attachments": [],
    "isSpamFolder": True
}

try:
    res = requests.post("http://localhost:8000/api/analyze", json=payload, headers={"Content-Type": "application/json"})
    print("STATUS:", res.status_code)
    print("RESPONSE:", json.dumps(res.json(), indent=2))
except Exception as e:
    print("ERROR:", e)
