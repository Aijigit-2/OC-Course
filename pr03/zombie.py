#!/usr/bin/env python3
import os
import subprocess
import sys
import time

sys.stdout.flush()
pid = os.fork()
if pid == 0:
    os._exit(0)

time.sleep(1)
print(f"Состояние ребёнка {pid} до wait:")
subprocess.run(["ps", "-o", "pid,ppid,stat,cmd", "-p", str(pid)], check=True)
os.waitpid(pid, 0)
print("После wait статус забран, зомби удалён")
