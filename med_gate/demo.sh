#!/data/data/com.termux/files/usr/bin/bash

echo ""
echo "=== SAME CHANGE, DIFFERENT CONDITIONS ==="
echo ""

echo "→ Case 1: Required condition PRESENT → should COMMIT"
safechange apply state_pass.json change.json --pretty --require renal_lab_present

echo ""
echo "→ Case 2: Required condition MISSING → should NOT become real"
safechange apply state_fail.json change.json --pretty --require renal_lab_present

echo ""
echo "→ Verify receipt trail"
safechange verify-audit recovery_gate_audit.jsonl --pretty

echo ""
echo "→ Replay independently (same input → same result)"
safechange replay recovery_gate_audit.jsonl --pretty

echo ""
echo "=== RESULT: EXECUTION IS CONTROLLED AT COMMIT ==="
