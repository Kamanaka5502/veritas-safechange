# Architecture

```text
proposed change
    ↓
snapshot pre-state
    ↓
apply change
    ↓
verify invariants
    ↓
commit or revert
    ↓
emit receipt
    ↓
replay / audit verify
```

SafeChange sits at the boundary where a risky change either becomes safe reality or fails closed with proof.
