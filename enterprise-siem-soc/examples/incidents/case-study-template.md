# Case 000 — Template (copy this for every real investigation)

## Initial Alert
_What arrived in the SOC mailbox: alert name, severity, MITRE mapping, timestamp._

## Hypothesis
_What you believe happened, based on the alert alone, before investigating._

## Evidence
_What you found — raw log excerpts (sanitized), screenshots, query results._

## Queries executed
_Copy the exact Wazuh/Loki/Grafana queries used — see `queries/README.md` for the
reusable baseline set._

## Errors encountered
_Any tooling/pipeline errors hit during the investigation itself — these are
useful signal for `docs/10-troubleshooting`._

## Endpoint investigation
_Findings from the affected endpoint(s): process trees, file activity, user
session context._

## File activity findings
_Specifically for data-movement investigations: what was actually touched/copied/
uploaded, distinct from what the alert merely suggested._

## Network evidence
_Firewall/wireless corroboration, if any (see `docs/07-network-security` §7.4
correlation table)._

## Conclusion
_True positive / false positive / benign-but-worth-tuning, and why._

## False-positive considerations
_What would have made this alert fire on entirely legitimate activity — is the
rule specific enough?_

## Detection improvements
_Concrete rule/runbook changes to propose, with the rule ID(s) affected._

## Lessons learned
_Anything that should change in this documentation as a result._
