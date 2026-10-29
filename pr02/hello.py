#!/usr/bin/env python3
import pathlib
import sys

if len(sys.argv) != 2:
    raise SystemExit(f"Использование: {sys.argv[0]} ФАЙЛ")

path = pathlib.Path(sys.argv[1])
data = path.read_bytes()
print(f"Файл: {path}")
print(f"Размер: {len(data)} байт")
