#!/usr/bin/env python3
"""ПР-4: CPU и I/O, 1/4 потока и 4 процесса, медиана трёх запусков."""
import argparse
import concurrent.futures
import multiprocessing as mp
import os
from pathlib import Path
import random
import statistics
import threading
import time
import urllib.request

WORKERS = 4


def generate(path: Path, count: int) -> None:
    random.seed(42)
    with path.open("w", encoding="ascii") as stream:
        for index in range(count):
            stream.write(f"{random.randrange(1000)}\n")
    print(f"Создан {path}: {count} чисел")


def part_sum(data: list[int], start: int, end: int) -> int:
    return sum(data[start:end])


def threaded_sum(data: list[int]) -> int:
    results = [0] * WORKERS
    threads = []
    for worker in range(WORKERS):
        start = len(data) * worker // WORKERS
        end = len(data) * (worker + 1) // WORKERS
        thread = threading.Thread(
            target=lambda s=start, e=end, w=worker: results.__setitem__(w, part_sum(data, s, e))
        )
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    return sum(results)


def process_entry(data: list[int], start: int, end: int, queue) -> None:
    queue.put(part_sum(data, start, end))


def process_sum(data: list[int]) -> int:
    context = mp.get_context("fork")
    queue = context.Queue()
    processes = []
    for worker in range(WORKERS):
        start = len(data) * worker // WORKERS
        end = len(data) * (worker + 1) // WORKERS
        process = context.Process(target=process_entry, args=(data, start, end, queue))
        processes.append(process)
        process.start()
    result = sum(queue.get() for _ in processes)
    for process in processes:
        process.join()
    return result


def median_time(function, repeats: int = 3) -> tuple[float, int]:
    timings = []
    result = 0
    for _ in range(repeats):
        started = time.perf_counter()
        result = function()
        timings.append(time.perf_counter() - started)
    return statistics.median(timings), result


def cpu(path: Path) -> None:
    started = time.perf_counter()
    data = [int(line) for line in path.read_text().splitlines()]
    print(f"Загрузка данных (вне замера): {time.perf_counter() - started:.3f} с")
    print(f"Чисел: {len(data)}; логических CPU: {os.cpu_count()}; повторов: 3")
    sequential, expected = median_time(lambda: sum(data))
    threaded, actual_threads = median_time(lambda: threaded_sum(data))
    processes, actual_processes = median_time(lambda: process_sum(data))
    assert expected == actual_threads == actual_processes
    print("РЕЖИМ             МЕДИАНА, с    УСКОРЕНИЕ")
    print(f"1 поток           {sequential:10.3f}    1.00x")
    print(f"4 потока          {threaded:10.3f}    {sequential / threaded:.2f}x")
    print(f"4 процесса        {processes:10.3f}    {sequential / processes:.2f}x")
    print(f"Контрольная сумма: {expected}")


def fetch(url: str) -> int:
    with urllib.request.urlopen(url, timeout=30) as response:
        return len(response.read())


def pool_fetch(urls: list[str], executor_class) -> int:
    with executor_class(max_workers=WORKERS) as executor:
        return sum(executor.map(fetch, urls))


def network(path: Path) -> None:
    urls = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    print(f"URL: {len(urls)}; повторов: 3; рабочих: {WORKERS}")
    sequential, expected = median_time(lambda: sum(fetch(url) for url in urls))
    threaded, actual_threads = median_time(
        lambda: pool_fetch(urls, concurrent.futures.ThreadPoolExecutor)
    )
    processes, actual_processes = median_time(
        lambda: pool_fetch(urls, concurrent.futures.ProcessPoolExecutor)
    )
    assert expected == actual_threads == actual_processes
    print("РЕЖИМ             МЕДИАНА, с    УСКОРЕНИЕ")
    print(f"Последовательно   {sequential:10.3f}    1.00x")
    print(f"4 потока          {threaded:10.3f}    {sequential / threaded:.2f}x")
    print(f"4 процесса        {processes:10.3f}    {sequential / processes:.2f}x")
    print(f"Получено байт: {expected}")


def memory() -> None:
    shared = [0] * 5
    thread = threading.Thread(target=shared.append, args=(1,))
    thread.start()
    thread.join()
    print(f"После потока список в родителе: {shared}")
    process = mp.get_context("fork").Process(target=shared.append, args=(2,))
    process.start()
    process.join()
    print(f"После процесса список в родителе: {shared}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--path", type=Path, default=Path("numbers.txt"))
    gen.add_argument("--count", type=int, default=10_000_000)
    cpu_parser = sub.add_parser("cpu")
    cpu_parser.add_argument("--path", type=Path, default=Path("numbers.txt"))
    net = sub.add_parser("network")
    net.add_argument("--urls", type=Path, default=Path("urls.txt"))
    sub.add_parser("memory")
    args = parser.parse_args()
    if args.command == "generate":
        generate(args.path, args.count)
    elif args.command == "cpu":
        cpu(args.path)
    elif args.command == "network":
        network(args.urls)
    else:
        memory()


if __name__ == "__main__":
    main()
