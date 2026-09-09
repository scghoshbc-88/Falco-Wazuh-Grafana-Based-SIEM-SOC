# Grafana Dashboard Exports

Each subdirectory holds one of the 5 SOC dashboards (plus the Investigation
Workspace) as an importable JSON export, per `docs/06-grafana` §6.3.

```
dashboards/
├── soc-overview/
├── endpoint-security/
├── business-data-protection/
├── network-firewall-security/
├── linux-container-security/
└── investigation-workspace/
```

Each directory should contain:
- `<name>.json` — the dashboard export (Grafana → Dashboard settings → JSON Model,
  or Share → Export).
- `README.md` — one paragraph on the operational question this dashboard answers,
  plus a per-panel table (Title, Data source, Query, Threshold, Known limitations)
  per `docs/06-grafana` §"Dashboard Panel Catalogue".

## Standardized alert-table schema

Every alert-table panel across every dashboard uses these columns, in this order,
so an analyst reading any dashboard sees a consistent layout:

| Time | Severity | Rule / Detection | Source | Affected Asset / User | MITRE Technique |
|---|---|---|---|---|---|

## Importing

1. Grafana → Dashboards → New → Import.
2. Upload the JSON, or paste its contents.
3. **Re-select the datasource for each panel** — datasource UIDs are
   instance-specific and will not match after import into a fresh Grafana
   instance.
4. Save, then validate every panel shows live data (not "No data") before
   considering the dashboard production-ready.
