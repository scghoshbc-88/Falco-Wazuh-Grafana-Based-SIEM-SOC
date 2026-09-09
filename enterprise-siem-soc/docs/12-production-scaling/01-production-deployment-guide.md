# Part 12 — Production Scaling Guide

This is the delta between the validated lab build (1 bare-metal host + 1 VM, ~10
agents) and a company-wide production rollout. Read this **before** provisioning
dedicated production resources — several decisions here (indexer topology,
network segmentation) are far cheaper to get right at build time than to retrofit.

## 12.1 Sizing

Wazuh's own sizing guidance is roughly linear in agent count and events-per-second
(EPS). Rough planning figures — validate against your own EPS once agents are
onboarded in waves rather than committing to hardware up front:

| Fleet size | Wazuh Manager | Wazuh Indexer | Grafana/Loki/Notification host |
|---|---|---|---|
| ~10 agents (lab, validated) | 4 vCPU / 8 GB | co-located with manager | 4 vCPU / 8 GB |
| ~100 agents | 8 vCPU / 16 GB | 8 vCPU / 32 GB, split node, SSD | 8 vCPU / 16 GB |
| ~500 agents | 16 vCPU / 32 GB, consider manager clustering | 3-node OpenSearch cluster, 16 vCPU / 64 GB each, SSD | 16 vCPU / 32 GB, consider separate Loki node |
| 1000+ agents | Wazuh cluster (multiple managers behind a load balancer) | Dedicated OpenSearch cluster sized per retention target | Dedicated Grafana + Loki hosts, consider Loki object-storage backend |

Storage sizing depends heavily on retention policy and per-agent EPS — measure
actual indexer disk growth over the first two weeks of a pilot wave before
finalizing production disk allocation, then apply your retention multiplier.

## 12.2 Migration path from lab to production

**Do not simply copy the lab VMs.** Rebuild each component from this
documentation onto new, right-sized infrastructure, and migrate configuration
(not live data) across:

1. Stand up production `<WAZUH_MANAGER_IP>` and `<SIEM_MONITOR_HOST>` per Parts 2–3
   on new hardware/VMs sized per 12.1.
2. Port the validated rule catalogue (`rules/wazuh/README.md`) and runbook set
   (`docs/09-alerting-framework`) — these are configuration, safe to carry over
   directly after a schema validation pass (Part 09 §9.4).
3. Re-onboard endpoints in waves via the Intune pilot-group process (Part 4.7),
   not a mass cutover.
4. Decommission the lab environment only after production has run one full alert
   cycle successfully (all of Part 11's test catalogue passing against
   production).

## 12.3 High availability

- **Wazuh Manager**: cluster mode (multiple managers, shared indexer) once a
  single manager's agent count or EPS approaches its sizing ceiling.
- **Wazuh Indexer**: minimum 3-node OpenSearch cluster in production for both
  performance and resilience — a single-node indexer is a lab simplification, not
  a production pattern.
- **Grafana**: can run as a single instance behind the reverse proxy for most
  organizations; add a second instance with shared external storage (Postgres
  backend for dashboards/alerting state) only if Grafana itself becomes a
  single-point-of-failure concern.
- **Notification Engine**: stateless by design — run two instances behind the
  reverse proxy/load balancer for redundancy; both read the same runbook
  directory (shared filesystem or synced via config management).

## 12.4 Security hardening for production

- **Network segmentation**: enforce the zones from `docs/01-architecture` §1.4 with
  actual firewall rules, not just documentation — management zone reachable only
  from a jump host/VPN, collection zone accepting only from known endpoint
  subnets.
- **TLS everywhere**: Grafana behind TLS-terminating reverse proxy with a valid
  certificate (not self-signed) in production; Wazuh agent-manager communication
  already uses its own TLS by default — do not disable it.
- **SSO/MFA for Grafana**: integrate with your identity provider (Entra ID SAML/
  OIDC) rather than local Grafana accounts at production scale.
- **Least-privilege API credentials**: separate read-only Grafana→Wazuh API
  credential, separate narrowly-scoped Graph API app registration for mail-send
  (Part 8.2) — never reuse a broad credential across integrations.
- **Secrets management**: SMTP/Graph credentials, Wazuh API passwords, and any
  client secrets go in a secrets manager (Vault, Azure Key Vault, or at minimum a
  root-only `.env` file with `chmod 600`) — never in a file that gets committed to
  this repository, sanitized or not.
- **`.gitignore` for this repository**: `.env`, `*.key`, `*.pem`, `credentials.yml`,
  `secrets.json`, and any file containing tenant IDs, client secrets, or real IP
  addresses. See `configs/.gitignore`.

## 12.5 Change control

Every procedure in this documentation that carries a `STATUS: Requires change
control` badge should go through your organization's standard change process once
in production — Wazuh rule edits, Intune assignment expansion, firewall log
forwarding changes, and app registration/permission changes chief among them.
Maintain a change log (`CHANGELOG.md` at the repo root) recording what changed,
when, by whom, and the validation result.

## 12.6 Monitoring the monitors

Production SOC infrastructure needs its own health monitoring, independent of
itself:

- Uptime checks (external to the SIEM stack) for Grafana, the Wazuh API, and the
  Notification Engine's `/health` endpoint.
- Alert on Wazuh agent disconnection counts exceeding a threshold (a wave of
  disconnects usually means a network or clock-sync issue, not ten simultaneous
  endpoint compromises).
- Alert on Notification Engine error-rate (HTTP 500s in its own logs) — this is
  the pipeline segment most likely to fail silently, per the lessons in Part 09.
- Disk usage alerting on the Wazuh Indexer and Loki volumes well before they fill
  (index write failures are much harder to recover from than a timely capacity
  alert).

## 12.7 Operational readiness checklist before go-live

- [ ] Full test catalogue (`docs/11-testing-validation`) passes against production
      infrastructure, not just the lab
- [ ] Backup/restore has been tested at least once against production (restore
      onto a scratch VM, not just "the backup job ran successfully")
- [ ] All `STATUS: Requires change control` procedures have a documented change
      process
- [ ] SSO/MFA enabled for Grafana; no shared/local admin accounts in daily use
- [ ] Secrets are in a secrets manager, not in configuration files
- [ ] On-call/escalation path defined for SOC alerts (who receives
      `<SOC_DISTRIBUTION_MAILBOX>` and what their response SLA is)
- [ ] Incident response workflow (`docs/13-incident-response`) reviewed with
      whoever will actually staff the SOC
