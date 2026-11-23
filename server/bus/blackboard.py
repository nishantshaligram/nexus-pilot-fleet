"""
NexusPilot Fleet - Shared Blackboard
Enables cross-worker knowledge broadcasting so agents reuse discovered contracts and patterns.
"""

import time
import hashlib
from typing import List, Dict, Any, Optional
from .db import FleetDatabase


class Blackboard:
    def __init__(self, db: FleetDatabase):
        self.db = db

    def broadcast(
        self,
        mission_id: str,
        topic: str,
        content: str,
        source_worker_id: Optional[str] = None
    ) -> str:
        raw = f"{mission_id}:{topic}:{content[:50]}:{time.time()}"
        fact_id = "fact_" + hashlib.sha256(raw.encode()).hexdigest()[:10]
        self.db.post_fact(
            fact_id=fact_id,
            mission_id=mission_id,
            topic=topic,
            content=content,
            source_worker_id=source_worker_id
        )
        return fact_id

    def query(self, mission_id: str, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.db.get_facts(mission_id=mission_id, topic=topic)

    def format_blackboard_summary(self, mission_id: str) -> str:
        facts = self.query(mission_id=mission_id)
        if not facts:
            return "No shared blackboard entries."
        lines = [f"### 📋 Shared Blackboard ({len(facts)} facts recorded):"]
        for f in facts:
            worker = f"[{f.get('source_worker_id') or 'system'}]"
            lines.append(f"- **{f['topic']}** {worker}: {f['content']}")
        return "\n".join(lines)
