# Veritas SafeChange — EU AI Act Evidence-Support Mapping

## Purpose

This document maps Veritas SafeChange to EU AI Act evidence-support concepts.

It does not claim that this repository satisfies the EU AI Act.

It identifies where this repository may support technical documentation, logging, risk management, oversight, robustness, and cybersecurity evidence when mapped into a specific regulated deployment.

## Mapping Discipline

Use:

```text
supports evidence for
may contribute to
can provide proof surface for
```

Do not use:

```text
satisfies
certifies
complies with by itself
legally guarantees
```

## Article 9 — Risk Management Support

SafeChange may support risk-management evidence by showing:

```text
pre-effect state-change evaluation
blocked change paths
revert / rollback behavior
failure-mode classification
bounded proof of what could not persist
```

## Article 11 — Technical Documentation Support

SafeChange may support technical documentation through:

```text
architecture description
runtime behavior description
boundary decision logic
receipt outputs
claim boundaries
limitations
```

## Article 12 — Record-Keeping / Logging Support

SafeChange may support record-keeping through:

```text
deterministic receipts
change decision records
state-change proof artifacts
replayable audit evidence where implemented
```

## Article 14 — Human Oversight Integration

Correct position:

```text
Human oversight governs the admissibility regime, thresholds, escalation paths, accountability, and override governance.

The runtime enforces bind-time admissibility at machine speed.
```

SafeChange can support oversight by routing unsafe or uncertain changes to refusal, revert, or escalation behavior.

## Article 15 — Accuracy, Robustness, Cybersecurity Support

SafeChange may support robustness and cybersecurity evidence by showing:

```text
controlled failure behavior
state-change verification
rollback or block behavior
receipt-based evidence
bounded proof under known conditions
```

## Non-Claim Boundary

```text
This repository does not establish EU AI Act compliance.
A deployment-specific role, intended use, risk classification, technical documentation package, oversight procedure, logging retention policy, cybersecurity controls, validation evidence, and legal review would be required.
```
