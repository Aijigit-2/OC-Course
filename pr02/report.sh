#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Использование: $0 КАТАЛОГ ERROR|WARN [--top N]" >&2
}

directory=""
level=""
top=""

while (($# > 0)); do
    case "$1" in
        --top)
            (($# >= 2)) || { usage; exit 1; }
            top="$2"
            shift 2
            ;;
        *)
            if [[ -z "$directory" ]]; then
                directory="$1"
            elif [[ -z "$level" ]]; then
                level="$1"
            else
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$directory" || -z "$level" || "$level" != "ERROR" && "$level" != "WARN" ]]; then
    usage
    exit 1
fi
if [[ ! -d "$directory" ]]; then
    echo "Ошибка: каталог '$directory' не существует" >&2
    exit 1
fi
if [[ -n "$top" && ! "$top" =~ ^[1-9][0-9]*$ ]]; then
    echo "Ошибка: --top ожидает положительное целое число" >&2
    exit 1
fi

shopt -s nullglob
files=("$directory"/*.log)
if ((${#files[@]} == 0)); then
    echo "Ошибка: в каталоге '$directory' нет файлов *.log" >&2
    exit 1
fi

results=$(awk -v wanted="$level" '
    $3 == wanted {
        for (i = 4; i <= NF; i++) {
            if ($i ~ /^module=/) {
                module = $i
                sub(/^module=/, "", module)
                counts[module]++
            }
        }
    }
    END { for (module in counts) print counts[module], module }
' "${files[@]}" | sort -k1,1nr -k2,2)

if [[ -z "$results" ]]; then
    echo "Сообщений уровня $level не найдено"
    exit 0
fi
if [[ -n "$top" ]]; then
    results=$(printf '%s\n' "$results" | sed -n "1,${top}p")
fi

printf '%-20s %s\n' "МОДУЛЬ" "КОЛИЧЕСТВО"
printf '%-20s %s\n' "--------------------" "----------"
while read -r count module; do
    printf '%-20s %s\n' "$module" "$count"
done <<< "$results"
