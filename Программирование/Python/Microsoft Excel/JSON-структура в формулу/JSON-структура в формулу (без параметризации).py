import re


def json_to_excel_formula(json_str):
    # Очистка строки: удаляем переносы и лишние пробелы
    cleaned = re.sub(r'[\n\r\t]', ' ', json_str)
    cleaned = re.sub(r' +', ' ', cleaned)
    cleaned = cleaned.strip()

    # Проверяем общую длину строки
    warning_message = None
    if len(cleaned) > 255:
        warning_message = (
            "\nВНИМАНИЕ: Длина текстовых значений в формулах не может превышать 255 символов. Чтобы создать в формуле текстовые значения длиннее 255 символов, воспользуйтесь функцией СЦЕПИТЬ или оператором сцепления (&).\n"
            f"Текущая длина: {len(cleaned)} символов\n"
        )

    # Экранирование кавычек для Excel
    excel_safe = cleaned.replace('"', '""')

    # Формируем формулу Excel
    result = f'="{excel_safe}"'

    return result, warning_message


if __name__ == "__main__":
    while True:
        try:
            print("Введите JSON-строку:")
            lines = []
            while True:
                line = input().strip()
                if line == "" and lines:
                    break
                if line:
                    lines.append(line)
                if not lines:
                    continue

            if not lines:
                break

            s_input = "\n".join(lines)
            s_output, warning = json_to_excel_formula(s_input)

            print(f"\nРезультат для вставки в Excel:")
            print(s_output)

            if warning:
                print(warning)

            print("-" * 80)
        except Exception as e:
            print(f"Ошибка: {e}")