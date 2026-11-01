# Experiment 01 — Screenshot evidence

**Experiment:** Controlled sudo authentication event, October 31, 2026.  
**Branch:** `research-homelab`.  
**Status:** Image files pending upload. Do not treat this directory as containing published screenshot evidence until the PNG files are present.

Expected sanitized images:

1. `01-controlled-command-and-journal.png` — Machine B terminal: unique run ID `SOCEXP01-20261031-235541`, sudo execution and local journal records.
2. `02-wazuh-authentication-alerts.png` — Wazuh Threat Hunting showing sudo/PAM rules 5402, 5501 and 5502 for Machine B.
3. `03-wazuh-exact-run-id-match.png` — Expanded Wazuh rule 5402 with the logger command, run ID and `sudo[62218]` process identifier.

**Evidence interpretation:** The source journal and Wazuh alert match at command and process-ID level for the controlled logger test. This supports SIEM event traceability, not a complete causal provenance graph.

**Privacy:** Publish only reviewed sanitized images. Remove private addresses, browser URLs, credentials and unrelated identifiers. Keep originals privately. No employer telemetry belongs in this research folder.
