# Part 3 — Wazuh Core

`STATUS: Production-safe (new build)` — treat any change to a live production
Wazuh Manager as `STATUS: Requires change control` once you've gone live.

## Prerequisites
- `<WAZUH_MANAGER_IP>` host provisioned per Part 2.
- Outbound internet access (for the install script) or a mirrored offline
  repository for air-gapped production sites.

## 3.1 Install Wazuh Manager, Indexer, Dashboard

For a single-node lab/pilot, use the all-in-one script; for production, split
Indexer onto its own node once you cross ~150 agents or event volume degrades
dashboard query time (see `docs/12-production-scaling`).

```bash
curl -sO https://packages.wazuh.com/4.9/wazuh-install.sh
sudo bash wazuh-install.sh -a          # all-in-one: manager + indexer + dashboard
```

Save the generated admin passwords immediately (`wazuh-install-files.tar`) into your
secrets manager — they are not recoverable from the script output after this step.

```bash
sudo systemctl status wazuh-manager wazuh-indexer wazuh-dashboard
```

## 3.2 Manager configuration essentials

Key file: `/var/ossec/etc/ossec.conf`. Baseline changes for a SOC deployment:

- `<email_notification>no</email_notification>` — **disable Wazuh's native mail**
  intentionally. The SOC Notification Engine (Part 09) is the single source of
  outbound alert email; running both produces duplicate/inconsistent alerts, which
  was an actual failure mode in the lab build (analysts got two different-looking
  emails for the same event).
- Keep `<email_alerts>` blocks and `email_alert_level` **in place** even while
  native mail is disabled — you may want to re-enable it quickly for diagnosis
  without rebuilding the block from scratch.
- `<logall>no</logall>` in production once custom rules are validated — full
  logging is useful during Part 3–4 build-out but adds indexer load at scale.

```bash
sudo cp /var/ossec/etc/ossec.conf /var/ossec/etc/ossec.conf.bak.$(date +%F)
sudo nano /var/ossec/etc/ossec.conf
sudo /var/ossec/bin/wazuh-control restart
```

## 3.3 Agent registration

```bash
# On the manager: register + get the enrollment key
sudo /var/ossec/bin/manage_agents

# On each endpoint (Linux example):
curl -sO https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.9.0-1_amd64.deb
sudo WAZUH_MANAGER='<WAZUH_MANAGER_IP>' dpkg -i ./wazuh-agent_4.9.0-1_amd64.deb
sudo systemctl daemon-reload
sudo systemctl enable --now wazuh-agent
```

Windows agent installation is covered in `docs/04-windows-endpoints` (including the
Intune-based rollout path for production-scale fleets).

## 3.4 API configuration

Wazuh's REST API is what Grafana queries. Confirm it's reachable and create a
least-privilege read-only API user for Grafana rather than using the default admin
credential:

```bash
curl -k -u <api_user>:<api_password> -X POST "https://<WAZUH_MANAGER_IP>:55000/security/user/authenticate"
```

## 3.5 Custom rule catalogue

All custom detections live in `/var/ossec/etc/rules/local_rules.xml`. Never edit
this file directly on a live production manager without: (1) backing it up, (2)
validating XML syntax offline, (3) applying, (4) restarting, (5) confirming the
manager comes back healthy. See the exact procedure in
`docs/10-troubleshooting/02-wazuh-rule-changes.md`.

```bash
STAMP=$(date +%F-%H%M)
sudo cp /var/ossec/etc/rules/local_rules.xml /var/ossec/etc/rules/local_rules.xml.backup-$STAMP
xmllint --noout /var/ossec/etc/rules/local_rules.xml     # validate before restart
sudo /var/ossec/bin/wazuh-control restart
sudo tail -f /var/ossec/logs/ossec.log                    # confirm clean startup
```

The full validated rule set built during the lab phase is catalogued in
`rules/wazuh/README.md` with rule ID, detection, MITRE mapping, and validation
status. Import these as your starting baseline rather than rebuilding from
scratch — see that file for the complete table (SSH activity, account lockout,
scheduled task creation, security log clearing, Defender detections, USB
telemetry, privilege escalation).

## 3.6 Backup and upgrade

```bash
# Backup (run before any change, and nightly via scripts/bash/backup-wazuh.sh)
sudo tar -czf /backup/wazuh-etc-$(date +%F).tar.gz /var/ossec/etc

# Upgrade path: always test on a staging manager first in production
sudo systemctl stop wazuh-manager
# ... follow official Wazuh upgrade docs for the target version ...
sudo systemctl start wazuh-manager
```

## Validation

```bash
sudo /var/ossec/bin/agent_control -l          # all expected agents "Active"
sudo /var/ossec/bin/wazuh-logtest             # test a sample log line against rules
curl -k -s https://<WAZUH_MANAGER_IP>:55000/manager/status --user <api_user>:<api_password>
```

Confirm: manager status "running", all onboarded agents show "Active", and a known
test log line matches its expected rule ID via `wazuh-logtest` before moving to
Part 4.
