# ПР-5. Планирование процессора

## Цель

Реализовать FCFS, SJF, SRTF, Priority и Round Robin, сравнить метрики, исследовать квант RR и aging.

## Запуск

```bash
python3 sched.py --algo fcfs set1.txt
python3 sched.py --algo sjf set1.txt
python3 sched.py --algo srtf set1.txt
python3 sched.py --algo priority set1.txt
python3 sched.py --algo rr --quantum 3 set1.txt
python3 sched.py --algo all set2.txt
python3 sched.py --sweep set2.txt
python3 sched.py --algo priority starve.txt
python3 sched.py --algo priority --aging 2 starve.txt
```

Формат входа: `PID arrival burst priority`; меньшее число priority означает более высокий приоритет. `--sweep` создаёт `rr_sweep.csv` и `rr_sweep.png` для квантов 1–10. Новые прибытия RR ставятся в очередь перед вытесненным процессом.

## Контрольные результаты

Для `set1.txt` и RR с квантом 3: waiting P1/P2/P3 = `6/4/7`, turnaround = `12/7/11`, среднее ожидание = `5.67`, среднее оборачиваемое время = `10.00`, отклик = `2.00`, утилизация = `100%`, переключений = `5`.

Для `starve.txt`: долгий низкоприоритетный процесс P1 получает первый отклик на `t=42` без aging и на `t=18` с `--aging 2`. Это демонстрирует устранение голодания.

## Вывод

FCFS прост, но короткие задачи могут ждать длинную. SJF минимизирует среднее ожидание при известных burst, SRTF дополнительно вытесняет текущий процесс. При маленьком кванте RR чаще переключает контекст; при большом приближается к FCFS. Aging повышает приоритет ожидающих процессов и не даёт им голодать.

**Почему SJF трудно применять?** Точное время следующего CPU burst заранее неизвестно, его приходится прогнозировать.

**Что даёт интерактивность RR?** Регулярные небольшие кванты ограничивают время до следующего ответа процесса.
