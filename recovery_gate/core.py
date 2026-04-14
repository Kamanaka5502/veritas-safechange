from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, Tuple

from .audit import AuditRecord, utc_now_iso
from .exceptions import ApplyError, SnapshotError
from .state import State
from .invariants import InvariantSet
from .signing import HmacSigner
from .audit_verify import audit_hash
from .derivation import DerivationRecord

Verifier = Callable[[Any], Tuple[bool, str]]
ChangeFn = Callable[[Any], Any]

class Decision(str, Enum):
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    APPLY_FAILED = "APPLY_FAILED"
    SNAPSHOT_FAILED = "SNAPSHOT_FAILED"

@dataclass
class ChainedContext:
    """In-process hash chain context (optional)."""
    prev_audit_hash: Optional[str] = None

@dataclass(frozen=True)
class RecoveryGate:
    """Provable rollback wrapper (v5 spec-first, derivation-emitting).

    Guarantees:
      - if invariant verification fails OR apply throws, state is restored to snapshot
      - emits AuditRecord (append-only) with stable audit_hash (+ optional chain + optional signature)
      - emits a DerivationRecord (language-agnostic proof artifact) when derivation_sink is provided
    """
    verifier: Optional[Verifier] = None
    invariants: Optional[InvariantSet] = None
    audit_sink: Optional[Callable[[AuditRecord], None]] = None
    signer: Optional[HmacSigner] = None
    chain: Optional[ChainedContext] = None
    derivation_sink: Optional[Callable[[DerivationRecord], None]] = None

    def _verify(self, state_value: Any) -> tuple[bool, str, Optional[list[dict]]]:
        if self.invariants is not None:
            ok, results = self.invariants.verify(state_value)
            if ok:
                return True, "ok", results
            failing = next((r for r in reversed(results) if not r["ok"]), results[-1] if results else {"name": "unknown"})
            return False, f"invariant_failed:{failing.get('name','unknown')}", results

        if self.verifier is None:
            return True, "ok", None

        ok, reason = self.verifier(state_value)
        return bool(ok), (reason or "ok"), None

    def _emit_derivation(self, audit_record: AuditRecord) -> None:
        if self.derivation_sink is None:
            return

        extra = audit_record.extra or {}
        invs = extra.get("invariants")
        ah = extra.get("audit_hash", "")

        because = ["audit_hash_matches", "content_identity"]
        if invs is not None:
            because.append("all_invariants_hold" if audit_record.decision == Decision.COMMITTED.value else "invariant_failed")
        if audit_record.decision in (Decision.ROLLED_BACK.value, Decision.APPLY_FAILED.value, Decision.SNAPSHOT_FAILED.value):
            because.append("rollback_available_or_attempted")

        claim = "Transition ACCEPTED" if audit_record.decision == Decision.COMMITTED.value else "Transition REJECTED_OR_REVERTED"

        d = DerivationRecord(
            claim=claim,
            because=because,
            decision=audit_record.decision,
            reason=audit_record.reason,
            before_hash=audit_record.before_hash,
            after_hash=audit_record.after_hash,
            audit_hash=ah,
            change_id=audit_record.change_id,
            timestamp=audit_record.timestamp,
            invariants=invs,
            signature=audit_record.signature,
        )
        self.derivation_sink(d)

    def _emit(self, record: AuditRecord) -> AuditRecord:
        # Add chain metadata first, then compute the canonical audit hash over the
        # full unsigned payload (excluding self-referential extra.audit_hash).
        extra = dict(record.extra or {})
        if self.chain is not None and self.chain.prev_audit_hash:
            extra["prev_audit_hash"] = self.chain.prev_audit_hash

        unsigned_record = AuditRecord(**{**record.to_dict(), "extra": extra, "signature": None})
        computed_hash = audit_hash(unsigned_record.to_dict())
        extra["audit_hash"] = computed_hash

        # Rebuild finalized unsigned record with declared audit_hash.
        record = AuditRecord(**{**record.to_dict(), "extra": extra, "signature": None})

        # Optional signature over the stable audit hash.
        if self.signer is not None:
            record = AuditRecord(**{**record.to_dict(), "signature": self.signer.sign(computed_hash)})

        if self.audit_sink:
            self.audit_sink(record)

        if self.chain is not None:
            self.chain.prev_audit_hash = computed_hash

        self._emit_derivation(record)
        return record

    def execute(self, state: State, change_fn: ChangeFn, *, change_id: str = "change") -> AuditRecord:
        # 1) Snapshot
        try:
            before_hash = state.snapshot()
        except Exception as e:
            record = AuditRecord(
                decision=Decision.SNAPSHOT_FAILED.value,
                reason=f"snapshot_failed:{e}",
                before_hash="",
                after_hash=state.digest(),
                state_kind=state.kind,
                change_id=change_id,
                timestamp=utc_now_iso(),
                extra=None,
                signature=None,
            )
            self._emit(record)
            raise SnapshotError(str(e)) from e

        # 2) Apply
        try:
            current = state.read()
            proposed = change_fn(current)
            state.write(proposed)
        except Exception as e:
            # rollback on apply failure
            try:
                state.restore(before_hash)
            except Exception as re:
                record = AuditRecord(
                    decision=Decision.APPLY_FAILED.value,
                    reason=f"apply_failed_and_restore_failed:apply={e} restore={re}",
                    before_hash=before_hash,
                    after_hash=state.digest(),
                    state_kind=state.kind,
                    change_id=change_id,
                    timestamp=utc_now_iso(),
                    extra=None,
                    signature=None,
                )
                self._emit(record)
                raise ApplyError(str(e)) from e

            record = AuditRecord(
                decision=Decision.APPLY_FAILED.value,
                reason=f"apply_failed:{e}",
                before_hash=before_hash,
                after_hash=state.digest(),
                state_kind=state.kind,
                change_id=change_id,
                timestamp=utc_now_iso(),
                extra=None,
                signature=None,
            )
            return self._emit(record)

        # 3) Verify
        ok, reason, inv_results = self._verify(state.read())
        extra = {"invariants": inv_results} if inv_results is not None else None

        # 4) Commit / rollback
        if ok:
            record = AuditRecord(
                decision=Decision.COMMITTED.value,
                reason=reason,
                before_hash=before_hash,
                after_hash=state.digest(),
                state_kind=state.kind,
                change_id=change_id,
                timestamp=utc_now_iso(),
                extra=extra,
                signature=None,
            )
            return self._emit(record)

        state.restore(before_hash)
        record = AuditRecord(
            decision=Decision.ROLLED_BACK.value,
            reason=reason,
            before_hash=before_hash,
            after_hash=state.digest(),
            state_kind=state.kind,
            change_id=change_id,
            timestamp=utc_now_iso(),
            extra=extra,
            signature=None,
        )
        return self._emit(record)
