# Evidence Inventory

This inventory separates **public portfolio evidence** from **raw assessment evidence**.

## Existing curated public evidence

The public repository already contains 26 curated screenshots across 7 folders:

- `01-architecture`
- `02-windows-server-ad`
- `03-domain-client-gpo`
- `04-entra-id`
- `05-hybrid-identity`
- `06-intune`
- `07-medsecure-login`

These screenshots were previously reviewed and cropped/redacted where required.

## New ICT932 security-assessment evidence

An additional set of **20 raw security-assessment captures** was produced during the authorised eduLAB testing.

The captures cover:

- baseline pytest result
- Zero Trust / ABAC pytest result
- final pytest result
- Bandit initial findings
- Bandit clean re-tests
- pip-audit clean re-test
- Gitleaks clean re-test
- OWASP ZAP activity and Ubuntu 429 logs
- patient own-record access
- cross-patient HTTP 403
- cross-patient security-audit evidence
- repeated-login HTTP 429 containment
- successful post-incident recovery
- SQL injection-style login test and rejected result
- Git branch/status evidence
- local MedSecure service startup / network reachability evidence

### Secure publication status

The raw captures are **not automatically committed**.

Several eduLAB screenshots include browser/header context that may expose a student identifier or unnecessary environment metadata. They must be cropped or redacted before being placed in the public repository.

Raw evidence should remain in the ignored local `evidence/` directory until reviewed.

Recommended public destination after redaction:

```text
screenshots/
└── 08-security-assessment/
    ├── 01-pytest-baseline.png
    ├── 02-bandit-initial-findings.png
    ├── 03-bandit-retest-clean.png
    ├── 04-pip-audit-clean.png
    ├── 05-gitleaks-clean.png
    ├── 06-zap-rate-limit.png
    ├── 07-patient-own-record.png
    ├── 08-cross-patient-403.png
    ├── 09-cross-patient-audit.png
    ├── 10-zero-trust-pytest.png
    ├── 11-incident-429.png
    ├── 12-incident-recovery.png
    ├── 13-sqli-attempt.png
    └── 14-sqli-rejected.png
```

Not every raw capture needs to be published. Prefer the minimum set that proves the result.

## Security-review checklist for screenshots

Before committing a screenshot:

- remove student IDs and account identifiers
- remove real email addresses unless strictly necessary
- remove tenant IDs, device IDs, serial numbers and application IDs unless already safely redacted
- remove MFA challenge numbers
- remove Personal Access Tokens, API keys, client secrets, cookies and session tokens
- remove password-manager prompts and stored credential values
- avoid showing real passwords; synthetic test strings should also be hidden where they add no evidentiary value
- keep only the technical context necessary to prove the result

Private RFC1918 lab addresses are not authentication secrets, but they should be retained only when they add technical value.

## Existing public evidence structure

```text
screenshots/
├── 01-architecture/
├── 02-windows-server-ad/
├── 03-domain-client-gpo/
├── 04-entra-id/
├── 05-hybrid-identity/
├── 06-intune/
└── 07-medsecure-login/
```

## Security assessment documentation

The assessment findings, remediation and final validation are documented in:

- [05-security-and-testing.md](05-security-and-testing.md)
- [07-ict932-security-assessment.md](07-ict932-security-assessment.md)
- [../SECURITY.md](../SECURITY.md)

All clinical and workforce records used in the project are synthetic.
