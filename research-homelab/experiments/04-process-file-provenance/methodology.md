# Experiment 04 — Methodology

## Design

A controlled Linux process hierarchy was generated using Python
subprocess execution.

The sequence was:

1. Parent Python process starts.
2. Parent creates and executes a child Python process.
3. Child creates and executes a grandchild Python process.
4. Grandchild opens a controlled text file for writing.
5. The resulting file content is checked.

## Telemetry

Linux Audit was configured temporarily to collect:

- Process creation: fork, vfork, clone, clone3.
- Process execution: execve, execveat.
- Write and attribute-change activity in the experiment evidence directory.

The audit rules were scoped to the experimental user where supported.
The directory watch was scoped to the experiment evidence directory.

## Evidence collection

Run identifier: SOCEXP04B-20261104-224858

Execution window:
2026-11-04 22:48:58 to 22:48:59, UTC-07:00.

Relevant audit records were identified using event timestamps,
audit serial numbers, process identifiers, syscall results, and
associated PATH and PROCTITLE records.

The evidence was exported in raw audit format and checked using SHA-256.

## Reconstruction procedure

Successful clone3 syscall return values were matched to the PIDs
of subsequently executed child processes.

Successful execve records were used to confirm execution.

The grandchild's successful write-mode openat operation was linked
to the target file using the audit PATH record.

The resulting relationships were represented in Graphviz.

## Evidence handling

Original audit evidence remains in private local storage.

Public figures and supporting summaries are derived from verified
audit records. They are not substitutes for the original records.

Temporary audit rules were removed after collection.

## Limitations

The experiment used a deliberately controlled workload.

The successful openat call demonstrates write-mode file opening,
not independently verified byte-level writes.

Process identifiers and audit serial numbers are local identifiers
and should be interpreted alongside timestamps and execution context.

The experiment does not measure detection accuracy, false positives,
attack reconstruction performance, or generalization to real incidents.

Audit health showed zero lost events at the observed checkpoints;
this does not establish that all possible system activity was captured.
