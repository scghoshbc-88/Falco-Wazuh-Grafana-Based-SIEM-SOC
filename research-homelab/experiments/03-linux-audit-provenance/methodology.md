# Experiment 03 — Methodology and reproducibility

## Scope

A benign, isolated Linux laboratory test of event-to-graph reconstruction. Linux Audit supplies system-call records; Python scripts convert selected records to Graphviz DOT; Graphviz renders PNG images. This is **not** a deployment of a complete provenance collector.

## Preparation and collection

1. Confirm `auditd` is running and record `sudo auditctl -s`.
2. Create a dedicated experiment directory with benign `test-data.txt` and an existing `output-data.txt` (the write watch is inode-specific).
3. Install **temporary** watches on the controlled files and an execution rule scoped to the laboratory user's effective UID. Substitute the actual user ID and experiment directory; do not copy another person's home path.
4. Record `sudo auditctl -l` and the experiment's run identifier.
5. Run the benign scenarios, record printed PIDs and PPIDs, and use `sudo ausearch -p <PID> -i` to correlate events.
6. Export the **original** records using `sudo ausearch -a <SERIAL> --raw`; preserve exports before editing or sanitizing.
7. Validate successful `execve` and `openat` calls, correlate PID/PPID/session/time, and extract file identity from `PATH` records (device + inode + path).
8. Generate DOT, render PNG with `dot -Tpng input.dot -o output.png`, and record file hashes.
9. Verify the SHA-256 manifest with `sha256sum -c`, inspect `auditctl -s`, remove only the experiment's own temporary rules, and verify again.

Example temporary rules (replace `$LAB` and `$UID_NUMBER`):

```bash
LAB="$HOME/pids-lab/experiment-03"
UID_NUMBER="$(id -u)"
sudo auditctl -w "$LAB/test-data.txt" -p r -k pids_exp03_read
sudo auditctl -w "$LAB/output-data.txt" -p w -k pids_exp03_write
sudo auditctl -a always,exit -F arch=b64 -S execve -S execveat -F euid="$UID_NUMBER" -k pids_exp03_exec
sudo auditctl -l
```

These are old-style watches and can have performance costs. Use only in the isolated test environment; avoid broad persistent execution monitoring. The experiment removed these three rules individually and confirmed `No rules` afterward. Do not indiscriminately flush all audit rules on a shared host.

## Controlled scenario 03F

The operator ran a Python parent which used `subprocess.run([sys.executable, script_path, "--child"], check=True)`. The child read the benign source with `Path.read_text()` and wrote `data.upper()` with `Path.write_text()`. The script printed parent and child PIDs/PPIDs and completion markers. The observed output matched the expected uppercase transformation.

**Run:** `SOCEXP03F-20261103-000558` (local time). Audit event serials 703–706 are **specific to this execution**, not stable identifiers for future reproductions.

## Parsing and graph semantics

- Group Linux Audit record lines by the common `msg=audit(timestamp:serial)` event identity; each event can contain `SYSCALL`, `PATH`, `EXECVE`, `CWD`, and `PROCTITLE` records.
- Parse **raw** syscall flags numerically. `ausearch --raw` records `a2` as a hexadecimal bitmask, while `ausearch -i` may display `O_RDONLY` or `O_WRONLY` text. The initial 03F parser incorrectly searched for the text in raw `a2`; the operator corrected it and successfully generated the graph.
- Treat `execve` as execution, `openat(O_RDONLY)` as a successful read-only **open**, and `openat(O_WRONLY|O_TRUNC)` as a successful write-capable **open**, not proof of completed byte transfer.
- Represent parent-child relationships as **PPID associations**, not observed process-creation events. Do not infer complete causality from matching PID alone: PID reuse and missing events are possible.
- Distinguish directly observed audit attributes from corroboration by process inspection or script output.

## Privacy and publication

Do not commit unreviewed raw audit logs, local usernames, home paths, hostnames, private IPs, secrets, or unredacted desktop screenshots. Publish sanitized examples only when independently checked. Original evidence and its hashes remain in private local storage; screenshots are secondary to raw records.

## Repeatability

A new run should use its **own** event serials, timestamps, file inode/device identifiers and checksum manifest. The documented historical IDs must not be hardcoded into a general-purpose reconstruction algorithm.
