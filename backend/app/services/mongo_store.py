from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from pymongo import MongoClient
from pymongo.errors import PyMongoError


class MongoAnalyticsStore:
    """Persist analysis artifacts to MongoDB for analytics and replay."""

    def __init__(self, uri: Optional[str] = None, database_name: str = "trustshield_ai", collection_name: str = "analyses") -> None:
        self.uri = uri
        self.database_name = database_name
        self.collection_name = collection_name
        self._client: Optional[MongoClient] = None

    def connect(self) -> None:
        if self._client is None and self.uri:
            self._client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)

    def is_available(self) -> bool:
        if not self.uri:
            return False
        try:
            self.connect()
            if self._client is None:
                return False
            self._client.admin.command("ping")
            return True
        except Exception:
            return False

    def store_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_available():
            return {"stored": False, "reason": "mongo_unavailable"}
        try:
            db = self._client[self.database_name]
            collection = db[self.collection_name]
            record = dict(payload)
            record['_id'] = str(uuid.uuid4())
            if 'id' not in record:
                record['id'] = record['_id']
            if 'timestamp' not in record:
                record['timestamp'] = datetime.now(timezone.utc).isoformat()
            
            result = collection.insert_one(record)
            return {"stored": True, "inserted_id": str(result.inserted_id)}
        except PyMongoError as exc:
            return {"stored": False, "reason": str(exc)}

    def _normalize_user_id(self, user_id: Optional[str]) -> str:
        return user_id or 'global'

    def _resolve_records(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.is_available():
            return []
            
        normalized_user_id = self._normalize_user_id(user_id)
        db = self._client[self.database_name]
        collection = db[self.collection_name]
        
        query = {}
        if user_id and normalized_user_id != 'global':
            query = {"user_id": normalized_user_id}
            # Fallback to global if empty for a specific user
            if collection.count_documents(query) == 0:
                query = {}

        # Fetch all, sorted by timestamp descending
        cursor = collection.find(query).sort("timestamp", -1)
        records = []
        for doc in cursor:
            doc['id'] = doc.get('id', str(doc.get('_id', '')))
            if '_id' in doc:
                del doc['_id']
            records.append(doc)
        return records

    def get_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        if not self.is_available():
            return {"success": False, "reason": "mongo_unavailable"}
            
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
            threat = record.get('threat_category') or 'unknown'
            top_threats[threat] = top_threats.get(threat, 0) + 1
            
            sender = record.get('sender', '')
            domain = 'unknown'
            if sender and '@' in sender:
                domain = sender.split('@')[-1].lower()
            if domain != 'unknown':
                top_brands_dict[domain] = top_brands_dict.get(domain, 0) + 1
                
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
        if not self.is_available():
            return {"success": False, "reason": "mongo_unavailable"}
            
        filtered = self._resolve_records(user_id)
        total = len(filtered)
        return {
            'success': True,
            'data': filtered[offset: offset + limit],
            'total': total,
            'limit': limit,
            'offset': offset,
        }
