# Part 4 — Windows Endpoint Telemetry

`STATUS: Requires change control` for anything touching production Intune
assignment groups — see 4.5.

## Prerequisites
- Part 3 complete; Wazuh Manager reachable from the endpoint subnet on 1514/1515.
- Local admin (for manual install) or Intune access (for fleet rollout).

## 4.1 Wazuh agent (Windows)

```powershell
# Manual/pilot install
Invoke-WebRequest -Uri https://packages.wazuh.com/4.x/windows/wazuh-agent-4.9.0-1.msi -OutFile $env:tmp\wazuh-agent.msi
msiexec.exe /i $env:tmp\wazuh-agent.msi /q WAZUH_MANAGER='<WAZUH_MANAGER_IP>' WAZUH_REGISTRATION_SERVER='<WAZUH_MANAGER_IP>'
NET START WazuhSvc
```

## 4.2 Sysmon

Install Sysmon with a curated config (`configs/sysmon/sysmonconfig.xml`) tuned for
SOC use: process creation, network connection, file create (targeted directories
only — not the whole disk; see 4.4), registry, and PowerShell-adjacent events.

```powershell
sysmon64.exe -accepteula -i configs\sysmon\sysmonconfig.xml
```

Point Wazuh's Windows Event Channel collection at `Microsoft-Windows-Sysmon/Operational`
in `ossec.conf` (agent-side `<localfile>` block) or centrally via a **shared agent
group configuration** on the manager — the latter is what you want at production
scale so every endpoint gets the same config from one place.

## 4.3 Windows Security auditing

Enable, at minimum, via Group Policy (production) or `auditpol` (pilot):

```powershell
auditpol /set /subcategory:"Logon" /success:enable /failure:enable
auditpol /set /subcategory:"Special Logon" /success:enable
auditpol /set /subcategory:"Security Group Management" /success:enable
auditpol /set /subcategory:"User Account Management" /success:enable
auditpol /set /subcategory:"Removable Storage" /success:enable /failure:enable
auditpol /set /subcategory:"Audit Policy Change" /success:enable
```

Key event IDs the rule set relies on: **4698** (scheduled task created), **4740**
(account lockout), **1102** (security log cleared), **4720/4732** (privileged group
membership change).

## 4.4 File Integrity Monitoring (FIM)

`STATUS: Requires change control in production` — an overly broad FIM scope
degraded agent stability in the lab build (a whole-drive `<directories>` block).

```xml
<!-- agent-side ossec.conf, or shared group config -->
<syscheck>
  <directories check_all="yes" realtime="yes">C:\Users\%USERNAME%\Downloads</directories>
  <directories check_all="yes" realtime="yes">C:\Windows\System32\drivers\etc</directories>
  <directories check_all="yes" realtime="no">C:\Program Files</directories>
</syscheck>
```

Rules of thumb learned in the lab: scope FIM to directories that matter for
detection (Downloads, startup folders, driver/host-file paths), use `realtime`
sparingly, and never monitor an entire drive letter recursively on a
production-scale fleet — it caused agent instability once telemetry volume
increased.

## 4.5 USB / removable-media telemetry

Three distinct, separately-ruled events (do not conflate them):

1. **USB device attached** — Sysmon Event ID 6416 / registry-based detection.
2. **File copied to removable media** — FIM on removable-drive paths, or Sysmon
   file-create events scoped to detected removable volumes.
3. **Executable created on removable media** — highest-severity variant; this is
   the one mapped to MITRE **T1052.001 — Exfiltration Over Physical Medium** in the
   rule catalogue (`rules/wazuh/README.md`, rule 110500 family).

## 4.6 Microsoft Defender integration

Forward Defender detections (Event ID 1116) into the same Wazuh event channel
collection as Sysmon; the manager-side rule maps this to a Critical-severity SOC
alert regardless of source overlap with other telemetry.

## 4.7 Fleet rollout via Intune (production scale)

`STATUS: Requires change control` — this is the step most likely to cause a
fleet-wide incident if scoped incorrectly.

1. Package the Wazuh agent + Sysmon + baseline config as a Win32 app (`.intunewin`).
2. Set the install command to run silently with the manager IP/registration
   parameters as install-time arguments (not hardcoded per device).
3. Add a detection rule (registry key or service existence) so Intune can confirm
   success.
4. **Assign to a dedicated pilot device group first** — never assign directly to
   "All Devices" or a broad production group.
5. Validate on the pilot group (agent shows Active in Wazuh, Sysmon events flowing,
   FIM baseline established) before expanding the assignment.
6. Expand in waves (e.g., 10% → 50% → 100%) with a rollback plan (uninstall command)
   ready at each wave.

> Never assign the onboarding application to broad production user/device groups
> until validation has completed on a dedicated test group. This came directly
> from a careful, deliberately staged onboarding process — skipping the pilot wave
> is the single riskiest shortcut available in this part of the build.

## Validation

- `sudo /var/ossec/bin/agent_control -i <agent_id>` shows Sysmon and FIM events
  flowing for a pilot device.
- Trigger each USB test case (`docs/11-testing-validation`, TC-005/TC-006) and
  confirm the expected Wazuh rule fires with the correct severity.
- Confirm Defender detections land as Wazuh alerts within one manager evaluation
  cycle of a (safe, test) detection event.
