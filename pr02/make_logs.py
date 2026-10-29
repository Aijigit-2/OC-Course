#!/usr/bin/env python3
"""Создаёт 50 учебных журналов, если преподавательский data/ отсутствует."""
from pathlib import Path
import random

random.seed(42)
data = Path("data")
data.mkdir(exist_ok=True)
modules = ["net", "auth", "disk", "scheduler", "ui"]
levels = ["INFO", "INFO", "INFO", "WARN", "ERROR"]
for number in range(1, 51):
    lines = []
    for index in range(200):
        level = random.choice(levels)
        module = random.choice(modules)
        lines.append(
            f"2026-02-14 10:{index // 60:02d}:{index % 60:02d} "
            f"{level} module={module} msg=event_{index}"
        )
    (data / f"{number:02d}.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("Создано 50 файлов в data/")
