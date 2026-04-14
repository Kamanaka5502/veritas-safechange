# Terminal examples

## Safe path

```bash
safechange apply examples/state.json examples/change.json --state-kind json --require status --audit audit.jsonl
safechange verify-audit audit.jsonl
```

Expected operator meaning: **SAFE**

## Reverted path

Use a change that violates a required invariant.

Expected operator meaning: **REVERTED**

## Blocked path

Use an invalid state path or malformed change spec.

Expected operator meaning: **BLOCKED**
