"""
Grafana webhook -> runbook lookup -> MITRE enrichment -> email render/send.

Defensive-coding requirement (docs/09-alerting-framework §9.5):
missing optional runbook fields must NEVER raise and kill the whole request.
A production incident traced to `runbook["mitre"]["technique"]` (direct
indexing) silently dropping real alert emails for weeks is the reason every
lookup below uses .get() with a default.
"""
import json
from pathlib import Path

from jinja2 import Template

from .mailer import send_email  # SMTP or Microsoft Graph, per config

TEMPLATE = Template((Path(__file__).parent.parent / "templates" / "alert_email.html.j2").read_text())


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def handle_grafana_alert(payload: dict, profile_map: dict, runbook_dir: Path) -> dict:
    alerts = payload.get("alerts", [payload])  # Grafana may send a batch or single alert
    sent = []

    for alert in alerts:
        alert_name = alert.get("labels", {}).get("alertname") or alert.get("ruleName", "Unknown Alert")
        profile_key = profile_map.get(alert_name)

        if not profile_key:
            # Unmapped alert type - don't crash, just skip enrichment and
            # send a bare-bones notification so nothing is silently dropped.
            runbook = {}
        else:
            runbook_path = runbook_dir / f"{profile_key}.json"
            runbook = _load_json(runbook_path) if runbook_path.exists() else {}

        mitre = runbook.get("mitre", {})
        mitre_technique = mitre.get("technique", "Not mapped")
        mitre_id = mitre.get("technique_id", "Not mapped")
        mitre_tactic = mitre.get("tactic", "Not mapped")

        checklist = runbook.get("investigation_checklist", [])
        response = runbook.get("response", {})

        html = TEMPLATE.render(
            alert_name=alert_name,
            severity=alert.get("labels", {}).get("severity", "unknown"),
            mitre_technique=mitre_technique,
            mitre_id=mitre_id,
            mitre_tactic=mitre_tactic,
            investigation_checklist=checklist,
            response_immediate=response.get("immediate", "Not defined"),
            response_short_term=response.get("short_term", "Not defined"),
            response_long_term=response.get("long_term", "Not defined"),
        )

        send_email(subject=f"[SOC ALERT] {alert_name}", html_body=html)
        sent.append(alert_name)

    return {"status": "sent", "alerts": sent}
