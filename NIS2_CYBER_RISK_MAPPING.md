# Veritas SafeChange — NIS2 Cyber Risk Mapping

## Purpose

This document maps Veritas SafeChange to NIS2-style cybersecurity governance evidence needs.

It is not a NIS2 compliance claim or legal attestation.

## NIS2-Relevant Evidence Surfaces

| NIS2 Pressure Surface | SafeChange Evidence Support |
|---|---|
| Cyber risk management | Controlled state-change evaluation and failure behavior. |
| Incident handling | Receipts and blocked/reverted change evidence may support incident review. |
| Operational continuity | Fail-closed and rollback patterns support continuity posture. |
| Supply-chain security | Change governance can contribute to supply-chain mutation control. |
| Access / privileged action governance | Protected change motion can be refused or reverted before persistence. |

## Correct Claim

```text
SafeChange may support NIS2-style cyber risk evidence by proving how protected state changes were admitted, reverted, blocked, or failed closed within a bounded corridor.
```

## Non-Claim Boundary

```text
This repository does not certify NIS2 compliance.
Entity-specific governance, incident process, security controls, access management, supply-chain review, and legal mapping are required.
```
