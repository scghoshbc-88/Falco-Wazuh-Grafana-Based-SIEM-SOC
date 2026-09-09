# Part 1 — Architecture

## 1.1 Logical data flow

```
Windows Endpoints                Linux/Docker Hosts             Network Devices
 - Sysmon                         - auditd                       - Palo Alto (syslog)
 - Security/Application logs      - Docker runtime                - UniFi (CEF syslog)
 - Wazuh FIM                      - Falco → Falcosidekick
 - USB/removable media
 - PowerShell script block log
        │                                │                              │
        │ Wazuh agent (TCP 1514/1515)    │ Wazuh agent                  │ Syslog (UDP/TCP 514)
        ▼                                ▼                              ▼
                              ┌────────────────────┐            ┌────────────────┐
                              │   WAZUH MANAGER     │            │   PROMTAIL     │
                              │ decoders/rules/     │            │ (log shipper)  │
                              │ correlation engine  │            └───────┬────────┘
                              └────────┬───────────┘                    ▼
                                       │                            ┌───────┐
                     ┌─────────────────┼─────────────┐              │ LOKI  │
                     ▼                 ▼             │              └───┬───┘
              Wazuh Indexer       Wazuh API           │                  │
              (OpenSearch)        (REST, JSON)        │                  │
                     │                 │              │                  │
                     └────────┬────────┘              │                  │
                              ▼                        │                  │
                          GRAFANA  ◄─────────────────────────────────────┘
                     (Wazuh-Indexer datasource,
                      Loki datasource, InfluxDB
                      datasource for ops metrics)
                              │
                              ▼
                     SOC Dashboards (5)
                              │
                              ▼
                  Grafana Alert Rules → Contact Point
                              │
                              ▼  HTTP webhook (POST)
                  SOC NOTIFICATION ENGINE (Flask, systemd)
                   - looks up alert profile → runbook (JSON)
                   - enriches with MITRE ATT&CK tactic/technique
                   - renders HTML email (Jinja2)
                   - sends via SMTP or Microsoft Graph
                              │
                              ▼
                     Analyst / SOC distribution mailbox

Microsoft 365 / Entra ID / Defender for Endpoint
        │
        │  Wazuh ms-graph module (Graph API)
        ▼
  WAZUH MANAGER  (same pipeline as above, from this point on)
```

## 1.2 Components and responsibilities

| Component | Role | Runs on |
|---|---|---|
| Wazuh Manager | Central correlation engine: decoders, rules, agent management, compliance mapping | Dedicated Linux VM |
| Wazuh Indexer | OpenSearch-based storage for all Wazuh alerts/events | Same VM as Manager (lab) / dedicated node (production) |
| Wazuh Dashboard | Native Wazuh UI — used for deep OpenSearch query/forensics, not daily SOC triage | Same VM |
| Wazuh Agents | Installed on every monitored endpoint (Windows, Linux) | Endpoints |
| Docker | Container runtime hosting Grafana, Loki, Promtail, InfluxDB | Bare-metal Linux host |
| Grafana | SOC visualization + alerting layer | Docker, on bare-metal host |
| Loki | Log aggregation for syslog sources (Palo Alto, UniFi) | Docker, same host |
| Promtail | Log shipper: tails syslog files, forwards to Loki | Bare-metal, same host (not containerized — avoids double-mounting host log files) |
| InfluxDB | Time-series store for non-security operational metrics (legacy from the factory-floor monitoring platform this project grew out of) | Docker, same host |
| Falco | Runtime security monitoring for the Docker host | Bare-metal, same host (not inside containers) |
| Falcosidekick | Routes Falco alerts to Wazuh | Docker, same host |
| SOC Notification Engine | Custom Flask app: Grafana-webhook → MITRE-enriched email | systemd service, bare-metal host |

## 1.3 Host inventory template

Fill this in before you start building. Use placeholders in every doc/config you
publish; keep the filled-in version internal.

| Placeholder | Purpose | Lab example | Production target |
|---|---|---|---|
| `<SIEM_MONITOR_HOST>` | Bare-metal Linux: Docker, Grafana, Loki, Promtail, InfluxDB, Falco, Notification Engine | `falco` / `192.168.100.184` | dedicated production host, static IP, DNS name |
| `<WAZUH_MANAGER_IP>` | Wazuh Manager + Indexer + Dashboard VM | `192.168.100.50` | separate VM, ideally separate from `<SIEM_MONITOR_HOST>` |
| `<WAZUH_INDEXER_IP>` | Wazuh Indexer (if split from Manager) | `192.168.100.201` | dedicated node once event volume requires it |
| `<PALO_ALTO_MGMT_IP>` | Firewall management/syslog source | — | site firewall mgmt IP |
| `<UNIFI_CONTROLLER_IP>` | UniFi controller (Cloud Key/self-hosted) | — | site controller |
| `<SMTP_SERVER>` / `<GRAPH_TENANT_ID>` | Outbound mail path for the Notification Engine | — | production mail relay or M365 tenant |
| `<SOC_DISTRIBUTION_MAILBOX>` | Where SOC alerts land | — | e.g. `soc-alerts@<company-domain>` |

## 1.4 Security zones

- **Management zone**: Wazuh Manager/Indexer, Grafana admin, Notification Engine —
  restrict to a jump host / VPN-only administrative network.
- **Collection zone**: agent → manager (1514/1515 TCP), syslog → Promtail (514
  UDP/TCP) — should only accept traffic from known endpoint/network device subnets.
- **Visualization zone**: analyst access to Grafana — reverse-proxied with TLS and
  SSO/MFA in production (see `docs/12-production-scaling`).
- **Notification zone**: outbound-only from the Notification Engine to your mail
  path (SMTP relay or Graph API) — no inbound access needed except from Grafana's
  alert webhook, which should be firewalled to Grafana's host only.

## 1.5 Design principles carried through every part

1. **Collect signal, not volume.** Every telemetry source (especially the firewall)
   is filtered at the source to security-relevant events before ingestion — see
   `docs/07-network-security` for the explicit "do not forward all logs" rule.
2. **Validate before you visualize.** Confirm raw events are landing (CLI/API)
   before building a Grafana panel on top of them. A panel showing "No data" is
   easy to misdiagnose as "the pipeline is broken" when the real fault is the
   query.
3. **Runbook-driven alerting.** Every alert type that reaches an analyst mailbox has
   a corresponding runbook (JSON) with a MITRE mapping, investigation checklist,
   and response guidance — not just a bare "something happened" email.
4. **Fail safe, not silent.** The Notification Engine (Part 09) is built so that
   missing enrichment data degrades the email gracefully rather than dropping the
   underlying alert. Lesson learned in the lab build: an unhandled `KeyError` on an
   optional MITRE field silently killed real alert delivery for weeks before being
   caught by a controlled test.
