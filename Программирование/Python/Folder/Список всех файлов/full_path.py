import os
import re

directory = 'F:\DC++'
with open('list.txt', 'w', encoding='utf-8') as file:
    for root, _, files in os.walk(directory):
        for filename in files:
            full_path = os.path.join(root, filename)
            relative_path = re.sub(r'^' + re.escape(directory), '', full_path)
            file.write(directory + relative_path + '\n')