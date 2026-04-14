# Security

Recovery Gate provides rollback and audit integrity controls. It does not claim to provide full system security by itself.

## Scope

- tamper-evident HMAC signing
- audit-hash chaining
- deterministic verification of recorded receipts

## Notes

- HMAC uses shared-secret trust, not asymmetric signatures
- protect audit logs and secrets separately
- verify receipts before treating them as trusted evidence
