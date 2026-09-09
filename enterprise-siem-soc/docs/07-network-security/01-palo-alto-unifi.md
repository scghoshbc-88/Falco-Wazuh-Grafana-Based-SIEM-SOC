# Part 7 — Network Security Telemetry (Palo Alto + UniFi)

`STATUS: Requires change control` — firewall/log-forwarding changes go through
your normal network change process even in a pilot.

## Prerequisites
- Loki/Promtail running (Part 6.2).
- Firewall and wireless controller management access.

## 7.1 The core principle: filter at the source

**Do not forward all firewall logs.** Enterprise SOCs typically discard 90–98% of
raw firewall traffic logs — the goal is security-relevant telemetry, not every
packet/session. Forwarding everything creates noise that actively hides real
signal and drives unnecessary storage/indexing cost at production scale.

## 7.2 Palo Alto — what to forward

| Log type | Forward? | Notes |
|---|---|---|
| Threat logs (virus, spyware, vulnerability, C2, DNS security) | ✅ Always | Becomes SOC Critical Alerts |
| WildFire (malware verdicts, unknown file detections) | ✅ Always | High severity |
| URL Filtering — malware/phishing/C2/newly-registered/dynamic-DNS categories only | ✅ Filtered | Exclude social media, shopping, streaming — pure noise |
| Authentication logs (VPN, admin login failures, admin config changes) | ✅ Always | Correlates with M365 sign-in data — see 7.4 |
| Configuration logs (policy/NAT/object changes, commits) | ✅ Always | Critical for incident investigation/change audit |
| System logs (HA failures, resource exhaustion, interface down) | ✅ Always | NetOps + SecOps value |
| Traffic logs — **denied only** (interzone/inbound deny, deny-from-internet) | ✅ Filtered | Reconnaissance detection |
| Traffic logs — allowed sessions | ❌ Do not forward | This is the 90–98% you discard |
| High-risk destination hits (known-malicious IP, TOR, geo-restricted) | ✅ Always | |
| Unusual destination ports (22, 3389, 445, 5900, 1433, 1521 from unexpected sources) | ✅ Always | Lateral-movement indicator |

Configure log forwarding profiles on the firewall to send only the above
categories via syslog to `<SIEM_MONITOR_HOST>`.

```
Palo Alto Firewall (syslog, filtered) → rsyslog on <SIEM_MONITOR_HOST> → Promtail → Loki → Grafana
                                                                        ↘ (optionally) Wazuh, for correlation
```

## 7.3 UniFi — what to forward

Configure the UniFi controller's remote syslog (CEF format) to
`<SIEM_MONITOR_HOST>`. Collect:

- Access point events: rogue AP detection, AP disconnects, firmware changes
- Client events: excessive auth failures, unknown devices, MAC flapping
- Network events: VLAN anomalies, DHCP anomalies, wireless intrusion alerts

```
UniFi Controller → CEF syslog → Promtail → Loki → Grafana (Network/Firewall Security dashboard)
```

## 7.4 Correlation examples (why this data matters together)

| Palo Alto signal | Combined with | = |
|---|---|---|
| Phishing URL access | M365 impossible-travel login | Compromised user alert |
| C2 DNS detection | Falco: unexpected shell in container | Container compromise alert |
| Multiple denied connections | Wazuh: Linux auth failures | Brute-force alert |
| Outbound to known-malicious IP | Defender endpoint alert | Potential malware infection |

These correlations are the actual justification for centralizing firewall +
endpoint + identity telemetry rather than leaving the firewall log in its own
silo — build the corresponding Grafana panels/alert rules once both data sources
are flowing (see `docs/06-grafana` and `docs/09-alerting-framework`).

## Validation

```bash
sudo tail -f /var/log/paloalto/threat.log      # confirm filtered logs are landing
sudo tail -f /var/log/unifi/unifi.log
```

- Loki query for each source returns recent events (`{source="palo-alto"}`,
  `{source="unifi"}`).
- Network/Firewall Security dashboard (Part 6.3) shows live panels for both
  sources.
- At least one correlation example from 7.4 is wired into an alert rule before
  calling this part complete.
