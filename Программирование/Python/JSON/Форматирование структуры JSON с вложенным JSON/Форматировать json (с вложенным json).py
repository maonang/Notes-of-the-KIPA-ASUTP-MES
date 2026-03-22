import json
import os

def main():
    input_file = "input.txt"
    output_file = "output.txt"
    
    if not os.path.exists(input_file):
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write("")
        return
    
    try:
        # Читаем исходный JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
        
        # Обрабатываем все поля, которые могут содержать вложенный JSON
        for key, value in data.items():
            if isinstance(value, str):
                try:
                    # Пробуем распарсить значение как JSON
                    inner_data = json.loads(value)
                    # Форматируем с отступами (4 пробела)
                    pretty_inner = json.dumps(inner_data, ensure_ascii=False, indent=4)
                    # Сохраняем обратно
                    data[key] = pretty_inner
                except:
                    pass
        
        # Форматируем внешний JSON
        result = json.dumps(data, ensure_ascii=False, indent=4)
        
        # Заменяем \n на реальные переносы строк
        result = result.replace('\\n', '\n')
        
        # Разбираем результат построчно
        lines = result.split('\n')
        final_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            final_lines.append(line)
            
            # Проверяем, является ли эта строка началом поля с вложенным JSON
            if ': "' in line and '"{\n' in line:
                # Находим позицию открывающей кавычки
                quote_pos = line.find(': "') + 3
                indent = ' ' * quote_pos
                
                i += 1
                # Обрабатываем первую строку вложенного JSON (открывающая скобка)
                if i < len(lines):
                    first_line = lines[i]
                    final_lines.append(indent + first_line.lstrip())
                    i += 1
                
                # Обрабатываем остальные строки вложенного JSON
                while i < len(lines):
                    current_line = lines[i]
                    if current_line.strip().endswith('"') and not current_line.strip().endswith('",'):
                        final_lines.append(indent + current_line.lstrip())
                        i += 1
                        break
                    else:
                        if current_line.strip():
                            final_lines.append(indent + current_line.lstrip())
                        else:
                            final_lines.append(current_line)
                        i += 1
            else:
                i += 1
        
        # Сохраняем результат
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(final_lines))

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()