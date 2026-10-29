#!/usr/bin/env python3
"""TrackedLock обнаруживает цикл ожидания до блокирующего acquire."""
import threading


class DeadlockDetected(RuntimeError):
    pass


class TrackedLock:
    registry = []
    graph_lock = threading.Lock()

    def __init__(self, name: str):
        self.name = name
        self.lock = threading.Lock()
        self.owner = None
        self.waiters = set()
        with self.graph_lock:
            self.registry.append(self)

    @classmethod
    def cycle_for(cls, start):
        graph = {}
        for lock in cls.registry:
            if lock.owner is not None:
                for waiter in lock.waiters:
                    graph.setdefault(waiter, []).append(lock.owner)
        path = [start]
        active = {start}

        def dfs(thread):
            for neighbour in graph.get(thread, []):
                if neighbour in active:
                    return path + [neighbour]
                path.append(neighbour)
                active.add(neighbour)
                cycle = dfs(neighbour)
                if cycle:
                    return cycle
                active.remove(neighbour)
                path.pop()
            return None
        return dfs(start)

    def acquire(self):
        me = threading.current_thread()
        with self.graph_lock:
            self.waiters.add(me)
            cycle = self.cycle_for(me)
            if cycle:
                self.waiters.remove(me)
                raise DeadlockDetected(" -> ".join(thread.name for thread in cycle))
        self.lock.acquire()
        with self.graph_lock:
            self.waiters.remove(me)
            self.owner = me

    def release(self):
        with self.graph_lock:
            self.owner = None
        self.lock.release()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *args):
        self.release()


def worker(name, first, second, barrier, errors):
    try:
        with first:
            if barrier is not None:
                barrier.wait()
            with second:
                pass
    except DeadlockDetected as error:
        errors.append(f"{name}: {error}")


def run_pair(first_order, second_order, synchronize=False):
    a, b = first_order
    barrier = threading.Barrier(2) if synchronize else None
    errors = []
    threads = [
        threading.Thread(name="T1", target=worker, args=("T1", a, b, barrier, errors)),
        threading.Thread(name="T2", target=worker, args=("T2", *second_order, barrier, errors)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return errors


if __name__ == "__main__":
    a, b = TrackedLock("A"), TrackedLock("B")
    errors = run_pair((a, b), (b, a), synchronize=True)
    assert errors, "цикл не обнаружен"
    print("Обнаружено вместо зависания:", errors[0])
    c, d = TrackedLock("C"), TrackedLock("D")
    errors = run_pair((c, d), (c, d))
    assert not errors
    print("Единый порядок C->D: OK")
