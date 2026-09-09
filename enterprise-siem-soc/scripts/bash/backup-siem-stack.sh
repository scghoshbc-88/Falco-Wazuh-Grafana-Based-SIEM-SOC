#!/usr/bin/env bash
# Nightly backup of SIEM stack configuration and Wazuh manager state.
# Deploy via systemd timer (see docs/02-infrastructure-preparation §2.5).
set -euo pipefail

BACKUP_ROOT="/backup/siem-stack"
STAMP=$(date +%F-%H%M)
DEST="${BACKUP_ROOT}/${STAMP}"
RETENTION_DAYS=30

mkdir -p "${DEST}"

# Grafana (dashboards, datasources, alerting state)
tar -czf "${DEST}/grafana.tar.gz" -C /opt/siem-stack grafana

# Notification Engine runbooks + config (excludes secrets - back those up
# separately via your secrets manager's own backup process)
tar -czf "${DEST}/notification-engine.tar.gz" \
    --exclude='*.env' \
    -C /opt/soc-notification-engine runbooks config

# Wazuh manager config + logs (run this section on the Wazuh Manager host)
if [ -d /var/ossec/etc ]; then
  tar -czf "${DEST}/wazuh-etc.tar.gz" /var/ossec/etc
fi

# Prune backups older than retention window
find "${BACKUP_ROOT}" -maxdepth 1 -type d -mtime +"${RETENTION_DAYS}" -exec rm -rf {} +

echo "Backup complete: ${DEST}"
