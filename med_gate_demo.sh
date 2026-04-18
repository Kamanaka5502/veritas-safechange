#!/data/data/com.termux/files/usr/bin/bash
set -e
cd ~/veritas-safechange

echo "----- PASS CASE (should be SAFE) -----"
safechange apply state_pass.json change.json --pretty --require renal_lab_present

echo ""
echo "----- FAIL CASE (should REVERT) -----"
safechange apply state_fail.json change.json --pretty --require renal_lab_present

echo ""
echo "----- VERIFY -----"
safechange verify-audit recovery_gate_audit.jsonl --pretty

echo ""
echo "----- REPLAY -----"
safechange replay recovery_gate_audit.jsonl --pretty
