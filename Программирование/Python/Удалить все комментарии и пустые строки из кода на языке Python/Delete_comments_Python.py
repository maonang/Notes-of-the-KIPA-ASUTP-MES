import os
import re

def def_remove_python_comments(s_input_file_name : str, s_output_file_name : str) -> None:
    if not os.path.exists(s_input_file_name):
        with open(s_input_file_name, 'w', encoding='utf-8') as f_out:
            f_out.write('')
        print(f"Файл {s_input_file_name} создан. Добавьте данные в него и запустите программу снова.")
        return
    # Читаем файл
    if os.path.getsize(s_input_file_name) == 0:
        print(f"Файл {s_input_file_name} пуст. Добавьте данные в него и запустите программу снова.")
        return

    with open(s_input_file_name, 'r', encoding='utf-8') as f_in:
        s_file_text = f_in.read()
    # Удаляем многострочные комментарии ''' и """
    s_file_text = re.sub(r'"""(.*?)"""', '', s_file_text, flags=re.DOTALL)
    s_file_text = re.sub(r"'''(.*?)'''", '', s_file_text, flags=re.DOTALL)
    # Удаляем однострочные комментарии, которые начинаются с #
    list_lines = s_file_text.splitlines()
    list_lines_filtered = []
    for s_line in list_lines:
        s_line_stripped = s_line.strip()
        if s_line_stripped.startswith('#') or not s_line_stripped:
            continue
        # Удаляем комментарии после кода на той же строке
        line = re.sub(r'\s*#.*', '', s_line).rstrip()
        if s_line.strip():
            list_lines_filtered.append(line)
    # Записываем результат в файл
    with open(s_output_file_name, 'w', encoding='utf-8') as f_out:
        f_out.write('\n'.join(list_lines_filtered))
    print(f"Файл {s_input_file_name} обработан. Результат сохранен в {s_output_file_name}.")

s_input_file_name = 'input.txt'
s_output_file_name = 'output.txt'
def_remove_python_comments(s_input_file_name, s_output_file_name)





