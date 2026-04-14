# Contributing

## Setup

```bash
python -m pip install -e ".[dev]"
pytest -q
```

## Guidelines

- keep the core contract small: snapshot, apply, verify, commit-or-rollback, receipt
- preserve deterministic audit verification
- add or update tests for every behavior change
- prefer explicit failure over silent widening
