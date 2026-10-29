#!/usr/bin/env python3
"""Дерево процессов текущего пользователя только по данным /proc."""
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class Process:
    pid: int
    ppid: int
    name: str
    state: str
    rss_kib: int


def read_process(directory: Path) -> Process | None:
    try:
        values = {}
        for line in (directory / "status").read_text().splitlines():
            key, _, value = line.partition(":")
            values[key] = value.strip()
        uid = int(values["Uid"].split()[0])
        if uid != os.getuid():
            return None
        return Process(
            pid=int(values["Pid"]),
            ppid=int(values["PPid"]),
            name=values["Name"],
            state=values["State"].split()[0],
            rss_kib=int(values.get("VmRSS", "0 kB").split()[0]),
        )
    except (FileNotFoundError, ProcessLookupError, PermissionError, KeyError, ValueError):
        return None


def main() -> None:
    processes = {}
    for directory in Path("/proc").iterdir():
        if directory.name.isdigit():
            process = read_process(directory)
            if process:
                processes[process.pid] = process
    children = {pid: [] for pid in processes}
    roots = []
    for process in processes.values():
        if process.ppid in children:
            children[process.ppid].append(process.pid)
        else:
            roots.append(process.pid)

    def show(pid: int, depth: int) -> None:
        process = processes[pid]
        print(
            f"{'  ' * depth}{process.name} PID={process.pid} "
            f"STATE={process.state} RSS={process.rss_kib} KiB"
        )
        for child in sorted(children[pid]):
            show(child, depth + 1)

    for root in sorted(roots):
        show(root, 0)


if __name__ == "__main__":
    main()
