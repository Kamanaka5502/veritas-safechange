from recovery_gate import InvariantSet, required_keys, monotone_min, non_negative
from recovery_gate.harness import run_invariants

def test_invariant_set_ok():
    invs = InvariantSet([
        required_keys("schema_version", "enabled"),
        monotone_min("schema_version", 1),
        non_negative("balance"),
    ])
    st = {"schema_version": 2, "enabled": True, "balance": 0}
    res = run_invariants(invs, st)
    assert res.ok is True
    assert res.summary == "ok"
    assert all(r["ok"] for r in res.results)

def test_invariant_set_fail_fast():
    invs = InvariantSet([
        required_keys("schema_version", "enabled"),
        monotone_min("schema_version", 1),
    ])
    st = {"schema_version": 0}
    res = run_invariants(invs, st)
    assert res.ok is False
    # First invariant fails due to missing enabled
    assert res.results[-1]["name"] == "required_keys_present"
    assert res.results[-1]["ok"] is False
