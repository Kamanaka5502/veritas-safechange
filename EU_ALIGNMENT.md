# Veritas SafeChange — EU Custody and Compliance Alignment

## Purpose

This document provides a public-safe EU regulatory alignment map for Veritas SafeChange.

It is not a legal opinion, certification, regulatory approval, or compliance attestation.

It explains how this repository supports custody, evidence, replay, fail-closed behavior, and execution governance concepts relevant to EU-style regulatory review.

## Repository Role

```text
Veritas SafeChange governs risky state change before protected consequence persists.
```

SafeChange demonstrates a bounded consequence-control pattern:

```text
proposed change
  -> pre-effect evaluation
  -> apply / verify / revert / block
  -> deterministic receipt
  -> replayable audit surface
```

## EU Alignment Surfaces

| EU Surface | Relevance | SafeChange Alignment |
|---|---|---|
| EU AI Act | Logging, risk controls, technical documentation, human oversight, accountable AI deployment. | Demonstrates bounded execution decisions, deterministic receipts, and refusal/revert paths. |
| DORA | ICT operational resilience, incident handling, testing, and operational controls for financial entities. | Supports safe change, rollback/revert behavior, receipt evidence, and controlled failure handling. |
| NIS2 | Cybersecurity risk management, incident response, supply-chain and operational security. | Provides execution-boundary evidence for state changes and protected mutation control. |
| Cyber Resilience Act | Security-by-design, lifecycle security, vulnerability handling for digital products. | Supports change safety, failure evidence, and repeatable verification. |
| GDPR | Accountability, security, minimization, and lawful processing boundaries where personal data exists. | This repo should avoid personal data in examples and preserve data-minimization boundaries. |

## Custody / Compliance Separation

SafeChange must preserve the distinction between:

```text
authority
change intent
pre-effect evaluation
execution result
rollback / revert path
receipt
replay
consequence
```

A log is not custody.
A successful change is not admissibility.
A receipt is not replay legitimacy unless replay preserves the decision basis.

## Current Alignment Strengths

```text
pre-effect state-change evaluation
safe / reverted / blocked outcome pattern
deterministic receipt surface
replayable proof posture
fail-closed behavior when verification fails
bounded proof claim
```

## Required Hardening For EU-Ready Review

```text
DATA_AND_PRIVACY_BOUNDARY.md
SECURITY_AND_INCIDENT_RESPONSE.md
RECEIPT_AND_REPLAY_POLICY.md
NON_CLAIM_BOUNDARY.md
SUPPLY_CHAIN_AND_DEPENDENCY_BOUNDARY.md
```

## Non-Claim Boundary

This repository does not claim:

```text
EU AI Act compliance certification
DORA compliance certification
NIS2 compliance certification
Cyber Resilience Act certification
GDPR legal compliance certification
production deployment in regulated infrastructure
complete prevention of software or operational risk
```

## Review Claim

```text
This repository demonstrates a bounded safe-change pattern that supports EU-aligned execution governance concepts: pre-effect evaluation, controlled failure, receipt evidence, replay posture, and non-silent consequence binding.
```
