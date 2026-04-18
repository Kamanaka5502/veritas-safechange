# Evidence Surface — Veritas Aegis

This system produces verifiable evidence for every attempted action.

## Each execution includes:

- Decision outcome (COMMITTED / ROLLED_BACK / BLOCKED)
- Reason for decision
- Before-state hash
- After-state hash
- Audit hash (receipt)
- Timestamp

## Verification

Audit trails can be verified:

safechange verify-audit <audit_file>

## Replay

Execution can be independently re-derived:

safechange replay <audit_file>

## Meaning

- Same input → same decision
- Tampering breaks verification
- No hidden execution paths

This creates a provable execution boundary.
