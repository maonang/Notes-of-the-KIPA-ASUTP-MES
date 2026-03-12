import os
import csv
import re
from datetime import datetime
from collections import defaultdict
import PyPDF2

def extract_figures_from_pdf(pdf_path, mode=1):
    """
    Извлекает рисунки из PDF файла.
    mode=1: одна строка с разделителем '/"
    mode=2: отдельные строки на русском и английском
    """
    if not os.path.exists(pdf_path):
        print(f"PDF файл не найден: {pdf_path}")
        return []

    print(f"\nОбработка PDF: {os.path.basename(pdf_path)}  (режим {mode})")
    print("-" * 60)

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            if mode == 1:
                # ----- РЕЖИМ 1 (как в Примере 1) -----
                found_figures = set()
                patterns = [
                    re.compile(r'Figure\s+(\d+).*?/\s*(Рисунок\s+(\d+)\s*[–—-]\s*[^\n]+)',
                               re.UNICODE | re.IGNORECASE | re.DOTALL),
                    re.compile(r'Figure\s+(\d+)\s*[–—-]\s*[^/]+/\s*(Рисунок\s+(\d+)\s+[^\n]+)',
                               re.UNICODE | re.IGNORECASE),
                    re.compile(r'(Рисунок\s+(\d+)\s*[–—-]\s*[^\n]+)', re.UNICODE),
                ]

                figures = []
                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if not text:
                        continue

                    lines = text.split('\n')
                    page_figures = []

                    for line in lines:
                        clean_line = ' '.join(line.split())
                        for pattern in patterns:
                            match = pattern.search(clean_line)
                            if match:
                                if len(match.groups()) == 3:
                                    figure_num = int(match.group(3))
                                    figure_name = match.group(2)
                                else:
                                    figure_name = match.group(1)
                                    figure_num = int(match.group(2))

                                figure_name = ' '.join(figure_name.split())
                                if (len(figure_name) < 200 and
                                        'Рисунок' in figure_name and
                                        figure_num not in found_figures):
                                    page_figures.append({
                                        'page': page_num + 1,
                                        'number': figure_num,
                                        'name': figure_name
                                    })
                                    found_figures.add(figure_num)
                                    break

                    if page_figures:
                        page_figures.sort(key=lambda x: x['number'])
                        for fig in page_figures:
                            figures.append(fig)

                figures.sort(key=lambda x: x['number'])
                return figures

            else:  # mode == 2
                # ----- РЕЖИМ 2 -----
                records = []  # все найденные строки
                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if not text:
                        continue

                    lines = text.split('\n')
                    for raw_line in lines:
                        line = raw_line.strip()
                        if not line:
                            continue
                        if line.startswith("Figure") or line.startswith("Рисунок"):
                            # Извлекаем номер для группировки
                            match = re.match(r'^(Figure|Рисунок)\s+(\d+)', line)
                            if match:
                                num = int(match.group(2))
                                records.append({
                                    'page': page_num + 1,
                                    'number': num,
                                    'full_text': line   # сохраняем всю строку
                                })

                # Группировка по номеру рисунка
                grouped = defaultdict(list)
                for rec in records:
                    grouped[rec['number']].append(rec)

                figures = []
                for num, items in grouped.items():
                    # Сортируем записи по странице (на всякий случай)
                    items.sort(key=lambda x: x['page'])
                    page = items[0]['page']
                    names = [item['full_text'] for item in items]
                    # Дополняем до двух названий (если вдруг только одно)
                    while len(names) < 2:
                        names.append('')
                    figures.append({
                        'page': page,
                        'number': num,
                        'name1': names[0],
                        'name2': names[1]
                    })

                # Сортируем по номеру
                figures.sort(key=lambda x: x['number'])
                return figures

    except Exception as e:
        print(f"Ошибка при обработке PDF: {e}")
        return []


def save_results_to_csv(results, pdf_path, mode, output_dir='results_csv'):
    """
    Сохраняет результаты в CSV файл.
    Для режима 1: поля: Страница, Номер рисунка, Название рисунка
    Для режима 2: поля: Страница, Номер рисунка, Название рисунка 1, Название рисунка 2
    """
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"{base_name}_{timestamp}.csv")

    if mode == 1:
        fieldnames = ['Страница', 'Номер рисунка', 'Название рисунка']
    else:
        fieldnames = ['Страница', 'Номер рисунка', 'Название рисунка 1', 'Название рисунка 2']

    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';', quotechar='"')
        writer.writeheader()

        for fig in results:
            row = {'Страница': fig['page'], 'Номер рисунка': fig['number']}
            if mode == 1:
                row['Название рисунка'] = fig['name']
            else:
                row['Название рисунка 1'] = fig['name1']
                row['Название рисунка 2'] = fig['name2']
            writer.writerow(row)

        # Итоговая строка
        writer.writerow({})
        if mode == 1:
            writer.writerow({
                'Страница': 'ИТОГО:',
                'Номер рисунка': '',
                'Название рисунка': f'Найдено рисунков: {len(results)}'
            })
        else:
            writer.writerow({
                'Страница': 'ИТОГО:',
                'Номер рисунка': '',
                'Название рисунка 1': f'Найдено рисунков: {len(results)}',
                'Название рисунка 2': ''
            })

    print(f"\nРезультаты сохранены: {output_path}")
    return output_path


def find_pdf_files(directory='.'):
    """Находит все PDF файлы в указанной директории."""
    pdf_files = []
    for file in os.listdir(directory):
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(directory, file))
    return pdf_files


def main():
    print("Выберите режим извлечения рисунков:")
    print("1 - одна строка с разделителем")
    print("2 - отдельные строки")
    mode_input = input("Введите 1 или 2: ").strip()
    while mode_input not in ('1', '2'):
        mode_input = input("Некорректный ввод. Введите 1 или 2: ").strip()
    mode = int(mode_input)

    pdf_files = find_pdf_files()
    if not pdf_files:
        print("\nPDF файлы не найдены в текущей папке")
        return

    print(f"\nНайдено PDF файлов: {len(pdf_files)}")
    total_records = 0

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}]")
        results = extract_figures_from_pdf(pdf_file, mode=mode)

        if results:
            save_results_to_csv(results, pdf_file, mode)
            total_records += len(results)
    print(f"Готово")

if __name__ == "__main__":
    main()