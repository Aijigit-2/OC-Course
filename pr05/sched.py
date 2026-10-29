#!/usr/bin/env python3
"""Симулятор FCFS, SJF, SRTF, Priority и RR с метриками и aging."""
import argparse
from collections import deque
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Process:
    name: str
    arrival: int
    burst: int
    priority: int
    number: int

@dataclass(frozen=True)
class Interval:
    start: int
    end: int
    name: str


def read_processes(path: Path) -> list[Process]:
    result = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, arrival, burst, priority = line.split()
        number = int("".join(character for character in name if character.isdigit()) or 0)
        result.append(Process(name, int(arrival), int(burst), int(priority), number))
    if not result:
        raise ValueError("пустой входной файл")
    return result


def simulate(processes: list[Process], algorithm: str, quantum: int = 3,
             aging: int | None = None) -> list[Interval]:
    processes = sorted(processes, key=lambda item: (item.arrival, item.number))
    remaining = {p.name: p.burst for p in processes}
    ready_since = {p.name: p.arrival for p in processes}
    waited = {p.name: 0 for p in processes}
    by_name = {p.name: p for p in processes}
    pending = processes.copy()
    ready: list[Process] = []
    rr_queue: deque[Process] = deque()
    current: Process | None = None
    expired: Process | None = None
    quantum_left = 0
    now = 0
    done = 0
    timeline = []

    def effective(process: Process) -> int:
        boost = waited[process.name] // aging if aging else 0
        return process.priority - boost

    while done < len(processes):
        arrivals = []
        while pending and pending[0].arrival == now:
            arrivals.append(pending.pop(0))
        ready.extend(arrivals)
        rr_queue.extend(arrivals)

        if algorithm == "rr" and expired is not None:
            rr_queue.append(expired)  # новые прибытия уже стоят в очереди
            expired = None

        for process in ready:
            waited[process.name] += 1

        if algorithm in ("fcfs", "sjf"):
            if current is None and ready:
                key = (lambda p: (p.arrival, p.number)) if algorithm == "fcfs" else (
                    lambda p: (p.burst, p.arrival, p.number)
                )
                current = min(ready, key=key)
                ready.remove(current)
        elif algorithm in ("srtf", "priority"):
            candidates = ready + ([current] if current else [])
            if candidates:
                if algorithm == "srtf":
                    key = lambda p: (remaining[p.name], p.arrival, p.number)
                    better = lambda candidate, running: remaining[candidate.name] < remaining[running.name]
                else:
                    key = lambda p: (effective(p), p.arrival, p.number)
                    better = lambda candidate, running: effective(candidate) < effective(running)
                chosen = min(candidates, key=key)
                if current is None or chosen.name != current.name and better(chosen, current):
                    if current is not None:
                        ready.append(current)
                        ready_since[current.name] = now
                    current = chosen
                    if current in ready:
                        ready.remove(current)
        elif algorithm == "rr":
            if current is None and rr_queue:
                current = rr_queue.popleft()
                quantum_left = quantum
        else:
            raise ValueError(f"неизвестный алгоритм: {algorithm}")

        timeline.append(current.name if current else "IDLE")
        if current is None:
            now += 1
            continue

        remaining[current.name] -= 1
        if remaining[current.name] == 0:
            done += 1
            current = None
            quantum_left = 0
        elif algorithm == "rr":
            quantum_left -= 1
            if quantum_left == 0:
                expired = current
                current = None
        now += 1

    intervals = []
    start = 0
    for index in range(1, len(timeline) + 1):
        if index == len(timeline) or timeline[index] != timeline[start]:
            if timeline[start] != "IDLE":
                intervals.append(Interval(start, index, timeline[start]))
            start = index
    return intervals


def metrics(processes: list[Process], intervals: list[Interval]) -> dict:
    per_process = []
    for process in processes:
        own = [item for item in intervals if item.name == process.name]
        first = min(item.start for item in own)
        completion = max(item.end for item in own)
        turnaround = completion - process.arrival
        per_process.append({
            "name": process.name,
            "completion": completion,
            "turnaround": turnaround,
            "waiting": turnaround - process.burst,
            "response": first - process.arrival,
        })
    count = len(processes)
    makespan = max(item["completion"] for item in per_process)
    switches = sum(
        1 for previous, current in zip(intervals, intervals[1:])
        if previous.name != current.name
    )
    return {
        "processes": per_process,
        "waiting": sum(item["waiting"] for item in per_process) / count,
        "turnaround": sum(item["turnaround"] for item in per_process) / count,
        "response": sum(item["response"] for item in per_process) / count,
        "cpu": sum(process.burst for process in processes) / makespan * 100,
        "switches": switches,
    }


def print_result(processes: list[Process], intervals: list[Interval]) -> None:
    result = metrics(processes, intervals)
    print("Гант:", " | ".join(f"{i.name}[{i.start}:{i.end}]" for i in intervals))
    print("PID  Completion  Turnaround  Waiting  Response")
    for item in result["processes"]:
        print(f"{item['name']:4} {item['completion']:10} {item['turnaround']:11} "
              f"{item['waiting']:8} {item['response']:8}")
    print(f"Среднее ожидание: {result['waiting']:.2f}")
    print(f"Средний оборот:   {result['turnaround']:.2f}")
    print(f"Средний отклик:   {result['response']:.2f}")
    print(f"Загрузка CPU:     {result['cpu']:.2f}%")
    print(f"Переключений:     {result['switches']}")


def sweep(processes: list[Process]) -> None:
    rows = []
    for quantum in range(1, 11):
        result = metrics(processes, simulate(processes, "rr", quantum))
        rows.append((quantum, result["waiting"], result["switches"]))
        print(f"q={quantum:2d} waiting={result['waiting']:6.2f} switches={result['switches']}")
    Path("rr_sweep.csv").write_text(
        "quantum,waiting,switches\n" + "".join(f"{q},{w:.2f},{s}\n" for q, w, s in rows)
    )
    import matplotlib.pyplot as plt
    figure, left = plt.subplots(figsize=(8, 4.8))
    right = left.twinx()
    left.plot([r[0] for r in rows], [r[1] for r in rows], marker="o", color="#2F6690", label="Ожидание")
    right.plot([r[0] for r in rows], [r[2] for r in rows], marker="s", color="#A63D40", label="Переключения")
    left.set_xlabel("Квант RR")
    left.set_ylabel("Среднее ожидание, такты", color="#2F6690")
    right.set_ylabel("Число переключений", color="#A63D40")
    left.set_xticks(range(1, 11))
    left.grid(alpha=0.25)
    figure.suptitle("Малый квант увеличивает переключения")
    figure.tight_layout()
    figure.savefig("rr_sweep.png", dpi=160)
    print("Сохранены rr_sweep.csv и rr_sweep.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--algo", choices=["fcfs", "sjf", "srtf", "priority", "rr", "all"], default="all")
    parser.add_argument("--quantum", type=int, default=3)
    parser.add_argument("--aging", type=int)
    parser.add_argument("--sweep", action="store_true")
    args = parser.parse_args()
    if args.quantum < 1 or args.aging is not None and args.aging < 1:
        parser.error("quantum и aging должны быть положительными")
    processes = read_processes(args.file)
    if args.sweep:
        sweep(processes)
        return
    algorithms = ["fcfs", "sjf", "srtf", "priority", "rr"] if args.algo == "all" else [args.algo]
    for algorithm in algorithms:
        print(f"\n=== {algorithm.upper()} ===")
        print_result(processes, simulate(processes, algorithm, args.quantum, args.aging))


if __name__ == "__main__":
    main()
