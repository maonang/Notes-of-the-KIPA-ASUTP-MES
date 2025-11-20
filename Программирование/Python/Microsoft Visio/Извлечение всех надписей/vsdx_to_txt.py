from vsdx import VisioFile
import os

# pip install vsdx

# pip install pyinstaller
# pyinstaller --onefile --windowed --distpath "C:\\Users\\User\\Desktop\\Извлечь текст из vsdx\\" "C:\\Users\\User\\Desktop\\Извлечь текст из vsdx\\vsdx_to_txt.py"

def def_extract_text_from_vsdx(s_vsdx_file_path : str) -> list[str]:
    """ Извлечение текста из файла vsdx

    :param s_vsdx_file_path:
    :return: Список с текстом из файла
    """
    # Путь к файлу Visio
    vsdx : VisioFile = VisioFile(s_vsdx_file_path)
    list_vsdx_text : list = []
    with VisioFile(s_vsdx_file_path) as vsdx:
        for page in vsdx.pages:                             # Перебираем все страницы
            for shape in page.child_shapes:                 # Перебираем все фигуры на странице
                if shape.text:       # Если у фигуры есть текст
                    if shape.text.count(chr(10)) > 0:       # Если текст содержит перенос строки, то удаляем его
                        s_text : str = shape.text.replace(chr(10), " ")
                    else:
                        s_text : str = shape.text
                    list_vsdx_text.append(s_text)           # Добавляем текст в список

    list_vsdx_text: list = sorted(list_vsdx_text)

    for i in range(len(list_vsdx_text)):
        list_vsdx_text[i] = list_vsdx_text[i].strip()
        while list_vsdx_text[i].count("  ") > 0:                    # Удаляем лишние пробелы
            list_vsdx_text[i] = list_vsdx_text[i].replace("  ", " ")

    while list_vsdx_text.count("") > 0:                             # Удаляем пустые строки
        list_vsdx_text.remove("")
    while list_vsdx_text.count(" ") > 0:                            # Удаляем элементы, содержащие только пробелы
        list_vsdx_text.remove(" ")
    while list_vsdx_text.count("\n") > 0:                           # Удаляем элементы, содержащие только перенос строки
        list_vsdx_text.remove("\n")

    return list_vsdx_text

if __name__ == '__main__':
    list_vsdx_text : list = []
    for file in os.listdir():
        if file.endswith(".vsdx"):
            print(file)
            list_vsdx_text : list = def_extract_text_from_vsdx(file)        # Извлекаем текст
            # Сохраняем текст из vsdx в txt-файл
            s_file_name : str = file.replace(".vsdx", ".txt")   # Имя txt-файла
            with open(s_file_name, 'w', encoding='utf-8') as f:
                f.write("\n".join(list_vsdx_text))

print("Готово.")
