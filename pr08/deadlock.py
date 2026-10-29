#!/usr/bin/env python3
"""Намеренный deadlock. Остановка: Ctrl+C или timeout 3s python3 deadlock.py."""
import threading

lock_a = threading.Lock()
lock_b = threading.Lock()
first_taken = threading.Barrier(2)


def worker(name, first, second):
    with first:
        print(f"{name}: захватил первый lock", flush=True)
        first_taken.wait()
        with second:
            print(f"{name}: это сообщение не появится", flush=True)


a = threading.Thread(target=worker, args=("T1", lock_a, lock_b))
b = threading.Thread(target=worker, args=("T2", lock_b, lock_a))
a.start(); b.start(); a.join(); b.join()
