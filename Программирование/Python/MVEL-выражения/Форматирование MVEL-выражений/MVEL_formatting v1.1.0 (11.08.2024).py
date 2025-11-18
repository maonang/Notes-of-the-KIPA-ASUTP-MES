'''
Добавить (по возможности):
- Проверку на пропущенные ";"
- Определять используемые методы. Учесть различные регистры. Пример: pow(), Math.log10(), sqrt()
- Добавить проверку наличия скобок для вараинтов if (() and ( || ))
- В условиях учесть неправильный порядок скобок вида if ) ... (. Количество и пара верная, но порядок - нет
'''

# Для копирования списков
import copy
# Для работы с файловой системой
import os
# Для работы с регулярными выражениями
import re
# Для запуска и завершения процессов Windows
import subprocess
# Для поиска процессов Windows
import psutil
# Для работы с выгрузкой из ОМ ZIIoT, которая имеет запись в формате Json
import json

# ---------------------
# Глобальные переменные
# ---------------------
s_global_help_text_0: str = ''
s_global_help_text_1: str = ''
# Список вещественных чисел с ошибками
s_global_buf_1: str = ''
# Количество пропущенных скобок по видам
s_global_buf_2: str = ''
# Количество кавычек
s_global_buf_3: str = ''
s_global_buf_4: str = ''
s_global_buf_5: str = ''
s_global_buf_6: str = ''
# Список переменных (атрибутов), которых нет в атрибутах и не имеют объявления типа данных
lst_global_undefind_var: list = []
# Список переменных (атрибутов), которых нет в атрибутах и не объявлены совсем
lst_global_not_declared_var: list = []
dict_global_buf_4: dict = {}
# Флаг, информирующий о том, что на вход был передан json из выгрузки ОМ ZIIoT
b_blobal_input_is_json: bool = False
# Глобальные переменные из выгрузки ОМ ZIIoT
s_global_json_tagid: str = ''
lst_global_json_variables: list = []
s_global_json_expression: str = ''
b_global_json_isflowcalc: bool = False
s_global_json_triggertype: str = ''
i_global_json_offsetinseconds: int = 0
i_global_json_periodinseconds: int = 0
# Глобальная переменная для определения категории тега
s_global_code_correct: str = ''
# Глобальная переменная, информирующая в консоли о том, что есть сообщения, требующие внимания пользователя
b_global_find_error: bool = False
# Глобальная переменная, информирующая в консоли о сохранении результатов работы программы в файлы
b_global_save_to_file: bool = False


def def_code_correct(s_code: str) -> str:
    '''
    Функция для обработки текста и удаления лишних пробелов

    :param s_code: Строка для обработки
    :return:
    '''
    # Список вещественных чисел с ошибками
    global s_global_buf_1
    # Количество пропущенных скобок по видам
    global s_global_buf_2
    # Количество кавычек
    global s_global_buf_3

    s_buf: str = s_code

    # Предварительная обработка строки
    s_buf = def_pre_change_text(s_buf)


    # Проверка строки на источник. Если это выгрузка из ОМ ZIIoT, то выделить из неё MVEL-выражение
    if def_json_valid(s_code):
        s_buf = def_value_of_key(s_buf, 'expression')

    # Проверка пар скобок
    s_global_buf_2 = ''
    if not(s_buf.count('(') == s_buf.count(')') and \
           s_buf.count('[') == s_buf.count(']') and \
           s_buf.count('{') == s_buf.count('}')):
        if s_buf.count('(') != s_buf.count(')'):
            s_global_buf_2 += f'Круглые скобки: {s_buf.count('(')} / {s_buf.count(')')}\n'
        if s_buf.count('[') != s_buf.count(']'):
            s_global_buf_2 += f'Квадратные скобки: {s_buf.count('[')} / {s_buf.count(']')}\n'
        if s_buf.count('{') != s_buf.count('}'):
            s_global_buf_2 += f'Фигурные скобки: {s_buf.count('{')} / {s_buf.count('}')}'

    # Проверка пар кавычек
    s_global_buf_3 = ''
    if not(s_buf.count('"') % 2 == 0 and s_buf.count("'") % 2 == 0):
        if s_buf.count('"') % 2 != 0:
            s_global_buf_3 += f'Двойные кавычки: {s_buf.count('"')} / {s_buf.count('"') + 1}\n'
        if s_buf.count("'") % 2 != 0:
            s_global_buf_3 += f'Одинарные кавычки: {s_buf.count("'")} / {s_buf.count("'") + 1}\n'

    # Исправление разделителя вещественного числа ("," -> ".")
    s_re_pattern = re.compile(r'-?\d+,\d+(?:[eE][+-]?\d+)?')
    lst_s_buf_incorrect_number = s_re_pattern.findall(s_buf)
    if len(lst_s_buf_incorrect_number):
        # Сохраняем информацию об ошибках в числах в лог-файл
        with open('output_info.txt', 'a', encoding='utf-8') as file:
            s_global_buf_1 = ", ".join(lst_s_buf_incorrect_number)
        s_buf = s_re_pattern.sub(lambda x: x.group().replace(',', '.'), s_buf)
    s_buf = s_buf.replace(',', ', ')

    # Исправление написания экспоненты
    s_buf = re.sub(r'([0-9])e([+-]?\d+)', r'\1E\2', s_buf)
    s_buf = s_buf.strip()
    s_buf = ' '.join(s_buf.split())
    return s_buf


def def_find_if(s_code: str) -> str:
    '''
    Функция для поиска и исправления ошибок во всех блоках с условием
    :param s_code: Строка с MVEL-выражением
    :return:
    '''
    # Глобальные переменные для передачи строк с ошибками в логических выражениях
    global s_global_buf_4, s_global_buf_5, s_global_buf_6
    # Переменная для внесения исправлений в исходное MVEL-выражение
    s_code_buf: str = s_code
    # Регулярное выражение, возвращающее все логическое выражение от "if" до "{" не включительно
    s_re_pattern: str = r'\bif\s*(.*?)\s*\{'
    lst_block_if: list = re.findall(s_re_pattern, s_code_buf)

    # print('\n'.join(lst_block_if))

    # Все блоки условий в одну строку для поиска в выражении пропущенного символа "="
    s_lst_block_if: str = ''.join(lst_block_if)

    # Регулярное выражение, возвращающее группу с найденным оператором присваивания
    s_re_pattern = r'[^=!<>]=[^=]'
    lst_block_equal: list = re.findall(s_re_pattern, s_lst_block_if)

    # Поиск блоков условия с ошибкой и формирование строки с указанием о них
    s_global_buf_4 = ''
    if lst_block_equal:
        for s_block_if in lst_block_if:
            if s_block_if.count(' = '):
                s_global_buf_4 += f'Условие №{lst_block_if.index(s_block_if) + 1}: {s_block_if}\n'
                # Исправление ошибки в MVEL-выражении
                s_code_buf = s_code_buf.replace(s_block_if, s_block_if.replace(' = ', ' == '))

    s_global_buf_5 = ''
    s_global_buf_6 = ''
    if lst_block_if:
        for i in range(len(lst_block_if)):
            # Поиск блоков условий с пропущенной скобкой вначале или в конце
            if not (lst_block_if[i].startswith('(') and lst_block_if[i].endswith(')')):
                s_global_buf_5 += f'Условие №{i + 1}: {lst_block_if[i]}\n'
                # Исправление ошибки в MVEL-выражении
                if not lst_block_if[i].startswith('('):
                    # Добавляем скобку вначале блока с условием
                    s_code_buf = s_code_buf.replace(lst_block_if[i], '(' + lst_block_if[i])
                    # Обновление значения списка для другой (следующей) проверки
                    lst_block_if[i] = '(' + lst_block_if[i]
                else:
                    # Добавляем скобку в конце блока с условием
                    s_code_buf = s_code_buf.replace(lst_block_if[i], lst_block_if[i] + ') ')
                    # Обновление значения списка для другой (следующей) проверки
                    lst_block_if[i] = lst_block_if[i] + ') '
                    # Удаление возможного дублирования пробелов
                    if s_code_buf.count('  '):
                        s_code_buf = s_code_buf.replace('  ', ' ')
                    if lst_block_if[i].count('  '):
                        lst_block_if[i] = lst_block_if[i].replace('  ', ' ')

            # Поиск блоков условий с пропущенными скобками в составе логического выражения
            if not(lst_block_if[i].count('(') == lst_block_if[i].count(')') and \
                   lst_block_if[i].count('[') == lst_block_if[i].count(']') and \
                   lst_block_if[i].count('{') == lst_block_if[i].count('}')):
                s_global_buf_6 += f'Условие №{i + 1}: {lst_block_if[i]}\n'

                if lst_block_if[i].count('(') != lst_block_if[i].count(')'):
                    s_global_buf_6 += f'\tКруглые скобки: {lst_block_if[i].count('(')} / {lst_block_if[i].count(')')}\n'
                if lst_block_if[i].count('[') != lst_block_if[i].count(']'):
                    s_global_buf_6 += f'\tКвадратные скобки: {lst_block_if[i].count('[')} / {lst_block_if[i].count(']')}\n'
                if lst_block_if[i].count('{') != lst_block_if[i].count('}'):
                    s_global_buf_6 += f'\tФигурные скобки: {lst_block_if[i].count('{')} / {lst_block_if[i].count('}')}\n'

    return s_code_buf


def def_var_local(s_code: str) -> str:
    '''
    Функция для формирования статистики: перечень всех локальных переменных, объявленных явно

    :param s_code:
    '''
    # Переменная для последующего исключения локальных переменных из общего списка, чтобы получить список глобальных переменных
    global dict_global_buf_4

    # Регулярное выражение для поиска объявлений локальных переменных
    s_re_pattern = r'\b(Boolean|Byte|Char|Double|Float|Int|Long|Short|String)\s+(\w+)'
    lst_data_types = ['boolean', 'byte', 'char', 'double', 'float', 'int', 'long', 'short', 'string']
    # Словарь для хранения всех локальных переменных с группировкой по ключу (типу данных)
    dict_global_buf_4 = {key: [] for key in lst_data_types}

    # Заполнение словаря переменными с разбивкой по ключу (типам данных)
    for lst_var_one in re.finditer(s_re_pattern, s_code, re.IGNORECASE):
        s_data_type, s_variable = lst_var_one[1].lower(), lst_var_one[2]
        dict_global_buf_4[s_data_type].append(s_variable)

    # Сортировка и удаление повторов переменных по имени в пределах ключей
    for data_type in lst_data_types:
        dict_global_buf_4[data_type] = sorted(list(set(dict_global_buf_4[data_type])))

    # Сохранение словаря в глобальную переменную dict_global_buf_4 для поиска глобальных переменных в будущем
    dict_global_buf_4 = copy.deepcopy(dict_global_buf_4)

    s_out = ''
    for data_type, variables in dict_global_buf_4.items():
        if variables and data_type:
            s_out += '\t' + data_type + ": " + ', '.join(variables) + '\n'
    return s_out


def def_clear_sub_str_type_1(s_str: str) -> str:
    '''
    Функция для удаления подстроки в кавычках

    :param s_str: Строка MVEL-выражения для поиска и удаления блоков с текстов в кавычках
    :return: Строка MVEL-выражения без текста в кавычках
    '''
    lst_result: list = []
    lst_stack: list = []
    i: int = 0
    while i < len(s_str):
        if s_str[i] in {'"', "'"}:
            if lst_stack and lst_stack[-1] == s_str[i]:
                lst_stack.pop()
            else:
                lst_stack.append(s_str[i])
        elif not lst_stack:
            lst_result.append(s_str[i])
        i += 1
    return ''.join(lst_result)


def def_clear_sub_str_type_2(s_str: str) -> str:
    '''
    Функция для удаления подстроки между /* и */

    :param s_str: Строка MVEL-выражения для поиска и удаления блоков с комментариями
    :return: Строка MVEL-выражения без комментариев
    '''
    s_re_pattern: str = r'/\*.*?\*/'
    return re.sub(s_re_pattern, '', s_str)



def def_var_all(s_code: str) -> str:
    '''
    Функция для поиска всех переменных в MVEL-выражении

    :param s_code: Строка с MVEL-выражением
    :return: строку в виде перечисления всех найденных переменных
    '''
    # Регулярное выражение для поиска переменных
    s_re_pattern: str = r'\b[A-Za-z_]\w*\b(?!\s*\()'
    # Список подстрок, которые нужно исключить из результата
    lst_s_code_delete_str: list = ['boolean', 'byte', 'char', 'double', 'else', 'false', 'float', 'if', 'int', 'long',
                                   'null', 'return', 'short', 'true', 'and', 'or', 'string', 'import']
    s_code_buf: str = s_code
    # Удаление подстрок между символами "
    s_code_buf = def_clear_sub_str_type_1(s_code_buf)
    # Удаление подстрок между символами /* и */
    s_code_buf = def_clear_sub_str_type_2(s_code_buf)

    lst_var: list = re.findall(s_re_pattern, s_code_buf)
    # Фильтрация совпадений, исключая переменные с точками слева или справа
    lst_var = [match for match in lst_var if not re.search(rf'\.{match}\b|\b{match}\.', s_code_buf)]
    lst_var = list(set(lst_var))
    # Фильтрация совпадений, исключая ключевые слова и функции
    lst_var = [match for match in lst_var if not match.lower() in lst_s_code_delete_str]
    # Сортировка списка без учета регистра
    lst_var = sorted(lst_var, key=lambda s: s.lower())
    return ', '.join(lst_var)

def def_code_formatting(s_code: str) -> str:
    '''
    Функция для форматирования MVEL-выражения

    :param code: строка с MVEL-выражением
    :return:
    '''
    # Разбивка кода на блоки списка по символам "{", "}", ";"
    lst_code: list = re.split(r'(\{|\}|;|/\*.*?\*/)', s_code, flags=re.DOTALL)
    lst_code = [s_lst_code.strip() for s_lst_code in lst_code]

    # Сборка элементов, исключая пустые строки
    lst_buf: list = []
    s_buf: str = ''
    for lst_code_one in lst_code:
        if lst_code_one.strip():
            if lst_code_one.startswith('/*') and lst_code_one.endswith('*/'):
                # Если найден комментарий, сразу добавляем его в список и очищаем буфер
                if s_buf:
                    lst_buf.append(s_buf.strip())
                    s_buf = ''
                lst_buf.append(lst_code_one)
            elif lst_code_one == '}' or lst_code_one == '{':
                lst_buf.append(s_buf.strip())
                lst_buf.append(lst_code_one)
                s_buf = ''
            elif lst_code_one == ';':
                if len(lst_buf) > 0 and lst_buf[len(lst_buf)-1] == '}':
                    lst_buf[len(lst_buf)-1] = lst_buf[len(lst_buf)-1] + ';'
                else:
                    lst_buf.append(s_buf.strip() + lst_code_one)
                s_buf = ''
            else:
                s_buf += lst_code_one
    if s_buf:
        lst_buf.append(s_buf.strip())
    # Удалить пустые элементы списка
    if lst_buf:
        lst_buf = list(filter(None, lst_buf))

    # Обрабатываем блоки if-else для добавления отступов
    s_code_new: str = ""
    i_tab_lvl: int = 0
    s_tab_char: str = "    " # 4 пробела

    for s_code_one in lst_buf:
        # Комментарии имеют нулевую вложенность
        # print('---', s_code_one)
        if s_code_one.startswith('/*') and s_code_one.endswith('*/'):
            # print('---')
            s_code_new += s_code_one + '\n'
        elif s_code_one.startswith('if') or s_code_one.startswith('else'):
            s_code_new += s_tab_char * i_tab_lvl + s_code_one + '\n'
        elif s_code_one.startswith('{'):
            s_code_new += s_tab_char * i_tab_lvl + s_code_one + '\n'
            i_tab_lvl += 1
        elif s_code_one.startswith('}'):
            i_tab_lvl -= 1
            s_code_new += s_tab_char * i_tab_lvl + s_code_one + '\n'
        else:
            s_code_new += s_tab_char * i_tab_lvl + s_code_one + '\n'
    return s_code_new


def def_check_file_size(s_file_name: str) -> bool:
    '''
    Функция для проверки размера файла (пустой или нет)
    Если файл пустой, то результат False (работа с файлом не имеет смысла)

    :param s_file_name: Имя файла, который нужно проверить на размер
    :return:
    '''
    return False if os.stat(s_file_name).st_size == 0 else True


def def_check_process(s_poc_name: str) -> int:
    '''
    Функция для проверки наличия активного процесса

    :param s_poc_name: Название процесса в Windows
    :return: Возвращает количество процессов с заданным именем
    '''
    lst_proc = [proc.info['name'] for proc in psutil.process_iter(['name']) if proc.info['name'] == s_poc_name]
    return len(lst_proc)


def def_check_and_create_file_txt(lst_file_name: list):
    '''
    Функция для проверки существования файла в каталоге с программой.
    Если файла нет, то он будет создан. Переменная s_file_name должна содержать формат файла.

    :param lst_file_name: Список с названиями файлов, которые нужно создать при их отсутствии
    '''
    for s_file_name_one in  lst_file_name:
        if not os.path.exists(s_file_name_one):
            with open(s_file_name_one, 'w', encoding='utf-8'):
                pass


def def_var_del_matches(s_str_1: str) -> str:
    '''
    Функция для удаления локальных переменных из общего списка всех переменных для получения списка глобальных
    :param s_str_1: Cтрока со всеми обнаруженными переменными
    :return:
    '''
    # dict_global_buf_4 - словарь с локальными переменными
    global dict_global_buf_4
    global lst_global_json_variables
    global lst_global_not_declared_var
    global s_global_code_correct

    # Список всех переменных
    lst_str_1 = list(s_str_1.split(", "))

    for lst_dict_value in dict_global_buf_4.values():
        if lst_dict_value:
            for s_lst_dict_value in lst_dict_value:
                if s_lst_dict_value in lst_str_1:
                    lst_str_1.remove(s_lst_dict_value)

    # Работа выгрузкой как с json
    # Если это выгрузка из ОМ ZIIoT в формате jdon, то глобальные переменные (атрибуты) берем из конфигурации json,
    # а не анализируем само выражение. Список lst_str_1 используем для определения неопределенных переменных.
    # Если это не выгрузка, то просто выводим список lst_str_1.
    if b_blobal_input_is_json:
        s_buf: str = ''
        # Словарь с аргументами и описанием к ним
        dict_local_var_and_desc: dict = {}
        # Определение максимальной длины ключа для выравнивания описания атрибутов
        i_max_len_key: int = 0
        for dict_lst_global_json_variables in lst_global_json_variables:
            i_max_len_key = max(i_max_len_key, len(dict_lst_global_json_variables.get('alias')))
        # Заполнение словаря атрибутами и описанием к ним
        for dict_lst_global_json_variables in lst_global_json_variables:
            # Список фрагментов пути к свойству атрибута в ОМ ZIIoT
            lst_sub_str = dict_lst_global_json_variables.get('value').split('|')
            dict_local_var_and_desc[dict_lst_global_json_variables.get('alias')] = str(lst_sub_str[1]) + ' [' + str(lst_sub_str[0]) + ']'
            s_buf += f'{dict_lst_global_json_variables.get('alias')} {' ' * (i_max_len_key - len(dict_lst_global_json_variables.get('alias')))}- {lst_sub_str[1]} [{lst_sub_str[0]}]\n'
        # Формирование списка локальных переменных без типа данных
        for s_lst_str_1 in lst_str_1:
            if not (s_lst_str_1 in dict_local_var_and_desc):
                if s_global_code_correct.count(s_lst_str_1 + ' = '):
                    lst_global_undefind_var.append(s_lst_str_1)
                else:
                    lst_global_not_declared_var.append(s_lst_str_1)
        return s_buf
    return ', '.join(lst_str_1)


def def_find_MVEL_result(s_code: str) -> str:
    '''
    Функция для получения списка результатов работы выражения MVEL.
    Извлекает текст между ";" и "}", проверяя, что нет символа "="

    :param s_code: строка с MVEL-выражением
    :return:
    '''
    s_re_pattern_1 = r';([^=}]*)}'
    s_re_pattern_2 = r';([^=}]*)[}]?$'
    s_re_pattern_3 = r'{([^=},]*)}'

    s_buf: str = s_code

    # Удаление подстрок между символами /* и */. Кавычки удалять нельзя, иначе нарушится содержимое строки
    s_buf = def_clear_sub_str_type_2(s_buf)
    # Если выражение сложное, то разбиваем на части через регулярное выражение, иначе сразу передаем как результат
    if s_buf.count('=') + s_buf.count('if (') + s_buf.count('{'):
        # Поиск внутри выражения
        lst_result_1 = re.findall(s_re_pattern_1, s_buf)

        # Поиск с правого края выражения
        lst_result_2 = re.findall(s_re_pattern_2, s_buf)
        lst_result_2 = sorted(list(set(lst_result_2)))

        # Поиск одичночных выражений внутри { }
        lst_result_3 = re.findall(s_re_pattern_3, s_buf)
        lst_result_3 = sorted(list(set(lst_result_3)))

        for s_lst_result_2 in lst_result_2:
            if not s_lst_result_2 in lst_result_1:
                lst_result_1.append(s_lst_result_2)

        for s_lst_result_3 in lst_result_3:
            if not s_lst_result_3 in lst_result_1:
                lst_result_1.append(s_lst_result_3)
        # Удаление символа ";" из результатов выражений (для чистоты)
        lst_result_1 = [s_result.replace(';', '') for s_result in lst_result_1]
        # Удаление пробелов по краям результатов выражений
        lst_result_1 = [s_result.strip() for s_result in lst_result_1]
        # Удаление дубликатов списка с последующей сортировкой
        lst_result_1 = sorted(list(set(lst_result_1)))
        return ', '.join(lst_result_1)
    return s_buf


def def_text_file_to_var(s_file_name: str, b_new_line:bool) -> str:
    '''
    Функция для передачи в переменную содержимого файла по его имени

    :param s_file_name: Имя файла
    :return: Содержимое файла. Если b_new_line = True, то будут добавлены переносы строк, иначе будет передана одна строка
    '''
    s_buf: str = ''
    lst_all_lines: list = []

    with open(s_file_name, 'r', encoding='utf-8') as file:
        if b_new_line:
            lst_all_lines = [s_one_line.rstrip() for s_one_line in file]
            s_buf += '\n'.join(lst_all_lines)
        else:
            s_buf = file.read()
    return s_buf


def def_write_to_file(s_filename: str, s_param: str, lst_text: list):
    """
    Функция для записи списка значений в файл.

    :param s_filename: Путь к файлу, в который нужно записать данные
    :param s_param: Параметр открытия файла (r, w, a)
    :param lst_text: Список значений для записи в файл
    """
    global b_global_save_to_file

    s_dir: str = os.path.dirname(s_filename)
    if s_dir and not os.path.exists(s_dir):
        print(f"Директория {s_dir} не существует.")
        return
    try:
        # Открытие файла с обработкой возможных исключений
        with open(s_filename, s_param, encoding='utf-8') as file:
            for s_text in lst_text:
                file.write(str(s_text))
        # print(f"Запись в файл {s_filename} выполнена успешно.")
        b_global_save_to_file = True
    except IOError as e:
        print(f"Ошибка при открытии файла {s_filename}: {e}")


def def_second_to_str(i_time_sec: int) -> str:
    '''
    Функция преобразования секунд в строку из полных часов, минут и секунд
    :param i_time_sec: Количество секунд
    :return:
    '''
    i_h: int = i_time_sec // 3600
    i_m: int = (i_time_sec % 3600) // 60
    i_sec: int = i_time_sec % 60

    lst_time_parts = []

    if i_h > 0:
        lst_time_parts.append(f"{i_h} ч")
    if i_m > 0:
        lst_time_parts.append(f"{i_m} мин")
    if i_sec > 0 or not lst_time_parts:  # выводим "0 сек", если нет других частей
        lst_time_parts.append(f"{i_sec} сек")

    return ' '.join(lst_time_parts)


def def_triggertype_to_rus(s_text: str) -> str:
    '''
    Функция для исправления английского написания параметра на русское
    :param s_text:
    :return:
    '''
    global i_global_json_offsetinseconds
    global i_global_json_periodinseconds
    dict_translate: dict = {'Periodic': 'Периодический',
                            'ListenData': 'Потоковый (по изменению любого атрибута)',
                            'ByTrigger': 'По триггеру (по изменению выбранных атрибутов)',
                            'OnDemand': 'По запросу',
                            'Periodic': 'Периодический'}
    if s_text == 'Periodic':
        s_text = (dict_translate.get(s_text) +
                  ' [Период: ' + str(def_second_to_str(i_global_json_periodinseconds)) +
                  '; Сдвиг: ' + str(def_second_to_str(i_global_json_offsetinseconds)) + ']')
        return s_text
    else:
        return dict_translate.get(s_text)


def def_code_1():
    '''
    Функция выполняет алгоритм по команде "1":
    '''
    # Глобальные переменные для заполнения лог-файла данными из других функций
    global s_global_buf_1, s_global_buf_2, s_global_buf_3, s_global_buf_4, s_global_buf_5, s_global_buf_6
    global s_global_code_correct, b_global_find_error, b_global_save_to_file
    global s_global_json_tagid, lst_global_json_variables, b_global_json_isflowcalc, s_global_json_triggertype

    if def_check_file_size('input.txt') == False:
        print('Файл input.txt пустой.')
        return 0

    with open('input.txt', 'r', encoding='utf-8') as file:
        s_code = file.read()

    # Проверяем и исправляем однострочное MVEL-выражение
    s_corrected_code = def_code_correct(s_code)

    # Поиск ошибок в блоках условия if (в самих логических выражениях)
    s_corrected_code = def_find_if(s_corrected_code)
    s_global_code_correct = s_corrected_code

    # Форматируем код
    s_formatted_code = def_code_formatting(s_corrected_code)

    # Сохраняем отформатированный код
    def_write_to_file('output_format.txt', 'w', [s_formatted_code])

    # Список всех переменных
    s_var_all: str = def_var_all(s_corrected_code)

    # Список локальных переменных
    s_var_local = def_var_local(s_corrected_code)

    # Список результатов выражения
    s_MVEL_result = def_find_MVEL_result(s_corrected_code)

    # Готовим список глобальных переменных
    s_var_global = def_var_del_matches(s_var_all) if (s_var_all and s_var_local) or lst_global_json_variables else s_var_all

    # Подмена пустого результата s_MVEL_result на переменные найденные переменные
    if not s_MVEL_result and lst_global_undefind_var:
        s_MVEL_result = '[Предварительно] ' + ','.join(lst_global_undefind_var)

    if not s_MVEL_result and not lst_global_undefind_var and s_var_local:
        s_MVEL_result = '[Предварительно] ' + s_var_local

    # Сохраняем исправленный код в лог-файл
    def_write_to_file('output_info.txt', 'w', ['MVEL-выражение:\n', s_corrected_code, '\n\n'])

    if s_global_buf_1 or s_global_buf_2 or s_global_buf_3 or s_global_buf_4 or lst_global_not_declared_var:
        def_write_to_file('output_info.txt', 'a', [f'{'▼▲' * 24}\n'])
        b_global_find_error = True

    # Сохраняем информацию об ошибках в числах в лог-файл
    if s_global_buf_1:
        def_write_to_file('output_info.txt', 'a',
                   ['░ ► [Исправлено] Обнаружены ошибки в десятичном разделителе вещественных числах:\n',
                           '░\t' + s_global_buf_1, '\n░\n'])
        b_global_save_to_file = True

    if s_global_buf_2 != '':
        s_global_buf_2 = '\n'.join(f"░\t{line}" for line in s_global_buf_2.splitlines())
        def_write_to_file('output_info.txt', 'a',
                   ['░ ► Обнаружено несовпадение количества скобок:\n',
                           s_global_buf_2, '\n░\n'])

    if s_global_buf_3 != '':
        s_global_buf_3 = '\n'.join(f"░\t{line}" for line in s_global_buf_3.splitlines())
        def_write_to_file('output_info.txt', 'a',
                   ['░ ► Обнаружено несовпадение количества кавычек:\n',
                           s_global_buf_3, '\n░\n'])

    if s_global_buf_4 != '':
        s_global_buf_4 = '\n'.join(f"░\t{line}" for line in s_global_buf_4.splitlines())
        def_write_to_file('output_info.txt', 'a',
                   ['░ ► [Исправлено] Обнаружен оператор присваивания вместо сравнения в логических выражениях:\n',
                           s_global_buf_4, '\n░\n'])

    if s_global_buf_5 != '':
        s_global_buf_5 = '\n'.join(f"░\t{line}" for line in s_global_buf_5.splitlines())
        def_write_to_file('output_info.txt', 'a',
                   ['░ ► [Исправлено] Обнаружены пропущенные скобки на краях логических выражений:\n',
                           s_global_buf_5, '\n░\n'])

    if s_global_buf_6 != '':
        s_global_buf_6 = '\n'.join(f"░\t{line}" for line in s_global_buf_6.splitlines())
        def_write_to_file('output_info.txt', 'a',
                   ['░ ► Обнаружены пропущенные скобки внутри логических выражений:\n',
                           s_global_buf_6, '\n░\n'])

    # Сохраняем список переменных, которые нигде не объявлены в лог-файл
    if lst_global_not_declared_var:
        def_write_to_file('output_info.txt', 'a',
                   ['░ ► Переменные, которые нигде не объявлены:\n',
                           '░\t' + ', '.join(lst_global_not_declared_var), '\n░\n'])

    if s_global_buf_1 or s_global_buf_2 or s_global_buf_3 or s_global_buf_4 or lst_global_not_declared_var:
        def_write_to_file('output_info.txt', 'a', [f'{'▼▲' * 24}\n\n'])

    # Сохраняем в лог-файл тег, в который производится запись результата выражения
    if s_global_json_tagid:
        def_write_to_file('output_info.txt', 'a',
                   ['Запись в тег:\n', '\t' + s_global_json_tagid, '\n\n'])

    # Сохраняем в лог-файл тип запуска выражения
    if s_global_json_triggertype:
        def_write_to_file('output_info.txt', 'a',
                   ['Тип запуска:\n', '\t' + def_triggertype_to_rus(s_global_json_triggertype), '\n\n'])

    # Сохраняем список глобальных переменных (атрибутов) в лог-файл
    if s_var_global:
        if b_blobal_input_is_json:
            s_var_global = '\n'.join(f"\t{line}" for line in s_var_global.splitlines())
        else:
            s_var_global = '\t' + s_var_global
        def_write_to_file('output_info.txt', 'a',
                   ['Атрибуты выражения:\n', s_var_global, '\n\n'])

    # Сохраняем список локальных переменных в лог-файл
    if s_var_local:
        def_write_to_file('output_info.txt', 'a',
                   ['Локальные переменные:\n', s_var_local, '\n\n'])

    # Сохраняем список переменных без типов данных в лог-файл
    if lst_global_undefind_var:
        def_write_to_file('output_info.txt', 'a',
                   ['Локальные переменные без явно указанного типа данных:\n',
                           '\t' + ', '.join(lst_global_undefind_var), '\n\n'])

    # Сохраняем список результатов выражений в лог-файл
    if s_MVEL_result:
        def_write_to_file('output_info.txt', 'a',
                   ['Результат работы выражения:\n', '\t' + s_MVEL_result, '\n\n'])

    if b_global_save_to_file:
        print('Готово. Результат сохранен в файлы.')
        print()


def def_code_2():
    '''
    Функция выполняет алгоритм по команде "2":
        - Проверяет файл output_format.txt на наличие текста
        - Извлекает строку из файла output_format.txt
        - Обрабатывает строку из файла output_format.txt
        - Сохраняет результат в файл input.txt
    '''
    # Проверка файла на наличие символов для обработки
    if not def_check_file_size('output_format.txt'):
        print('Файл output_format.txt пустой.')
        return 0

    # Чтение файла и получение из него строки для последующей обработки
    s_text_file = def_text_file_to_var('output_format.txt', False)

    # Обработка полученной строки с последующим сохранением в файл input.txt
    def_save_MVEL_to_File(s_text_file)


def def_pre_change_text(s_text: str) -> str:
    '''
    Функция для предварительной обработки строки.

    :param s_text: Исходная строка
    :return: Возвращает измененную строку
    '''
    s_buf: str = s_text
    lst_text_replace: list = ['\t', '\n']

    # Удаление символов в строке из списка
    for s_text_replace in lst_text_replace:
        while s_buf.count(s_text_replace) > 0:
            s_buf = s_buf.replace(s_text_replace, ' ')

    # Удалить повторяющиеся пробелы
    while s_buf.count('  ') > 0:
        s_buf = s_buf.replace('  ', ' ')

    # Добавить недостающие пробелы
    dict_replacement: dict = {
        '=': ' = ',
        '>': ' > ',
        '<': ' < ',
        '+': ' + ',
        '/': ' / ',

        '  .': '.',
        ' .': '.',

        '  ,': ',',
        ' ,': ',',

        ' \'': '\'',
        '*': ' * ',

        '*  -': '*-',
        '* -': '*-',

        '\'  *': '\'*',
        '\' *': '\'*',

        '*  \'': '*\'',
        '* \'': '*\'',

        '. *': '.*',
        '*  /': '*/',
        '/  *': '/*',

        '|  |': ' || ',
        '| |': ' || ',
        '||': ' || ',

        '=  =': '==',
        '= =': '==',

        '!  =': ' != ',
        '! =': ' != ',

        '<  =': ' <= ',
        '< =': ' <= ',

        '>  =': ' >= ',
        '> =': ' >= ',

        ';': '; '
    }
    for s_old, s_new in dict_replacement.items():
        s_buf = s_buf.replace(s_old, s_new)

    # Удаление пробела после символа "{", если есть
    s_re_pattern = r'\{\s'
    s_buf = re.sub(s_re_pattern, '{', s_buf)

    # Удаление пробела перед символом "}", если есть
    s_re_pattern = r'\s\}'
    s_buf = re.sub(s_re_pattern, '}', s_buf)

    # Удаление пробела после символа "(", если есть
    s_re_pattern = r'\(\s'
    s_buf = re.sub(s_re_pattern, '(', s_buf)

    # Удаление пробела перед символом ")", если есть
    s_re_pattern = r'\s\)'
    s_buf = re.sub(s_re_pattern, ')', s_buf)

    # Удаление пробела после символа "[", если есть
    s_re_pattern = r'\[\s'
    s_buf = re.sub(s_re_pattern, '[', s_buf)

    # Удаление пробела перед символом "]", если есть
    s_re_pattern = r'\s\]'
    s_buf = re.sub(s_re_pattern, ']', s_buf)

    # Добавление пробела после символа "}", если за ним нет символа ";"
    s_re_pattern = r'}(?!\s*;)'
    s_buf = re.sub(s_re_pattern, '} ', s_buf)

    # Удаление пробела между символами "}", если есть
    s_re_pattern = r'\}\s\}'
    s_buf = re.sub(s_re_pattern, '}}', s_buf)

    # Удалить повторяющиеся пробелы, возникшие после обработки
    while s_buf.count('  ') > 0:
        s_buf = s_buf.replace('  ', ' ')
    return s_buf

def def_save_MVEL_to_File(s_text: str):
    '''
    Функция для сохранения выражения MVEL в файл input.txt, если не выбрали ни одну из команд,
    но ввели выражение вручную или вставили из буфера обмена

    :param s_text: Строка, предположительно, с MVEL-выражением
    :return: Сохраняет результат обработки в файл
    '''
    # Предварительная обработка строки
    s_text: str = def_pre_change_text(s_text)
    # Сохраняем обработанное однострочное MVEL-выражение в файл input.txt для последующей обработки
    def_write_to_file('input.txt', 'w', [s_text])


def def_json_valid(s_text: str) -> bool:
    '''
    Функция для проверки строки на формат записи Json.
    Если результат True, то с ней можно работать как со словарем

    :param s_text: строка для проверки
    :return: True или False
    '''
    try:
        json.loads(s_text)
        return True
    except ValueError:
        return False


def def_value_of_key(s_text: str, s_json_key: str) -> str:
    '''
    Функция для возврата значения по ключу из json выгрузки ОМ ZIIoT

    :param s_text: Строка из таблицы с выгрузкой ОМ из платформы ZIIoT
    :return: Возвращает MVEL-выражение из общей строки выгрузки
    '''
    if def_json_valid(s_text):
        dict_json_text: dict = json.loads(s_text)
        if s_json_key in dict_json_text:
            return dict_json_text.get(s_json_key)
    return s_text


def def_check_symbol(s_text: str) -> bool:
    '''
    Функция для проверки наличия в строке русских символов
    :param s_text: Команда или строка, вводимая в консоль
    :return:
        True - проверка не пройдена. Строка не будет принята в работу
        False - проверка пройдена успешно. "Препятствий" нет.
    '''
    # Исходный текст нулевой длины
    if len(s_text) == 0:
        return True

    if s_text.startswith('+') or s_text.startswith('-'):
        b_buf = not(all(not ('\u0400' <= char <= '\u04FF') for char in s_text))
        return b_buf
    # Если строка начинается не с "+", то потенциально может быть скопирована из выгрузки ОМ ZIIoT и содержать названия
    # аргументов на русском языке
    return False

def def_json_parsing(s_code: str):
    global s_global_json_tagid
    global lst_global_json_variables
    global s_global_json_expression
    global b_global_json_isflowcalc
    global s_global_json_triggertype
    global i_global_json_offsetinseconds
    global i_global_json_periodinseconds

    # Заполняем словарь значениями из выгрузки ОМ ZIIoT
    dict_json_text: dict = json.loads(s_code)
    # Заполняем глобальные переменные значениями из выгрузки ОМ ZIIoT
    s_global_json_tagid = dict_json_text.get('tagId') if 'tagId' in dict_json_text else ''
    lst_global_json_variables = dict_json_text.get('variables') if 'variables' in dict_json_text else []
    s_global_json_expression = dict_json_text.get('expression') if 'expression' in dict_json_text else ''
    b_global_json_isflowcalc = dict_json_text.get('isFlowCalc') if 'isFlowCalc' in dict_json_text else False
    s_global_json_triggertype = dict_json_text.get('triggerType') if 'triggerType' in dict_json_text else ''
    i_global_json_offsetinseconds = dict_json_text.get('offsetInSeconds') if 'offsetInSeconds' in dict_json_text else 0
    i_global_json_periodinseconds = dict_json_text.get('periodInSeconds') if 'periodInSeconds' in dict_json_text else 0


def def_reset_global_var():
    '''
    Функция для сброса глобальных переменных перед обработкой нового MVEL-выражения или команды
    '''
    global lst_global_undefind_var
    global lst_global_not_declared_var
    global b_global_find_error
    global b_global_save_to_file
    global s_global_json_tagid
    global lst_global_json_variables
    global s_global_json_expression
    global b_global_json_isflowcalc
    global s_global_json_triggertype
    global i_global_json_offsetinseconds
    global i_global_json_periodinseconds
    global s_global_buf_1
    global s_global_buf_2
    global s_global_buf_3
    global s_global_buf_4
    global s_global_buf_5
    global s_global_buf_6

    b_global_find_error = False
    b_global_json_isflowcalc = False
    b_global_save_to_file = False
    i_global_json_offsetinseconds = 0
    i_global_json_periodinseconds = 0
    lst_global_json_variables = []
    lst_global_not_declared_var = []
    lst_global_undefind_var = []
    s_global_buf_1 = ''
    s_global_buf_2 = ''
    s_global_buf_3 = ''
    s_global_buf_4 = ''
    s_global_buf_5 = ''
    s_global_buf_6 = ''
    s_global_json_expression = ''
    s_global_json_tagid = ''
    s_global_json_triggertype = ''

def main():
    global s_global_help_text_0
    global s_global_help_text_1
    global b_blobal_input_is_json
    global lst_global_undefind_var
    global lst_global_not_declared_var
    global b_global_find_error
    global b_global_save_to_file



    print(s_global_help_text_0)

    # Проверка файлов на наличие. Если их нет, то создать в каталоге с программой
    def_check_and_create_file_txt(['input.txt', 'output_format.txt', 'output_info.txt'])

    while True:
        while True:
            # Сброс глобальных переменных
            def_reset_global_var()
            s_code: str = ''
            s_buf: str = ''
            # Ввод команды или строки в консоль сопровождается проверкой
            while def_check_symbol(s_code):
                s_code = str(input('-> '))

            # Завершение работы программы
            if s_code == '0':
                return 0
            # Отформатировать выражение MVEL
            elif s_code == '1':
                s_buf = def_text_file_to_var("input.txt", False)
                if def_json_valid(s_buf):
                    # На вход был передан json
                    b_blobal_input_is_json = True
                    def_json_parsing(s_buf)
                # Заполнение глобальных переменных выгрузкой из ОМ ZIIoT
                def_code_1()
            # Обработать изменения, внесенные в отформатированный файл и получить однострочное выражение
            elif s_code == '2':
                def_code_2()
                def_code_1()
            # Отобразить содержимое txt в консоли
            elif s_code.lower() == '+i':
                s_buf = def_text_file_to_var("output_info.txt", True)
                print(s_buf)
                print()
            # Отобразить содержимое txt в консоли
            elif s_code.lower() == '+f':
                s_buf = def_text_file_to_var("output_format.txt", True)
                print(s_buf)
                print()
            # Завершить все процессы notepad.exe
            elif s_code.lower() == '-n':
                # Проверка наличия процессов блокнота
                if def_check_process("notepad.exe"):
                    os.system('chcp 65001')
                    subprocess.run(['taskkill', '/f', '/im', 'notepad.exe'])
            # Открыть через блокнот файлы txt
            elif s_code.lower() == '+n':
                subprocess.Popen(['notepad.exe', "output_format.txt"])
                subprocess.Popen(['notepad.exe', "output_info.txt"])
            # Открыть через блокнот файл input.txt
            elif s_code.lower() == '+ni':
                subprocess.Popen(['notepad.exe', "input.txt"])
            # Отобразить список команд
            elif s_code.lower() == 'help':
                print('Список команд:')
                print(s_global_help_text_1)
                print()
            # Обработка MVEL-выражения из выгрузки объектной модели ZIIoT (поле "Configuration")
            elif def_json_valid(s_code):
                # На вход был передан json
                b_blobal_input_is_json = True
                # Заполнение глобальных переменных выгрузкой из ОМ ZIIoT
                def_json_parsing(s_code)
                # Сохранение MVEL-выражения в файл input.txt
                if s_global_json_expression:
                    def_save_MVEL_to_File(s_global_json_expression)
                    def_code_1()
            # Обработка MVEL-выражения, введенного вручную или вставленного из буфера обмена
            else:
                if not s_code.startswith('{"tagId":"'):
                    def_save_MVEL_to_File(s_code)
                    def_code_1()
            if b_global_find_error:
                print('░ ► В файле output.txt присутствует информация, требующая внимания пользователя.')

def def_fill_global_var():
    '''
    Функция для заполнения некоторых глобальных переменных
    '''
    global s_global_help_text_0
    global s_global_help_text_1

    s_global_help_text_0 = 'Программа предназначена для форматирования однострочных MVEL-выражений.\n' \
                            'Версия 1.1.0 от 11.08.2024. Автор: Петров М.Ю.\n' \
                            '\n' \
                            '\tФайл output_info.txt содержит обобщенную статистику по обработанному MVEL-выражению.\n' \
                            '\tФайл output_format.txt содержит скорректированное выражение в отформатированном виде.\n' \
                            '\n' \
                            'Для получения списка команд введите help.\n'

    s_global_help_text_1 = '\t0 - Выход из программы;\n' \
             '\t1 - Отформатировать MVEL-выражение: input.txt -> output_info.txt и output_format.txt;\n' \
             '\t2 - Преобразовать исправленное отформатированное MVEL-выражение в одну строку: output_format.txt -> output_info.txt;\n' \
             '\t+n - Открыть в блокноте файлы output_format.txt и output_info.txt;\n' \
             '\t+ni - Открыть в блокноте файл input.txt;\n' \
             '\t-n - Завершить все процессы notepad.exe;\n' \
             '\t+i - Отобразить содержимое файла output_info.txt в консоли;\n' \
             '\t+f - Отобразить содержимое файла output_format.txt в консоли;\n' \
             '\thelp - Отобразить список команд;\n' \
             '\tили введите MVEL-выражение.'

if __name__ == '__main__':
    # Заполнение ряда глобальных переменных
    def_fill_global_var()
    # Выполнение основной программы
    main()