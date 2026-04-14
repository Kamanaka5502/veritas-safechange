import json
from pathlib import Path

from recovery_gate import RecoveryGate, JsonFileState

def invariants(state):
    return ("schema_version" in state and state["schema_version"] >= 1), "ok"

def test_json_file_state(tmp_path: Path):
    p = tmp_path / "state.json"
    p.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
    st = JsonFileState(str(p))
    gate = RecoveryGate(invariants)

    def ch(s):
        n = dict(s)
        n["schema_version"] = 0
        return n

    rec = gate.execute(st, ch, change_id="bad")
    assert rec.decision == "ROLLED_BACK"
    assert json.loads(p.read_text(encoding="utf-8"))["schema_version"] == 1
