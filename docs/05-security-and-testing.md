# Security and Testing

Security was treated as part of the application design rather than an extra page added at the end.

## Route-level RBAC

MedSecure uses a `roles_required()` decorator to protect role-specific routes.

When a user attempts to access a route outside their role, the application:

1. records an `UNAUTHORIZED_ACCESS` security event
2. marks the result as `BLOCKED`
3. returns HTTP 403

## Entra workforce checks

The workforce authentication path performs additional checks after Microsoft authentication:

- the token tenant ID must match the configured MedSecure tenant
- exactly one recognised MedSecure app role must be present
- the matching local workforce profile must exist
- the workforce profile must be active

Successful Entra authentication and role selection are also written to the security-event log.

## Web security controls

The application sets security-focused HTTP response headers including:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- Content Security Policy
- a restrictive Permissions Policy
- `Cache-Control: no-store, no-cache, must-revalidate`

Other controls include:

- CSRF protection
- HTTP-only session cookies
- SameSite session cookies
- password hashing
- login rate limiting
- 1 MB request-size limit
- 15-minute permanent-session lifetime

The local lab currently runs over HTTP, so `SESSION_COOKIE_SECURE` is disabled in development. It should be enabled behind HTTPS in production.

## Automated tests

`tests/test_security.py` verifies:

1. valid authentication
2. patient access to their own record
3. prevention of broken patient-to-patient access
4. admin least privilege
5. nurse clinical access
6. security-log access restrictions
7. security response headers
8. login brute-force rate limiting

Run the tests with:

```bash
python -m pytest -v
```

Additional local checks used for the project:

```bash
bandit -r app.py
pip-audit
```

## What I would add for production

This lab is intentionally small. A production healthcare application would also need:

- HTTPS everywhere
- production secrets management
- managed database and encrypted backups
- centralised logging/SIEM
- stronger monitoring and alerting
- formal identity lifecycle processes
- conditional-access design
- vulnerability management
- dependency and container/image scanning where applicable
- disaster recovery planning
- formal privacy, clinical safety and compliance review
