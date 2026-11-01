# Experiment 01 — Controlled Authentication Telemetry (Preliminary)

**Date:** October 31, 2026 (local time UTC−07:00)  
**Status:** Preliminary; baseline event visibility demonstrated, original action-to-alert matching unresolved.  
**Environment:** Independent Ubuntu endpoint (Machine B), Wazuh agent 4.14.9, Wazuh manager/indexer/dashboard. No employer data.

## Objective

Determine whether a controlled authentication-related action on Machine B can be traced from the operator's ground-truth record through local journald telemetry to an indexed Wazuh alert. This is a **conventional SIEM baseline**, not a provenance graph or an attack-detection evaluation.

## Procedure and observations

1. On Machine B, the operator ran `date -Is; sudo -k; sudo -v; date -Is`. The first timestamp was `2026-10-31T23:45:58-07:00`; the last was `2026-10-31T23:46:06-07:00`. The command completed without a visible error.
2. A Wazuh Threat Hunting view filtered to `agent.name: ubuntusg` initially showed SSH authentication success (rule 5715) and PAM session opened (rule 5501) at approximately 23:44:58. These **preceded** the controlled sudo action and are not evidence of its detection.
3. A later Threat Hunting view showed three sudo/PAM alerts around 23:50:02: successful sudo to root (rule 5402), PAM session opened (5501), and PAM session closed (5502). The detail view identified agent ID 002, `location: journald`, `decoder.name: pam`, `predecoder.program_name: sudo`, and the PAM close event as rule 5502.
4. Local journal inspection covering 23:45–23:51 showed a sudo session at `2026-10-31T23:50:00-07:00` and close at `23:50:01-07:00`. The logged sudo command was `/usr/bin/journalctl` (PID 62124), executed as root. These events match the **subsequent investigation command**, not the original `sudo -v` action.
5. A narrower journal query for 23:45:45–23:46:20 returned no matching `sudo|pam_unix` lines in the screenshot. This does not establish whether the original action produced no journal record at all; only the shown filtered query is evidenced.

## Results and interpretation

| Claim | Status |
|---|---|
| Machine B connected to Wazuh | Previously verified |
| Machine B authentication events searchable | Verified |
| Sudo/PAM activity collected from journald and indexed as Wazuh alerts | Verified for the 23:50 journalctl sudo session |
| The original 23:46 `sudo -v` action produced an indexed alert | **Not demonstrated** |
| Full raw-log capture, causal dependency edges, or attack reconstruction | **Not tested** |

The difference between **event correlation** and **causal attribution** is material to the research question: timestamps and matching categories alone do not establish that a particular operator action caused an indexed alert.

## Evidence and reproducibility

Evidence was supplied as operator terminal and Wazuh dashboard screenshots during the October 31 session. The originals are retained privately; new screenshots from this experiment have **not yet been added** to the repository. Any future public copies must redact private addresses, browser URLs, and unnecessary identifiers.

Reproduction should use a unique run ID, capture timestamps with time-zone offsets, collect an unfiltered source-journal excerpt, and match the indexed event using timestamp, program, PID or other available attributes. A new controlled test should avoid confusing observation commands with test actions.

## Next checkpoint

Perform a single timestamped, harmless command on Machine B that reliably creates a journaled sudo session; inspect the local journal and the indexed Wazuh event, and record a unique run ID and matching fields. Do not infer provenance edges from SIEM alerts alone.

## Follow-up: uniquely identified sudo test — verified

**Run ID:** `SOCEXP01-20261031-235541` (31 October 2026, 23:55:41 UTC-07:00).

On Machine B, the operator executed `sudo /usr/bin/logger -t SOC-EXP01 "$RUN_ID controlled sudo test"`. The local journal recorded the sudo command under PID **62218**, a tagged logger message under PID **62221**, and sudo session-open/session-close entries. The exact run ID appeared in both the source journal and the Wazuh alert.

Wazuh Threat Hunting, filtered to agent `ubuntusg` (ID 002), displayed rule **5402** (`Successful sudo to ROOT executed`) for the original logger command. Its expanded event contains `data.command` with `/usr/bin/logger -t SOC-EXP01 SOCEXP01-20261031-235541 controlled sudo test` and `full_log` identifying `sudo[62218]`, with source log time `Nov 01 06:55:41` (UTC, corresponding to local 23:55:41). The event is marked as collected from `journald`. Rules **5501** and **5502** for PAM session open/close were also visible in the surrounding period. A later separate sudo invocation of `journalctl` (PID **62237**) produced additional alerts and is not conflated with the controlled test.

**Conclusion:** Exact command-level traceability from a controlled operator action to a local journal record and an indexed Wazuh rule-5402 alert is **verified** for this run. This demonstrates conventional SIEM collection and alerting, **not** causal provenance graph reconstruction. The tagged logger message's independent appearance as a Wazuh alert was not verified.

**Evidence:** Operator terminal screenshot showing the run ID and journal records, plus a Wazuh expanded event screenshot showing matching command, run ID, and PID. Before publishing screenshot binaries, sanitize private IP addresses, browser URLs, and unrelated host details.
