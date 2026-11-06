# Experiment 05 — Process-chain provenance and telemetry-loss sensitivity

**Research status:** Completed controlled feasibility run; simulation model requires independent validation before generalization.  
**Run ID:** `SOCEXP05-RUN02-20261106T040501Z`  
**Date:** 2026-11-05 (local); 2026-11-06 (UTC)  
**Environment:** Independent, isolated home research lab. No employer telemetry or configuration is included.  
**Research focus:** Can Linux Audit and Falco jointly support reconstruction of a known process lineage, and how does a simple synthetic telemetry-loss model affect reconstruction?

## Research question and scope

This is a narrow, controlled proof of feasibility for process-level provenance reconstruction in a small SOC telemetry environment. It is **not** an evaluation of malicious-activity detection accuracy, attack attribution, enterprise coverage, or the performance of a production SIEM. A separate Wazuh alert confirms one end-to-end ingestion path, but is **not** from the same execution as the process-chain baseline.

## Controlled procedure and ground truth

A Python process invoked a shell, which executed `id`. The expected directed process graph contained two edges:

```text
python3 (PID 22254)
    | clone3
    v
sh (PID 22257)
    | vfork
    v
id (PID 22258)
```

PIDs are ephemeral identifiers from this one run, not stable host identifiers. The process executable observed for `id` was `/usr/lib/cargo/bin/coreutils/id`.

### Independent observations

| Source | Observed evidence | Interpretation |
|---|---|---|
| Linux Audit | Successful `clone3`, parent 22254, return/child PID 22257 | Python-to-shell creation edge |
| Linux Audit | Successful `vfork`, parent 22257, return/child PID 22258 | Shell-to-id creation edge |
| Linux Audit | `execve` for PID 22258, PPID 22257, executable `/usr/lib/cargo/bin/coreutils/id` | Corroborates execution of the child |
| Falco | Rule `SOC Experiment 05 Process Execution`, `proc.pid=22258`, `proc.ppid=22257`, `proc.name=id`, `proc.pname=sh` | Independently corroborates shell-to-id edge |
| Wazuh | Production rule 100705, agent 002, `id` process PID 23077 | Verified alert ingestion **for a separate controlled execution**, not the baseline chain |

The Falco baseline event timestamp was `2026-11-06T04:05:01.137555122Z`. The distinct Wazuh alert occurred at `2026-11-05T22:49:04.053-0700`. These events must not be treated as one correlated execution.

## Baseline reconstruction

| Metric | Result |
|---|---:|
| Expected directed process edges | 2 |
| Linux Audit confirmed edges | 2 |
| Falco corroborated edges | 1 |
| Union of reconstructed edges | 2 |
| Process-edge completeness | 100% |

**Definition:** process-edge completeness = reconstructed ground-truth directed edges / expected ground-truth directed edges. This metric is specific to the two-edge test chain and does not imply complete system-wide provenance.

## Synthetic telemetry-loss analysis

The analysis program `evaluate_exp05.py` was executed after a timestamp-filter correction so it could parse the saved audit format. The experiment ran **1,000 simulation iterations per loss condition**, producing 3,000 result rows plus a CSV header. Reported values are:

| Nominal synthetic loss | Simulations | Mean edge completeness | Complete-chain rate |
|---|---:|---:|---:|
| 0% | 1,000 | 100.0% | 100.0% |
| 10% | 1,000 | 95.1% | 90.2% |
| 25% | 1,000 | 84.4% | 70.5% |

**Interpretation:** Under the implemented simulation, higher nominal loss corresponded to lower observed reconstruction completeness. These are *model outputs*, not observed sensor packet-loss rates or measured SIEM ingestion failure rates. The sampling unit is a simulated removal applied to one observed two-edge chain; 1,000 repetitions do **not** represent 1,000 independent attacks or endpoint traces. The exact event-drop assumptions, random seed, and independence structure must be reviewed against the original `evaluate_exp05.py` before this simulation is used for comparative claims.

## Evidence integrity and reproducibility

The following checks passed on the research host:

- Eight original source files passed `sha256sum -c SHA256SUMS-FINAL.txt`.
- Three baseline artifacts passed `sha256sum -c EXP05-BASELINE-SHA256SUMS.txt`.
- Three analysis artifacts passed `sha256sum -c analysis/EXP05-ANALYSIS-SHA256SUMS.txt`.
- `analysis/EXP05-LOSS-RESULTS.csv` contained 3,001 lines (header + 3,000 simulation rows).

The source bundle contained Audit execution/process extracts, Falco event JSONL, ground truth, run identifier, UTC timestamps, and the separate Wazuh alert. The original host-specific raw files and full manifests remain in private research storage; they are **not** included in this public documentation because they can contain usernames, addresses, machine identifiers, and operational metadata.

**Local-only verification commands (run against the private evidence bundle):**

```bash
cd /root/research-evidence/experiment-05
sha256sum -c SHA256SUMS-FINAL.txt
sha256sum -c EXP05-BASELINE-SHA256SUMS.txt
(cd analysis && sha256sum -c EXP05-ANALYSIS-SHA256SUMS.txt)
wc -l analysis/EXP05-LOSS-RESULTS.csv
cat analysis/EXP05-LOSS-SUMMARY.json
```

These commands are a record of the local verification workflow, **not** a claim that the private bundle is available in this repository. A fully reproducible public package would additionally require reviewed/sanitized inputs, the exact analysis script, explicit loss-model assumptions and dependency/environment metadata.

## Limitations and next experiments

1. **Single benign scenario:** only one known `python3 → sh → id` chain was assessed. No multi-stage intrusion or general detection accuracy was measured.
2. **Partial cross-sensor overlap:** Falco corroborated the second edge, while Linux Audit supplied both; this is not full multi-sensor provenance coverage.
3. **Wazuh evidence is separate:** alert 100705 proves ingestion for another controlled run, not end-to-end correlation of the baseline process IDs.
4. **Synthetic loss:** the model does not establish behavior under real collector failures, burst loss, correlated loss, or adversarial telemetry suppression.
5. **Small ground-truth graph:** completeness on two edges is highly sensitive to event definitions and cannot be generalized to long attack chains.
6. **Method validation pending:** public reproducibility requires reviewing the exact simulation implementation, its randomization, and the mapping between removed records and reconstructed edges.

**Proposed next work:** replay multiple controlled multi-stage scenarios with independent ground-truth timelines; compare Audit-only, Falco-only, and combined reconstruction; test random versus burst/correlated loss; measure false edges, reconstruction time, analyst effort, and resource overhead.

## Research provenance

Prepared from verified terminal outputs and hash-check results for the independent home-lab Experiment 05. This record distinguishes directly observed process relationships from synthetic sensitivity analysis and a separate Wazuh alert. No raw production or employer data is published.
