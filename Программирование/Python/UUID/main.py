import os
import re
import pandas as pd
import warnings

"""
    Скрипт для поиска UUID объекта из SQL-запроса в поле ID таблицы XLSX.
"""

# Игнорирование предупреждений от openpyxl
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

def def_list_json_files(s_file_type : str) -> list:
    """
        Сформировать список всех файлов рядом с программой, имеющих формат s_file_type
    """
    # Получаем содержимое текущего каталога
    current_dir = os.getcwd()
    # Список всех файлов с расширением s_file_type
    list_files= [f for f in os.listdir(current_dir) if f.endswith("." + s_file_type)]
    return list_files

def def_display_file_list(s_file_type : str, list_file : list):
    """
        Вывести список всех файлов рядом с программой, имеющих формат s_file_type
    """
    print(f"Список {s_file_type} файлов:")
    for i_index, s_file_name in enumerate(list_file):
        print(f"\t{i_index + 1}. {s_file_name}")

def def_from_num_get_file(i_file_cnt : int) -> int:
    """
        Обработка файла по индексу, введенного с клавиатуры
    """
    if i_file_cnt > 1:
        while True:
            try:
                i_index_file = int(input("Введите номер файла из списка для обработки: "))
                if 1 <= i_index_file <= i_file_cnt:
                    # Возвращаем индекс файла
                    return i_index_file - 1
                else:
                    if i_file_cnt > 1:
                        print(f"Пожалуйста, введите номер от 1 до {i_file_cnt}.")
            except ValueError:
                print("Пожалуйста, введите корректный номер.")
    else:
        return 0

def def_set_data_sql(file_path : str) -> set:
    """
        Множество всех значений UUID по маске из SQL-файла.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        s_data_sql = file.read()

    # Паттерн UUID вида 00000000-0000-0000-0000-000000000000
    re_pattern = r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
    list_data_sql = re.findall(re_pattern, s_data_sql)
    return set(list_data_sql)

def def_set_data_xlsx(file_path : str, col_name : str = "Id") -> set:
    """
        Множество всех значений из поля col_name в Excel-файле
    """
    df = pd.read_excel(file_path)
    if col_name not in df.columns:
        raise ValueError(f"В Excel-файле отсутствует столбец с именем {col_name}.")
    set_data_xlsx = set(df[col_name].astype(str))
    return set_data_xlsx


def def_set_miss_data(set_data_sql, set_data_xlsx : set) -> set:
    """
        Возвращает пропущенные UUID, сравнивая два множества.
    """
    set_miss_data = set_data_sql - set_data_xlsx
    return set_miss_data

def def_miss_data_to_txt(set_miss_data : set):
    if set_miss_data:
        with open("Result.txt", "w", encoding="utf-8") as f:
            print("Не найдены следующие UUID:")
            f.write("Не найдены следующие UUID:\n")
            for s_data in set_miss_data:
                print(f"\t{s_data}")
                f.write(f"\t{s_data}\n")
    else:
        print("Все UUID из SQL-файла найдены в Excel.")
        s_file_name : str = "Result.txt"
        if os.path.exists(s_file_name):
            os.remove(s_file_name)
            print(f"Файл {s_file_name} был удалён, так как все UUID были найдены.")


def def_main(s_sql_file_path, s_xlsx_file_path : str):
    print()
    print(f"Обработка SQL-файла {s_sql_file_path}", end=' ')
    set_data_sql = def_set_data_sql(s_sql_file_path)
    print('-> Готово.')

    print(f"Обработка Excel-файла {s_xlsx_file_path}", end=' ')
    set_data_xlsx = def_set_data_xlsx(s_xlsx_file_path)
    print('-> Готово.')

    print()

    print(f"Найдено {len(set_data_sql)} UUID в SQL-файле.")
    print(f"Найдено {len(set_data_xlsx)} UUID в xlsx-файле.")
    print()

    set_miss_data = def_set_miss_data(set_data_sql, set_data_xlsx)
    # Сохранение результата в файл txt
    def_miss_data_to_txt(set_miss_data)

print('Программа предназначена для формирования списка UUID объектов модели, используемых в SQL-запросе, но отсутствующих в выгрузке объектной модели. Для работы в каталоге с программой должны находится 2 файла: sql и xlsx. Результат работы будет выведен в консоль и выходной файл Result.txt\n'
      'Версия 1.0 от 24.11.2024. Автор: Петров М.Ю.')
print()
# SQL
list_sql_file_name : list = def_list_json_files("sql")
if not list_sql_file_name:
    print("Ошибка: Файлы с расширением .sql не найдены рядом с программой.")
    input()
    exit()
elif len(list_sql_file_name) > 1:
    def_display_file_list("sql", list_sql_file_name)
sql_file_path = list_sql_file_name[def_from_num_get_file(len(list_sql_file_name))]

print()

# xlsx
list_xlsx_file_name : list = def_list_json_files("xlsx")
if not list_xlsx_file_name:
    print("Ошибка: Файлы с расширением .xlsx не найдены рядом с программой.", end=' ')
    input()
    exit()
elif len(list_xlsx_file_name) > 1:
    def_display_file_list("xlsx", list_xlsx_file_name)
excel_file_path = list_xlsx_file_name[def_from_num_get_file(len(list_xlsx_file_name))]

def_main(sql_file_path, excel_file_path)
input()