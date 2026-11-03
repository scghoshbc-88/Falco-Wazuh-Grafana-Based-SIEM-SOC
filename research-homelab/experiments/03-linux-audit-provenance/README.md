# Experiment 03 — Linux Audit-supported partial provenance reconstruction

**Dates:** 2026-11-02–03 (America/Vancouver, UTC-07:00)  
**Status:** Controlled tests completed; evidence and generated graphs verified locally; no complete causal provenance graph claimed.  
**Environment:** Independent Ubuntu Machine B, Linux Audit (auditd/auditctl/ausearch), Python 3, Graphviz. No employer telemetry.

## Research question

Can low-cost Linux Audit telemetry support reproducible reconstruction of process ancestry and file-access relationships in an SME-style SOC laboratory? This is a **feasibility experiment**, not a detection-accuracy or analyst-effort comparison.

## Results at a glance

| Test | Audit serials | Observed relationship | Artifact |
| --- | --- | --- | --- |
| 03E: single process | 414, 415 | `cat` (PID 97847, PPID 93853) successfully executed and opened a controlled test file read-only | `provenance-03.dot`, `provenance-03.png` (local) |
| 03F: two Python processes | 703–706 | Parent Python PID 99117 executed; child PID 99118 executed with PPID 99117; child opened test file read-only and output file for writing/truncation | `provenance-03f.dot`, `provenance-03f.png` (local) |

**03F run ID:** `SOCEXP03F-20261103-000558`. The controlled script printed `PARENT_PID=99117 PPID=93853`, `CHILD_PID=99118 PPID=99117`, and completion messages. The resulting output contained the uppercase transformation of benign test data.

### Evidence-to-claim mapping

- **Audit 414**: successful `execve` for `cat` PID 97847, PPID 93853. **Audit 415**: same PID, successful `openat` with read-only flags on the test file (inode 791981, device 103:02).
- **Audit 703** (00:05:57.984): successful `execve` for Python parent PID 99117, PPID 93853.
- **Audit 704** (00:05:58.026): successful `execve` for Python child PID 99118, PPID 99117.
- **Audit 705** (00:05:58.063): successful `openat` of source file with `O_RDONLY|O_CLOEXEC`, child PID 99118, inode 791981.
- **Audit 706** (00:05:58.063): successful `openat` of destination with `O_WRONLY|O_CREAT|O_TRUNC|O_CLOEXEC`, child PID 99118, inode 791990.
- The Bash parent identity was separately corroborated with `ps` (PID 93853, started 21:15:11). No audit records matched that Bash PID under the scoped collection rules.

The file-open records do **not** independently prove that bytes were read or written, or that information flowed from source to destination. The process association uses recorded PPIDs; `fork`/`clone` events were **not captured**.

## Evidence handling

Original `ausearch --raw` exports, the local generator scripts, DOT files, and original PNGs were retained on the isolated laboratory machine. Four 03F raw exports contained 20 lines in total (6/6/4/4). A local `SHA256SUMS.txt` covered four raw exports, the 03F generator, DOT and PNG; **7/7 entries verified OK**, including after cleanup. The locally created experiment manifest is not covered by that earlier checksum list.

A final `auditctl -s` check showed `enabled 1`, `lost 0`, `backlog 0`, `backlog_limit 8192`. This is a point-in-time kernel counter observation, **not** proof of complete collection. All three temporary experiment-specific rules were removed; `auditctl -l` returned `No rules` while auditing remained enabled.

The operator visually inspected both original Graphviz PNGs on a separate laboratory desktop. **The actual PNG binaries and raw audit exports are not included in this documentation commit.** They should only be added following sanitization and a separate file-integrity review. Do not mistake the graph descriptions for independently uploaded image evidence.

## Reproduction and limitations

See [Methodology](methodology.md) for the scoped collection procedure and [Results and limitations](results.md) for event details and interpretation. Public paths and identifiers here are representative or limited to experiment PIDs/inodes; raw records contain private host/user/path metadata and are deliberately excluded.

**Next experiment:** capture process creation explicitly, use stronger process identity than PID alone, test telemetry loss and reconstruction completeness, and compare analyst-relevant outcomes with Falco/Wazuh baselines. No comparative performance claim is made here.
