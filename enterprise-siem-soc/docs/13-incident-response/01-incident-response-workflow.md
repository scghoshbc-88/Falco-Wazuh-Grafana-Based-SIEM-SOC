# Part 13 — Incident Response Workflow

## 13.1 Workflow

```
Detection → Validation → Triage → Evidence Collection → Correlation
    → Scope → Containment → Remediation → Recovery → Lessons Learned
```

- **Detection**: alert arrives via the Notification Engine email, with severity,
  MITRE mapping, and an investigation checklist already attached.
- **Validation**: work the investigation checklist from the runbook before
  assuming the alert is a true positive — the checklist exists specifically to
  separate "detection" from "proof."
- **Triage**: assign severity/priority using the risk score in the email;
  cross-reference the Investigation Workspace dashboard (`docs/06-grafana` §6.4)
  for related activity on the same asset/user.
- **Evidence collection**: capture the specific Wazuh/Grafana/Loki queries used,
  not just a screenshot — queries are reusable, screenshots are not.
- **Correlation**: check the correlation table in `docs/07-network-security` §7.4
  and `docs/08-microsoft-security` §8.4 for adjacent signals across
  firewall/identity/endpoint sources.
- **Scope, Containment, Remediation, Recovery**: standard IR practice — driven by
  the runbook's response guidance (immediate / short-term / long-term) plus your
  organization's IR plan.
- **Lessons learned**: feed back into the rule catalogue, the runbook, or this
  documentation. A detection that produced a false positive should result in a
  rule tuning change, not a suppressed alert.

## 13.2 Case study template

Use this template for every investigated incident, sanitized, in
`examples/incidents/`:

```markdown
# Case NNN — <short title>

## Initial Alert
## Hypothesis
## Evidence
## Queries executed
## Errors encountered
## Endpoint investigation
## File activity findings
## Network evidence
## Conclusion
## False-positive considerations
## Detection improvements
## Lessons learned
```

The value of this template is specifically in capturing **detection vs. proof**
gaps — e.g., an alert indicating cloud-storage activity is not by itself proof a
specific file was uploaded; the case study should document what evidence would
have been needed to confirm or refute the hypothesis, and whether the detection
rule should be tightened as a result.

## 13.3 Escalation

Define, before go-live:
- Who receives `<SOC_DISTRIBUTION_MAILBOX>` and what their acknowledgement SLA is
  by severity (e.g., Critical: 15 minutes, High: 1 hour).
- Escalation path if the primary analyst doesn't acknowledge within SLA.
- Communication template for notifying leadership of a confirmed incident
  (severity, scope, containment status, next update time).
