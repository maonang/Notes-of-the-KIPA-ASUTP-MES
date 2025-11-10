import re

while True:
    s_MVEL: str = input('Введите MVEL-выражение: ')

    # Удаляем лишние пробелы
    s_MVEL = re.sub(r'\s+', ' ', s_MVEL).strip()

    # Извлекаем части выражения
    re_match = re.match(r'(.*?=)(.*?;)(.*)', s_MVEL)
    if not re_match:
        raise ValueError("Не удалось разделить выражение на части.")

    s_MVEL_expression_before = re_match.group(1).strip()  # Часть до '=' -> r'(.*?=)'. Пример: Double Debalance =
    s_MVEL_expression_only = re_match.group(2).strip(';')  # Выражение между '=' и ';' -> r'(.*?;)'. Пример: (F943 + ... + FT23402)  * (1) + (F14401 + ... + FT2451) * (-1)
    s_MVEL_expression_after = re_match.group(3).strip()  # Часть после ';' -> r'(.*)'. Пример: ; Debalance

    re_pattern = r'(?<!\w)([A-Za-z][A-Za-z0-9]*)(?!\w)'
    list_var: list = re.findall(re_pattern, s_MVEL_expression_only)

    # Убираем дубликаты переменных, сохраняя порядок
    list_unique_var = []
    for var in list_var:
            if var not in list_unique_var:
                list_unique_var.append(var)

    # Формируем блоки проверки
    list_block: list = []
    for s_var in list_unique_var:
        s_block: str = (
            f"Double D{s_var}; "
            f"if (Fn.badVal(${s_var}, '*')) {{D{s_var} = 0}} else {{D{s_var} = {s_var}}};"
        )
        list_block.append(s_block)

    # Заменяем переменные в выражении
    s_MVEL_expression_change: str = re.sub(re_pattern, lambda match: f"D{match.group(1)}", s_MVEL_expression_only)
    # Объединяем части
    s_MVEL_new: str = f"{s_MVEL_expression_before}{s_MVEL_expression_change}; {s_MVEL_expression_after}"
    s_result: str = "\n".join(list_block) + "\n" + s_MVEL_new
    print(s_result)