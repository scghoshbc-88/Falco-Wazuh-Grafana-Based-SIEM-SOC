# Part 6 — Grafana, Loki, Promtail & SOC Dashboards

`STATUS: Production-safe`

## Prerequisites
- Wazuh Manager/Indexer reachable from Grafana.
- Loki/InfluxDB running per Part 2's `docker-compose.yml`.

## 6.1 Datasources

Add three Grafana datasources (`configs/grafana/datasources.yaml`):

1. **Wazuh Indexer (OpenSearch)** — primary SOC data source. Use a read-only API
   credential (Part 3.4), not the Wazuh admin account.
2. **Loki** — for Palo Alto/UniFi syslog (see Part 7).
3. **InfluxDB** — for operational/factory metrics unrelated to security, kept
   separate so a SOC dashboard never accidentally mixes non-security data into a
   security panel.

## 6.2 Promtail configuration

Promtail runs bare-metal on `<SIEM_MONITOR_HOST>` and tails the syslog files
written by rsyslog for Palo Alto and UniFi (configured in Part 7). Config:
`configs/promtail/promtail-config.yaml`. Key labels to apply at ingestion —
`source` (palo-alto / unifi), `log_type`, and `severity` if extractable — so Loki
queries in Grafana can filter cheaply.

```bash
sudo systemctl enable --now promtail
sudo journalctl -u promtail --since "5 minutes ago"
```

## 6.3 The 5-dashboard model

`STATUS: Production-safe` — this is a deliberate architecture decision (ADR-005),
not the default "one dashboard per data source" sprawl. Fewer dashboards, each with
a clear operational question, reduces duplicated panels and keeps analyst triage
fast.

| Dashboard | Operational question it answers |
|---|---|
| **SOC Overview** | What's the current alert volume/severity mix across the whole environment, right now? |
| **Endpoint Security** | What's happening on Windows/Linux endpoints (Sysmon, FIM, USB, Defender, privilege events)? |
| **Business Data Protection** | Is sensitive data moving somewhere it shouldn't (USB, cloud upload, SharePoint/OneDrive anomalies)? |
| **Network/Firewall Security** | What's the firewall/wireless layer telling us (threat logs, denied traffic, rogue APs)? |
| **Linux/Container Security** | What is Falco/the Docker host reporting? |

Each dashboard's panels use a **standardized alert-table schema** so an analyst
reading any of the five sees the same columns in the same order: Time, Severity,
Rule/Detection, Source, Affected Asset/User, MITRE Technique (if mapped).

Import the validated JSON exports from `dashboards/<name>/<name>.json` — do not
hand-build from scratch; adjust the datasource UID after import to match your
environment.

## 6.4 The Investigation Workspace

A sixth, purpose-built dashboard (not one of the five above) acts as the pivot
point for active investigations: templated variables for hostname/user/IP, and
panels that update to show all cross-source activity for the selected entity. This
is where an analyst goes *after* triaging on one of the five main dashboards.

## 6.5 Grafana Alerting

Alert rules live on top of the dashboards above (typically SOC Overview and
Endpoint Security carry the alert-rule-bearing panels). Standard labels used for
routing:

```
environment = lab | production
team        = soc
severity    = high | critical
notify      = email
```

Notification policy routing matchers must match these labels **exactly** —
mismatched label casing/spelling (e.g., `team=SOC` vs `team=soc`) is the single
most common cause of "alert fired but no notification" in this stack. See
`docs/10-troubleshooting/03-alert-not-delivered.md`.

Contact point: a webhook pointing at the SOC Notification Engine (Part 09), not
Grafana's built-in email — the Engine is what adds MITRE enrichment and the
investigation checklist.

```
Grafana → Alerting → Contact points → New → Webhook
URL: http://<SIEM_MONITOR_HOST>:8090/api/v1/grafana/alerts
```

Recommended timing values (validated in the lab build to avoid demo/production
"alert fired, email seemingly late" confusion):

```
Group wait:      10s
Group interval:  1m
Repeat interval: 4h
```

## Validation

```bash
curl -s http://localhost:3000/api/health
```

- Each of the 5 dashboards loads with live data (not "No data") for at least one
  panel per data source.
- Grafana → Alerting → Contact points → *Test* returns success for the
  Notification Engine webhook.
- A real (test) detection walks end-to-end: endpoint → Wazuh → Grafana panel →
  alert fires → webhook POST → email received. This full-chain test is
  TC-005/TC-006 in `docs/11-testing-validation`.
