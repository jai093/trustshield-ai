"""
Whitelist & Trusted Domains Service
Provides domain and email verification for trusted academic, governmental,
and enterprise organizations so that legitimate emails (such as college placement
and university notices) are never falsely flagged as phishing.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

SERVICE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SERVICE_DIR / "trusted_domains.json"

# Default preconfigured trusted domains and institutions
DEFAULT_TRUSTED_CONFIG = {
    "trusted_emails": [
        "placement@sairamce.edu.in",
        "principal@sairamce.edu.in",
        "hod@sairamce.edu.in",
        "info@sairamce.edu.in",
        "exam@sairamce.edu.in",
        "placement@sairam.edu.in",
    ],
    "trusted_domains": [
        "sairamce.edu.in",
        "sairam.edu.in",
        "sairamgroup.in",
        "annauniv.edu",
        "aicte-india.org",
        "nptel.ac.in",
        "swayam.gov.in",
        "internshala.com",
    ],
    "trusted_tlds_and_suffixes": [
        ".edu.in",
        ".ac.in",
        ".res.in",
        ".gov.in",
        ".edu",
    ],
    "institution_names": {
        "sairamce.edu.in": "Sri Sairam College of Engineering",
        "sairam.edu.in": "Sri Sairam Engineering College",
        "sairamgroup.in": "Sairam Institutions",
        "annauniv.edu": "Anna University",
        "aicte-india.org": "AICTE India",
        "nptel.ac.in": "NPTEL",
    }
}


class WhitelistService:
    """Manages whitelisted domains and senders for false-positive prevention."""

    def __init__(self, config_path: Optional[Path | str] = None) -> None:
        self.config_path = Path(config_path or CONFIG_FILE)
        self.trusted_emails: Set[str] = set()
        self.trusted_domains: Set[str] = set()
        self.trusted_suffixes: List[str] = []
        self.institution_names: Dict[str, str] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load whitelist configuration from file or use defaults."""
        data = DEFAULT_TRUSTED_CONFIG.copy()
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    if isinstance(file_data, dict):
                        data["trusted_emails"] = list(set(data.get("trusted_emails", []) + file_data.get("trusted_emails", [])))
                        data["trusted_domains"] = list(set(data.get("trusted_domains", []) + file_data.get("trusted_domains", [])))
                        data["trusted_tlds_and_suffixes"] = list(set(data.get("trusted_tlds_and_suffixes", []) + file_data.get("trusted_tlds_and_suffixes", [])))
                        if "institution_names" in file_data:
                            data["institution_names"].update(file_data["institution_names"])
            except Exception as e:
                print(f"[WhitelistService] Warning: Failed to load {self.config_path}: {e}")

        # Check environment variable overrides
        env_domains = os.getenv("TRUSTED_EMAIL_DOMAINS")
        if env_domains:
            for d in env_domains.split(","):
                d = d.strip().lower()
                if d:
                    data["trusted_domains"].append(d)

        env_emails = os.getenv("TRUSTED_EMAIL_ADDRESSES")
        if env_emails:
            for em in env_emails.split(","):
                em = em.strip().lower()
                if em:
                    data["trusted_emails"].append(em)

        self.trusted_emails = {em.strip().lower() for em in data.get("trusted_emails", [])}
        self.trusted_domains = {d.strip().lower() for d in data.get("trusted_domains", [])}
        self.trusted_suffixes = [s.strip().lower() for s in data.get("trusted_tlds_and_suffixes", [])]
        self.institution_names = data.get("institution_names", {})

        # Ensure config file exists
        if not self.config_path.exists():
            self.save_config()

    def save_config(self) -> None:
        """Save active whitelist configuration to JSON."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump({
                    "trusted_emails": sorted(list(self.trusted_emails)),
                    "trusted_domains": sorted(list(self.trusted_domains)),
                    "trusted_tlds_and_suffixes": sorted(self.trusted_suffixes),
                    "institution_names": self.institution_names,
                }, f, indent=2)
        except Exception as e:
            print(f"[WhitelistService] Error saving {self.config_path}: {e}")

    def extract_domain(self, sender: str) -> str:
        """Extract domain from an email address or string."""
        if not sender:
            return ""
        # Match email inside brackets like 'Placement Cell <placement@sairamce.edu.in>'
        match = re.search(r"[\w\.-]+@([\w\.-]+)", sender.lower())
        if match:
            return match.group(1).lower()
        if "@" in sender:
            return sender.split("@")[-1].strip(" >)]'\"").lower()
        return sender.strip().lower()

    def extract_email(self, sender: str) -> str:
        """Extract clean email address from sender string."""
        if not sender:
            return ""
        match = re.search(r"([\w\.-]+@[\w\.-]+)", sender.lower())
        if match:
            return match.group(1).lower()
        return sender.strip().lower()

    def is_trusted_sender(self, sender: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if sender is a trusted individual or institutional domain.
        Returns:
            (is_trusted, institution_or_reason, domain)
        """
        clean_email = self.extract_email(sender)
        domain = self.extract_domain(sender)

        # 1. Exact email match (e.g., placement@sairamce.edu.in)
        if clean_email in self.trusted_emails:
            inst = self.institution_names.get(domain, "Verified Academic Organization")
            return True, f"Verified Email: {clean_email} ({inst})", domain

        # 2. Exact domain match or subdomain match (e.g., sairamce.edu.in)
        for td in self.trusted_domains:
            if domain == td or domain.endswith("." + td):
                inst = self.institution_names.get(td, self.institution_names.get(domain, "Verified Academic Institution"))
                return True, f"Verified Domain: {domain} ({inst})", domain

        # 3. Trusted educational/governmental TLD suffix (e.g., .edu.in, .ac.in)
        for suffix in self.trusted_suffixes:
            if domain.endswith(suffix):
                return True, f"Accredited Educational/Institutional Domain: {domain}", domain

        return False, None, domain

    def add_trusted_domain(self, domain: str, institution_name: Optional[str] = None) -> None:
        """Add a new trusted domain."""
        domain = domain.strip().lower()
        if domain:
            self.trusted_domains.add(domain)
            if institution_name:
                self.institution_names[domain] = institution_name
            self.save_config()

    def add_trusted_email(self, email: str, institution_name: Optional[str] = None) -> None:
        """Add a new trusted email address."""
        email = email.strip().lower()
        if email:
            self.trusted_emails.add(email)
            domain = self.extract_domain(email)
            if domain and domain not in self.trusted_domains:
                self.trusted_domains.add(domain)
            if institution_name and domain:
                self.institution_names[domain] = institution_name
            self.save_config()


# Global singleton
whitelist_service = WhitelistService()
