# Part 0 — Project Overview

## What this platform is

A self-hosted SIEM/SOC stack built from open-source and existing enterprise tooling,
without a commercial SIEM license. It centralizes security telemetry from Windows
endpoints, Linux/Docker hosts, network firewalls/wireless controllers, and Microsoft
365/Entra ID, correlates it into rules, visualizes it in Grafana, and routes
high-fidelity alerts to a professional, MITRE ATT&CK-mapped notification email.

## What it is not

- Not a replacement for endpoint EDR — Defender for Endpoint still does the actual
  endpoint containment/remediation. Wazuh correlates and forwards its alerts.
- Not a full SOAR platform — the Notification Engine formats and routes alerts; it
  does not (yet) auto-remediate.
- Not multi-tenant — this design assumes a single organization's environment.

## Why this architecture

| Decision | Reason |
|---|---|
| Wazuh as the core SIEM | Free, agent-based, strong Windows/Linux telemetry, active rule ecosystem, good API |
| Grafana instead of the Wazuh dashboard for SOC use | One pane of glass across Wazuh + Loki (network syslog) + InfluxDB (ops metrics); Wazuh dashboard remains available for deep OpenSearch queries |
| Falco on the Docker **host**, not inside every container | One agent instead of N; catches container escape/breakout by design; simpler upgrade path |
| Custom Flask "Notification Engine" instead of Wazuh's native `maild` alone | Wazuh's native email is functional but not analyst-friendly; the engine adds severity/risk scoring, MITRE mapping, and a runbook-driven investigation checklist per alert type |
| 5-dashboard Grafana model instead of one dashboard per data source | Reduces duplicate panels, keeps analyst triage speed high, matches how an analyst actually investigates (overview → pivot into one of 4 specialist views) |

## Deployment phases (how this documentation is organized)

1. **Infrastructure foundation** — hosts, Docker, storage, backup (`docs/02`)
2. **Wazuh core** — manager, indexer, dashboard, agents, base rule set (`docs/03`)
3. **Windows endpoint depth** — Sysmon, FIM, USB telemetry, Defender ingestion,
   Intune-based agent rollout (`docs/04`)
4. **Linux/container runtime security** — Falco + Falcosidekick (`docs/05`)
5. **Visualization + alerting substrate** — Grafana, Loki, Promtail, InfluxDB,
   dashboard design (`docs/06`)
6. **Network telemetry** — Palo Alto firewall, UniFi wireless (`docs/07`)
7. **Cloud/identity telemetry** — Microsoft 365, Entra ID, Defender for Endpoint via
   Graph API (`docs/08`)
8. **SOC alerting framework** — the Notification Engine, MITRE mapping, runbooks
   (`docs/09`)
9. **Operational hardening** — troubleshooting reference, test catalogue, production
   scaling and change control (`docs/10`–`docs/12`)

Each phase produces a working, validated checkpoint before the next begins. Do not
skip ahead — most Part 09 (alerting) failures in the original lab build traced back
to schema mismatches introduced by skipping validation in an earlier phase.

## Roles this documentation assumes

- **Platform engineer**: builds Parts 02–08, owns the servers.
- **SOC analyst**: consumes Parts 06 (dashboards), 09 (alert format), 11 (test
  cases), 13 (incident response).
- **Security/IT leadership**: consumes this README, `docs/01-architecture`, and the
  status table above.
