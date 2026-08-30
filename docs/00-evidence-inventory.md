# Evidence Inventory

I reviewed the screenshot archive before preparing the public portfolio set.

## Source archive

The uploaded archive contained **26 screenshots across 7 folders**:

- `01-architecture`
- `02-windows-server-ad`
- `03-domain-client-gpo`
- `04-entra-id`
- `05-hybrid-identity`
- `06-intune`
- `07-medsecure-login`

The folders `08-role-dashboards`, `09-security-audit`, and `10-testing` were not present in the uploaded ZIP, so I did not invent evidence for them.

## Cleanup performed before publishing

- Normalised screenshot numbering and filenames.
- Renamed the client screenshot from `domain-client-identity-network` to `domain-client-network` because the image shows IP configuration, not identity.
- Moved the screenshot originally called `02-ou-structure` into the Group Policy section because it actually shows the `GPO-User-Restrictions` link.
- Renamed the DNS screenshot to `dns-server-zones` to match what is visible.
- Fixed duplicate numbering in the MedSecure login folder.
- Removed the Microsoft account-picker screenshot from the public set because it exposed more account information than the portfolio needed.
- Cropped `dsregcmd /status` to show Hybrid Join state while removing device-specific IDs.
- Cropped Intune device evidence so the focus is management/compliance rather than user-identifying fields.
- Cropped the Intune remote Sync evidence to remove serial/device-specific information.
- Redacted MFA challenge numbers and account addresses.
- Kept the already-blurred Entra Application ID/Object ID fields redacted.

## Final evidence structure

```text
screenshots/
├── 01-architecture/
│   ├── 01-domain-client-network.jpg
│   └── 02-domain-controller-network.jpg
├── 02-windows-server-ad/
│   ├── 01-active-directory-domain.jpg
│   ├── 02-sarah-williams-account.jpg
│   ├── 03-daniel-doctor-account.jpg
│   └── 04-dns-server-zones.jpg
├── 03-domain-client-gpo/
│   ├── 01-group-policy-domain-structure.jpg
│   ├── 02-gpo-security-policy-settings.jpg
│   └── 03-gpo-user-restrictions-link.jpg
├── 04-entra-id/
│   ├── 01-entra-users-directory.jpg
│   ├── 02-medsecure-enterprise-application.jpg
│   ├── 03-medsecure-app-roles.jpg
│   ├── 04-medsecure-role-assignments.jpg
│   └── 05-medsecure-authentication-config.jpg
├── 05-hybrid-identity/
│   ├── 01-entra-connect-synchronization-settings.jpg
│   ├── 02-entra-connect-sync-success.jpg
│   ├── 03-entra-device-directory.jpg
│   └── 04-dsregcmd-hybrid-join-status.jpg
├── 06-intune/
│   ├── 01-intune-admin-overview.jpg
│   ├── 02-intune-managed-device-overview.jpg
│   ├── 03-intune-remote-sync.jpg
│   └── 04-intune-display-policy-succeeded.jpg
└── 07-medsecure-login/
    ├── 01-medsecure-login-page.jpg
    ├── 02-doctor-mfa-desktop-and-mobile-redacted.jpg
    └── 03-nurse-dashboard-sso-success.jpg
```

All clinical and workforce records shown in this lab are synthetic.
