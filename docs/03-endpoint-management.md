# Intune Endpoint Management

The Intune section became one of the most useful parts of this lab because it forced me to connect Active Directory OU design, Group Policy, Entra identity, licensing and Windows MDM enrollment.

## Enrollment path

The final path was:

```text
CLIENT-WORKSTAT
    ↓
Active Directory Workstations OU
    ↓
Intune auto-enrollment GPO
    ↓
Microsoft Entra hybrid join
    ↓
Licensed Entra workforce user
    ↓
Windows EnterpriseMgmt enrollment
    ↓
Microsoft Intune
```

## Intune tenant

![Intune overview](../screenshots/06-intune/01-intune-admin-overview.jpg)

## Managed Windows client

After resolving the enrollment issues, `CLIENT-WORKSTAT` appeared in Intune as a corporate Windows endpoint.

![Managed device](../screenshots/06-intune/02-intune-managed-device-overview.jpg)

The published screenshot is cropped so that the evidence focuses on device management state rather than user-identifying fields.

## Remote sync

I used the Intune **Sync** action to trigger an immediate device check-in.

![Remote sync](../screenshots/06-intune/03-intune-remote-sync.jpg)

## Configuration profile

To prove that the device was not only enrolled but actually receiving configuration, I created a small Windows settings profile named:

`MedSecure - Display Control`

The profile was assigned to all enrolled devices in the lab. Because this tenant had one managed Windows client, the result was easy to verify.

![Policy success](../screenshots/06-intune/04-intune-display-policy-succeeded.jpg)

The final result showed:

- Succeeded: 1
- Error: 0
- Conflict: 0
- Not applicable: 0
- In progress: 0

That was the point where I considered the Intune portion of the lab complete.
