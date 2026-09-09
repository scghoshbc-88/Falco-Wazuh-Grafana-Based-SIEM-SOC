# Part 10 — Troubleshooting Reference

Each entry: Symptom → Likely cause → Diagnostic → Fix. These are drawn from actual
failures encountered building the original lab environment — keep this file
growing as production surfaces new ones.

## 10.1 "Alert fired in Grafana but no email arrived"

**Likely causes, in the order to check them:**

1. **Contact point misconfigured or disabled.** Grafana → Alerting → Contact
   points → open the contact point → confirm integration type, recipient/webhook
   URL, enabled state, no duplicate/obsolete entries.
2. **Notification policy label mismatch.** Alerting → Notification policies —
   confirm matcher labels (`team`, `environment`, `severity`) exactly match the
   labels on the alert rule. Case and spelling must match exactly
   (`team=TMC2-SOC` on the policy will never match `team=SOC` on the rule).
3. **Grouping/mute timing.** Check `Group wait` / `Group interval` / `Repeat
   interval` on the notification policy, and `Alerting → Silences` for an
   unintentionally broad silence matching the alert's labels.
4. **Webhook reachable but the receiving app is failing downstream.** Test the
   contact point (`Test` button) — a `200`/success here only proves the HTTP
   endpoint is reachable, **not** that email generation succeeded. Cross-check
   `sudo journalctl -u soc-notification-engine.service --since "10 minutes ago"`
   for `KeyError`, `Traceback`, or HTTP `500` entries corresponding to the real
   alert (not the synthetic test payload). See Part 09 §9.6 — this exact failure
   mode (test succeeds, real alert 500s on a schema mismatch) is the most
   time-consuming class of bug in this stack.
5. **Wazuh native mail vs. custom engine confusion.** If you disabled Wazuh's
   native `<email_notification>` for a cleaner analyst experience, confirm you
   disabled *only* that block and not the Grafana SMTP/webhook path — they are
   independent and easy to conflate when troubleshooting under time pressure.

## 10.2 "Notification Engine crashes on a real alert but Grafana's test succeeds"

**Cause:** runbook JSON schema mismatch — a runbook using an old flat schema
(`mitre_technique` as a top-level key) against code expecting the nested schema
(`runbook["mitre"]["technique"]`). Grafana's built-in test payload doesn't
exercise the real runbook-lookup code path, so it passes even when a specific
alert type's runbook is broken.

**Fix:**
1. `sudo journalctl -u soc-notification-engine --since "1 hour ago"` — find the
   exact `KeyError` and file/line.
2. Back up the suspect runbook: `cp runbooks/<name>.json runbooks/<name>.json.bak-$(date +%F)`
3. Run the schema validator (`docs/09-alerting-framework` §9.4) against all
   runbooks, not just the one that failed — fix the whole set at once.
4. Re-run the schema validator until all runbooks report `OK`.
5. Re-trigger a **real** test event (not the Grafana synthetic test) and confirm
   HTTP 200 in the journal with no traceback.

## 10.3 Wazuh rule change causes agent instability or manager fails to restart

**Cause, most common:** malformed XML in `local_rules.xml`, or an over-broad FIM
`<directories>` scope (e.g., monitoring an entire drive recursively).

**Fix sequence — always in this order:**
```bash
sudo cp /var/ossec/etc/rules/local_rules.xml /var/ossec/etc/rules/local_rules.xml.bak-$(date +%F-%H%M)
xmllint --noout /var/ossec/etc/rules/local_rules.xml      # catch syntax errors before restart
sudo /var/ossec/bin/wazuh-control restart
sudo tail -50 /var/ossec/logs/ossec.log                    # confirm clean startup, no rule-load errors
sudo /var/ossec/bin/agent_control -l                       # confirm agents reconnect
```
If agents stay disconnected after a config push, check for clock drift
(`timedatectl status` on both manager and agent) before assuming a network issue.

## 10.4 Grafana panel shows "No Data" despite raw telemetry existing

**Likely causes:**
- Wrong datasource UID after importing a dashboard JSON exported from a different
  Grafana instance — re-select the datasource per panel after import.
- Wrong field selection in the query (e.g., querying a keyword field expecting a
  text field, or vice versa) — verify field names directly against the Wazuh
  Indexer/Loki API before assuming the panel query is correct.
- Time-range mismatch — the panel's default time window doesn't include the test
  event's timestamp. Always widen the time range as the first diagnostic step.

## 10.5 Palo Alto / UniFi panels show "No Data"

**Likely causes:**
- Log forwarding profile on the firewall/controller not actually attached to a
  security policy rule (forwarding config exists but isn't applied).
- Promtail not tailing the right file path, or rsyslog not writing to the path
  Promtail expects — check `sudo journalctl -u promtail` and `sudo journalctl -u
  rsyslog` together.
- Loki label mismatch between what Promtail applies at ingestion and what the
  Grafana panel's LogQL query filters on.

## 10.6 Duplicate alert emails

**Cause:** both Wazuh's native `maild` and the SOC Notification Engine are active
for the same detection, or a Grafana notification policy has both a broad and a
narrow matcher both routing the same alert to two contact points.

**Fix:** disable Wazuh native mail per Part 3.2; audit notification policies for
overlapping matchers.

## 10.7 Intune agent deployment failure (fleet rollout)

**Likely causes:** install command missing required parameters (manager IP not
passed correctly at install time), detection rule referencing a registry key that
doesn't exist until after a reboot, or assignment scoped to a device group with
mixed OS versions/architectures.

**Fix:** validate the packaged app against the pilot group first (Part 4.7); check
Intune's "Device install status" report for the specific error code before
widening the rollout wave.

## 10.8 SSH access / API access fails while the Wazuh Manager service is "running"

**Cause:** the manager process being up doesn't guarantee SSH or the REST API is
reachable — check firewall rules (`ufw status`) and the API's own service status
independently rather than assuming manager-healthy implies everything-healthy.

```bash
sudo systemctl status wazuh-manager
sudo ss -lntp | grep 55000        # confirm API is actually listening
sudo ufw status verbose            # confirm the source subnet is allowed
```
