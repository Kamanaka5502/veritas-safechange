from __future__ import annotations

import argparse
import json
from typing import Any

from . import __version__

from .audit import JsonlAuditSink
from .core import RecoveryGate, ChainedContext
from .state import JsonFileState
from .sqlite_state import SqliteFileState
from .invariants import InvariantSet, required_keys, monotone_min, non_negative
from .signing import HmacSigner
from .audit_verify import verify_jsonl
from .derivation import JsonlDerivationSink

def load_change(path: str):
    with open(path, "r", encoding="utf-8") as f:
        change = json.load(f)
    if not isinstance(change, dict):
        raise ValueError("change spec must be a JSON object")
    if not set(change).issubset({"set", "remove"}):
        unknown = sorted(set(change) - {"set", "remove"})
        raise ValueError(f"unsupported change spec keys: {unknown}")
    if "set" in change and not isinstance(change.get("set"), dict):
        raise ValueError("'set' must be a JSON object")
    if "remove" in change and not isinstance(change.get("remove"), list):
        raise ValueError("'remove' must be a JSON array")
    return change

def make_change_fn(change_spec: dict):
    sets = change_spec.get("set", {})
    removes = change_spec.get("remove", [])

    def apply_fn(state: Any):
        if isinstance(state, dict):
            new = dict(state)
            for k, v in sets.items():
                new[k] = v
            for k in removes:
                new.pop(k, None)
            return new
        return state
    return apply_fn

def build_invariants(args) -> InvariantSet:
    invs = []
    if args.require:
        invs.append(required_keys(*args.require))
    for spec in args.monotone_min:
        if ":" in spec:
            key, m = spec.split(":", 1)
            invs.append(monotone_min(key, float(m)))
        else:
            invs.append(monotone_min(spec, 1))
    if args.non_negative:
        invs.append(non_negative(*args.non_negative))
    return InvariantSet(invs)

def cmd_apply(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="safechange apply",
        description="Allow a risky change to become real only when verification and rollback are both available."
    )
    p.add_argument("--state-kind", choices=["json", "sqlite"], default="json")
    p.add_argument("state_path", help="Path to state file (JSON or SQLite)")
    p.add_argument("change_json", help="Path to JSON change spec: {set:{}, remove:[]}")
    p.add_argument("--audit", default="recovery_gate_audit.jsonl", help="Audit log path (JSONL)")
    p.add_argument("--derivation-out", default=None, help="Derivation JSONL path (defaults to <audit>.derivations.jsonl)")
    p.add_argument("--change-id", default="change", help="Change id for audit record")
    p.add_argument("--pretty", action="store_true", help="Print a short operator-facing summary before the JSON record")

    # Invariant flags
    p.add_argument("--require", action="append", default=[], help="Required key (repeatable)")
    p.add_argument("--monotone-min", action="append", default=[], help="Numeric key >= min. key or key:min")
    p.add_argument("--non-negative", action="append", default=[], help="Numeric key >= 0 if present (repeatable)")

    # Tamper-evidence
    p.add_argument("--hmac-secret", default=None, help="Sign each audit record by HMAC over audit_hash")
    p.add_argument("--chain", action="store_true", help="Add prev_audit_hash to create an in-process hash chain")

    args = p.parse_args(argv)

    sink = JsonlAuditSink(args.audit)
    invset = build_invariants(args)
    signer = HmacSigner(args.hmac_secret.encode("utf-8")) if args.hmac_secret else None
    chain = ChainedContext() if args.chain else None

    derivation_path = args.derivation_out or (args.audit + ".derivations.jsonl")
    deriv_sink = JsonlDerivationSink(derivation_path)

    gate = RecoveryGate(
        invariants=invset,
        audit_sink=sink.write,
        signer=signer,
        chain=chain,
        derivation_sink=deriv_sink.write,
    )

    state = JsonFileState(args.state_path) if args.state_kind == "json" else SqliteFileState(args.state_path)
    change = load_change(args.change_json)
    record = gate.execute(state, make_change_fn(change), change_id=args.change_id)

    status_map = {
        "COMMITTED": "SAFE",
        "ROLLED_BACK": "REVERTED",
        "APPLY_FAILED": "BLOCKED",
        "SNAPSHOT_FAILED": "BLOCKED",
    }
    data = json.loads(record.to_json())
    data["operator_status"] = status_map.get(record.decision, record.decision)
    if args.pretty:
        next_step = "run receipt verification or replay the path"
        print(
            f"status: {data['operator_status']}\n"
            f"reason: {data.get('reason', '')}\n"
            f"receipt: {data.get('audit_hash', '')[:16]}...\n"
            f"next step: {next_step}"
        )
    print(json.dumps(data, sort_keys=True))
    return 0 if record.decision in ("COMMITTED", "ROLLED_BACK") else 2

def cmd_verify(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="safechange verify-audit",
        description="Verify a JSONL audit log and confirm that receipts still hold."
    )
    p.add_argument("audit_jsonl", help="Path to audit JSONL file")
    p.add_argument("--hmac-secret", default=None, help="Verify HMAC signatures using this secret")
    p.add_argument("--require-chain", action="store_true", help="Require prev_audit_hash on every record")
    p.add_argument("--pretty", action="store_true", help="Print a short operator-facing verification summary before the JSON record")
    args = p.parse_args(argv)

    res = verify_jsonl(args.audit_jsonl, hmac_secret=args.hmac_secret, require_chain=args.require_chain)
    if res.ok:
        if args.pretty:
            print("status: PASS\nreason: receipt trail is internally consistent\nnext step: retain the receipt or replay independently")
        print(json.dumps({"ok": True}, sort_keys=True))
        return 0
    if args.pretty:
        print("status: FAIL\nreason: receipt trail verification found errors\nnext step: inspect the errors and rerun")
    print(json.dumps({"ok": False, "errors": res.errors}, sort_keys=True, indent=2))
    return 2

def cmd_replay(argv=None) -> int:
    # v5 replay is verification framed as independent re-derivation.
    return cmd_verify(argv)

def main(argv=None) -> int:
    top = argparse.ArgumentParser(
        prog="safechange",
        add_help=True,
        description="Safe production changes with provable rollback, receipts, and replay verification."
    )
    top.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = top.add_subparsers(dest="cmd", required=True)

    sub_apply = sub.add_parser("apply", help="Run a governed change with proof")
    sub_apply.set_defaults(_fn=cmd_apply)

    sub_verify = sub.add_parser("verify-audit", help="Verify receipt trail")
    sub_verify.set_defaults(_fn=cmd_verify)

    sub_replay = sub.add_parser("replay", help="Replay receipt trail")
    sub_replay.set_defaults(_fn=cmd_replay)

    args, rest = top.parse_known_args(argv)
    return args._fn(rest)

if __name__ == "__main__":
    raise SystemExit(main())
