from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any, Optional

@dataclass(frozen=True)
class DerivationRecord:
    """A minimal, language-agnostic proof object for one transition.

    This is *not* a formal theorem prover output. It's a compact, replay-friendly
    derivation artifact that explains *why* a decision was made.
    """
    claim: str
    because: list[str]
    decision: str
    reason: str
    before_hash: str
    after_hash: str
    audit_hash: str
    change_id: str
    timestamp: str
    invariants: Optional[list[dict[str, Any]]] = None
    signature: Optional[str] = None  # signature over audit_hash (if present)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)

class JsonlDerivationSink:
    """Append-only JSONL sink for derivation artifacts."""
    def __init__(self, path: str):
        self.path = path

    def write(self, record: DerivationRecord) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(record.to_json())
            f.write("\n")
