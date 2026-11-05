# Experiment 04 — Results

## Run identification

Run: SOCEXP04B-20261104-224858

Date: November 4, 2026

## Verified audit events

| Event | Syscall | Observed result |
|---|---|---|
| 1406 | execve | Parent PID 12988 executed successfully |
| 1408 | clone3 | PID 12988 created PID 12990 |
| 1409 | execve | Child PID 12990 executed successfully |
| 1414 | clone3 | PID 12990 created PID 12995 |
| 1415 | execve | Grandchild PID 12995 executed successfully |
| 1419 | openat | PID 12995 opened controlled-data.txt in write mode |

All six records refer to the November 4, 2026 execution window.

## Reconstructed relationships

Parent (12988)
  -> Child (12990)
  -> Grandchild (12995)
  -> controlled-data.txt

The file-access edge represents a successful write-mode openat call.

The openat record included:

- success=yes
- O_WRONLY
- O_CREAT
- O_TRUNC
- O_CLOEXEC

The controlled test script reported writing the file, and a subsequent
content check confirmed the expected test string.

The audit record itself does not establish a completed write syscall
or byte-level data transfer.

## Evidence integrity

The following raw evidence exports passed SHA-256 verification:

- 04b-process-create.audit
- 04b-process-exec.audit
- 04b-file-access.audit

The audit subsystem reported:

- lost: 0
- backlog: 0

Temporary experiment rules were subsequently removed.

## Interpretation

Linux Audit records provided sufficient information to reconstruct
the observed process-creation hierarchy and associate the grandchild
process with a successful write-mode file-open operation.

This establishes a preliminary provenance reconstruction capability
for the controlled scenario.

It does not yet demonstrate superior intrusion detection or
investigative performance compared with conventional SIEM monitoring.

## Next research steps

1. Evaluate a controlled multi-stage security scenario.
2. Compare alert-only and provenance-enriched investigation.
3. Introduce controlled telemetry loss.
4. Measure reconstruction completeness and analyst effort.
5. Assess operational overhead and limitations.
