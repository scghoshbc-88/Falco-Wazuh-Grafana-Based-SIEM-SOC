"""
SOC Notification Engine
Receives Grafana alert webhooks, enriches with MITRE ATT&CK + runbook data,
renders an HTML email, and sends via SMTP or Microsoft Graph.

Deploy under Gunicorn in production - see docs/09-alerting-framework §9.2.
"""
import json
import logging
from pathlib import Path

from flask import Flask, request, jsonify

from integrations.grafana_webhook import handle_grafana_alert

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

BASE_DIR = Path(__file__).parent
RUNBOOK_DIR = BASE_DIR / "runbooks"

# Maps a Grafana alert rule title to a runbook profile.
# Keep this in sync with rules/wazuh/README.md - every detection that should
# produce a SOC email needs an entry here and a matching runbook JSON.
PROFILE_MAP = {
    "SIEM - USB Data Transfer Detected": "usb_large_copy",
    # "SIEM - SSH Brute Force Detected": "ssh_bruteforce",
    # "SIEM - Falco Container Shell Detected": "container_shell",
}


@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="online", service="SOC Notification Engine")


@app.route("/api/v1/grafana/alerts", methods=["POST"])
def grafana_alerts():
    payload = request.get_json(force=True, silent=True) or {}
    try:
        result = handle_grafana_alert(payload, PROFILE_MAP, RUNBOOK_DIR)
        return jsonify(result), 200
    except Exception:
        logging.exception("Failed to process Grafana alert payload")
        # Do not leak internals in the response, but always return a clear
        # 500 so it's visible in Grafana's contact-point delivery history.
        return jsonify(error="internal error processing alert"), 500


if __name__ == "__main__":
    # Development only - use Gunicorn in production (docs/09-alerting-framework §9.2)
    app.run(host="0.0.0.0", port=8090)
