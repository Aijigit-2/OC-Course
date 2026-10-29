#!/usr/bin/env python3
"""Строит wait-for graph по acquire/release/wait и ищет цикл DFS."""
import argparse
from pathlib import Path


def wait_graph(events):
    holder = {}
    waiting = {}
    for action, process, resource in events:
        if action == "acquire":
            holder[resource] = process
            waiting.pop(process, None)
        elif action == "release":
            holder.pop(resource, None)
        elif action == "wait":
            waiting[process] = resource
    graph = {process: [] for process in waiting}
    for process, resource in waiting.items():
        if resource in holder and holder[resource] != process:
            graph[process].append(holder[resource])
    return graph


def find_cycle(graph):
    visited = set()
    active = []
    active_set = set()

    def dfs(node):
        visited.add(node)
        active.append(node)
        active_set.add(node)
        for neighbour in graph.get(node, []):
            if neighbour in active_set:
                start = active.index(neighbour)
                return active[start:] + [neighbour]
            if neighbour not in visited:
                cycle = dfs(neighbour)
                if cycle:
                    return cycle
        active.pop()
        active_set.remove(node)
        return None

    for node in graph:
        if node not in visited:
            cycle = dfs(node)
            if cycle:
                return cycle
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    args = parser.parse_args()
    events = [tuple(line.split()) for line in args.log.read_text().splitlines()
              if line.strip() and not line.startswith("#")]
    graph = wait_graph(events)
    print("Wait-for graph:", graph)
    cycle = find_cycle(graph)
    print("DEADLOCK: " + " -> ".join(cycle) if cycle else "NO DEADLOCK")


if __name__ == "__main__":
    main()
