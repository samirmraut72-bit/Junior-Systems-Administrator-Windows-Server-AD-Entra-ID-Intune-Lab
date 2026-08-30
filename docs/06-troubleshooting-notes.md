# Troubleshooting Notes

This page is intentionally written as a build log rather than a polished architecture description. These were the problems that taught me the most.

## 1. Windows edition and domain join

The client initially did not have the Windows edition required for the domain-join workflow I wanted to test.

I moved the lab client to Windows 11 Pro and then completed the `medsecure.local` domain join.

**Lesson:** check operating-system capability before spending time troubleshooting the server.

## 2. DNS and client/domain communication

The Windows client needed to use the domain controller correctly for domain DNS.

I tested the client/server addressing and domain connectivity while building the environment.

**Lesson:** Active Directory troubleshooting often starts with DNS, not with Active Directory itself.

## 3. Group Policy and OU placement

One of the early GPO exercises did not apply as expected because the target objects and GPO links were not aligned correctly.

Later, the same design issue appeared again while configuring Intune auto-enrollment.

The important discovery was that `CLIENT-WORKSTAT` was still located in the default AD `Computers` container while my enrollment GPO was linked under:

```text
MEDSECURE
└── COMPUTERS
    └── Workstations
```

I moved the workstation into the intended OU structure, refreshed Group Policy and then verified that the Windows `EnterpriseMgmt` tasks were created.

**Lesson:** a GPO can be perfectly configured and still do nothing if the object is outside its scope.

## 4. Entra Connect

I worked through Entra Connect configuration and synchronisation until I could verify successful sync operations and matching workforce identities in Microsoft Entra.

**Lesson:** I found it easier to troubleshoot hybrid identity one layer at a time: AD identity, sync, Entra identity, device state, then application identity.

## 5. Hybrid join

`dsregcmd /status` became one of the most useful checks in this lab.

The final device state showed both:

```text
AzureAdJoined : YES
DomainJoined  : YES
```

That confirmed the client was in the hybrid state I was aiming for.

## 6. Intune enrollment: GPO was working, enrollment still failed

After fixing the OU placement, the `EnterpriseMgmt` task existed. This was an important clue because it proved the MDM auto-enrollment GPO was reaching the device.

The next enrollment attempt still did not put the device in Intune.

I checked:

- hybrid join
- Entra PRT
- MDM discovery URL
- MDM user scope
- scheduled enrollment task

The task result led me toward licensing.

## 7. Intune user licensing and usage location

The workstation was originally being tested with an administrator account that did not have the Intune entitlement needed for user-credential enrollment.

I switched the test to a synced workforce account. License assignment then failed because the account did not yet have a valid usage location.

I set the cloud usage location to Australia, assigned Microsoft Intune Plan 1, signed into the workstation using the synced workforce identity and retried enrollment.

The device then appeared in Intune.

**Lesson:** successful hybrid join does not automatically mean successful MDM enrollment. Device identity, user identity, MDM scope and licensing all have to line up.

## 8. Proving Intune management

After enrollment, I did not want to stop at “the device appears in the portal.”

I:

1. triggered an Intune remote Sync
2. created `MedSecure - Display Control`
3. assigned it to the managed device scope
4. synchronised the endpoint
5. verified the profile reported `Succeeded: 1`

That gave me a simple end-to-end proof of management.

## 9. Entra app-role testing

While changing MedSecure application-role assignments, an existing browser session still contained an older token and therefore did not show the updated role claim.

A fresh authentication session returned the expected role.

**Lesson:** identity troubleshooting should always consider token/session caching before assuming the directory configuration is wrong.

## Final takeaway

The biggest lesson from this project was that infrastructure problems rarely stay inside one product.

A problem that looks like “Intune is broken” can actually be an AD OU issue, a GPO-scope issue, an Entra identity issue or a licensing issue. Working through the layers in order was much faster than repeatedly changing settings at random.
