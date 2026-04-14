from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .hashing import sha256_bytes

@dataclass
class SqliteFileState:
    """SQLite database file state.

    Safety model: snapshot/restore is file-level and assumes no concurrent writers.
    Use for migrations in controlled contexts (maintenance window / single-writer).
    """
    path: str
    kind: str = "sqlite_file"

    _snap_path: str | None = None
    _snap_id: str | None = None

    def _p(self) -> Path:
        return Path(self.path)

    def read(self) -> Any:
        # This adapter is file-based; returning path is enough for change functions that operate externally.
        return {"sqlite_path": self.path}

    def write(self, value: Any) -> None:
        # No-op: mutations happen via external SQLite tooling/migrations.
        # Keep interface compatibility.
        return None

    def snapshot(self) -> str:
        p = self._p()
        if not p.exists():
            raise FileNotFoundError(f"SQLite file not found: {p}")
        snap = p.with_suffix(p.suffix + ".recovery_gate.bak")
        shutil.copy2(p, snap)
        self._snap_path = str(snap)
        self._snap_id = self.digest()
        return self._snap_id

    def restore(self, snapshot_id: str) -> None:
        if self._snap_path is None or self._snap_id is None:
            raise RuntimeError("No snapshot available")
        if snapshot_id != self._snap_id:
            raise RuntimeError("Snapshot id mismatch (possible tamper)")
        p = self._p()
        tmp = p.with_suffix(p.suffix + ".tmp_restore")
        shutil.copy2(self._snap_path, tmp)
        tmp.replace(p)

    def digest(self) -> str:
        p = self._p()
        data = p.read_bytes()
        return sha256_bytes(data)
