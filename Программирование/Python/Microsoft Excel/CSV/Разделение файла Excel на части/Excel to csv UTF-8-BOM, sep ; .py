import os
import pandas as pd
import argparse
from pathlib import Path


def split_file_by_rows(rows_per_file):
    """
    Разделяет файл на несколько частей по указанному количеству строк

    Args:
        rows_per_file (int): Количество строк данных в каждом выходном файле
    """

    # Поиск файла в текущей директории
    current_dir = os.getcwd()
    supported_extensions = ['.xls', '.xlsx', '.csv']
    input_file = None

    for file in os.listdir(current_dir):
        file_ext = os.path.splitext(file)[1].lower()
        if file_ext in supported_extensions:
            input_file = file
            break

    if input_file is None:
        print("Ошибка: Не найден файл с расширением .xls, .xlsx или .csv в текущей директории")
        return

    print(f"Найден исходный файл: {input_file}")

    try:
        # Определение расширения файла и его чтение
        file_ext = os.path.splitext(input_file)[1].lower()

        if file_ext == '.csv':
            # Для CSV пробуем разные разделители при чтении
            separators = [';', ',', '\t', '|']
            df = None
            for sep in separators:
                try:
                    df = pd.read_csv(input_file, encoding='utf-8', sep=sep)
                    break
                except:
                    try:
                        df = pd.read_csv(input_file, encoding='cp1251', sep=sep)
                        break
                    except:
                        continue
            if df is None:
                raise Exception("Не удалось прочитать CSV файл с известными разделителями")
        else:
            # Для Excel файлов
            df = pd.read_excel(input_file)

        # Получение имени файла без расширения
        base_name = os.path.splitext(input_file)[0]

        # Получение заголовка (первая строка)
        header = df.columns.tolist()

        # Расчет количества выходных файлов
        total_data_rows = len(df)
        num_files = (total_data_rows + rows_per_file - 1) // rows_per_file

        # Создание директории для выходных файлов
        output_dir = Path(current_dir) / f"{base_name}_split"
        output_dir.mkdir(exist_ok=True)

        # Разделение и сохранение файлов
        for i in range(num_files):
            start_idx = i * rows_per_file
            end_idx = min((i + 1) * rows_per_file, total_data_rows)

            # Количество записей в текущем файле
            current_rows = end_idx - start_idx

            # Получение среза данных
            df_chunk = df.iloc[start_idx:end_idx].copy()

            # Создание имени выходного файла с указанием количества записей
            # Формат: ИсходноеИмя_записей_XXX__YYY.csv
            # где XXX - количество записей в файле, YYY - порядковый номер
            output_file = output_dir / f"{base_name}_записей_{current_rows}__{i + 1:03d}.csv"

            # Сохранение в CSV с BOM и разделителем ";"
            df_chunk.to_csv(output_file, index=False, encoding='utf-8-sig', sep=';')

        print(f"\nФайлы сохранены в директории: {output_dir}")

    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")


def main():
    while True:
        try:
            rows_per_file = int(input("Введите количество строк для одного выходного файла: "))
            if rows_per_file > 0:
                break
            else:
                print("Пожалуйста, введите целое положительное число")
        except ValueError:
            print("Пожалуйста, введите целое положительное число")
    split_file_by_rows(rows_per_file)


if __name__ == "__main__":
    main()