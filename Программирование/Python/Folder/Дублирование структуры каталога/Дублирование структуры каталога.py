import os
from pathlib import Path


def collect_directories(source_dir):
    """Собирает все подкаталоги в исходной директории"""
    dirs = []
    for root, directories, _ in os.walk(source_dir):
        for directory in directories:
            dir_path = os.path.join(root, directory)
            dirs.append(dir_path)
    return dirs


def create_target_structure(source_dir, target_dir, dirs):
    """Создает структуру каталогов в целевой директории"""
    long_paths = []
    created_count = 0

    # Создаем файл для логов
    with open(os.path.join(target_dir, 'info.txt'), 'w', encoding='utf-8') as log_file:
        for dir_path in dirs:
            # Получаем относительный путь
            rel_path = os.path.relpath(dir_path, source_dir)
            # Формируем полный путь в целевой директории
            full_target_path = os.path.join(target_dir, rel_path)

            # Проверяем длину пути
            if len(full_target_path) > 255:
                log_file.write(f"-> {full_target_path}\n")
                long_paths.append(full_target_path)
                continue

            # Создаем каталог, если его нет
            try:
                os.makedirs(full_target_path, exist_ok=True)
                created_count += 1
            except OSError as e:
                log_file.write(f"Ошибка при создании каталога {full_target_path}: {e}\n")

    return created_count, len(long_paths)


def main():
    print("Программа для копирования структуры папок")

    source_dir = input("Введите путь до каталога для копирования структуры: ").strip()
    target_dir = input("Введите путь до каталога для создания структуры: ").strip()

    # Проверяем существование исходного каталога
    if not os.path.isdir(source_dir):
        print("Ошибка: исходный каталог для копирования структуры не существует.")
        return

    # Создаем целевой каталог, если его нет
    os.makedirs(target_dir, exist_ok=True)

    # Собираем все подкаталоги
    print("Анализ структуры каталогов для копирования...")
    dirs = collect_directories(source_dir)
    print(f"Найдено {len(dirs)} каталогов для создания")

    # Создаем структуру в целевом каталоге
    print("Создание структуры каталогов...")
    created, long_paths = create_target_structure(source_dir, target_dir, dirs)

    # Выводим отчет
    print(f"\nГотово! Создано {created} каталогов.")
    if long_paths > 0:
        print(f"Пропущено {long_paths} каталогов с длиной пути >255 символов.")
        print(f"Подробности в файле info.txt в целевом каталоге.")

    print(f"Целевой каталог: {target_dir}")


if __name__ == "__main__":
    main()