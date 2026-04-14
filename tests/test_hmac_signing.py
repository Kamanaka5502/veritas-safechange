import json
from recovery_gate import RecoveryGate, DictState, InvariantSet, required_keys
from recovery_gate.signing import HmacSigner
from recovery_gate.audit_verify import verify_jsonl

def test_audit_signature_and_chain(tmp_path):
    invs = InvariantSet([required_keys("x")])
    signer = HmacSigner(b"secret")
    audit_path = tmp_path / "a.jsonl"

    # collect audit records
    def sink(rec):
        with open(audit_path, "a", encoding="utf-8") as f:
            f.write(rec.to_json()); f.write("\n")

    gate = RecoveryGate(invariants=invs, signer=signer, audit_sink=sink, chain=None)

    st = DictState({"x": 1})
    gate.execute(st, lambda s: dict(s), change_id="noop1")
    gate.execute(st, lambda s: dict(s), change_id="noop2")

    # verify signatures (chain not required here because chain=None)
    res = verify_jsonl(str(audit_path), hmac_secret="secret", require_chain=False)
    assert res.ok is True
