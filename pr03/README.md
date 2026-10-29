# ПР-3. Процессы в Linux

## Цель

Изучить `/proc`, `fork/exec/wait`, зомби, сироту и copy-on-write.

## Запуск

```bash
python3 ptree.py
python3 runner.py -n 3 sleep 1
python3 runner.py -n 2 /bin/echo hello
python3 zombie.py
python3 orphan.py
sleep 3
ps -eo pid,ppid,stat,cmd | grep -E 'zombie|orphan|defunct' || true
python3 cow.py
```

`ptree.py` не вызывает `ps`: PID, PPID, состояние и RSS читаются из `/proc/<PID>/status`. `runner.py` ждёт всех детей и выводит код и время каждого.

## Контрольный результат

```text
job=1 pid=2501 exit=0 time=0.207s
job=2 pid=2502 exit=0 time=0.206s

PID  PPID STAT CMD
2504 2503 Z    [python3] <defunct>
После wait статус забран, зомби удалён

CHILD before KiB: {'VmRSS': 84464, 'Shared_Dirty': 80728, 'Private_Dirty': 900}
CHILD after KiB:  {'VmRSS': 84880, 'Shared_Dirty': 2352, 'Private_Dirty': 79276}
PARENT data[0]=0: изменения ребёнка не видны родителю
```

PID и память на другом компьютере отличаются. У сироты новый PPID может быть `1` или PID `systemd --user`/subreaper — в отчёт записывается фактический вывод.

## Вывод

Зомби — завершившийся процесс, чей статус ещё не забран родителем через `wait`. Сирота получает нового родителя. При COW общие страницы копируются только после записи: `Shared_Dirty` уменьшается, `Private_Dirty` растёт.

**Почему `fork` возвращает разные значения?** Ребёнок получает `0`, родитель — PID ребёнка, что разделяет их ветки кода.

**`exec` без `fork`.** Он заменит текущую программу новой; прежний код не продолжится, хотя PID сохранится.
