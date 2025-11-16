import PyPDF2
import re
import os

def find_keywords_in_pdf(pdf_path, keywords_file, output_file):
    if not os.path.exists(keywords_file):
        print("Ошибка: Файл с ключевыми словами не найден.")
        return

    with open(keywords_file, 'r', encoding='utf-8') as f:
        keywords = f.read().splitlines()

    if not keywords:
        print("Ошибка: Файл с ключевыми словами пустой.")
        return

    if not os.path.exists(pdf_path):
        print("Ошибка: Файл PDF не найден.")
        return

    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)

        with open(output_file, 'w', encoding='utf-8') as out_file:
            keywords_found = 0
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text().lower()

                found_keywords = []
                for keyword in keywords:
                    keyword_pattern = re.compile(r'\b' + re.escape(keyword.lower()) + r'\b')
                    matches = keyword_pattern.findall(page_text)
                    if matches:
                        found_keywords.extend([(keyword, page_num + 1) for _ in range(len(matches))])
                        keywords_found += 1

                for keyword, page_number in found_keywords:
                    out_file.write(f'{keyword} - страница {page_number}\n')

                if (page_num + 1) % 100 == 0:
                    print(f"Обработано {page_num + 1} страниц из {num_pages}.")

            print("Поиск завершен.")
            print(f"Найдено ключевых слов: {keywords_found} из {len(keywords)}.")

pdf_path = "D:/Файл.pdf"
keywords_file = "D:/keyword.txt"
output_file = "D:/out.txt"

find_keywords_in_pdf(pdf_path, keywords_file, output_file)

