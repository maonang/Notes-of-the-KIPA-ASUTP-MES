from pathlib import Path
from urllib.parse import unquote
import argparse
import os
import pandas as pd
import re
import warnings


def f_split_file_by_rows(input_file, rows_per_file):
    """
    Разделяет файл на несколько частей по указанному количеству строк
    """

    current_dir = os.getcwd()
    input_ext = os.path.splitext(input_file)[1].lower()
    
    try:
        # Определение расширения файла и его чтение
        if input_ext == '.csv':
            # Для CSV пробуем разные разделители при чтении
            separators = [';', ',', '\t', '|']
            # Определяем разделитель, читая первую строку
            with open(input_file, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                if ';' in first_line:
                    sep = ';'
                elif ',' in first_line:
                    sep = ','
                elif '\t' in first_line:
                    sep = '\t'
                else:
                    sep = '|'
            
            df = None
            try:
                df = pd.read_csv(input_file, encoding='utf-8', sep=sep)
            except:
                df = pd.read_csv(input_file, encoding='cp1251', sep=sep)
            if df is None:
                raise Exception("Не удалось прочитать CSV файл")
        else:
            # Для Excel файлов
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                df = pd.read_excel(input_file)
       
        # Получение имени файла без расширения
        base_name_full = os.path.splitext(input_file)[0]
        # Очищаем имя от проблемных символов
        decoded_name = unquote(base_name_full)
        clean_base_name = re.sub(r'[<>:"/\\|?*]', '_', decoded_name)

        # Расчет количества выходных файлов
        total_data_rows = len(df)
        num_files = (total_data_rows + rows_per_file - 1) // rows_per_file
        
        # Создание директории для выходных файлов
        output_dir = Path(current_dir) / f"{clean_base_name}_split"
        output_dir.mkdir(exist_ok=True)
        
        files_created = 0
        
        # Разделение и сохранение файлов
        for i in range(num_files):
            start_idx = i * rows_per_file
            end_idx = min((i + 1) * rows_per_file, total_data_rows)
            
            # Количество записей в текущем файле
            current_rows = end_idx - start_idx
            
            # Формируем новое имя файла
            output_filename = f"{clean_base_name}_записей_{current_rows}__{i + 1:03d}"
            output_file = output_dir / f"{output_filename}{input_ext}"
            
            # Получение среза данных
            df_chunk = df.iloc[start_idx:end_idx].copy()
            
            # Сохранение в том же формате, что и исходный файл
            try:
                if input_ext == '.csv':
                    # Для CSV используем UTF-8 с BOM и разделителем ";"
                    df_chunk.to_csv(output_file, index=False, encoding='utf-8-sig', sep=';', lineterminator='\n')
                    files_created += 1
                elif input_ext in ['.xls', '.xlsx']:
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=UserWarning)
                        if input_ext == '.xlsx':
                            df_chunk.to_excel(output_file, index=False, engine='openpyxl')
                        else:  # .xls
                            df_chunk.to_excel(output_file, index=False, engine='xlwt')
                    files_created += 1
            except Exception as save_error:
                print(f"Ошибка при сохранении: {save_error}")
                import traceback
                traceback.print_exc()
       
        print(f"\nФайлы сохранены в директории: {output_dir}. Количество: {files_created}")
        
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")


def f_find_files():
    """
    Находит все файлы .xls, .xlsx, .csv в текущей директории
    """
    current_dir = os.getcwd()
    supported_ext = ['.xls', '.xlsx', '.csv']
    supported_files = []
    
    for file in os.listdir(current_dir):
        # Пропускаем временные файлы
        if file.startswith('~$'):
            continue
        file_ext = os.path.splitext(file)[1].lower()
        if file_ext in supported_ext:
            if os.path.isfile(os.path.join(current_dir, file)):
                supported_files.append(file)
    
    return sorted(supported_files)


def f_display_files_list(files):
    """
    Отображает нумерованный список файлов
    """
    if not files:
        print("  В текущей директории нет файлов в формате .xls, .xlsx, .csv")
        return
    
    for idx, file in enumerate(files, 1):
        print(f"  {idx:3d}. {file}")

def f_get_file_name(files):
    """
    Получает от пользователя номер выбранного файла
    """
    while True:
        try:
            choice = int(input(f"\nВыберите файл (1-{len(files)}): "))
            if 1 <= choice <= len(files):
                return files[choice - 1]
            else:
                print(f"  Ошибка: Пожалуйста, введите число от 1 до {len(files)}")
        except ValueError:
            print("  Ошибка: Пожалуйста, введите число")

def get_rows_per_file():
    """
    Получает от пользователя количество строк для разделения
    """
    while True:
        try:
            rows = input("\nВведите количество строк для одного выходного файла: ")
            if not rows:
                print("  Пожалуйста, введите число")
                continue
                
            rows_per_file = int(rows)
            if rows_per_file > 0:
                return rows_per_file
            else:
                print("  Ошибка: Пожалуйста, введите целое положительное число")
        except ValueError:
            print("  Ошибка: Пожалуйста, введите целое положительное число")

def main():
    # Поиск файлов
    supported_files = f_find_files()
    
    # Проверка наличия файлов
    if not supported_files:
        print("В текущей директории нет файлов в формате .xls, .xlsx, .csv")
        return
    
    # Логика выбора файла
    if len(supported_files) == 1:
        selected_file = supported_files[0]
    else:
        # Отображение списка файлов
        f_display_files_list(supported_files)
    
        # Выбор файла пользователем
        selected_file = f_get_file_name(supported_files)
    
    # Получение количества строк
    rows_per_file = get_rows_per_file()
    
    # Обработка выбранного файла
    f_split_file_by_rows(selected_file, rows_per_file)
    
if __name__ == "__main__":
    main()