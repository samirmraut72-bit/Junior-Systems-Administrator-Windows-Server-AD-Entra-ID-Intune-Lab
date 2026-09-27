# ICT932 Security Assessment Evidence

This document records the authorised security-testing and assurance work completed against the MedSecure educational prototype.

> **Scope and safety:** All testing was performed against systems and synthetic data that were explicitly authorised for the lab. No real patient data, production credentials, public targets, or unauthorised networks were used.

## Test environment

- **Target:** MedSecure Flask application hosted on an Ubuntu Server in the university eduLAB.
- **Testing host:** Kali Linux in the same authorised eduLAB network.
- **Application service:** Flask/Werkzeug development service on TCP 5000 during the lab.
- **Source control:** GitHub with a security-focused GitHub Actions workflow.
- **Data:** Synthetic patient and workforce records only.

## Security controls assessed

The assessment exercised the following controls and design features:

- patient-record isolation and least privilege
- role-based access control (RBAC)
- Zero Trust / attribute-based access control (ABAC)
- Microsoft Entra workforce identity checks
- CSRF protection
- password hashing
- HTTP security headers
- session restrictions
- login rate limiting
- security-event logging
- dependency and secret hygiene
- automated DevSecOps security gates

## Test and remediation register

| Area | Tool / technique | Initial result | Remediation / interpretation | Final result |
|---|---|---|---|---|
| Python SAST | Bandit | 2 Low findings: B110 `try_except_pass` | Silent rollback exceptions were replaced with explicit warning logging | 0 Low / 0 Medium / 0 High findings |
| Dependency scan | pip-audit | 8 known vulnerabilities reported in `setuptools 59.6.0` | Upgraded the lab environment to `setuptools 84.0.0`, then ran regression tests | No known vulnerabilities found in the final scan |
| Regression / control validation | pytest | 8 original tests passed | Added Zero Trust / ABAC tests | 11 tests passed |
| Dynamic web testing | OWASP ZAP | Automated requests reached the running application | Login rate limiting returned HTTP 429; this demonstrated a working defence but limited complete automated coverage of the login endpoint | Rate-limiter behaviour captured in server audit logs |
| Attack-surface discovery | Nmap + `ss` | TCP 21, 22, 80, 443 and 5000 were reachable in the lab | Service ownership was validated locally; Flask was confirmed on TCP 5000. Host-level services were not automatically attributed to MedSecure | Attack surface documented and scoped |
| FTP transport check | OpenSSL STARTTLS probe | FTPS handshake was not established on TCP 21 | Treated as a host/lab exposure, not a MedSecure application vulnerability | Recorded as residual host-level risk / configuration observation |
| Secrets scan | Gitleaks | Repository/history scan performed | No secret remediation required | No leaks found |
| Broken access control | Manual authorised test | Patient 1 attempted `/patient/2` | Ownership policy denied the request | HTTP 403 and security audit evidence |
| Login abuse | Manual incident simulation | Repeated invalid passwords | Rate limiter contained the activity after the configured threshold | HTTP 429, audit event, then successful legitimate login after recovery window |
| Injection | Manual SQLi login test | SQL injection-style username payload submitted | ORM-based lookup treated input as data; no authentication bypass was observed | Login rejected |
| Advanced feature | Zero Trust / ABAC policy engine | Existing route-specific controls were centralised and extended | Deny-by-default policy evaluates identity, role, account state, resource, sensitivity, action, HTTP method and ownership | Explainable `ZT_POLICY` allow/deny logs and 11 passing tests |
| DevSecOps | GitHub Actions | Manual security tools initially run locally | Added automated build/syntax check, Bandit, pytest, pip-audit, Gitleaks and a final security gate | Final workflow passed on `main` after the Zero Trust PR merge |

## OWASP-relevant web tests

### Broken Access Control

A logged-in patient was permitted to access the clinical record linked to that identity. Changing the URL to another patient identifier returned HTTP 403. The server-side audit trail recorded the policy decision and the blocked request.

### Authentication / automated login abuse

Repeated invalid login submissions produced failed-authentication events. Once the configured rate threshold was exceeded, MedSecure returned HTTP 429 and logged the containment event. After the rate-limit window expired, a legitimate login succeeded again.

### Injection

A SQL injection-style payload was submitted in the patient username field. The attempt did not bypass authentication and was recorded as a failed password-authentication event. This result applies only to the tested login path and is not a claim that every possible injection vector has been exhaustively tested.

## Zero Trust / ABAC advanced feature

The advanced feature is a central policy engine rather than a replacement for authentication. It evaluates protected requests using multiple subject, resource and context attributes.

Example attributes include:

- authenticated identity
- role
- workforce account status
- identity provider
- resource type
- resource sensitivity
- requested action
- HTTP method
- patient ownership

The policy is deny-by-default. Each decision is written to the security audit trail with the resource, action, sensitivity, decision reason, result and policy-evaluation latency. This makes the advanced control both demonstrable and measurable.

## Incident-response simulation

The incident scenario used repeated failed patient login attempts.

1. **Detection:** `PASSWORD_AUTH FAILED` events were logged.
2. **Response:** the rate limiter detected excessive login POST requests.
3. **Containment:** the application returned HTTP 429 and recorded `LOGIN_RATE_LIMIT BLOCKED`.
4. **Recovery:** after the configured window expired, normal authentication became available.
5. **Validation:** valid credentials successfully reached the dashboard.

## DevSecOps security pipeline

The GitHub Actions workflow runs on pushes and pull requests targeting `main`.

It performs:

1. repository checkout
2. ephemeral CI test-credential generation
3. Python setup
4. dependency installation
5. syntax/build validation
6. Bandit SAST
7. pytest security regression tests
8. pip-audit dependency scanning
9. Gitleaks history scan
10. final security gate

The CI workflow uses per-run generated test credentials instead of hard-coded reusable passwords in the repository.

## Final validation state

The final local validation recorded:

- Bandit: no issues identified
- pytest: 11 passed
- pip-audit: no known vulnerabilities found
- Gitleaks: no leaks found
- Zero Trust / ABAC feature: merged through Pull Request #1
- GitHub Actions: final security workflow passed on `main`

## Limitations and residual risk

This is an educational prototype, not a production healthcare deployment.

Important limitations include:

- the eduLAB application was intentionally exposed through the Flask development server on HTTP port 5000 for authorised testing
- the ZAP GUI was resource-intensive in the eduLAB Kali VM and did not provide exhaustive authenticated coverage
- the Nmap-discovered FTP, Apache and other host services belong to the lab host and should not automatically be described as MedSecure application services
- the manual SQL injection result covers the tested login path only
- Zero Trust / ABAC is a prototype application-layer policy engine rather than a full enterprise policy-decision platform
- a production deployment would require production TLS termination, managed secrets, centralised logging/SIEM, monitored backups, formal privacy/compliance review, broader DAST and operational hardening

## Evidence handling

Raw assessment screenshots are deliberately kept outside Git tracking until reviewed because browser/eduLAB captures may include student identifiers, account context, local environment details or other unnecessary metadata.

Before publishing evidence:

- crop or redact student IDs and account identifiers
- remove or obscure any real email addresses, tenant IDs, device IDs and MFA challenge details
- never publish Personal Access Tokens, client secrets, passwords, cookies or session tokens
- avoid showing password-manager prompts or stored credentials
- keep only the minimum context needed to prove the test result
- publish curated copies under a dedicated screenshot folder rather than the ignored local `evidence/` directory

Private RFC1918 lab addresses are not credentials, but they should still be shown only where they add technical value.
