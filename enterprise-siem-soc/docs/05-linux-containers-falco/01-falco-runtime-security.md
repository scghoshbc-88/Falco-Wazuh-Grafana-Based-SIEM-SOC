# Part 5 — Linux Host & Container Runtime Security (Falco)

`STATUS: Production-safe`

## Prerequisites
- Part 2 (Docker on `<SIEM_MONITOR_HOST>`) and Part 3 (Wazuh Manager) complete.

## 5.1 Design decision

Run Falco **on the Docker host directly**, not as a sidecar inside every
container. One host-level Falco instance sees all container activity via the
kernel/eBPF driver; installing an agent inside every application container does
not scale and multiplies upgrade effort. (See `docs/14-decisions/ADR-004`.)

## 5.2 Install

```bash
curl -fsSL https://falco.org/repo/falcosecurity-3672BA8F.asc | sudo gpg --dearmor -o /usr/share/keyrings/falco-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/falco-archive-keyring.gpg] https://download.falco.org/packages/deb stable main" | sudo tee /etc/apt/sources.list.d/falcosecurity.list
sudo apt update && sudo apt -y install falco
sudo systemctl enable --now falco
```

## 5.3 Rule scope

Start from the Falco default ruleset, then layer custom rules for this
environment's actual containers (Grafana, Loki, InfluxDB, the Notification Engine)
in `/etc/falco/falco_rules.local.yaml`. Detection categories in production:

- Shell spawned inside a container
- Sensitive file read/write inside a container (e.g., `/etc/shadow`, SSH keys)
- Unexpected outbound network connection from a container
- Privilege escalation / capability changes
- Container escape indicators (namespace/cgroup manipulation)
- Unexpected process execution inside the Grafana/InfluxDB containers specifically
  (these are the containers most likely to be targeted since they're internet- or
  network-adjacent)

## 5.4 Falcosidekick → Wazuh

Falcosidekick receives Falco's gRPC/HTTP output and forwards it as a webhook.
Point it at a Wazuh listener (or write Falco alerts to a file Wazuh's `localfile`
config tails) so Falco events flow into the same correlation engine as everything
else, rather than living in a separate silo.

```bash
docker run -d --name falcosidekick \
  -p 2801:2801 \
  -e WEBHOOK_ADDRESS=http://<WAZUH_MANAGER_IP>:<listener_port>/falco \
  falcosecurity/falcosidekick:latest
```

Update `/etc/falco/falco.yaml` to add the Falcosidekick output target, then:

```bash
sudo systemctl restart falco
```

## 5.5 Grafana integration

Falco/Falcosidekick alerts land in Wazuh like any other agent event and become
queryable in Grafana via the Wazuh Indexer datasource — no separate Falco panel
type is needed. Confirm they carry a distinguishable `rule.groups` or `location`
tag so a dashboard panel can filter to "container/runtime" specifically.

## Validation

```bash
# Generate a benign but detectable test event
docker exec -it <any_running_container> sh -c "cat /etc/shadow" 2>/dev/null

sudo journalctl -u falco --since "5 minutes ago" | grep -i shadow
```

Confirm: the event appears in the Falco journal, is forwarded by Falcosidekick, and
lands as a Wazuh alert visible via `agent_control`/API within one evaluation cycle.
