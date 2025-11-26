#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import hashlib
import chardet
from tqdm import tqdm


def detect_encoding(file_path: str, b_print: bool) -> str:
    """
    Определение кодировки файла.
    """
    with open(file_path, "rb") as f:
        raw = f.read(100_000)     # Быстрее, чем читать всё
    result = chardet.detect(raw)
    encoding = result.get("encoding", "utf-8")
    if b_print:
        print(f"[INFO] Кодировка определена: {encoding}")
    return encoding


def detect_delimiter(file_path: str, encoding: str, b_print: bool) -> str:
    """
    Определение разделителя CSV (, ; табуляция).
    """
    with open(file_path, "r", encoding=encoding, newline="") as f:
        sample = f.read(4096)

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t"])
        delim = dialect.delimiter
        if b_print:
            print(f"[INFO] Разделитель определён: '{delim}'")

            # ░░ Вывод количества записей в файле ░░
            total = count_file_lines(file_path, encoding) - 1
            print(f"[INFO] Количество записей в файле: {total}")

        return delim

    except Exception:
        print("[WARN] Не удалось определить разделитель, используется ','")

        if b_print:
            total = count_file_lines(file_path, encoding) - 1
            print(f"[INFO] Количество записей в файле: {total}")

        return ","


def header_hash(header: list[str]) -> str:
    """
    Создаёт хэш заголовка CSV.
    """
    joined = "|".join([h.strip() for h in header])
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def read_csv_header(file_path: str, encoding: str, delimiter: str, b_print: bool) -> list[str]:
    """
    Чтение заголовка CSV файла.
    """
    with open(file_path, "r", encoding=encoding, newline="") as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            if b_print:
                print(f"[INFO] Заголовок: {', '.join(row)}")
            return row
    return []


def count_file_lines(file_path: str, encoding: str) -> int:
    """
    Быстрое определение количества строк (для прогресс-бара).
    """
    with open(file_path, "r", encoding=encoding, newline="") as f:
        return sum(1 for _ in f)


def read_csv_rows(file_path: str, encoding: str, delimiter: str) -> list[list[str]]:
    """
    Чтение всех строк CSV без заголовка.
    Используется tqdm для отображения прогресса.
    """
    total = count_file_lines(file_path, encoding) - 1
    rows = []

    with open(file_path, "r", encoding=encoding, newline="") as f:
        reader = csv.reader(f, delimiter=delimiter)
        next(reader, None)  # пропускаем заголовок

        for row in tqdm(reader, total=total, desc=f"Чтение {os.path.basename(file_path)}"):
            rows.append(row)

    return rows


def merge_csv_files(file_paths: list[str], output_name: str):
    """
    Объединение CSV-файлов одной группы.
    """

    print("\n[INFO] === НАЧАТО ОБЪЕДИНЕНИЕ ФАЙЛОВ ===")

    first_file = file_paths[0]
    encoding = detect_encoding(first_file, False)
    delimiter = detect_delimiter(first_file, encoding, False)

    # Читаем заголовок
    header = read_csv_header(first_file, encoding, delimiter, False)

    output_file = output_name + ".csv"
    print(f"[INFO] Создание итогового файла: {output_file}")

    total_written = 0  # Для подсчёта итоговых записей

    with open(output_file, "w", encoding=encoding, newline="") as f_out:
        writer = csv.writer(f_out, delimiter=delimiter)
        writer.writerow(header)

        for file in file_paths:
            enc = detect_encoding(file, False)
            delim = detect_delimiter(file, enc, False)

            rows = read_csv_rows(file, enc, delim)
            writer.writerows(rows)
            total_written += len(rows)

    print(f"\n[INFO] Файл успешно сформирован.")
    print(f"[INFO] Количество записей в итоговом файле: {total_written}")


def main():
    print("=== Объединение CSV по совпадающим наборам полей ===")

    base_dir = os.path.dirname(os.path.abspath(__file__))

    csv_files = [
        os.path.join(base_dir, f)
        for f in os.listdir(base_dir)
        if f.lower().endswith(".csv")
    ]

    if not csv_files:
        print("CSV-файлы не найдены.")
        return

    print(f"[INFO] Найдено CSV-файлов: {len(csv_files)}")

    groups = {}

    # Определяем хэши заголовков
    for csv_file in csv_files:
        print(f"\n[INFO] Анализ файла: {os.path.basename(csv_file)}")

        encoding = detect_encoding(csv_file, True)
        delimiter = detect_delimiter(csv_file, encoding, True)
        header = read_csv_header(csv_file, encoding, delimiter, True)

        if not header:
            print(f"[WARN] Файл {os.path.basename(csv_file)} пропущен: нет заголовка.")
            continue

        h = header_hash(header)
        groups.setdefault(h, []).append(csv_file)

    # Обработка групп
    for h, files in groups.items():
        if len(files) < 2:
            continue

        print("\n===========================================")
        print("[INFO] Обнаружена группа файлов с одинаковыми полями:")
        for f in files:
            print(" -", os.path.basename(f))

        answer = input("\nОбъединить эти файлы? (y/n): ").strip().lower()
        if answer != "y":
            print("[INFO] Пропуск.")
            continue

        output_name = input("Введите имя итогового файла без расширения: ").strip()

        if not output_name:
            print("[ERROR] Имя файла пустое. Пропуск.")
            continue

        merge_csv_files(files, os.path.join(base_dir, output_name))

    print("\n[INFO] Готово.")


if __name__ == "__main__":
    main()
