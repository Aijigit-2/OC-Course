# Операционные системы — ПР-1–ПР-8, уровень B

Готовый репозиторий по методическим указаниям «Часть 3А». Среда: Ubuntu 22.04+ или WSL2, Python 3.11+.

## Установка зависимостей

```bash
sudo apt update
sudo apt install -y git python3 python3-matplotlib build-essential strace shellcheck
```

## Содержимое

| Каталог | Тема |
|---|---|
| `pr01` | Пользователи, группы, права, `.bashrc` |
| `pr02` | Bash-отчёт по журналам и `strace` |
| `pr03` | `/proc`, `fork/exec/wait`, зомби, сироты, COW |
| `pr04` | Потоки, процессы, CPU и сетевые замеры |
| `pr05` | FCFS, SJF, SRTF, Priority, RR и aging |
| `pr06` | Мьютексы, семафоры, condition, барьер |
| `pr07` | FIFO, Unix-сокеты, `shared_memory`, `Pipe` |
| `pr08` | Банкир, детектор циклов, `TrackedLock`, философы |

В каждом каталоге есть свой `README.md` с командами запуска, результатами и выводами.

## Быстрая проверка

```bash
cd pr02 && bash report.sh data ERROR --top 5
cd ../pr03 && python3 runner.py -n 2 sleep 1
cd ../pr05 && python3 sched.py --algo rr --quantum 3 set1.txt
cd ../pr06 && python3 sync.py semaphore
cd ../pr08 && printf 'P1 1 0 2\n' | python3 banker.py bank1.txt
```

Для ПР-2 сначала поместите журналы преподавателя в `pr02/data/` или создайте учебные командой `python3 make_logs.py`. Для ПР-4 большой `numbers.txt` создаётся локально и не загружается в GitHub.
