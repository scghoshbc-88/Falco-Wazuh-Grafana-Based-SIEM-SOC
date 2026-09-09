# Architecture Decision Records

Each ADR: Context, Problem, Options considered, Decision, Reason, Consequences.

## ADR-001 — Use Wazuh as the primary SIEM
**Context:** need a SIEM without a commercial license, with strong Windows/Linux
agent telemetry.
**Decision:** Wazuh Manager + Indexer + Dashboard.
**Reason:** free, active rule ecosystem, good REST API for integration into
Grafana, agent-based (works equally on endpoints and servers).
**Consequences:** takes on the operational burden of running/scaling OpenSearch
ourselves (see `docs/12-production-scaling`).

## ADR-002 — Use Grafana for SOC visualization, not the native Wazuh dashboard
**Decision:** Grafana as the analyst-facing tool; Wazuh Dashboard reserved for deep
OpenSearch forensics.
**Reason:** one pane of glass across Wazuh + Loki (network syslog) + InfluxDB
(ops metrics); richer alerting/notification integration.
**Consequences:** two UIs to maintain; mitigated by keeping Wazuh Dashboard use
to specialist/forensic queries only.

## ADR-003 — Use Loki for network syslog (Palo Alto/UniFi) rather than ingesting into Wazuh directly
**Decision:** Promtail → Loki → Grafana for firewall/wireless syslog, filtered at
source.
**Reason:** avoids overloading the Wazuh Indexer with high-volume network log
data that isn't agent-based telemetry; keeps Wazuh focused on endpoint/host
correlation.
**Consequences:** two log stores to query when correlating; addressed via the
Investigation Workspace dashboard's cross-datasource panels.

## ADR-004 — Run Falco on the Docker host, not inside every container
**Decision:** single host-level Falco instance with eBPF/kernel-module visibility.
**Reason:** one agent to install/upgrade instead of N; catches container-escape
patterns by design (an in-container agent can't observe its own container
escaping).
**Consequences:** Falco requires host-level kernel access — document this as a
security exception during infrastructure hardening reviews.

## ADR-005 — Consolidate to a 5-dashboard SOC model
**Decision:** SOC Overview, Endpoint Security, Business Data Protection,
Network/Firewall Security, Linux/Container Security — plus one Investigation
Workspace, not a dashboard-per-data-source sprawl.
**Reason:** fewer dashboards with stronger operational purpose, standardized
alert-table schema, faster analyst triage.
**Consequences:** some data sources share a dashboard rather than getting their
own; addressed with clear panel grouping within each dashboard.

## ADR-006 — Separate Wazuh native alerting from Grafana/Notification-Engine alerting
**Decision:** disable Wazuh's native `<email_notification>`; the Notification
Engine is the single outbound alert-email path.
**Reason:** running both produced duplicate, inconsistently formatted alerts in
testing.
**Consequences:** Wazuh's `<email_alerts>` config block is kept (not removed) so
it can be quickly re-enabled for diagnosis without reconstruction.

## ADR-007 — Use Intune for endpoint agent rollout at production scale
**Decision:** package the Wazuh agent + Sysmon + baseline config as an Intune
Win32 app, staged rollout via pilot device group.
**Reason:** manual per-device installation does not scale to a company-wide
fleet; Intune gives detection rules and reporting for install success/failure.
**Consequences:** requires careful assignment-group scoping discipline (Part 4.7)
to avoid a fleet-wide incident from a bad package.

## ADR-008 — Build a dedicated business-data-protection detection layer
**Decision:** treat USB exfiltration, cloud-storage uploads, and
SharePoint/OneDrive anomalies as a distinct detection category rather than
folding them into generic endpoint monitoring.
**Reason:** these detections need a different investigative posture (proving data
movement, not just detecting an event) and a different dashboard audience
(data-protection/compliance stakeholders, not just SOC analysts).
**Consequences:** a dedicated runbook set and dashboard (`docs/06-grafana` — the
Business Data Protection dashboard).
