import pandas as pd
import re

file_path = "D:/PIMS.csv"
df = pd.read_csv(file_path, encoding='cp1251', low_memory=False)
grouped_data = df.groupby('ID')
for tagname, group in grouped_data:
    tagname = re.sub(r'[\\/:*?"<>|]', '_', str(tagname))
    output_file_name = f"D:/out/PIMS_{tagname}.csv"
    group.to_csv(output_file_name, index=False, encoding='utf-8')
print("Обработка завершена. Создано 2360 файлов.")

