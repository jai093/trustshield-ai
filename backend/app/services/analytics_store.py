from __future__ import annotations

import csv
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class InMemoryAnalyticsStore:
    """Simple runtime analytics store for live dashboard data."""

    def __init__(self, max_records: int = 1000) -> None:
        self.max_records = max_records
        self.records: List[Dict[str, Any]] = []
        self._seed_demo_records()

    def _seed_demo_records(self) -> None:
        pass  # Removed seeded demo records as per user request to show accurate real-time data.

    def _normalize_user_id(self, user_id: Optional[str]) -> str:
        return user_id or 'global'

    def store_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        record = {
            'id': str(uuid.uuid4()),
            'user_id': self._normalize_user_id(payload.get('user_id')),
            'sender': payload.get('sender'),
            'subject': payload.get('subject'),
            'risk_score': payload.get('risk_score', 0),
            'risk_level': payload.get('risk_level', 'LOW'),
            'threat_category': payload.get('threat_category'),
            'prevention_actions': payload.get('prevention_actions', []),
            'timestamp': payload.get('timestamp') or datetime.now(timezone.utc).isoformat(),
        }
        self.records.insert(0, record)
        if len(self.records) > self.max_records:
            self.records = self.records[: self.max_records]
        return record

    def _resolve_records(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        normalized_user_id = self._normalize_user_id(user_id)
        if not user_id or normalized_user_id == 'global':
            return list(self.records)

        matching = [record for record in self.records if record['user_id'] == normalized_user_id]
        if matching:
            return matching

        return list(self.records)

    def get_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        filtered = self._resolve_records(user_id)
        total = len(filtered)
        total_phishing = 0
        total_blocked = 0
        for record in filtered:
            score = record.get('risk_score', 0)
            suggested_action = record.get('suggested_action')
            is_blocked = (suggested_action == 'block') or (not suggested_action and score >= 75)
            is_threat = is_blocked or (suggested_action == 'warn') or (not suggested_action and score >= 50)
            if is_blocked:
                total_blocked += 1
            if is_threat:
                total_phishing += 1
                
        detection_rate = round((total_phishing / total) if total else 0, 2)

        top_threats: Dict[str, int] = {}
        top_brands_dict: Dict[str, int] = {}
        timeline_dict: Dict[str, Dict[str, int]] = {}

        for record in filtered:
            # Threats
            threat = record.get('threat_category') or 'unknown'
            top_threats[threat] = top_threats.get(threat, 0) + 1
            
            # Brands (Extract domain from sender)
            sender = record.get('sender', '')
            domain = 'unknown'
            if sender and '@' in sender:
                domain = sender.split('@')[-1].lower()
            if domain != 'unknown':
                top_brands_dict[domain] = top_brands_dict.get(domain, 0) + 1
                
            # Timeline (Group by Date YYYY-MM-DD)
            ts = record.get('timestamp')
            if ts:
                try:
                    date_str = ts.split('T')[0]
                except Exception:
                    date_str = "unknown"
                
                if date_str not in timeline_dict:
                    timeline_dict[date_str] = {'date': date_str, 'total': 0, 'phishing': 0}
                
                timeline_dict[date_str]['total'] += 1
                score = record.get('risk_score', 0)
                suggested_action = record.get('suggested_action')
                is_threat = (suggested_action in ['block', 'warn']) or (not suggested_action and score >= 50)
                if is_threat:
                    timeline_dict[date_str]['phishing'] += 1

        top_threats_list = [
            {'threat': threat, 'count': count}
            for threat, count in sorted(top_threats.items(), key=lambda item: item[1], reverse=True)
        ]
        
        top_brands_list = [
            {'brand': brand, 'count': count}
            for brand, count in sorted(top_brands_dict.items(), key=lambda item: item[1], reverse=True)
        ]
        
        # Sort timeline by date
        timeline_list = sorted(timeline_dict.values(), key=lambda x: x['date'])

        return {
            'success': True,
            'data': {
                'total_emails_analyzed': total,
                'total_phishing_detected': total_phishing,
                'total_blocked': total_blocked,
                'detection_rate': detection_rate,
                'top_threats': top_threats_list[:5],
                'top_brands': top_brands_list[:5],
                'timeline': timeline_list,
            },
        }

    def get_history(self, user_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        filtered = self._resolve_records(user_id)
        total = len(filtered)
        return {
            'success': True,
            'data': filtered[offset: offset + limit],
            'total': total,
            'limit': limit,
            'offset': offset,
        }
