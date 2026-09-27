# ICT932 Security Assessment Evidence

This folder is reserved for **curated, redacted** security-assessment screenshots.

Raw eduLAB captures are intentionally kept outside Git tracking until they have been reviewed for privacy and secret exposure.

## Planned evidence set

Recommended public filenames:

1. `01-pytest-baseline.png`
2. `02-bandit-initial-findings.png`
3. `03-bandit-retest-clean.png`
4. `04-pip-audit-clean.png`
5. `05-gitleaks-clean.png`
6. `06-zap-rate-limit.png`
7. `07-patient-own-record.png`
8. `08-cross-patient-403.png`
9. `09-cross-patient-audit.png`
10. `10-zero-trust-pytest.png`
11. `11-incident-429.png`
12. `12-incident-recovery.png`
13. `13-sqli-attempt.png`
14. `14-sqli-rejected.png`

## Publication rules

Before adding an image here:

- remove student IDs and account identifiers
- remove real email addresses unless strictly necessary
- remove tenant IDs, device IDs, serial numbers and MFA challenge details
- never expose Personal Access Tokens, client secrets, API keys, cookies or session tokens
- hide password-manager content and real password values
- keep only the minimum technical context needed to prove the result
- use synthetic data only

See [docs/00-evidence-inventory.md](../../docs/00-evidence-inventory.md) and [SECURITY.md](../../SECURITY.md) for the full evidence-handling policy.
