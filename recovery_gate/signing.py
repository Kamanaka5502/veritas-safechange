from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

@dataclass(frozen=True)
class HmacSigner:
    """Tamper-evident signing using HMAC-SHA256 (shared secret).

    v0.3+ convention: sign a stable *audit hash* (hex string), not raw JSON text.
    """
    secret: bytes

    def sign(self, audit_hash_hex: str) -> str:
        return hmac.new(self.secret, audit_hash_hex.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify(self, audit_hash_hex: str, signature_hex: str) -> bool:
        expected = self.sign(audit_hash_hex)
        return hmac.compare_digest(expected, signature_hex)
