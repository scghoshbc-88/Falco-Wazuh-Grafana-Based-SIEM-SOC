#!/usr/bin/env python3
"""Minimal parser for Linux Audit raw event records."""

import re
from pathlib import Path


def get_field(line, name):
    """Extract a named field from an audit record."""
    pattern = (
        rf'(?:^|\s){re.escape(name)}='
        rf'(?:"([^"]*)"|(\S+))'
    )

    match = re.search(pattern, line)

    if not match:
        raise ValueError(f"Missing audit field: {name}")

    return match.group(1) if match.group(1) is not None else match.group(2)


def load_events(directory):
    """Load audit events without assuming specific serial numbers."""
    directory = Path(directory)
    events = []

    for path in sorted(directory.glob("*.audit")):
        records = path.read_text(encoding="utf-8").splitlines()

        syscall = next(
            (line for line in records
             if line.startswith("type=SYSCALL ")),
            None,
        )

        if syscall is None:
            continue

        match = re.search(
            r'msg=audit\([^:]+:(\d+)\)',
            syscall,
        )

        if not match:
            raise ValueError(f"Invalid audit event: {path.name}")

        events.append({
            "serial": int(match.group(1)),
            "syscall": get_field(syscall, "syscall"),
            "pid": get_field(syscall, "pid"),
            "ppid": get_field(syscall, "ppid"),
            "success": get_field(syscall, "success"),
            "flags": get_field(syscall, "a2"),
            "records": records,
        })

    return events


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_dir")
    args = parser.parse_args()

    events = load_events(args.evidence_dir)

    for event in events:
        print(
            f"serial={event['serial']} "
            f"syscall={event['syscall']} "
            f"pid={event['pid']} "
            f"ppid={event['ppid']} "
            f"success={event['success']}"
        )

    print(f"Loaded {len(events)} audit events")
