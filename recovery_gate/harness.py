from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

from .invariants import InvariantSet

@dataclass(frozen=True)
class HarnessResult:
    ok: bool
    summary: str
    results: list[dict]

    def to_json(self) -> str:
        return json.dumps(
            {"ok": self.ok, "summary": self.summary, "results": self.results},
            sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )

def run_invariants(invariants: InvariantSet, state_value: Any) -> HarnessResult:
    ok, results = invariants.verify(state_value)
    summary = "ok" if ok else f"failed:{next((r['name'] for r in results if not r['ok']), 'unknown')}"
    return HarnessResult(ok=ok, summary=summary, results=results)
