import os

def def_rename(s_root_dir : str, s_pattern : str):
    ''' Процедура переименования файлов и папок

    :param s_root_dir: Исходная папка
    :param s_pattern: Регулярное выражение для удаления строки из названий файлов и папок
    '''
    # Количество файлов и папок
    i_cnt: int = 0
    for root, dirs, files in os.walk(s_root_dir, topdown=False):
        # Переименовываем файлы
        for name in files:
            # Путь к файлу до переименования
            s_path_old : str = os.path.join(root, name)
            # Новое имя файла
            s_name_new : str = name.replace(s_pattern, '')
            if s_name_new != name:
                # Путь к файлу после переименования
                s_path_new : str = os.path.join(root, s_name_new)
                # Переименовываем
                os.rename(s_path_old, s_path_new)
                i_cnt += 1
        # Переименовываем папки
        for name in dirs:
            # Путь к папке до переименования
            s_path_old = os.path.join(root, name)
            # Новое имя папки
            s_name_new: str = name.replace(s_pattern, '')
            if s_name_new != name:
                # Путь к папке после переименования
                s_path_new = os.path.join(root, s_name_new)
                # Переименовываем
                os.rename(s_path_old, s_path_new)
                i_cnt += 1
    print()
    print(f"Переименовано суммарно файлов и папок: {i_cnt}")

# Путь к корневой папке
s_iput_dir = input("Введите путь к корневой папке: ")
# Строка для удаления
s_pattern = input('Введите строку для удаления (например, [eground.org]): ')

def_rename(s_iput_dir, s_pattern)
print("Готово.")

