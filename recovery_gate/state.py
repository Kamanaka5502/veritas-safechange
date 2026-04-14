from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from .hashing import sha256_json, canonical_json

class State(Protocol):
    """State adapter interface. Concrete implementations must be reversible."""
    kind: str

    def read(self) -> Any:
        ...

    def write(self, value: Any) -> None:
        ...

    def snapshot(self) -> str:
        """Capture pre-state. Returns snapshot id (content hash)."""
        ...

    def restore(self, snapshot_id: str) -> None:
        """Restore to the last snapshot; must match snapshot_id."""
        ...

    def digest(self) -> str:
        """Content-based identity."""
        ...

@dataclass
class DictState:
    """In-memory dict state (reference to a dict)."""
    data: dict
    kind: str = "dict"

    _snap: dict | None = None
    _snap_id: str | None = None

    def read(self) -> Any:
        return self.data

    def write(self, value: Any) -> None:
        if not isinstance(value, dict):
            raise TypeError("DictState requires a dict value")
        self.data.clear()
        self.data.update(value)

    def snapshot(self) -> str:
        self._snap = copy.deepcopy(self.data)
        self._snap_id = self.digest()
        return self._snap_id

    def restore(self, snapshot_id: str) -> None:
        if self._snap is None or self._snap_id is None:
            raise RuntimeError("No snapshot available")
        if snapshot_id != self._snap_id:
            raise RuntimeError("Snapshot id mismatch (possible tamper)")
        self.write(copy.deepcopy(self._snap))

    def digest(self) -> str:
        return sha256_json(self.data)

@dataclass
class JsonFileState:
    """JSON file state with atomic write + in-memory snapshot."""
    path: str
    kind: str = "json_file"

    _snap_text: str | None = None
    _snap_id: str | None = None

    def _p(self) -> Path:
        return Path(self.path)

    def read(self) -> Any:
        p = self._p()
        if not p.exists():
            return {}
        return json.loads(p.read_text(encoding="utf-8"))

    def write(self, value: Any) -> None:
        p = self._p()
        tmp = p.with_suffix(p.suffix + ".tmp")
        text = canonical_json(value)
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(p)

    def snapshot(self) -> str:
        p = self._p()
        self._snap_text = p.read_text(encoding="utf-8") if p.exists() else canonical_json({})
        self._snap_id = sha256_json(json.loads(self._snap_text))
        return self._snap_id

    def restore(self, snapshot_id: str) -> None:
        if self._snap_text is None or self._snap_id is None:
            raise RuntimeError("No snapshot available")
        if snapshot_id != self._snap_id:
            raise RuntimeError("Snapshot id mismatch (possible tamper)")
        self.write(json.loads(self._snap_text))

    def digest(self) -> str:
        return sha256_json(self.read())
