# Naming Conventions & Placeholders

Fill in this table with your real values in a private copy before you begin
building; keep placeholders in anything committed to a shared or public
repository.

| Placeholder | Meaning | Example (lab) |
|---|---|---|
| `<SIEM_MONITOR_HOST>` | Bare-metal Linux host: Docker/Grafana/Loki/Promtail/InfluxDB/Falco/Notification Engine | `siem-monitor01` |
| `<WAZUH_MANAGER_IP>` | Wazuh Manager (+ Indexer + Dashboard if co-located) | `10.0.10.10` |
| `<WAZUH_INDEXER_IP>` | Wazuh Indexer, if split out | `10.0.10.11` |
| `<PALO_ALTO_MGMT_IP>` | Firewall management/syslog source | `10.0.1.1` |
| `<UNIFI_CONTROLLER_IP>` | UniFi controller | `10.0.2.1` |
| `<ENTRA_APP_CLIENT_ID>` | App registration client ID (Graph API) | secret — do not commit |
| `<M365_TENANT_ID>` | Microsoft 365 tenant ID | secret — do not commit |
| `<CLIENT_SECRET>` | App registration client secret | secret — do not commit, secrets manager only |
| `<SMTP_SERVER>` | Outbound mail relay for the Notification Engine | `smtp.<company-domain>` |
| `<SOC_DISTRIBUTION_MAILBOX>` | Where SOC alerts land | `soc-alerts@<company-domain>` |
| `<api_user>` / `<api_password>` | Wazuh REST API read-only credential for Grafana | secret — do not commit |

Never commit: `.env`, `*.key`, `*.pem`, `credentials.yml`, `secrets.json`, or any
file containing a real tenant ID, client secret, or production IP address. See
`configs/.gitignore`.
