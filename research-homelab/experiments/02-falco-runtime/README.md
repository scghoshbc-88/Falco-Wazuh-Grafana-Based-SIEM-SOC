# Experiment 02A — Controlled Falco Runtime Detection

**Date:** 2026-11-01 (UTC-07:00)  
**Status:** Verified controlled Falco alert; SIEM ingestion and full provenance reconstruction not tested.  
**Environment:** Independent Ubuntu 26.04.1 LTS Machine B; Linux 7.0.0-38-generic; Falco 0.45.2 using the modern eBPF driver. No employer telemetry.

## Objective

Evaluate whether Falco captures useful runtime context for a deliberately generated file-access event, as a complement to the Wazuh authentication telemetry baseline in Experiment 01.

## Prerequisites verified

- `falco-modern-bpf.service` was active.
- Falco logged `Opening 'syscall' source with modern BPF probe` and started its ring engine.
- Prior spontaneous alerts demonstrated that Falco was processing file-access events.

## Controlled procedure

On Machine B, the operator ran:

```bash
RUN_ID="SOCEXP02-$(date +%Y%m%d-%H%M%S)"
echo "RUN_ID=$RUN_ID"
date -Is
sudo cat /etc/shadow > /dev/null
date -Is
```

**Run ID:** `SOCEXP02-20261101-005026`  
**Test interval:** 2026-11-01 00:50:26 to 00:50:27 UTC-07:00.

The command read a sensitive local file without displaying its contents or modifying it. The run ID is a test-session label; it was **not embedded in the Falco event**.

To capture the matching alert with precise source-journal timestamp, the operator queried:

```bash
sudo journalctl -u falco-modern-bpf.service \
  --since "2026-11-01 00:50:20" \
  --until "2026-11-01 00:50:35" \
  -o short-iso-precise --no-pager
```

## Observed result

The journal showed one matching Falco warning at **2026-11-01T00:50:27.015532-07:00**, with the rule output `Sensitive file opened for reading by non-trusted program`.

| Field | Observed value |
|---|---|
| Severity | Warning |
| File | `/etc/shadow` |
| Event type | `openat` |
| Process | `cat` |
| Process executable | `/usr/lib/cargo/binutils/cat` |
| Command | `cat /etc/shadow` |
| Parent | `sudo` |
| Grandparent | `bash` |
| Great-grandparent | `sshd-session` |
| Effective user | root |
| Container ID | host |

The command, target path, process context and timestamp correspond to the controlled test. The operator-reported Falco output timestamp was `00:50:27.015019879`, distinct from the journal timestamp. The original terminal display is not reproduced in this repository.

## Interpretation

**Verified:** Falco 0.45.2 on this Linux 7.0 kernel captured and alerted on the controlled sensitive-file read using modern eBPF. The alert provided process, ancestor-process, file and syscall context.

**Not verified:** An independent raw-syscall archive, complete process/file dependency graph, durable causal edges, attack reconstruction, Wazuh ingestion of this Falco alert, or comparative detection effectiveness. The alert is a rule-triggered runtime observation, not a provenance graph. No inference of malicious intent is warranted for this deliberately benign test.

## Evidence

The controlled command, matching Falco warning, and precise journal timestamp were reviewed from operator-provided terminal output during the experiment. **No screenshot or raw journal export has been committed to this repository for Experiment 02A.** Consequently, this README is a documented observation record, not independently inspectable primary evidence. A sanitized journal excerpt or screenshot may be added later only if the original source can be retrieved and verified; it must not be recreated and represented as contemporaneous evidence.

## Next checkpoint

**Subsequently completed in Experiment 02B (2026-11-02):** Falco JSON output was collected by the Wazuh agent, received by the manager, and matched by custom rule `100700` (level 8) during a live controlled test. The alert included the Falco rule name, source file, process, and ancestry context. The corresponding raw archive and alert evidence remain local; they are not published here. This confirms SIEM ingestion and alerting, **not** a complete provenance graph. See the [Experiment 02B record](../02b-falco-wazuh-ingestion/README.md) for the verified pipeline, event-to-alert mapping, and evidence limitations.
