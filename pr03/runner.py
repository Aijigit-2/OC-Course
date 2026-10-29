#!/usr/bin/env python3
"""Запускает одну команду в N дочерних процессах через fork + exec."""
import argparse
import os
import sys
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-n", "--count", type=int, default=2)
parser.add_argument("command", nargs=argparse.REMAINDER)
args = parser.parse_args()
if args.count < 1 or not args.command:
    parser.error("нужны N >= 1 и команда, например: -n 3 sleep 1")

children = []
sys.stdout.flush()
for number in range(args.count):
    started = time.perf_counter()
    pid = os.fork()
    if pid == 0:
        try:
            os.execvp(args.command[0], args.command)
        except OSError as error:
            print(f"exec: {error}", file=sys.stderr, flush=True)
            os._exit(127)
    children.append((number + 1, pid, started))

failed = False
for number, pid, started in children:
    _, status = os.waitpid(pid, 0)
    elapsed = time.perf_counter() - started
    if os.WIFEXITED(status):
        code = os.WEXITSTATUS(status)
    else:
        code = 128 + os.WTERMSIG(status)
    failed = failed or code != 0
    print(f"job={number} pid={pid} exit={code} time={elapsed:.3f}s")
sys.exit(1 if failed else 0)
