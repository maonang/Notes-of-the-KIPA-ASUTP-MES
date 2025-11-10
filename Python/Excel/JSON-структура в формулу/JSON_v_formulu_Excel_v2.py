import json

def json_to_excel_formula(json_str):
    """
    Преобразует JSON-строку в строку формулы для вставки в Excel.
    """
    try:
        def def_process_item(item):
            '''
            # Рекурсивная функция для обработки всех значений словаря (json-структуры)
            '''
            if isinstance(item, dict):
                return {key: def_process_item(value) for key, value in item.items()}
            elif isinstance(item, list):
                return [def_process_item(elem) for elem in item]
            elif isinstance(item, str):
                if len(item) > 254:
                    # Разбиваем длинную строку на части по 250 символов
                    parts = [item[i:i + 254] for i in range(0, len(item), 254)]
                    return '" & '+ " & ".join(f'"{part}"' for part in parts) + ' & "'
                return f'" & "{item}" & "'
            return item
        # Загрузка строки как JSON
        dict_json = json.loads(json_str)
        dict_json_change = def_process_item(dict_json)
        s_json = str(dict_json_change)
        s_json = s_json.replace('\'', '""')
        s_json = s_json.replace('\\""', "'") # ПРОВЕРИТЬ!
        s_json = s_json.replace(' True', "true")
        s_json = s_json.replace(' False', "false")
        return f'="{s_json}"'
    except json.JSONDecodeError:
        return "Ошибка: Некорректная JSON-строка"

if __name__ == "__main__":
    while (True):
        s_input = input("Введите JSON-строку: ").strip()
        s_output = json_to_excel_formula(s_input)
        print("\nРезультат для вставки в Excel:")
        print(s_output)
        print()
