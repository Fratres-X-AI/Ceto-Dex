# Security Policy

Ceto-Dex is **research software** from [Fratres X AI](https://www.fratres-x.com).
We assume breach. Reports that demonstrate containment bypass with measurable
blast-radius expansion are highest priority.

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
| < 0.1   | Best effort |

## Reporting a vulnerability

1. **Do not** open a public GitHub issue for sensitive containment bypasses.
2. Use [GitHub private vulnerability reporting](https://github.com/Fratres-X-AI/Ceto-Dex/security/advisories/new)
   on `Fratres-X-AI/Ceto-Dex`, or contact Fratres X AI via
   [fratres-x.com](https://www.fratres-x.com).
3. Include: reproduction steps, affected module (e.g. `cetodex/refusal.py`,
   `cetodex/replay.py`), expected vs actual behavior, and impact assessment.

We aim to acknowledge reports within **72 hours**.

## Scope

**In scope:**

- Evidence ledger tampering or hash-chain bypass
- Refusal gate bypass that allows unsupported labels without audit trail
- Manifest integrity failures that could misrepresent provenance
- Path traversal or unsafe deserialization in replay bundle handling

**Out of scope:**

- Model accuracy or false-positive/false-negative rates (see KNOWN_LIMITS)
- Third-party training datasets or inference runtimes you connect
- Social engineering of operators
- Denial of service against public infrastructure outside this repository

## Safe harbor

We will not pursue legal action against good-faith researchers who:

- Avoid privacy violations, data destruction, and service disruption beyond
  what is needed to demonstrate the issue
- Do not exploit the finding beyond proof of concept
- Report promptly and keep details private until a fix or coordinated
  disclosure window ends

## Philosophy

Perfect perimeter blocking is not the claim. Ceto-Dex succeeds when egress is
controlled, measured, and auditable under adversarial pressure — and when
refusal defaults protect conservation workflows from overconfident automation.
