# Security and Responsible Testing

MedSecure is an educational security lab and portfolio project.

## Authorised-use scope

Security testing for this repository must be limited to systems, accounts and data that the tester owns or has explicit permission to assess. Do not use the project against real patients, real organisations, university infrastructure outside the authorised lab, or any unauthorised network.

## Data handling

- Use synthetic patient and workforce data only.
- Do not commit `.env` files or production secrets.
- Do not commit Personal Access Tokens, Microsoft Entra client secrets, session cookies, private keys or database credentials.
- Do not publish screenshots containing student IDs, account addresses, tenant/device identifiers, MFA challenge details or password-manager content.
- Review and redact evidence before placing it in the public `screenshots/` tree.

Local raw assessment evidence should remain under the ignored `evidence/` directory until it has been reviewed.

## Development secrets

Environment-specific values belong in local environment variables or an approved secret-management system. CI test credentials are generated ephemerally for each workflow run.

## Reporting security issues

If a security issue is found in this educational repository, document:

1. affected component
2. preconditions
3. observed impact
4. safe reproduction steps in an authorised environment
5. remediation
6. re-test result

Do not include live credentials or sensitive user information in issue reports.

## Production note

The current project is not a production healthcare system. A production deployment would require additional security, privacy, availability, monitoring and compliance controls.
