# Part 9 — SOC Alerting Framework (Notification Engine)

`STATUS: Production-safe once schema-validated` — see 9.6 before going live.

## Prerequisites
- Grafana Alerting configured with a contact point pointing at this engine
  (Part 6.5).
- Python 3.10+ available on `<SIEM_MONITOR_HOST>`.

## 9.1 Why a custom engine instead of native Wazuh/Grafana email

Wazuh's native `maild` and Grafana's built-in email both work, but neither
produces an analyst-ready alert: severity/risk scoring, a MITRE ATT&CK mapping,
and a per-alert-type investigation checklist all need to be assembled from a
runbook, not hand-written per rule. The Notification Engine is a small Flask app
that:

1. Receives Grafana's alert webhook (`POST /api/v1/grafana/alerts`).
2. Maps the firing alert's rule name to a **profile** (`PROFILE_MAP`), which
   points to a **runbook JSON file**.
3. Loads the runbook, pulls MITRE tactic/technique, investigation checklist, and
   response guidance.
4. Renders an HTML email (Jinja2) and sends it via SMTP or Microsoft Graph
   (`MAIL_TRANSPORT` config).

## 9.2 Deployment (systemd service)

```bash
sudo mkdir -p /opt/soc-notification-engine/{runbooks,integrations,config}
# deploy app.py, integrations/grafana_webhook.py, and runbooks/*.json here
python3 -m venv /opt/soc-notification-engine/venv
/opt/soc-notification-engine/venv/bin/pip install flask requests jinja2
```

`/etc/systemd/system/soc-notification-engine.service`:

```ini
[Unit]
Description=SOC Notification Engine
After=network.target

[Service]
User=soc-alerting
Group=soc-alerting
WorkingDirectory=/opt/soc-notification-engine
ExecStart=/opt/soc-notification-engine/venv/bin/python /opt/soc-notification-engine/app.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo useradd -r -s /usr/sbin/nologin soc-alerting
sudo systemctl daemon-reload
sudo systemctl enable --now soc-notification-engine.service
```

Run behind a production WSGI server (Gunicorn) rather than Flask's development
server before go-live:

```bash
/opt/soc-notification-engine/venv/bin/pip install gunicorn
# ExecStart= /opt/soc-notification-engine/venv/bin/gunicorn -w 2 -b 0.0.0.0:8090 app:app
```

Flask's dev server prints `WARNING: This is a development server` for a reason —
treat this as a required hardening step, not optional, for a production rollout.

## 9.3 Runbook schema (standardized, mandatory)

Every runbook JSON **must** conform to this nested schema:

```json
{
  "mitre": {
    "technique": "Exfiltration Over Physical Medium",
    "technique_id": "T1052.001",
    "tactic": "Exfiltration"
  },
  "investigation_checklist": [
    "Confirm business justification with the user.",
    "Identify the removable-media device, manufacturer and ownership.",
    "Review files copied and total transfer volume.",
    "Correlate Wazuh FIM and Sysmon endpoint telemetry.",
    "Review Microsoft Defender device timeline.",
    "Determine whether sensitive business data was transferred.",
    "Escalate if the transfer was unauthorized."
  ],
  "response": {
    "immediate": "...",
    "short_term": "...",
    "long_term": "..."
  }
}
```

> **Lesson learned (kept here deliberately):** an earlier flat schema
> (`mitre_technique`, `mitre_id`, `mitre_tactic` as top-level keys, with a single
> unsplit `investigation_checklist` string) caused a `KeyError: 'mitre'` in
> production that **silently dropped real alert emails for weeks** — the Grafana
> contact-point "Test" button used a synthetic payload that didn't exercise the
> real runbook lookup path, so the test kept reporting success while the real USB
> detection alert kept failing with HTTP 500. Validate every runbook against the
> schema below before it goes live, and always test with a *real* triggering event,
> not just Grafana's built-in test alert.

## 9.4 Runbook schema validator

Run this before enabling any new runbook or after editing an existing one
(`scripts/bash/validate-runbooks.py`):

```python
import json
from pathlib import Path

for p in sorted(Path("runbooks").glob("*.json")):
    try:
        data = json.loads(p.read_text())
        missing = []
        if "mitre" not in data:
            missing.append("mitre")
        else:
            for key in ("technique", "technique_id", "tactic"):
                if key not in data["mitre"]:
                    missing.append("mitre." + key)
        if "investigation_checklist" not in data:
            missing.append("investigation_checklist")
        elif not isinstance(data["investigation_checklist"], list):
            missing.append("investigation_checklist (must be a list, not a string)")
        if "response" not in data:
            missing.append("response")
        print(f"{'FAIL' if missing else 'OK'} {p.name}" + (f": missing {', '.join(missing)}" if missing else ""))
    except Exception as e:
        print(f"ERROR {p.name}: {e}")
```

Run this in CI (or a pre-deploy git hook) for every pull request that touches
`runbooks/*.json` — this is the single highest-leverage regression test in the
whole alerting framework.

## 9.5 Defensive coding requirement

`grafana_webhook.py` must **never** crash the whole request on missing optional
enrichment data. Use `.get()` with defaults, not direct dictionary indexing:

```python
mitre = runbook.get("mitre", {})
mitre_technique = mitre.get("technique", "Not mapped")
mitre_id = mitre.get("technique_id", "Not mapped")
mitre_tactic = mitre.get("tactic", "Not mapped")
```

Missing enrichment should degrade the email gracefully (show "Not mapped") — it
must never prevent delivery of the underlying security alert. This is the
architectural fix that followed the incident described in 9.3.

## 9.6 End-to-end validation sequence

Do not consider this part complete until you've walked the **entire** chain with
a real (not synthetic) triggering event:

```
1. Trigger a real test event on an endpoint (e.g., TC-005 USB insertion)
2. Confirm Wazuh rule fires:        sudo /var/ossec/bin/agent_control -i <id>
3. Confirm Grafana alert = Firing:  Alerting → Alert rules → <rule> → History
4. Confirm webhook POST succeeds:   sudo journalctl -u soc-notification-engine -f
                                     (look for "POST /api/v1/grafana/alerts" 200,
                                      not 500/KeyError/Traceback)
5. Confirm the email lands in the SOC distribution mailbox
6. Confirm the email content: correct severity, correct MITRE technique,
   correct investigation checklist for that alert type
```

Grafana's built-in contact-point "Test" only proves the webhook endpoint is
reachable — it does **not** prove a specific alert type's runbook resolves
correctly. Both tests are required, and they are not substitutes for each other.

## Validation checklist

- [ ] Every file in `runbooks/*.json` passes the validator in 9.4
- [ ] `grafana_webhook.py` uses `.get()` with defaults for all optional runbook
      fields (9.5)
- [ ] Service runs under Gunicorn (or equivalent), not Flask's dev server
- [ ] Full end-to-end chain (9.6) walked with a real triggering event, not just
      Grafana's synthetic test
- [ ] Wazuh's native email (`<email_notification>`) is disabled to avoid duplicate
      alerts, per Part 3.2
