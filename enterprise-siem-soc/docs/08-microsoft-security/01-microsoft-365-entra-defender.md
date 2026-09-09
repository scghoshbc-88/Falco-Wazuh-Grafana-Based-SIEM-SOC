# Part 8 — Microsoft 365 / Entra ID / Defender for Endpoint

`STATUS: Requires change control` — app registration and Graph API scopes are
tenant-wide changes.

## Prerequisites
- Microsoft 365 Business Premium (or equivalent, with Defender for Endpoint and
  Entra ID P1+ for conditional access/sign-in log detail).
- Global Admin or Application Administrator access to create an app registration.

## 8.1 Data flow

```
Microsoft 365 / Entra ID / Defender for Endpoint
        │  Microsoft Graph API (application permissions, client-credentials flow)
        ▼
   Wazuh Manager (ms-graph module)
        │
        ▼
  Wazuh Indexer → Grafana (same pipeline as everything else)
```

## 8.2 App registration (Entra ID)

1. Entra ID → App registrations → New registration. Name it descriptively, e.g.
   `<COMPANY>-SOC-Graph-Integration`.
2. API permissions → Microsoft Graph → **Application permissions** (not delegated —
   this runs unattended):
   - `SecurityEvents.Read.All`
   - `SecurityAlert.Read.All`
   - `AuditLog.Read.All`
   - `Directory.Read.All` (for sign-in/Entra context enrichment)
3. Grant admin consent.
4. Create a client secret; store it in your secrets manager, never in
   `local_rules.xml` or a plaintext config committed to this repository.

Keep two app registrations distinct if you separate concerns: one broad
read-security-data registration for Wazuh's `ms-graph` module, and (if you build
the mailbox-restricted notification path from Part 9) a separate, narrowly-scoped
`Mail.Send`-only registration for outbound alert email. Do not reuse one
application's credentials for both purposes — the blast radius of a leaked secret
should match the narrowest permission set that needs it.

## 8.3 Wazuh `ms-graph` module configuration

```xml
<!-- /var/ossec/etc/ossec.conf on the manager -->
<wodle name="ms-graph">
  <enabled>yes</enabled>
  <run_on_start>yes</run_on_start>
  <interval>1m</interval>
  <api_auth>
    <client_id><ENTRA_APP_CLIENT_ID></client_id>
    <tenant_id><M365_TENANT_ID></tenant_id>
    <secret_value><CLIENT_SECRET></secret_value>
    <api_type>security-alerts</api_type>
  </api_auth>
  <resource name="security-alerts">
    <relationship>alerts_v2</relationship>
  </resource>
</wodle>
```

Sources available through this integration: Defender endpoint alerts/malware
detections/device risk, Entra ID sign-in failures/impossible travel/MFA
failures/conditional access, Exchange Online mail-flow anomalies/phishing
detections/suspicious inbox rules, and audit logs (user/admin actions,
configuration changes).

```bash
sudo /var/ossec/bin/wazuh-control restart
sudo tail -f /var/ossec/logs/ossec.log | grep -i ms-graph
```

## 8.4 Correlation value

This is the identity/endpoint half of the correlation examples in
`docs/07-network-security/01-palo-alto-unifi.md` §7.4 — an Entra ID impossible-
travel sign-in combined with a Palo Alto phishing-URL hit on the same user/asset
is a materially stronger signal than either alone.

## Validation

- Wazuh log shows successful Graph API authentication and event ingestion
  (`ossec.log` grep, no auth errors).
- A test/known Defender or Entra event appears in Wazuh within one polling
  interval and is queryable in Grafana.
- Confirm least-privilege: run `az ad app permission list` (or the Entra portal
  equivalent) and verify no unused permissions remain granted.
