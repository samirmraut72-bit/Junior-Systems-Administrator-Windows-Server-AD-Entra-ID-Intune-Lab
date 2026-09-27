# Security and Testing

Security is integrated into MedSecure's design, implementation, testing and CI workflow rather than being treated as a final scanner-only step.

## Authentication and identity

Patient authentication uses local development credentials stored as password hashes. Workforce authentication is designed around Microsoft Entra ID.

The workforce authentication path validates:

- the configured tenant
- exactly one recognised MedSecure application role
- the corresponding application profile
- workforce account status

Production credentials and Entra secrets are not committed to the repository.

## RBAC and least privilege

MedSecure uses role-based access controls for role-specific functions.

Examples include:

- patients may access only the clinical record linked to their identity
- nurses and doctors may access authorised clinical workflow
- nurses cannot read the security-log administration page
- administrators are intentionally blocked from clinical patient records

Denied access is logged and returns HTTP 403.

## Zero Trust / ABAC advanced feature

The advanced security feature adds a central deny-by-default policy engine for protected resources.

The policy evaluates attributes such as:

- authenticated identity
- role
- workforce account status
- identity provider
- resource type
- resource sensitivity
- requested action
- HTTP method
- patient ownership

Policy decisions generate explainable `ZT_POLICY` audit events that include the resource, action, sensitivity, reason, result and evaluation latency.

This extends RBAC rather than replacing authentication. The same role can receive different decisions depending on resource, action and context.

## Web security controls

The application sets security-focused HTTP response headers including:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- Content Security Policy
- restrictive Permissions Policy
- `Cache-Control: no-store, no-cache, must-revalidate`

Other controls include:

- CSRF protection
- HTTP-only session cookies
- SameSite session cookies
- password hashing
- login rate limiting
- 1 MB request-size limit
- 15-minute permanent-session lifetime
- security-relevant HTTP error auditing

The local eduLAB test service intentionally used HTTP on Flask's development port. Production should terminate TLS through a production-grade web server or reverse proxy and enable secure-cookie handling.

## Automated security tests

`tests/test_security.py` currently validates 11 behaviours:

1. valid patient authentication
2. patient access to their own record
3. prevention of patient-to-patient broken access control
4. admin least privilege for clinical records
5. nurse clinical access
6. security-log access restrictions
7. security response headers
8. login brute-force rate limiting
9. Zero Trust patient write denial
10. Zero Trust nurse clinical-note write allowance
11. Zero Trust denial audit evidence

Run:

```bash
python -m pytest -v
```

## SAST - Bandit

Bandit scans the Python source code for insecure coding patterns.

Initial assessment result:

- 2 Low-severity B110 `try_except_pass` findings

Remediation:

- silent database rollback exceptions were replaced with explicit warning logging

Final re-test:

- no issues identified
- 0 Low / 0 Medium / 0 High findings

## Dependency scanning - pip-audit

The initial eduLAB environment reported:

- 8 known vulnerabilities
- affected package: `setuptools 59.6.0`

Remediation:

- upgraded the environment to `setuptools 84.0.0`
- ran the security regression suite to validate application behaviour

Final re-test:

- no known vulnerabilities found

## Dynamic testing - OWASP ZAP

OWASP ZAP was used against the running MedSecure instance in the authorised eduLAB.

During active testing, repeated login POST requests triggered the application's rate limiter and returned HTTP 429. The application audit trail recorded the blocked activity.

This result is interpreted in two ways:

- positive: the rate limiter actively contained high-rate login traffic
- limitation: the defensive control reduced automated coverage of the protected login endpoint

The eduLAB Kali VM was also resource constrained, so the ZAP GUI was not treated as exhaustive authenticated coverage.

## Attack-surface discovery - Nmap

Nmap identified reachable services on the Ubuntu lab host, including TCP 21, 22, 80, 443 and 5000.

Local `ss` validation was used to identify service ownership. Flask was confirmed listening on TCP 5000 using `0.0.0.0` during the lab so the Kali VM could reach the application.

Important interpretation:

- an open port is an exposed service, not automatically a confirmed vulnerability
- `0.0.0.0` is a local bind address, not a claim of internet-wide reachability
- FTP/Apache/other host services discovered on the lab image should not automatically be attributed to MedSecure

An OpenSSL STARTTLS probe did not establish FTPS on TCP 21. This was recorded as a host/lab configuration observation rather than a MedSecure application vulnerability.

## Secrets scanning - Gitleaks

Gitleaks scanned repository history and reported:

- no leaks found

Local secret-bearing files such as `.env` are excluded from Git tracking.

Raw assessment evidence is also ignored until manually reviewed and redacted.

## Manual OWASP-relevant tests

### Broken Access Control

A patient account could access its own record. Changing the URL to another patient's identifier returned HTTP 403 and produced a security audit event.

### Authentication / login abuse

Repeated invalid login attempts produced `PASSWORD_AUTH FAILED` events. Once the configured threshold was exceeded, the application returned HTTP 429 and logged the rate-limit containment event.

After the configured window expired, valid credentials successfully authenticated again.

### Injection

A SQL injection-style payload was submitted to the login username field. No authentication bypass was observed and the request was logged as a failed authentication attempt.

This result applies to the tested login path only and is not an exhaustive claim covering every possible injection vector.

## Incident-response simulation

The repeated-login scenario was used as a simple incident-response workflow:

1. detection - failed authentication events
2. response - rate limiter evaluates repeated requests
3. containment - HTTP 429 and blocked audit event
4. recovery - rate-limit window expires
5. validation - legitimate login succeeds

## DevSecOps pipeline

GitHub Actions runs on pushes and pull requests targeting `main`.

The workflow performs:

- ephemeral CI credential generation
- Python setup
- dependency installation
- syntax/build validation
- Bandit
- pytest
- pip-audit
- Gitleaks
- final security gate

The CI workflow does not store reusable demo passwords in the repository. Per-run test credentials are generated and exported only to the workflow environment.

## Final validation

The final assessment validation recorded:

- Bandit: no issues identified
- pytest: 11 passed
- pip-audit: no known vulnerabilities found
- Gitleaks: no leaks found
- Zero Trust / ABAC: merged through Pull Request #1
- GitHub Actions: final security workflow passed on `main`

For the complete testing/remediation register, see [07-ict932-security-assessment.md](07-ict932-security-assessment.md).

## Production improvements

A production healthcare application would require additional controls, including:

- HTTPS everywhere with a production-grade WSGI/reverse-proxy deployment
- managed secrets and key rotation
- managed database and encrypted backups
- centralised logging/SIEM
- monitored alerting and escalation
- formal identity lifecycle and conditional-access design
- broader authenticated DAST
- vulnerability-management processes
- disaster recovery
- formal privacy, clinical safety and compliance review
