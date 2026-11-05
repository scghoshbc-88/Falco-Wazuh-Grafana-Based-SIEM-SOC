#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "evidence" / "controlled-data.txt"
DATA.parent.mkdir(parents=True, exist_ok=True)

def report(role):
    print(
        f"{role}: PID={os.getpid()} "
        f"PPID={os.getppid()}",
        flush=True
    )

if len(sys.argv) == 1:
    report("PARENT")
    subprocess.run(
        [sys.executable, __file__, "child"],
        check=True
    )

elif sys.argv[1] == "child":
    report("CHILD")
    subprocess.run(
        [sys.executable, __file__, "grandchild"],
        check=True
    )

elif sys.argv[1] == "grandchild":
    report("GRANDCHILD")
    DATA.write_text("SOCEXP04 controlled test data\n")
    print(f"FILE_WRITTEN={DATA}", flush=True)
