#!/usr/bin/env python3
"""Кольцевой буфер 5, 3 производителя, 2 потребителя, 1000 элементов."""
import argparse
import threading

CAPACITY = 5
TOTAL = 1000
STOP = object()


class RingBuffer:
    def __init__(self, mode: str):
        self.data = [None] * CAPACITY
        self.read_pos = 0
        self.write_pos = 0
        self.count = 0
        self.mode = mode
        self.violations = []
        if mode == "semaphore":
            self.mutex = threading.Lock()
            self.empty = threading.Semaphore(CAPACITY)
            self.full = threading.Semaphore(0)
        else:
            self.condition = threading.Condition()

    def _put(self, item) -> None:
        if self.count >= CAPACITY:
            self.violations.append("переполнение")
        self.data[self.write_pos] = item
        self.write_pos = (self.write_pos + 1) % CAPACITY
        self.count += 1

    def _get(self):
        if self.count <= 0:
            self.violations.append("чтение пустого буфера")
        item = self.data[self.read_pos]
        self.read_pos = (self.read_pos + 1) % CAPACITY
        self.count -= 1
        return item

    def put(self, item) -> None:
        if self.mode == "semaphore":
            self.empty.acquire()
            with self.mutex:
                self._put(item)
            self.full.release()
        else:
            with self.condition:
                while self.count == CAPACITY:
                    self.condition.wait()
                self._put(item)
                self.condition.notify_all()

    def get(self):
        if self.mode == "semaphore":
            self.full.acquire()
            with self.mutex:
                item = self._get()
            self.empty.release()
            return item
        with self.condition:
            while self.count == 0:
                self.condition.wait()
            item = self._get()
            self.condition.notify_all()
            return item


def producer(buffer: RingBuffer, producer_id: int) -> None:
    for item in range(producer_id, TOTAL, 3):
        buffer.put(item)


def consumer(buffer: RingBuffer, consumed: list, lock: threading.Lock) -> None:
    while True:
        item = buffer.get()
        if item is STOP:
            return
        with lock:
            consumed.append(item)


def buffer_demo(mode: str) -> None:
    buffer = RingBuffer(mode)
    consumed = []
    consumed_lock = threading.Lock()
    producers = [threading.Thread(target=producer, args=(buffer, i)) for i in range(3)]
    consumers = [threading.Thread(target=consumer, args=(buffer, consumed, consumed_lock)) for _ in range(2)]
    for thread in consumers + producers:
        thread.start()
    for thread in producers:
        thread.join()
    for _ in consumers:
        buffer.put(STOP)
    for thread in consumers:
        thread.join()
    assert not buffer.violations, buffer.violations
    assert len(consumed) == TOTAL, f"потреблено {len(consumed)}"
    assert sorted(consumed) == list(range(TOTAL)), "есть потери или повторы"
    assert buffer.count == 0
    print(f"{mode}: OK; элементов={len(consumed)}; переполнений=0; повторов=0")


class ReusableBarrier:
    def __init__(self, parties: int):
        self.parties = parties
        self.arrived = 0
        self.generation = 0
        self.condition = threading.Condition()

    def wait(self) -> None:
        with self.condition:
            generation = self.generation
            self.arrived += 1
            if self.arrived == self.parties:
                self.arrived = 0
                self.generation += 1
                self.condition.notify_all()
            else:
                while generation == self.generation:
                    self.condition.wait()


def barrier_demo() -> None:
    barrier = ReusableBarrier(4)
    log = []
    lock = threading.Lock()

    def worker(worker_id: int) -> None:
        for phase in range(3):
            with lock:
                log.append((phase, worker_id))
            barrier.wait()

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(log) == 12
    for phase in range(3):
        assert sorted(worker for p, worker in log if p == phase) == [0, 1, 2, 3]
    print("barrier: OK; 4 потока прошли 3 синхронизированные фазы")


def lost_wakeup_demo() -> None:
    condition = threading.Condition()
    checked = threading.Event()
    allow_notify = threading.Event()
    ready = False
    consumed = False

    def broken_consumer() -> None:
        nonlocal consumed
        with condition:
            checked.set()
            allow_notify.wait()
            if not ready:  # ОШИБКА: после wait нет повторной проверки
                condition.wait(timeout=2)
            consumed = True

    thread = threading.Thread(target=broken_consumer)
    thread.start()
    checked.wait()
    allow_notify.set()
    with condition:
        condition.notify_all()  # пробуждение без выполнения условия ready
    thread.join()
    print(f"if: consumed={consumed}, ready={ready} — ложное потребление")
    print("while повторно проверил бы ready и не позволил бы продолжить")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo", choices=["semaphore", "condition", "barrier", "lost-wakeup"])
    args = parser.parse_args()
    if args.demo in ("semaphore", "condition"):
        buffer_demo(args.demo)
    elif args.demo == "barrier":
        barrier_demo()
    else:
        lost_wakeup_demo()
