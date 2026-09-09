# Investigation Queries

Reusable queries referenced throughout the docs and incident case studies. Keep
these here rather than only in screenshots — a query is reusable, a screenshot
isn't.

## Wazuh Indexer (OpenSearch/Lucene) — via Grafana

**All alerts for a specific rule ID, last 24h:**
```
rule.id:110500 AND @timestamp:[now-24h TO now]
```

**All alerts for a specific agent/hostname:**
```
agent.name:"<hostname>" AND rule.level:>=8
```

**USB-related events, all severities:**
```
rule.groups:"usb" OR rule.description:*removable*
```

## Loki (LogQL) — Palo Alto / UniFi

**All Palo Alto threat-log entries, last hour:**
```
{source="palo-alto"} |= "THREAT"
```

**All denied traffic from a specific source IP:**
```
{source="palo-alto"} |= "DENIED" |= "<source_ip>"
```

**UniFi device-offline events:**
```
{source="unifi"} |= "STA_DISCONNECT" or {source="unifi"} |= "AP_LOST_CONTACT"
```

## Correlation query pattern (cross-source)

Build these as separate panels on the Investigation Workspace dashboard
(`docs/06-grafana` §6.4), templated on a `$hostname` or `$user` dashboard variable,
rather than as one combined query — Wazuh Indexer and Loki are separate
datasources and cannot be joined in a single query.
