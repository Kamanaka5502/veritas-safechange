import json
from pathlib import Path

from recovery_gate import RecoveryGate, DictState, InvariantSet, required_keys
from recovery_gate.derivation import JsonlDerivationSink

def test_derivation_emitted(tmp_path: Path):
    deriv_path = tmp_path / "d.jsonl"

    invs = InvariantSet([required_keys("x")])
    st = DictState({"x": 1})

    sink = JsonlDerivationSink(str(deriv_path))
    gate = RecoveryGate(invariants=invs, derivation_sink=sink.write)

    gate.execute(st, lambda s: dict(s), change_id="noop")

    lines = deriv_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    obj = json.loads(lines[0])
    assert "claim" in obj and "because" in obj and "audit_hash" in obj
