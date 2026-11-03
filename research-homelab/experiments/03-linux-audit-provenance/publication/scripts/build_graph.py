#!/usr/bin/env python3
"""Build a sanitized, audit-supported process/file graph."""

import argparse
import os
from pathlib import Path

from audit_parser import get_field, load_events


def path_record(event):
    for line in event["records"]:
        if (
            line.startswith("type=PATH ")
            and "nametype=NORMAL" in line
        ):
            return line
    raise ValueError("Missing normal PATH record")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_dir", type=Path)
    parser.add_argument("output_dot", type=Path)
    args = parser.parse_args()

    events = load_events(args.evidence_dir)
    execs, reads, writes = [], [], []

    for event in events:
        if event["success"] != "yes":
            continue

        if event["syscall"] in ("59", "322"):
            execs.append(event)

        elif event["syscall"] == "257":
            flags = int(event["flags"], 16)
            access = flags & os.O_ACCMODE

            if access == os.O_RDONLY:
                reads.append(event)
            elif access == os.O_WRONLY:
                writes.append(event)

    if not (len(execs) == 2 and len(reads) == 1
            and len(writes) == 1):
        raise ValueError("Unexpected audit event structure")

    execs.sort(key=lambda event: event["serial"])
    parent, child = execs
    source, destination = reads[0], writes[0]

    if not (
        child["ppid"] == parent["pid"]
        and source["pid"] == child["pid"]
        and destination["pid"] == child["pid"]
    ):
        raise ValueError("Process relationships do not match")

    if not (
        parent["serial"] < child["serial"]
        < source["serial"] < destination["serial"]
    ):
        raise ValueError("Unexpected event ordering")

    write_flags = int(destination["flags"], 16)

    if not write_flags & os.O_TRUNC:
        raise ValueError("Expected truncating output operation")

    source_name = Path(
        get_field(path_record(source), "name")
    ).name

    destination_name = Path(
        get_field(path_record(destination), "name")
    ).name

    if (
        source_name != "test-data.txt"
        or destination_name != "output-data.txt"
    ):
        raise ValueError("Unexpected experiment files")

    dot = """digraph Experiment03F {
    rankdir=TB;
    nodesep=0.9;
    ranksep=1.1;
    graph [
        label="Experiment 03F - Audit-supported process/file relationships",
        labelloc=t,
        fontsize=16
    ];
    node [shape=box, style=rounded];

    parent [label="Python parent process"];
    child [label="Python child process"];
    source [label="Controlled source file"];
    destination [label="Controlled destination file"];

    parent -> child [
        label="Observed PPID association / execve"
    ];

    source -> child [
        label="Successful read-only openat"
    ];

    child -> destination [
        label="Successful write-only openat / O_TRUNC"
    ];
}
"""

    args.output_dot.parent.mkdir(
        parents=True, exist_ok=True
    )
    args.output_dot.write_text(dot, encoding="utf-8")

    print("Validation: PASSED")
    print("Graph:", args.output_dot)
    print("Processes: 2")
    print("File-access events: 2")
    print("Sensitive identifiers in graph: omitted")
    print("Limitation: Partial provenance reconstruction")


if __name__ == "__main__":
    main()
