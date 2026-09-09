# Contributing / Maintaining this Documentation

- **New detection rule:** add it to `rules/wazuh/README.md`, include the rule
  fragment in `rules/wazuh/`, and if it should reach an analyst mailbox, add a
  matching runbook under `configs/notification-engine/runbooks/` and run
  `scripts/bash/validate-runbooks.py` before merging.
- **New dashboard/panel:** export the JSON into `dashboards/<name>/`, update its
  panel-catalogue README, and confirm the standardized alert-table schema
  (`dashboards/README.md`) if it's an alert-table panel.
- **New troubleshooting entry:** append to
  `docs/10-troubleshooting/01-troubleshooting-reference.md` using the Symptom →
  Likely cause → Diagnostic → Fix format — do not just describe the fix, capture
  the diagnostic path that got there.
- **New test case:** append to `docs/11-testing-validation/01-test-case-catalogue.md`
  using the full template (Objective, Prerequisites, Procedure, Expected
  endpoint/rule/Grafana/email/severity, Cleanup, Result).
- **Any production-impacting change:** log it in `CHANGELOG.md` before making it,
  not after.
- **Sanitization:** before committing, confirm no real IP addresses, tenant IDs,
  client secrets, or credentials are present — use the placeholders in
  `docs/01-architecture/03-naming-and-placeholders.md`.
