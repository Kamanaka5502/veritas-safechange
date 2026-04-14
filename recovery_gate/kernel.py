"""Recovery Gate v5 Final — reference kernel surface.

This module intentionally exposes the minimal primitives that define the spec:
- RecoveryGate
- Invariant / InvariantSet
- State adapters
- Audit verification / replay

v5 is defined primarily by the specification documents in /docs.
"""

from .core import RecoveryGate, ChainedContext
from .invariants import Invariant, InvariantSet, required_keys, monotone_min, non_negative
from .state import DictState, JsonFileState
from .sqlite_state import SqliteFileState
from .audit_verify import verify_jsonl
