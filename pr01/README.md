# ПР-1. Пользователи, группы, права и Bash

## Цель

Создать `student2` и группу `developers`, настроить `/srv/shared` без `chmod 777`, проверить права и настроить `.bashrc`.

## Выполнение

```bash
sudo groupadd developers
sudo useradd -m -s /bin/bash student2
sudo passwd student2
sudo usermod -aG developers student2
id student2

sudo mkdir -p /srv/shared
sudo chown root:developers /srv/shared
sudo chmod 2775 /srv/shared
ls -ld /srv/shared

sudo -u student2 bash -c 'echo "file from student2" > /srv/shared/from_student2.txt'
ls -l /srv/shared/from_student2.txt
cat /srv/shared/from_student2.txt
rm /srv/shared/from_student2.txt
```

Права `2775`: владелец и группа имеют `rwx`, остальные — `r-x`; setgid-бит заставляет новые файлы наследовать группу `developers`. Если основной пользователь не входит в группу, удаление вернёт `Permission denied`: для удаления нужна запись в родительский каталог, а не владение файлом.

## Настройка ~/.bashrc

Добавить в конец файла через `nano ~/.bashrc`:

```bash
alias ll='ls -alF'
alias gs='git status --short'
export OS_COURSE="$HOME/os-course"
```

Проверка в новой сессии:

```bash
alias ll
alias gs
echo "$OS_COURSE"
ll "$OS_COURSE"
```

## Ответы

**`su` и `sudo`.** `su` открывает сессию другого пользователя и требует его пароль. `sudo` выполняет отдельную команду с привилегиями по правилам `sudoers` и обычно спрашивает пароль текущего пользователя.

**Почему root заблокирован.** Это уменьшает риск постоянной работы с полными правами и случайных повреждений. Администрирование выполняется через `sudo`.

## Вывод

Созданы пользователь и группа. Каталог имеет владельца `root`, группу `developers` и права `2775`. `student2` может создавать файлы, а пользователь вне группы не может удалять их. Alias `ll`, `gs` и переменная `OS_COURSE` работают в новой сессии.
