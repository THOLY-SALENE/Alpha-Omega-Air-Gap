# Alpha Omega Air Gap (AOAG)

AOAG is a local-first, fail-closed policy mediation framework for model input/output safety, release control, and auditable decision gating.

It is designed to reduce unsafe output release risk by combining:
- kernel-style entry/exit bookends
- MCP 9-heart drift checks
- SFL-style consensus review
- audit logging
- bounded release decisions (`approve`, `constrain`, `block`)

## Status

Early public prototype.

This repository currently documents the architecture and core policy structure. It is not yet presented as a production-ready or independently validated security system.

## What AOAG is

AOAG is a logical isolation and safety-boundary layer for local or local-first model deployments.

Its purpose is to:
- inspect requests before release
- evaluate multi-signal risk
- gate outputs through explicit policy decisions
- preserve an auditable trail of safety-relevant decisions
- fail closed when confidence or consensus breaks down

## What AOAG is not

AOAG is not:
- a hardware air gap
- a guarantee against host compromise
- a substitute for OS, network, or endpoint security
- a complete defense against all adversarial prompting
- a certified medical, legal, or safety-critical control system

## Core concepts

### 1. Kernel bookends
Requests are checked on entry and outputs are checked on exit. If either side fails policy, release is blocked or constrained.

### 2. MCP 9-heart grammar
AOAG evaluates release behavior across multiple interpretive lanes:
- White: truth / fidelity
- Black: adversarial pressure
- Red: execution
- Yellow: signaling pace
- Blue: continuity / integrity
- Purple: synthesis / coherence
- Green: homeostasis / regulation
- Orange: ignition / coupling eligibility
- Gold: humility / boundedness

### 3. SFL consensus
AOAG can require quorum-style agreement before release, reducing single-path failure risk.

### 4. Auditability
All decisions are structured, hashed, and recorded into an audit log with bounded retention.

## Output modes

AOAG supports three release outcomes:
- `approved`
- `constrained`
- `blocked`

This keeps the framework fail-closed by default.

## Threat model

AOAG is intended to reduce risk from:
- prompt injection
- context override attempts
- unsafe transformation requests
- drift between policy signals
- unsafe release under uncertainty

AOAG does not claim to defend against:
- compromised hosts
- malicious firmware or OS layers
- model-weight backdoors
- physical device access
- upstream supply-chain attacks

## Repository roadmap

Planned improvements:
- complete source publication without placeholders
- runnable examples
- reproducible tests
- documented threat model
- adversarial evaluation suite
- versioned releases

## Current limitations

This public repository is still incomplete as a review artifact.
Some implementation sections are scaffolded and need to be replaced with full inspectable source, tests, and evaluation material.

## Next steps

1. Publish complete implementation
2. Add tests and regression cases
3. Add eval documentation
4. Add release tags
5. Add license

## Philosophy

AOAG is built around a simple posture:

**Do not release raw outputs under uncertainty.  
Filter, bound, audit, and fail closed.**
