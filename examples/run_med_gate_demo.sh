#!/data/data/com.termux/files/usr/bin/bash
set -e
cd ~/veritas-safechange

echo "----- PASS CASE (should be SAFE) -----"
safechange apply examples/state_pass.json examples/med_gate_change.json --pretty --require renal_lab_present

echo ""
echo "----- FAIL CASE (should REVERT) -----"
safechange apply examples/state_fail.json examples/med_gate_change.json --pretty --require renal_lab_present

echo ""
echo "----- VERIFY -----"
safechange verify-audit recovery_gate_audit.jsonl --pretty

echo ""
echo "----- REPLAY -----"
safechange replay recovery_gate_audit.jsonl --pretty
