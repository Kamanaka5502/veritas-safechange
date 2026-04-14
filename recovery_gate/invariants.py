from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple, Optional

Evidence = Dict[str, Any]

@dataclass(frozen=True)
class Invariant:
    """A named, deterministic property check with structured evidence."""
    name: str
    check: Callable[[Any], bool]
    evidence: Callable[[Any], Evidence]
    description: str = ""

    def evaluate(self, state: Any) -> Tuple[bool, Evidence]:
        ok = bool(self.check(state))
        ev = self.evidence(state)
        if not isinstance(ev, dict):
            # keep evidence JSON-safe and structured
            ev = {"evidence": ev}
        return ok, ev

@dataclass(frozen=True)
class InvariantSet:
    """Ordered invariant set (deterministic evaluation)."""
    invariants: List[Invariant]

    def verify(self, state: Any) -> Tuple[bool, List[dict]]:
        results: List[dict] = []
        for inv in self.invariants:
            ok, ev = inv.evaluate(state)
            results.append({
                "name": inv.name,
                "ok": ok,
                "description": inv.description,
                "evidence": ev,
            })
            if not ok:
                return False, results
        return True, results

# Built-in invariant factories (safe defaults)
def required_keys(*keys: str) -> Invariant:
    keys = tuple(keys)
    return Invariant(
        name="required_keys_present",
        description="All required keys must exist.",
        check=lambda s: isinstance(s, dict) and all(k in s for k in keys),
        evidence=lambda s: {"missing": [k for k in keys if not (isinstance(s, dict) and k in s)]},
    )

def monotone_min(key: str, minimum: float = 1) -> Invariant:
    return Invariant(
        name=f"{key}_min_{minimum}",
        description=f"'{key}' must be numeric and >= {minimum}.",
        check=lambda s: isinstance(s, dict) and isinstance(s.get(key), (int, float)) and s[key] >= minimum,
        evidence=lambda s: {key: (s.get(key) if isinstance(s, dict) else None), "minimum": minimum},
    )

def non_negative(*keys: str) -> Invariant:
    keys = tuple(keys)
    return Invariant(
        name="non_negative_values",
        description="Selected keys must be numeric and non-negative if present.",
        check=lambda s: isinstance(s, dict) and all(
            (k not in s) or (isinstance(s.get(k), (int, float)) and s[k] >= 0) for k in keys
        ),
        evidence=lambda s: {k: (s.get(k) if isinstance(s, dict) else None) for k in keys},
    )
