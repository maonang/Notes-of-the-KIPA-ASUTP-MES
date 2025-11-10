import pandas as pd

file_path = "D:/PIMS and LIMS/PIMS.csv"
output_txt_file = "D:/PIMS and LIMS/output_txt_file.txt"

df = pd.read_csv(file_path, encoding='cp1251', low_memory=False)

# Определение кол-ва строк в документе
num_rows = df.shape[0]
print("Количество строк в документе:", num_rows)

# Определение уникальных тегов и их количество
tag_counts = df['ID'].value_counts() # Если указать TAGNAME, то обрабатывает  соседний столбец с датой
num_unique_tags = len(tag_counts)
with open(output_txt_file, 'w', encoding='utf-8') as txt_file:
    for tag, count in tag_counts.items():
        txt_file.write(f"{tag} - {count}\n")
print("Количество уникальных значений в столбце TAGNAME:", num_unique_tags)
print("Уникальные значения и их количество сохранены в файл:", output_txt_file)
