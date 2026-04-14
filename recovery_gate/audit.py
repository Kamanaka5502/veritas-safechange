from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Optional

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass(frozen=True)
class AuditRecord:
    """Immutable audit record for one guarded execution."""
    decision: str
    reason: str
    before_hash: str
    after_hash: str
    state_kind: str
    change_id: str
    timestamp: str
    extra: Optional[dict[str, Any]] = None
    signature: Optional[str] = None  # optional tamper-evident signature over canonical JSON

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)

class JsonlAuditSink:
    """Append-only JSONL sink."""
    def __init__(self, path: str):
        self.path = path

    def write(self, record: AuditRecord) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(record.to_json())
            f.write("\n")
