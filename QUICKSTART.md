# Quickstart

```bash
pip install veritas-safechange
safechange apply examples/state.json examples/change.json --state-kind json --require status --audit audit.jsonl --pretty
safechange verify-audit audit.jsonl --pretty
```

Expected operator-facing states:
- SAFE
- REVERTED
- BLOCKED
