
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional, Any

from .hashing import sha256_bytes
from .signing import HmacSigner

def _canon_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def canonical_audit_payload(record_dict: dict) -> dict:
    """Return the canonical payload used for audit hashing.

    Excludes:
      - top-level ``signature``
      - ``extra.audit_hash`` (self-referential field)
    Preserves:
      - ``extra.prev_audit_hash`` and invariant evidence
    """
    d = dict(record_dict)
    d.pop("signature", None)
    extra = d.get("extra")
    if isinstance(extra, dict):
        extra = dict(extra)
        extra.pop("audit_hash", None)
        d["extra"] = extra
    return d

def audit_hash(record_dict: dict) -> str:
    """Stable content hash for an audit record."""
    payload = canonical_audit_payload(record_dict)
    return sha256_bytes(_canon_json(payload).encode("utf-8"))

@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    errors: list[str]

def verify_jsonl(path: str, *, hmac_secret: Optional[str] = None, require_chain: bool = False) -> VerifyResult:
    errors: list[str] = []
    signer = HmacSigner(hmac_secret.encode("utf-8")) if hmac_secret else None

    prev_hash: Optional[str] = None
    line_no = 0
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line_no += 1
            line = raw_line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception as e:
                errors.append(f"line {line_no}: invalid json: {e}")
                continue

            computed = audit_hash(rec)
            extra = rec.get("extra") or {}
            declared = extra.get("audit_hash")
            declared_prev = extra.get("prev_audit_hash")

            if declared is None:
                errors.append(f"line {line_no}: missing audit_hash")
            elif declared != computed:
                errors.append(f"line {line_no}: audit_hash mismatch")

            # Chain validation
            if require_chain:
                if line_no == 1:
                    # First record may legitimately have no previous link.
                    if declared_prev not in (None, ""):
                        errors.append(f"line {line_no}: first record should not point to a previous audit hash")
                else:
                    if declared_prev in (None, ""):
                        errors.append(f"line {line_no}: missing prev_audit_hash (chain required)")
                    elif declared_prev != prev_hash:
                        errors.append(f"line {line_no}: chain break (prev_audit_hash mismatch)")
            else:
                if prev_hash is not None and declared_prev not in (None, "") and declared_prev != prev_hash:
                    errors.append(f"line {line_no}: chain break (prev_audit_hash mismatch)")

            # Signature validation (HMAC)
            if signer is not None:
                sig = rec.get("signature")
                if not sig:
                    errors.append(f"line {line_no}: missing signature")
                elif not signer.verify(computed, sig):
                    errors.append(f"line {line_no}: signature invalid")

            prev_hash = computed

    return VerifyResult(ok=(len(errors) == 0), errors=errors)
