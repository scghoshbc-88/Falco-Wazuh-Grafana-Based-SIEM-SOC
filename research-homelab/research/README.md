# Research context and publication boundaries

**Project:** Provenance-Based Intrusion Detection in SME Environments Using Real-Time SOC Telemetry  
**Academic context:** Ongoing undergraduate BTech Cybersecurity and Digital Forensics research at BCIT.  
**Status:** Literature review and proposal in development; preliminary feasibility experiments available.

## Central research question

To what extent can provenance-assisted analysis identify and explain multi-stage cyberattacks using SOC telemetry available to resource-constrained SMEs, compared with conventional SIEM and runtime-security correlation against shared ground truth?

This work does not propose that Wazuh or Falco is itself a provenance-based intrusion detection system. It asks what defensible causal relationships can be reconstructed from instrumented commodity telemetry, and what information remains missing.

## Literature foundation

An ongoing thematic review covers **113 selected references**, grouped into **five themes and twelve sub-themes**: system provenance and reconstruction; PIDS scalability, learning and evaluation; SOC telemetry and analyst workload; SME and managed-service constraints; and emerging/adaptive threats. The review is a **structured thematic review**, not a systematic review with documented screening counts. Important source-level claims require full-text verification before publication. The complete academic review remains a working document and is not published here.

## Study design — proposed, not completed

- **A — Conventional SIEM:** Wazuh/Sysmon event- and rule-based analysis.
- **B — SIEM plus runtime security:** Wazuh and Falco correlated using timestamps and shared identifiers.
- **C — Provenance-assisted analysis:** Evidence-supported process/file/network relationships and lightweight tag propagation.
- **Conditions:** complete baseline, approximately 10% controlled event loss, and approximately 25% controlled event loss.
- **Design:** three analysis configurations crossed with three telemetry conditions; the same ground-truth attack scenarios should be evaluated across conditions.
- **Candidate scenarios:** persistence, credential compromise, lateral movement, and privilege escalation/data access. These scenarios have **not** been completed as the comparative experiment.
- **Outcomes:** attack-stage detection, precision/recall, false positives/negatives, causal-chain reconstruction, ATT&CK coverage, analyst evidence reviewed/time, latency, and resource cost.

The experimental protocol must define event-drop sampling, comparable sensor access, ground-truth annotation, and graph-edge confidence before results are compared. Any difference attributable to extra telemetry rather than analytical method must be identified.

## Evidence available today

The [home-lab experiments](../experiments/) demonstrate controlled Wazuh authentication events, Falco runtime monitoring and Wazuh ingestion, Linux Audit event interpretation, and a manually reconstructed process-creation/file-open chain in [Experiment 04](../experiments/04-process-file-provenance/results.md). They do **not** establish detection superiority, generalization to real SME attacks, or an automated PIDS.

## Responsible publication

No employer telemetry, personal data, credentials, private IP addresses, raw security logs, or student identifiers should be committed. The concept map and full review are maintained separately pending privacy and citation checks. Existing commit history must be reviewed separately from the current file tree.
