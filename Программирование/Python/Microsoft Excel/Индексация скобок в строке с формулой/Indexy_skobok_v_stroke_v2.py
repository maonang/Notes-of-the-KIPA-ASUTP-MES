# pyinstaller --onefile "D:\FLASH\Python\Индексы скобок в строке.py" --distpath "D:\FLASH\Python\"

def insert_spaces(s):
    s_lst = list(s)
    i, cnt_bracket, cnt_bracket_buf = 0, 0, 0
    while i < len(s_lst) - 1:
        if s_lst[i] in ['(', ')', '{', '}', '[', ']']:
            cnt_bracket += 1 if s_lst[i] in ['(', '{', '['] else -1
            cnt_bracket_buf = cnt_bracket if s_lst[i] in ['(', '{', '['] else cnt_bracket + 1
        if (s_lst[i] in ['(', ')', '{', '}', '[', ']']) and (s_lst[i + 1] in ['(', ')', '{', '}', '[', ']']):
            # Количество разрядов в индексе скобки
            bracket_index_len = len(str(cnt_bracket_buf))
            # Добавление разделителя между символами исходной строки в списке для того, чтобы индексы в нижестоящей строке не были вместе
            s_lst.insert(i + 1, ' ' * bracket_index_len)
            i += bracket_index_len - 1
        i += 1
    return ''.join(s_lst)

def find_error(s:str) -> bool:
    b_flg_error = False
    # Проверка №1
    if (s.count('(') + s.count(')')) % 2 != 0:
        b_flg_error = True
        print('-- Ошибка! В строке присутствуют круглые скобки без пар.')
    if (s.count('{') + s.count('}')) % 2 != 0:
        b_flg_error = True
        print('-- Ошибка! В строке присутствуют фигурные скобки без пар.')
    if (s.count('[') + s.count(']')) % 2 != 0:
        b_flg_error = True
        print('-- Ошибка! В строке присутствуют квадратные скобки без пар.')
    return b_flg_error

def s_stat(s: str):
    global b_flg_error
    print(f'- Общее количество символов: {len(s)}')
    if b_flg_error == False:
        print(f'- Количество пар скобок:')
        if s.count('(') + s.count(')') > 0:
            print(f'\t\t (...): {s.count('(')} шт')
        if s.count('{') + s.count('}') > 0:
            print('\t\t {...}:', s.count('{'), 'шт')
        if s.count('[') + s.count(']') > 0:
            print(f'\t\t [...]: {s.count('[')} шт')

def add_bracket_numbers(s):
    s_out_lst = []
    c_cnt_bracket = 0
    # Длина текущего символа. Если не скобка, то 1, если скобка, то длина по количеству разрядов её индекса
    flg_cnt = 1
    for i, c in enumerate(s):
        if c in ['(', ')', '{', '}', '[', ']']:
            c_cnt_bracket += 1 if c in ['(', '{', '['] else -1
            s_out_lst.append(str(c_cnt_bracket + (1 if c in [')', '}', ']'] else 0)))
            flg_cnt = len(str(c_cnt_bracket + (1 if c in [')', '}', ']'] else 0)))
        else:
            # Добавление разделителя для обычного символа
            s_out_lst.append(' ' if flg_cnt == 1 else '')
            # Обратный счетчик длины для скобок
            flg_cnt -= 1 if flg_cnt != 1 else 0
    return ''.join(s_out_lst)


def print_in_chanks(s1: str, s2: str, chunk_size: int = 100):
    for i in range(0, len(s1), chunk_size):
        s1_out = s1[i:i + chunk_size]
        s2_out = s2[i:i + chunk_size]
        if len(s1) > 100:
            print(f'Часть {i + 1}-{i + chunk_size}')
        print(s1_out)
        print(s2_out)
        print()

# Удаление пробелов вначале и в конце строки
def delete_space(s: str, par:int) -> str:
    cnt_space = 0
    for c in s[::par]:
        if c == ' ':
            cnt_space += 1
        else:
            break
    if par == 1:
        return s[cnt_space::]
    else:
        return s[:len(s)-cnt_space:]

def s_change(s: str) -> str:
    while s.count(chr(9)) > 0:
        s = s.replace(chr(9), '', 1)
    # Удаление пробелов вначале и в конце строки
    s = delete_space(s,1)
    s = delete_space(s,-1)
    return s


if __name__ == "__main__":
    while True:
        b_flg_error = False
        input_string = ''
        print('-' * 100)
        while ((input_string == '') or (
                input_string.count('(') + input_string.count('{') + input_string.count('[') +
                input_string.count(')') + input_string.count('}') + input_string.count(']') == 0)):
            input_string = input('Введите строку для обработки: ')
            # Удаление лишних символов
            input_string = s_change(input_string)
            b_flg_error = find_error(input_string)
        # Информационное поле
        s_stat(input_string)
        # Обработка исходной строки
        input_string_change = insert_spaces(input_string)
        # Формирование строки с порядковыми номерами скобок
        bracket_in_string = add_bracket_numbers(input_string_change)
        print('-' * 100)
        print_in_chanks(input_string_change, bracket_in_string)
