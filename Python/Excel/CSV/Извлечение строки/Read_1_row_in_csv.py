import os
import sys
import csv
import json
from datetime import datetime

def detect_data_type(value):
    """
    Определяет тип данных значения, включая даты.
    """
    if value == "":
        return "Empty", 0, value  # Пустое значение
    try:
        json_value = json.loads(value)
        if isinstance(json_value, (dict, list)):  # JSON-объект или массив
            formatted_value = json.dumps(json_value, indent=4, ensure_ascii=False)
            return "JSON", len(value), formatted_value
    except (json.JSONDecodeError, TypeError):
        pass
    try:
        if "." in value:  # Проверка на число с плавающей точкой
            float_value = float(value)
            return "float", len(value), float_value
        else:  # Проверка на целое число
            int_value = int(value)
            return "int", len(value), int_value
    except ValueError:
        pass
    try:
        # Попытка распознать дату и время
        parsed_date = datetime.fromisoformat(value)  # ISO 8601 формат
        return "datetime", len(value), parsed_date
    except ValueError:
        pass
    # Если ничего не подошло, это строка
    return "str", len(value), value

input_file = "input.csv"
output_file = "output_1 row.txt"

# Увеличиваем лимит размера поля
csv.field_size_limit(10_000_000)  # 10 миллионов символов

# Проверяем наличие файла рядом с программой
if not os.path.isfile(input_file):
    print(f"Ошибка: Файл '{input_file}' не найден.")
    sys.exit(1)

with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    s_headers = next(reader)
    s_data = next(reader)
    row_count = sum(1 for _ in reader) + 1

data_dict = dict(zip(s_headers, s_data))

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"Название файла: {input_file}\n")
    f.write(f"Общее количество строк: {row_count}\n\n")
    f.write(f"Содержимое первой строки:\n")
    for key, value in data_dict.items():
        data_type, char_count, formatted_value = detect_data_type(value)
        if data_type == "JSON":
            f.write(f"{key} : {data_type}, {char_count} симв. =\n{formatted_value}\n")
        else:
            f.write(f"{key} : {data_type}, {char_count} симв. = {formatted_value}\n")
        f.write("-" * 100 + "\n")
print(f"Данные успешно сохранены в {output_file}")