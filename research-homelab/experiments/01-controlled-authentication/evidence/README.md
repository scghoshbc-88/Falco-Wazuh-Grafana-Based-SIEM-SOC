# Experiment 01 screenshot evidence

- `01-controlled-command-and-journal.png`: controlled logger test with run ID and local journal showing sudo PID 62218.
- `02-wazuh-authentication-alerts.png`: Wazuh alerts, including 5402, 5501, and 5502. These include events from separate sudo invocations.
- `03-wazuh-exact-run-id-match.png`: expanded Wazuh 5402 event showing the matching command, run ID, and sudo PID 62218.

The screenshots support command-level event traceability; they do not demonstrate causal provenance graph reconstruction. The browser address bar has been cropped and the agent private IP has been obscured in the detailed event screenshot. Review before publishing.
