from __future__ import annotations

import hashlib
import json
from typing import Any

def canonical_json(obj: Any) -> str:
    """Deterministic JSON encoding (stable hash across runs/platforms)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_json(obj: Any) -> str:
    return sha256_bytes(canonical_json(obj).encode("utf-8"))
