# Experiment 02B — Falco runtime alert ingestion into Wazuh

**Test date:** 2026-11-02 (America/Vancouver, UTC-07:00)  
**Status:** Live end-to-end alert path verified from operator-reviewed records; original logs remain private and are **not included in this repository**.  
**Environment:** Independent Ubuntu laboratory; Falco 0.45.2 on Machine B (modern eBPF), Wazuh agent 4.14.9 on Machine B, Wazuh manager 4.14.9 in a separate Ubuntu VM. No employer telemetry.

## Objective

Verify that a Falco runtime event is exported as JSON, collected by the Wazuh agent, delivered to the Wazuh manager, and elevated to a Wazuh security alert by an explicit custom rule. This tests **SIEM integration**, not causal provenance reconstruction.

## Architecture and telemetry path

```text
Machine B: Falco modern eBPF
   -> local Falco JSON event log
   -> Wazuh agent JSON localfile collector
   -> Wazuh manager (via restricted lab transport)
   -> manager raw JSON archive (temporarily enabled)
   -> custom Wazuh rule 100700, level 8
   -> manager alerts.json
```

Machine names, private network addresses, user identifiers and secrets are deliberately omitted.

### Collection configuration

On Machine B, the Wazuh agent was configured to collect Falco JSON events using a `localfile` entry:

```xml
<localfile>
  <log_format>json</log_format>
  <location>/var/log/falco/events.json</location>
</localfile>
```

The Falco JSON output was written to `/var/log/falco/events.json` with restricted access. Wazuh logcollector was verified to have opened the file. On the Wazuh VM, `<logall_json>yes</logall_json>` was **temporarily** enabled to inspect the raw manager archive. This increases retained event volume and should be disabled after evidence preservation.

### Custom Wazuh rule

The following rule was validated using `wazuh-analysisd -t` and matched with `wazuh-logtest` before the live test:

```xml
<group name="falco,runtime_detection,">
  <rule id="100700" level="8">
    <decoded_as>json</decoded_as>
    <field name="rule" type="pcre2">^Read sensitive file untrusted$</field>
    <field name="source" type="pcre2">^syscall$</field>
    <description>Falco: Sensitive file access detected</description>
    <group>falco,filesystem,</group>
  </rule>
</group>
```

The rule matches a **specific Falco rule name and source**; it does not itself prove malicious activity. The manager configuration test passed, and the Wazuh manager remained active after restart.

## Controlled live test

**Run ID:** `SOCEXP02B-LIVE-20261102-220143`  
**Action:** A controlled read of `/etc/shadow` using `sudo cat /etc/shadow > /dev/null` on Machine B. This test was confined to the research machine; contents were not printed to the terminal or changed. The run ID was an operator label, **not a field embedded in the event**.

The corresponding records were inspected at the Falco JSON output, Wazuh manager raw archive and Wazuh alert output.

## Verified observations

| Stage / field | Observed result |
| --- | --- |
| Falco rule | `Read sensitive file untrusted` |
| Falco source | `syscall` |
| Falco event timestamp | 2026-11-02 22:01:55.040398883 (local time, UTC-07:00) |
| Syscall | `openat` |
| Target | `/etc/shadow` |
| Process | `cat` |
| Parent / ancestry context | `sudo`, `bash`, `sshd-session` |
| Wazuh agent ID | `002` (lab identifier) |
| Wazuh source location | `/var/log/falco/events.json` |
| Wazuh alert rule | `100700` |
| Wazuh alert level | `8` |
| Wazuh alert timestamp | 2026-11-02T22:01:56.725-0700 |
| Wazuh alert destination | `/var/ossec/logs/alerts/alerts.json` |

The operator observed the matching Falco event in the manager archive and the corresponding custom-rule alert in `alerts.json`. The alert retained the rule name and target-file context, including `data.output_fields.fd.name=/etc/shadow`.

**Timestamp interpretation:** The displayed Falco event and Wazuh alert timestamps differ by approximately **1.685 seconds**. This is an observed timestamp difference, **not** a measured end-to-end latency distribution: the timestamps may represent different pipeline stages, and no clock/latency measurement study was performed. The Falco `evt.time` nanosecond-resolution integer may require special care when parsed/re-serialized; precision preservation was not systematically validated.

## Evidence status and integrity

- **Reviewed during the live session:** Falco JSON, Wazuh agent collection status, manager raw archive, Wazuh rule-test results and the live `alerts.json` record.
- **Not published:** original raw JSON event, manager archive excerpt, alert JSON, terminal screenshots, configuration backups or hashes for this run.
- **Reproducibility:** configuration snippets and event identifiers above document the procedure, but readers cannot independently revalidate the original event without the preserved private records.
- **Privacy:** original host identifiers, private IP addresses and any potentially identifying log fields must be removed before any future public evidence upload. Never present recreated terminal output as an original contemporaneous screenshot.

## Interpretation and limitations

**Supported:** A real Falco runtime detection was collected as JSON by Wazuh and triggered a level-8 custom Wazuh alert during a controlled test. This confirms the functioning of the selected telemetry-to-alert path.

**Not supported:** Complete provenance graph generation, causal dependency inference, attack attribution, general detection accuracy, false-positive rates, performance under load, analyst-time reduction, or a demonstrated advantage over standalone Falco. The controlled test is a single benign event, not an attack campaign.

## Follow-up work

1. Preserve a **sanitized, verifiable** Falco source event and matching Wazuh alert with redaction and checksum records.
2. Disable temporary `logall_json` archiving after preservation; verify the final manager configuration and storage use.
3. Add log rotation/retention for Falco JSON and review file permissions.
4. Compare the observed SIEM alert context with the Linux Audit partial graphs documented in [Experiment 03](../03-linux-audit-provenance/README.md), using explicit reconstruction and analyst-effort measures rather than assuming causal relationships.

Related baseline: [Experiment 02A — Controlled Falco Runtime Detection](../02-falco-runtime/README.md).
