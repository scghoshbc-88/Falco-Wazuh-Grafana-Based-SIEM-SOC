# Part 2 — Infrastructure Foundation

`STATUS: Production-safe (new build)`

## Prerequisites
- Bare-metal or dedicated VM host for `<SIEM_MONITOR_HOST>`: Ubuntu 24.04 LTS,
  minimum 8 vCPU / 32 GB RAM / 500 GB SSD for a production build (see
  `docs/12-production-scaling` for sizing math based on endpoint count).
- Separate VM for `<WAZUH_MANAGER_IP>`: Ubuntu 24.04 LTS, 8 vCPU / 16 GB RAM / 200 GB
  SSD minimum.
- Static IP addressing and DNS entries for both hosts before you begin.
- A non-root administrative user with sudo on both hosts.

## 2.1 Base OS hardening (both hosts)

```bash
sudo apt update && sudo apt -y upgrade
sudo timedatectl set-ntp true
sudo apt -y install ufw fail2ban unattended-upgrades auditd chrony
sudo systemctl enable --now auditd chrony
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp        # SSH — restrict source in production, see docs/12
sudo ufw enable
```

Set correct time before anything else — Wazuh/OpenSearch and TLS all depend on
clock sync, and the original lab build hit confusing "agent disconnected" symptoms
that were actually clock drift.

## 2.2 Docker on `<SIEM_MONITOR_HOST>`

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $(whoami)
newgrp docker
docker --version
docker compose version
```

Create the working directory structure:

```bash
sudo mkdir -p /opt/siem-stack/{grafana,loki,promtail,influxdb,falco}
sudo chown -R $(whoami):$(whoami) /opt/siem-stack
```

## 2.3 Core `docker-compose.yml`

See `configs/docker-compose.yml` for the full file. Summary of services:

| Service | Image | Purpose | Persistent volume |
|---|---|---|---|
| grafana | `grafana/grafana:latest` (pin a version in production) | SOC dashboards, alerting | `/opt/siem-stack/grafana` |
| loki | `grafana/loki:latest` | Log store for syslog sources | `/opt/siem-stack/loki` |
| influxdb | `influxdb:2.7` | Time-series metrics (legacy/ops) | `/opt/siem-stack/influxdb` |

Promtail and Falco run **bare-metal**, not in Docker, for two reasons validated in
the lab build: (1) Promtail needs direct access to host log files without extra
bind-mount indirection, and (2) Falco needs kernel-level visibility that is simpler
to grant to a host process than to a container.

```bash
cd /opt/siem-stack
docker compose up -d
docker compose ps
```

## 2.4 Reverse proxy

Put Grafana behind a reverse proxy (nginx or Caddy) with TLS termination even in
the lab — do not expose Grafana's raw port. See `configs/nginx-grafana.conf`. In
production this proxy also enforces SSO — see `docs/12-production-scaling`.

## 2.5 Backup strategy

`STATUS: Production-safe`

- **Daily**: `docker compose` volume snapshots for Grafana (dashboards/datasources),
  Wazuh Manager `/var/ossec/etc` and `/var/ossec/logs`, and the Notification Engine's
  `/opt/tmc2-notification-engine/runbooks/`.
- **Retention**: 30 days local, replicate to a NAS or object store weekly for
  production.
- Script: `scripts/bash/backup-siem-stack.sh` — run via cron/systemd timer.

```bash
# /etc/systemd/system/siem-backup.timer + siem-backup.service
# calls scripts/bash/backup-siem-stack.sh nightly at 02:00
```

## 2.6 Disaster recovery notes

Document, per host: what it runs, how it's provisioned (config-as-code vs manual),
and how long a rebuild takes. In the lab build this was informal; for production,
this becomes `docs/12-production-scaling/03-disaster-recovery.md` and should be
tested at least once before go-live (restore from backup onto a scratch VM).

## Validation

```bash
docker compose ps                      # all services "Up"
curl -sf http://localhost:3000/api/health   # Grafana health check
curl -sf http://localhost:3100/ready        # Loki ready
sudo ufw status verbose
```

All four checks should return healthy/success before proceeding to Part 3.
