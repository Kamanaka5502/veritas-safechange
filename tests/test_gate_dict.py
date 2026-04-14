from recovery_gate import RecoveryGate, DictState

def invariants_ok(state):
    if state.get("x", 0) < 0:
        return False, "x_negative"
    return True, "ok"

def test_commit():
    st = DictState({"x": 1})
    gate = RecoveryGate(invariants_ok)
    def ch(s):
        n = dict(s)
        n["x"] = 2
        return n
    rec = gate.execute(st, ch, change_id="commit")
    assert rec.decision == "COMMITTED"
    assert st.read()["x"] == 2

def test_rollback_on_invariant_fail():
    st = DictState({"x": 1})
    gate = RecoveryGate(invariants_ok)
    def ch(s):
        n = dict(s)
        n["x"] = -5
        return n
    rec = gate.execute(st, ch, change_id="bad")
    assert rec.decision == "ROLLED_BACK"
    assert st.read()["x"] == 1

def test_rollback_on_apply_exception():
    st = DictState({"x": 1})
    gate = RecoveryGate(invariants_ok)
    def ch(_s):
        raise RuntimeError("boom")
    rec = gate.execute(st, ch, change_id="explode")
    assert rec.decision == "APPLY_FAILED"
    assert st.read()["x"] == 1
