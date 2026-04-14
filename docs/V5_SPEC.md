# Recovery Gate v5 Final Specification (Normative)

v5 Final defines Recovery Gate as a *specification* with a minimal reference implementation.

## Axioms (Final)
1. Every accepted transition MUST have a provable rollback.
2. Rollback MUST restore identical content identity (hash equality).
3. Invariants MUST be deterministic for a given state value.
4. Invariants MUST emit structured evidence or explicitly emit none.
5. Audit MUST be append-only.
6. Each record MUST include `audit_hash` computed from record content (excluding signature).
7. Optional chaining MUST use `prev_audit_hash` with a single linear chain.
8. Optional signing MUST sign `audit_hash` (stable).
9. Replay MUST be possible without trusting the original system.

## Canonical Audit Record (JSON object)
Required fields:
- decision (string)
- reason (string)
- before_hash (string)
- after_hash (string)
- state_kind (string)
- change_id (string)
- timestamp (string, ISO8601)
- extra (object or null) — if present MUST include:
    - audit_hash (string, hex)
    - prev_audit_hash (string, hex) optional
    - invariants (array) optional (deterministic order)
Optional fields:
- signature (string, hex) — signature over `extra.audit_hash`

This schema is frozen. Backward-compatible additions MUST be optional and MUST NOT change `audit_hash` computation rules.

## Optional Derivation Artifacts (Recommended)

A Recovery Gate implementation MAY emit a separate append-only derivation stream.
Each derivation record is a compact, language-agnostic proof object describing:

- claim (accepted / rejected_or_reverted)
- because[] (reasons like `audit_hash_matches`, `all_invariants_hold`, `rollback_available_or_attempted`)
- decision + reason
- before/after hashes
- audit_hash (+ optional signature)

Derivation artifacts MUST NOT replace audit logs; they are supplementary and replay-friendly.
