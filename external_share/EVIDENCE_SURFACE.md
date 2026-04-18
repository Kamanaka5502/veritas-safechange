# Veritas Aegis — Evidence Surface

This system produces verifiable evidence for every attempted action.

## Each execution attempt produces
- decision outcome
- reason
- before-state hash
- after-state hash
- audit hash
- timestamp
- invariant evidence when applicable

## Canonical operator outcomes
- SAFE -> COMMITTED
- REVERTED -> ROLLED_BACK
- BLOCKED -> APPLY_FAILED or SNAPSHOT_FAILED

## Verification
Audit trail verification:
safechange verify-audit <audit_jsonl>

Replay verification:
safechange replay <audit_jsonl>

## Meaning
- Same basis -> same result
- Failed invariants produce visible rollback
- Tampering breaks trust in the receipt trail
- No hidden execution path is treated as valid proof

## Boundary statement
The evidence surface exists to prove not only what happened,
but whether the move was allowed to become real under governance.
