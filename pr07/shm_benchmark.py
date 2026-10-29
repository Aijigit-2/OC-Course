#!/usr/bin/env python3
"""Передача array('q') через shared_memory и Pipe; n=10_000_000 по умолчанию."""
import argparse
import array
import multiprocessing as mp
from multiprocessing import shared_memory
import time


def shm_reader(name: str, expected: int, queue) -> None:
    segment = shared_memory.SharedMemory(name=name)
    try:
        values = memoryview(segment.buf).cast("q")
        queue.put((len(values), sum(values)))
        assert len(values) == expected
        values.release()
    finally:
        segment.close()


def pipe_reader(connection, expected_bytes: int, queue) -> None:
    chunks = []
    received = 0
    while received < expected_bytes:
        chunk = connection.recv_bytes()
        chunks.append(chunk)
        received += len(chunk)
    values = array.array("q")
    values.frombytes(b"".join(chunks))
    queue.put((len(values), sum(values)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=10_000_000)
    args = parser.parse_args()
    context = mp.get_context("spawn")
    data = array.array("q", range(args.count))
    raw = data.tobytes()
    expected = (args.count, sum(data))
    print(f"Элементов: {args.count}; байт: {len(raw)}")

    segment = shared_memory.SharedMemory(create=True, size=len(raw))
    try:
        segment.buf[:] = raw
        queue = context.Queue()
        process = context.Process(target=shm_reader, args=(segment.name, args.count, queue))
        started = time.perf_counter()
        process.start()
        actual = queue.get()
        process.join()
        shared_time = time.perf_counter() - started
        assert actual == expected
        print(f"shared_memory: {shared_time:.4f} с; сумма={actual[1]}")
    finally:
        segment.close()
        segment.unlink()

    receive, send = context.Pipe(duplex=False)
    queue = context.Queue()
    process = context.Process(target=pipe_reader, args=(receive, len(raw), queue))
    started = time.perf_counter()
    process.start()
    send.send_bytes(raw)
    actual = queue.get()
    process.join()
    pipe_time = time.perf_counter() - started
    receive.close()
    send.close()
    assert actual == expected
    print(f"Pipe:          {pipe_time:.4f} с; сумма={actual[1]}")
    print(f"Pipe / shared_memory: {pipe_time / shared_time:.2f}x")


if __name__ == "__main__":
    main()
