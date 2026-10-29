# ПР-2. Bash и системные вызовы

## Цель

Построить отчёт по журналам и сравнить системные вызовы `cat` и Python.

## Запуск

Если преподавательский `data/` отсутствует:

```bash
python3 make_logs.py
```

Основные команды:

```bash
chmod +x report.sh hello.py
./report.sh data ERROR --top 5
./report.sh data WARN
./report.sh; echo "код=$?"
./report.sh missing ERROR; echo "код=$?"
shellcheck report.sh

strace -f -o trace.txt python3 hello.py data/01.log
strace -c -o cat_stats.txt cat data/01.log
strace -c -o python_stats.txt python3 hello.py data/01.log
cat cat_stats.txt
cat python_stats.txt
grep 'data/01.log' trace.txt
```

Без аргументов скрипт выводит справку и возвращает `1`. Реализованы проверка каталога, уровни `ERROR/WARN` и `--top N`.

## Контрольный результат

```text
МОДУЛЬ         КОЛИЧЕСТВО
-------------------- ----------
scheduler            413
auth                 400
ui                   383

Файл: data/01.log
Размер: 10132 байт
```

## Анализ strace

В `cat_stats.txt` и `python_stats.txt` записано общее число вызовов. В `trace.txt` к собственно файлу относятся `openat` с `data/01.log`, последующие `read` и `close`. Остальные вызовы запускают интерпретатор, открывают библиотеки и модули, управляют памятью.

## Вывод

У Python больше системных вызовов, чем у `cat`, из-за запуска интерпретатора и загрузки библиотек. Полезное чтение файла в обоих случаях использует `openat`, `read`, `close`.

**Почему нельзя обратиться к диску напрямую?** Пользовательский режим не разрешает привилегированные операции; ядро проверяет запрос и работает с драйвером.

**Что дороже?** Системный вызов дороже вызова обычной функции из-за перехода в режим ядра и проверок.
