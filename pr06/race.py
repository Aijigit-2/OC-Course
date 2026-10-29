#!/usr/bin/env python3
"""Намеренно небезопасный счётчик для демонстрации гонки."""
import threading
import time

counter = 0
started = time.perf_counter()


def worker() -> None:
    global counter
    for _ in range(100_000):
        counter += 1


threads = [threading.Thread(target=worker) for _ in range(4)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
print(f"Результат: {counter}; ожидалось: 400000; время: {time.perf_counter() - started:.3f} с")
assert counter == 400_000, "Обнаружено состояние гонки: инкременты потеряны"
