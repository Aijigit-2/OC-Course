#!/usr/bin/env python3
"""Пять философов: naive, ordered и waiter; meals приёмов пищи у каждого."""
import argparse
import threading
import time


def run(mode: str, meals: int) -> None:
    count = 5
    forks = [threading.Lock() for _ in range(count)]
    waiter = threading.Semaphore(count - 1)
    start = threading.Barrier(count)
    all_left = threading.Barrier(count)
    eaten = [0] * count

    def philosopher(index: int) -> None:
        left, right = forks[index], forks[(index + 1) % count]
        start.wait()
        for _ in range(meals):
            if mode == "waiter":
                waiter.acquire()
            first, second = (left, right)
            if mode == "ordered" and index == count - 1:
                first, second = right, left
            first.acquire()
            if mode == "naive":
                all_left.wait()  # гарантированно: все держат левую вилку
            second.acquire()
            eaten[index] += 1
            time.sleep(0.001)
            second.release()
            first.release()
            if mode == "waiter":
                waiter.release()

    threads = [threading.Thread(target=philosopher, args=(i,)) for i in range(count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print(f"{mode}: OK; meals={eaten}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["naive", "ordered", "waiter"])
    parser.add_argument("--meals", type=int, default=20)
    args = parser.parse_args()
    run(args.mode, args.meals)
