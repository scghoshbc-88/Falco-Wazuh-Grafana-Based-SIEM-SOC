# Independent Research Home Lab

**Working research title:** Investigating the Practical Value of System Provenance for Security Incident Reconstruction in Resource-Constrained SOC Environments

## Purpose

This directory documents an independent, personally operated cybersecurity laboratory intended to support research into security-event correlation, causal reconstruction, and the practical investigative value of system provenance. It is separate from the earlier enterprise SIEM/SOC engineering documentation elsewhere in this repository.

The initial environment establishes a conventional SIEM telemetry baseline. **It is not yet a provenance-based intrusion detection system (PIDS).** Future experiments will investigate how event sequences can be reconstructed, what causal relationships can be established from available telemetry, and where ordinary SIEM alerts are insufficient.

## Implemented baseline (October 2026)

- **Host A:** Ubuntu 26.04 LTS physical machine running KVM/libvirt and a Wazuh agent.
- **Wazuh VM:** Ubuntu Server 24.04 LTS guest with Wazuh 4.14.9 manager, indexer and dashboard.
- **Host B:** Separate Ubuntu 26.04 LTS physical machine running a second Wazuh agent.
- **Connectivity:** The Wazuh VM resides on a libvirt NAT network. Restricted TCP forwarding on Host A allows Host B to communicate with the Wazuh manager.
- **Validation:** Both agents were observed active in the Wazuh dashboard; persistent systemd relay services were enabled and active; the TCP 1515 relay was verified to reject an unauthorized source. API reachability was confirmed, but successful authenticated API access is not yet documented.

The baseline above is based on recorded setup and troubleshooting sessions. Reproducible command logs, redacted screenshots, and experiment data will be added as they are reviewed.

## Research questions

1. What investigative context is lost when security events are analyzed as isolated SIEM alerts rather than as connected causal sequences?
2. How much attack reconstruction can be supported by telemetry obtainable from a resource-constrained, small-organization SOC?
3. How do missing events, collection overhead, and ambiguous dependencies affect the reliability of reconstruction?
4. What additional evidence is required to justify provenance relationships rather than merely time-ordered event correlations?

## Planned experiments — not yet completed

1. Establish reproducible benign and controlled adversarial activity in the isolated laboratory.
2. Collect and normalize relevant host and network telemetry.
3. Build incident timelines from Wazuh alerts and raw event records.
4. Explore provenance-oriented process, file and network relationships where the sensors support them.
5. Evaluate reconstruction completeness, analyst effort, false causal inferences and telemetry overhead.

## Evidence and reproducibility policy

- Do not commit passwords, API tokens, private keys, raw authentication logs, personal identifiers, or employer-specific information.
- Replace private addressing and machine-specific identifiers with descriptive placeholders in public examples.
- Record software versions, topology, configuration changes, test commands and validation criteria.
- Label observations as **verified**, **partially verified**, or **planned**.
- Distinguish a chronological incident timeline from a causally justified provenance graph.

## Project status

**Phase 1 — SIEM baseline established; evidence curation and controlled experiments in progress.**

This research directory is a work in progress, not a claim of a completed doctoral research contribution.

## Completed experiment records (November 2026)

- [Experiment 01 — Controlled Wazuh authentication telemetry](experiments/01-controlled-authentication/README.md)
- [Experiment 02A — Falco runtime detection](experiments/02-falco-runtime/README.md)
- [Experiment 02B — Falco JSON to Wazuh custom alert](experiments/02b-falco-wazuh-ingestion/README.md)
- [Experiment 03 — Linux Audit partial provenance reconstruction](experiments/03-linux-audit-provenance/README.md)

These are controlled feasibility demonstrations, not a complete PIDS or a measured comparison of detection accuracy. Raw source evidence remains private unless separately sanitized and published. The earlier baseline and planned-experiments sections describe the original project plan and should not be interpreted as the current experiment status.
