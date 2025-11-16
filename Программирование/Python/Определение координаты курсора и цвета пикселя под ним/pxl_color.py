# Программа определяет поординаты курсора и цвет пикселя. Клавиша Esc завершает работу программы.
# Компиляция в exe: pyinstaller --onefile "C:\Users\*\Desktop\pxl color.py"
# Путь до exe: C:\Users\*\dist

import pyautogui
from PIL import ImageGrab
import time
import keyboard
import os

# Функция определяет цвет пикселя под курсором
def def_get_pxl_color(x,y):
    img = ImageGrab.grab().load()
    return img[x, y]

# Функция изменяет цвет текста
def def_color_text(text, color):
    r, g, b = color[0], color[1], color[2]
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def main():
    last_pos = pyautogui.position()
    last_color = def_get_pxl_color(last_pos.x, last_pos.y)
    while True:
        if keyboard.is_pressed('esc'):
            print('Выход из программы.')
            break
        pos = pyautogui.position()
        color = def_get_pxl_color(pos.x, pos.y)

        if pos != last_pos or color != last_color:
            color_block = def_color_text("██", color)
            print(f"x,y = {pos.x},{pos.y}\t\tRGB{color}\t\t█{color_block}█")
            last_pos = pos
            last_color = color
        time.sleep(0.1)

if __name__ == "__main__":
    if os.name == 'nt':
        os.system('color')
    main()


