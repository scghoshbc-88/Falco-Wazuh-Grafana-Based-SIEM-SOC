# Experiment 03 — Results, interpretation and limitations

## Verified observations

| Run | Event | Local timestamp (UTC-07:00) | Evidence |
| --- | --- | --- | --- |
| 03E | 414 | 2026-11-02 22:59:34.798 | `cat` PID 97847 executed successfully; PPID 93853 |
| 03E | 415 | 2026-11-02 22:59:34.802 | Same PID opened test-data.txt read-only; inode 791981, device 103:02 |
| 03F | 703 | 2026-11-03 00:05:57.984 | Python parent PID 99117 executed; PPID 93853 |
| 03F | 704 | 2026-11-03 00:05:58.026 | Python child PID 99118 executed; PPID 99117 |
| 03F | 705 | 2026-11-03 00:05:58.063 | Child opened test-data.txt read-only; inode 791981 |
| 03F | 706 | 2026-11-03 00:05:58.063 | Child opened output-data.txt with write/create/truncate flags; inode 791990 |

**Observed file transformation:** the controlled output was `PIDS CONTROLLED EXPERIMENT - BENIGN TEST DATA`. The script's printed parent/child PIDs and PPIDs matched the audit records. Successful `openat` operations were recorded; individual `read`/`write` syscalls and byte-level flow were not audited in this experiment.

## Graph artifacts

- **Figure 3.1 — Single-process audit-supported graph:** Bash PID 93853 (identity corroborated by `ps`) → `cat` PID 97847 (audit 414) → test file (audit 415). The Bash-to-`cat` edge represents a PPID association.
- **Figure 3.2 — Multi-process audit-supported graph:** Python parent PID 99117 → Python child PID 99118 (PPID association, audit 703–704); source file → child (read-only open, audit 705); child → destination file (write-capable open, audit 706). The file edges indicate opening operations, **not** proven dataflow.

The operator generated `provenance-03.png` (529 × 379) and `provenance-03f.png` (633 × 379) using Graphviz and visually inspected both on the laboratory desktop. These PNGs are retained locally, not embedded in this commit.

## Evidence preservation

The 03F raw audit export comprises four files with 6, 6, 4 and 4 lines respectively. A checksum manifest was generated for those files plus the 03F generator, DOT and PNG. All seven checksum verifications returned `OK`, including a post-cleanup recheck. The manifest created later was outside that checksum set. This establishes consistency **since hashing**, not independent proof of acquisition time or an externally attested chain of custody.

Final audit status: enabled, `lost=0`, `backlog=0`, `backlog_limit=8192`; experiment rules removed (`No rules`). Zero kernel-reported loss does not establish full event coverage or downstream completeness.

## Limitations and threats to validity

1. **Incomplete causal capture:** no `fork`/`clone`, `read`/`write` byte counts, socket flow, or full dependency edges were recorded.
2. **Process identity:** PID/PPID and timestamps are useful but do not alone prevent PID-reuse errors or establish historical ancestry when parent creation was not audited.
3. **Selective collection:** narrow watches capture only chosen files; absence of an event elsewhere is not evidence of absence.
4. **Small, benign scenario:** one controlled run of each scenario, with no adversarial activity, realistic workload, attack ground-truth scoring or comparative sample.
5. **Operational metrics:** no measured precision, recall, F1, analyst time, resource overhead, or resilience under deliberately injected telemetry loss.
6. **Graph semantics:** direction and labels represent observed open operations and PPID association; they should not be mistaken for full information-flow provenance.

## Conclusion

Linux Audit supplied sufficient evidence to reconstruct **selected** process-execution and file-open relationships and render repeatable partial graphs from preserved records. This establishes feasibility for the next phase, not that provenance-based detection outperforms Falco/Wazuh or improves SME analyst outcomes. Those claims require a separately designed, measured comparison.
