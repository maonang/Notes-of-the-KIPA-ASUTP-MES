# Поиск совпадения тегов из файла F1.txt в файле F2.txt
file1_path = 'D:/F1.txt'  # Что ищем
file2_path = 'D:/F2.txt'  # Где ищем
output_file_path = 'D:/out.txt'  # Результат поиска

with open(file1_path, 'r') as f1:
    tags_file1 = f1.read().splitlines()

with open(file2_path, 'r') as f2:
    tags_file2 = f2.read().splitlines()

with open(output_file_path, 'w') as output:
    for tag1 in tags_file1:
        matching_tags = []
        for tag2 in tags_file2:
            if tag1.lower() in tag2.lower():
                matching_tags.append(tag2)

        if len(matching_tags) > 0:
            if len(matching_tags) > 20:
                output.write(f"{tag1}: ...\n")
            else:
                output.write(f"{tag1}: {', '.join(matching_tags)}\n")