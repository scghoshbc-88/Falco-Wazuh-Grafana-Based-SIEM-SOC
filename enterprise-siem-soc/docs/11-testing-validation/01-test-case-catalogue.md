# Part 11 — Test Case Catalogue

Every test case follows the same template: Objective, Prerequisites, Procedure,
Expected endpoint event, Expected Wazuh rule, Expected Grafana result, Expected
email, Expected severity, Cleanup, Result. Run the full catalogue after any change
to rules, dashboards, or the Notification Engine, and again after every production
wave expansion (Part 4.7).

| ID | Test | Validates |
|---|---|---|
| TC-001 | Defender malware detection (safe EICAR test file) | Defender → Wazuh → Grafana → email, end to end |
| TC-002 | Account lockout (deliberate bad-password lockout on a test account) | Rule 100640, Event 4740 |
| TC-003 | Security log cleared | Rule 100650, Event 1102, Critical severity path |
| TC-004 | Scheduled task created | Rule 100630, Event 4698 |
| TC-005 | USB device insertion | USB telemetry pipeline, device-attached detection |
| TC-006 | Executable created on removable media | Rule 110500 family, MITRE T1052.001, full alert-to-email chain |
| TC-007 | PowerShell-dropped executable | PowerShell/process-creation correlation |
| TC-008 | SSH login (success + failure) | Rule 100700–100703 family |
| TC-009 | Falco: shell spawned in a monitored container | Falco → Falcosidekick → Wazuh |
| TC-010 | UniFi device offline | Loki/Promtail ingestion, Network Security dashboard |
| TC-011 | Palo Alto denied traffic | Filtered log forwarding, Network Security dashboard |
| TC-012 | Grafana alert → Notification Engine → email (synthetic test) | Webhook reachability only — **not sufficient alone**, always pair with TC-006 or another real-event test |

## Example: TC-006 (full detail)

**Objective:** confirm a real USB exfiltration-pattern event flows end-to-end into
an analyst email with correct MITRE enrichment.

**Prerequisites:** Parts 3, 4, 6, and 9 complete; validated runbook for the
`usb_large_copy` profile (schema per Part 09 §9.3).

**Procedure:**
1. On a test Windows endpoint, insert a USB drive and create a `.exe` file on it
   (e.g., copy `notepad.exe` to the drive).
2. Watch the Notification Engine log in real time:
   `sudo journalctl -u soc-notification-engine -f`
3. Wait one Grafana alert-rule evaluation cycle (default 1 minute).

**Expected endpoint event:** Sysmon file-create event on a removable-media path.

**Expected Wazuh rule:** 110500-family, severity High.

**Expected Grafana result:** the corresponding alert rule transitions
Normal → Alerting within the evaluation window.

**Expected email:** MITRE tactic "Exfiltration", technique "T1052.001 —
Exfiltration Over Physical Medium", the USB-specific investigation checklist, and
no "Not mapped" placeholders.

**Expected severity:** High.

**Cleanup:** remove the test executable from the USB drive; document the run in
`examples/incidents/` if this run surfaced anything worth keeping as a case study.

**Result:** record PASS/FAIL with a timestamp and, if FAIL, a link to the relevant
troubleshooting entry (`docs/10-troubleshooting`).

## Running the full catalogue

Track results in a simple table per run (date, tester, environment — lab vs.
production pilot):

```
| Test  | Run date   | Environment | Result | Notes                    |
|-------|------------|-------------|--------|---------------------------|
| TC-001| 2026-08-18 | lab         | PASS   |                           |
| TC-006| 2026-08-18 | lab         | PASS   | MITRE T1052.001 confirmed |
```

Any production wave expansion (Part 4.7) should re-run at minimum TC-001, TC-005,
TC-006, and TC-012 against the newly onboarded devices before widening further.
