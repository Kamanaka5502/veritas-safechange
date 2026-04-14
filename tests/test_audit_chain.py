from pathlib import Path
from recovery_gate import RecoveryGate, DictState, InvariantSet, required_keys
from recovery_gate.core import ChainedContext
from recovery_gate.audit_verify import verify_jsonl

def test_chain_verification(tmp_path: Path):
    invs = InvariantSet([required_keys("x")])
    audit_path = tmp_path / "audit.jsonl"

    def sink(rec):
        with open(audit_path, "a", encoding="utf-8") as f:
            f.write(rec.to_json()); f.write("\n")

    gate = RecoveryGate(invariants=invs, audit_sink=sink, chain=ChainedContext())

    st = DictState({"x": 1})
    gate.execute(st, lambda s: dict(s), change_id="a")
    gate.execute(st, lambda s: dict(s), change_id="b")

    res = verify_jsonl(str(audit_path), require_chain=True)
    assert res.ok is True
