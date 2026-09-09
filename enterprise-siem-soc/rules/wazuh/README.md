# Custom Wazuh Rule Catalogue

Validated custom detections built during the lab phase. Import these as your
starting baseline into `local_rules.xml` (Part 3.5) rather than rebuilding from
scratch. Always run `xmllint --noout` before restarting the manager, and back up
first — see `docs/10-troubleshooting/01-troubleshooting-reference.md` §10.3.

| Rule ID | Detection | Source | Severity | MITRE | Status |
|---|---|---|---|---|---|
| 100610 | Privileged local group activity | Windows Security (4732) | High | T1098 | Validated |
| 100620 | Suspicious process creation | Sysmon (Event ID 1) | High | T1059 | Validated |
| 100630 | Scheduled task created | Windows Security (4698) | High | T1053 | Validated |
| 100640 | Account lockout | Windows Security (4740) | Medium | — | Validated |
| 100650 | Security log cleared | Windows Security (1102) | Critical | T1070.001 | Validated |
| 100660 | Microsoft Defender malware detection | Windows (1116) | Critical | varies by detection | Validated |
| 100680 | Application shimming suppression (sdbinst.exe/PcaSvc) | Sysmon | — (suppression rule) | T1546.011 | Needs hardening — see note below |
| 100700 | SSH login success | Linux auth log | Info | — | Validated |
| 100701 | SSH login failure | Linux auth log | Medium | T1110 | Validated |
| 100702 | Multiple authentication failures (brute force), frequency=5, timeframe=120s | Linux auth log | High | T1110 | Validated |
| 100703 | SSH login from unusual source | Linux auth log | Medium | — | Validated |
| 110500 | USB removable-media telemetry (device attach / file copy / executable created) | Windows (Sysmon + FIM) | Info–High, tiered by sub-event | T1052.001 | Validated |
| 92203 | Executable created on USB | Windows | High | T1052.001 | Validated |
| 92205 | PowerShell dropped executable | Windows | High | T1059.001 | Validated |
| 92221 | Office macro execution | Windows | Medium | T1204.002 | Validated |

## Rule 100680 — known limitation

This suppression rule (targeting MITRE T1546.011, Application Shimming via
`sdbinst.exe`/`PcaSvc`) currently uses an **unanchored substring match** and relies
on PE metadata fields that an attacker could manipulate to evade the rule. Do not
treat this rule as a hard control — it reduces noise for a known benign pattern,
but should not be relied upon as the sole detection for this technique. Harden the
match (anchored regex, additional corroborating fields) before depending on it in
production.

## Adding a new rule

1. Draft the rule in a scratch file, validate with `xmllint --noout`.
2. Test against a sample log line with `wazuh-logtest` (Part 3.6) before adding to
   the live `local_rules.xml`.
3. Add the entry to this table (Rule ID, Detection, Source, Severity, MITRE,
   Status = "Testing" until validated in Part 11's test catalogue, then
   "Validated").
4. If the rule feeds a SOC alert email, create/update the corresponding runbook
   (`docs/09-alerting-framework` §9.3) and run the schema validator before go-live.
