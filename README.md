# MedSecure

MedSecure is a secure healthcare information management prototype demonstrating enterprise identity, role-based access control, audit logging, secure application development, and DevSecOps practices.

> Synthetic patient and workforce data only. No real patient information is stored.

## Features

- Microsoft Entra ID workforce authentication
- Role-Based Access Control (RBAC)
- Nurse, Doctor, Administrator, and Patient roles
- Patient record isolation
- Administrative least privilege
- Workforce directory and employee profiles
- Organisation, facility, and department management
- Security event and authentication logging
- CSRF protection
- Secure HTTP response headers
- Login rate limiting
- Secure session controls
- Automated security tests with Pytest

## Identity and Access Model

Workforce users authenticate primarily through Microsoft Entra ID.

Microsoft Entra application roles:
- `MedSecure.Nurse`
- `MedSecure.Doctor`
- `MedSecure.Admin`

Local workforce accounts are retained only for development, testing, and fallback purposes.

Patients use a separate patient portal identity and may access only the clinical record associated with their account.

## Role-Based Access Control

| Role | Patient Records | Clinical Notes | Organisation | Workforce | Security Logs |
|---|---|---|---|---|---|
| Patient | Own record only | No | No | No | No |
| Nurse | Authorised patient records | Yes | No | No | No |
| Doctor | Authorised patient records | Yes | No | No | No |
| Administrator | Restricted | No | Yes | Yes | Yes |

## Technology Stack

- Python
- Flask
- SQLAlchemy
- Microsoft Entra ID
- Pytest
- Bandit
- pip-audit
- Git / GitHub

## Security Testing

```bash
python -m pytest -v
bandit -r app.py
pip-audit
```

Planned authorised testing includes OWASP ZAP, Nikto, Nmap, and Kali Linux.

## Planned Enterprise Lab Integration

- Cisco Packet Tracer network architecture
- VLAN segmentation
- Routing and switching
- Windows Server Active Directory
- DNS and Group Policy
- Domain-joined endpoints
- Microsoft Entra ID
- Application and database servers
- Kali Linux security testing
- GitHub Actions CI/CD

## Environment Configuration


Example:

```env
SECRET_KEY=your-secret-key
ENTRA_CLIENT_ID=your-client-id
ENTRA_TENANT_ID=your-tenant-id
ENTRA_CLIENT_SECRET=your-client-secret
ENTRA_REDIRECT_URI=http://localhost:5000/auth/callback
```

## Disclaimer

MedSecure is an educational prototype and is not intended for production healthcare use.

All patient, workforce, clinical, and organisational information is synthetic.
