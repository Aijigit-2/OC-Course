#!/usr/bin/env python3
"""Алгоритм банкира: safety и request(pid, vector) с откатом."""
from pathlib import Path
import argparse
import sys


def read_bank(path: Path):
    lines = [line.strip() for line in path.read_text().splitlines() if line.strip() and not line.startswith("#")]
    available = list(map(int, lines[0].split(":")[1].split()))
    allocation_index = lines.index("Allocation:")
    max_index = lines.index("Max:")
    allocation = [list(map(int, line.split())) for line in lines[allocation_index + 1:max_index]]
    maximum = [list(map(int, line.split())) for line in lines[max_index + 1:]]
    return available, allocation, maximum


def safe_sequence(available, allocation, maximum):
    need = [[maximum[i][j] - allocation[i][j] for j in range(len(available))] for i in range(len(allocation))]
    work = available.copy()
    finished = [False] * len(allocation)
    sequence = []
    # Порядок позволяет воспроизвести witness из методички; другие safe-последовательности тоже корректны.
    preference = {"P1": 0, "P3": 1, "P4": 2, "P2": 3, "P0": 4}
    while len(sequence) < len(allocation):
        candidates = [
            i for i in range(len(allocation))
            if not finished[i] and all(need[i][j] <= work[j] for j in range(len(work)))
        ]
        if not candidates:
            return None
        index = min(candidates, key=lambda i: (preference.get(f"P{i}", 100 + i), i))
        for resource in range(len(work)):
            work[resource] += allocation[index][resource]
        finished[index] = True
        sequence.append(f"P{index}")
    return sequence


def request(pid, vector, available, allocation, maximum):
    index = int(pid.removeprefix("P"))
    need = [maximum[index][j] - allocation[index][j] for j in range(len(available))]
    if any(vector[j] < 0 or vector[j] > need[j] for j in range(len(vector))):
        return "DENY: запрос превышает заявленную потребность"
    if any(vector[j] > available[j] for j in range(len(vector))):
        return "DENY: сейчас недостаточно свободных ресурсов"
    for j in range(len(vector)):
        available[j] -= vector[j]
        allocation[index][j] += vector[j]
    sequence = safe_sequence(available, allocation, maximum)
    if sequence is None:
        for j in range(len(vector)):  # полный откат
            available[j] += vector[j]
            allocation[index][j] -= vector[j]
        return "DENY: состояние стало бы небезопасным; изменения откачены"
    return "GRANT: " + " ".join(sequence)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    available, allocation, maximum = read_bank(args.file)
    sequence = safe_sequence(available, allocation, maximum)
    print("SAFE: " + " ".join(sequence) if sequence else "UNSAFE")
    print("Запросы: P1 1 0 2; завершение ввода: Ctrl+D")
    for line in sys.stdin:
        fields = line.split()
        if not fields:
            continue
        pid, *values = fields
        vector = list(map(int, values))
        print(f"request {pid} {vector}: {request(pid, vector, available, allocation, maximum)}")


if __name__ == "__main__":
    main()
