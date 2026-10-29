#!/usr/bin/env python3
"""RSS и dirty-страницы ребёнка до/после изменения унаследованного списка."""
import os
import sys


def sizes() -> dict[str, int]:
    result = {"VmRSS": 0, "Shared_Dirty": 0, "Private_Dirty": 0}
    with open("/proc/self/status", encoding="ascii") as status:
        for line in status:
            if line.startswith("VmRSS:"):
                result["VmRSS"] = int(line.split()[1])
    with open("/proc/self/smaps_rollup", encoding="ascii") as rollup:
        for line in rollup:
            key = line.partition(":")[0]
            if key in ("Shared_Dirty", "Private_Dirty"):
                result[key] = int(line.split()[1])
    return result


data = list(range(2_000_000))
sys.stdout.flush()
pid = os.fork()
if pid == 0:
    before = sizes()
    for index in range(len(data)):
        data[index] = index + 1
    after = sizes()
    print(f"CHILD before KiB: {before}", flush=True)
    print(f"CHILD after KiB:  {after}", flush=True)
    os._exit(0)
os.waitpid(pid, 0)
print(f"PARENT data[0]={data[0]}: изменения ребёнка не видны родителю")
