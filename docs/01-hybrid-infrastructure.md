# Hybrid Infrastructure

This part of the project started with a small Windows domain and then extended it into Microsoft cloud identity.

## On-premises lab

The lab uses:

- `MS-DC01` — Windows Server 2022 domain controller
- `CLIENT-WORKSTAT` — Windows 11 client
- Active Directory domain — `medsecure.local`
- Active Directory Domain Services
- DNS
- Group Policy

The client and server were placed on the same lab LAN. The domain controller uses a fixed address so the client can reliably locate domain services.

![Domain controller network](../screenshots/01-architecture/02-domain-controller-network.jpg)

## Active Directory structure

I created a `MEDSECURE` OU structure to keep users, groups, servers and workstations separate instead of leaving everything in the default AD containers.

![Active Directory domain](../screenshots/02-windows-server-ad/01-active-directory-domain.jpg)

Workforce accounts were created in Active Directory and later aligned with their Microsoft Entra identities.

Examples from the lab:

![Sarah AD account](../screenshots/02-windows-server-ad/02-sarah-williams-account.jpg)

![Daniel AD account](../screenshots/02-windows-server-ad/03-daniel-doctor-account.jpg)

## DNS

The domain controller also provides DNS for the `medsecure.local` environment.

![DNS server zones](../screenshots/02-windows-server-ad/04-dns-server-zones.jpg)

## Group Policy

Group Policy was used to apply workstation/user controls and later to trigger Intune automatic MDM enrollment.

![Group Policy structure](../screenshots/03-domain-client-gpo/01-group-policy-domain-structure.jpg)

One of the security policies restricts Command Prompt access for the targeted user scope.

![GPO security settings](../screenshots/03-domain-client-gpo/02-gpo-security-policy-settings.jpg)

The user restriction GPO is linked to the MedSecure users OU.

![User restriction GPO link](../screenshots/03-domain-client-gpo/03-gpo-user-restrictions-link.jpg)

## Entra Connect

Microsoft Entra Connect synchronises the on-premises directory with Microsoft Entra ID.

![Entra Connect settings](../screenshots/05-hybrid-identity/01-entra-connect-synchronization-settings.jpg)

The Synchronization Service Manager was used to confirm successful directory synchronisation operations.

![Entra Connect sync](../screenshots/05-hybrid-identity/02-entra-connect-sync-success.jpg)

## Hybrid join

After the identity synchronisation and device configuration were in place, the Windows client appeared in Microsoft Entra.

![Entra devices](../screenshots/05-hybrid-identity/03-entra-device-directory.jpg)

I then verified the Windows device state locally with `dsregcmd /status`.

![Hybrid join verification](../screenshots/05-hybrid-identity/04-dsregcmd-hybrid-join-status.jpg)

The important result was that the client was both domain joined and Azure/Entra joined, which is the hybrid state I wanted for the lab.
