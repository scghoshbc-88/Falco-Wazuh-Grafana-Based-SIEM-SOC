#!/usr/bin/env python3
"""
Validate every runbook JSON against the required schema before deploying.
Run this after any change to configs/notification-engine/runbooks/*.json.

Usage: ./venv/bin/python scripts/bash/validate-runbooks.py [runbook_dir]
"""
import json
import sys
from pathlib import Path

runbook_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("configs/notification-engine/runbooks")

failures = 0
for p in sorted(runbook_dir.glob("*.json")):
    try:
        data = json.loads(p.read_text())
        missing = []

        if "mitre" not in data:
            missing.append("mitre")
        else:
            for key in ("technique", "technique_id", "tactic"):
                if key not in data["mitre"]:
                    missing.append(f"mitre.{key}")

        if "investigation_checklist" not in data:
            missing.append("investigation_checklist")
        elif not isinstance(data["investigation_checklist"], list):
            missing.append("investigation_checklist (must be a list, not a string)")
        elif len(data["investigation_checklist"]) < 2:
            missing.append("investigation_checklist (suspiciously short - check it wasn't left as one unsplit string)")

        if "response" not in data:
            missing.append("response")
        else:
            for key in ("immediate", "short_term", "long_term"):
                if key not in data["response"]:
                    missing.append(f"response.{key}")

        if missing:
            failures += 1
            print(f"FAIL  {p.name}: missing {', '.join(missing)}")
        else:
            print(f"OK    {p.name}")

    except Exception as e:
        failures += 1
        print(f"ERROR {p.name}: {e}")

sys.exit(1 if failures else 0)
