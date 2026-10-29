#!/usr/bin/env python3
import os
import sys
import time

sys.stdout.flush()
pid = os.fork()
if pid == 0:
    print(f"Ребёнок PID={os.getpid()}, исходный PPID={os.getppid()}", flush=True)
    time.sleep(2)
    print(f"После смерти родителя новый PPID={os.getppid()}", flush=True)
    os._exit(0)
print(f"Родитель PID={os.getpid()} завершается; ребёнок {pid} продолжает работу", flush=True)
