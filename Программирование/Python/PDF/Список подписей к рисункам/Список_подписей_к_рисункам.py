"""
Извлечение подписей к рисункам из PDF файлов.
Версия 3.1
"""

import os
import csv
import re
import logging
import unicodedata
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

import PyPDF2

# ---------------------------------------------------------------------------
# Настройки
# ---------------------------------------------------------------------------

OUTPUT_DIR = "results_csv"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"

# Регулярные выражения для режима 1
PATTERNS_MODE1 = [
    re.compile(
        r'Figure\s+(\d+).*?/\s*(Рисунок\s+(\d+)\s*[–—-]\s*[^\n]+)',
        re.UNICODE | re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r'Figure\s+(\d+)\s*[–—-]\s*[^/]+/\s*(Рисунок\s+(\d+)\s+[^\n]+)',
        re.UNICODE | re.IGNORECASE,
    ),
    re.compile(r'(Рисунок\s+(\d+)\s*[–—-]\s*[^\n]+)', re.UNICODE),
]

FIGURE_NAME_MAX_LEN = 200


# ---------------------------------------------------------------------------
# Структуры данных
# ---------------------------------------------------------------------------

@dataclass
class Figure:
    """Единица данных — одна запись о рисунке."""
    page: int
    number: int
    name: str = ""          # режим 1
    name1: str = ""         # режим 2 (первая строка)
    name2: str = ""         # режим 2 (вторая строка)


@dataclass
class ExtractionResult:
    """Итог обработки одного PDF."""
    pdf_path: Path
    mode: int
    figures: list[Figure] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return not self.errors

    @property
    def count(self) -> int:
        return len(self.figures)


# ---------------------------------------------------------------------------
# Логирование
# ---------------------------------------------------------------------------

def setup_logging() -> logging.Logger:
    logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT, level=logging.INFO)
    return logging.getLogger(__name__)


logger = setup_logging()


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

# Невидимые символы, которые часто встречаются в PDF-тексте:
#   \u00ad — мягкий дефис (soft hyphen)
#   \u200b — нулевой пробел (zero-width space)
#   \u200c — разделитель без ширины (zero-width non-joiner)
#   \u200d — объединитель без ширины (zero-width joiner)
#   \u200e — маркер слева направо (left-to-right mark)
#   \u200f — маркер справа налево (right-to-left mark)
#   \u202a…\u202e — управляющие символы направления текста
#   \u2060 — word joiner
#   \ufeff — BOM / zero-width no-break space
#   \u00a0 — неразрывный пробел (non-breaking space)
#   \u2002…\u200a — различные типографские пробелы
_INVISIBLE_RE = re.compile(
    r"[\u00ad\u00a0"
    r"\u2000-\u200f"
    r"\u2028\u2029"
    r"\u202a-\u202f"
    r"\u2060\u2061"
    r"\ufeff]",
    re.UNICODE,
)


def normalize(text: str) -> str:
    """
    Очищает строку от невидимых Unicode-символов и лишних пробелов.

    1. Удаляет все невидимые/управляющие символы (мягкий дефис, BOM,
       нулевые пробелы, маркеры направления и т.п.).
    2. Заменяет неразрывные и типографские пробелы на обычный пробел.
    3. Схлопывает множественные пробелы в один и убирает пробелы по краям.
    """
    # Шаг 1: удаляем невидимые символы
    text = _INVISIBLE_RE.sub("", text)
    # Шаг 2: нормализуем Unicode (например, лигатуры, совместимые формы)
    text = unicodedata.normalize("NFKC", text)
    # Шаг 3: схлопываем пробелы (str.split() обрабатывает все whitespace-символы)
    return " ".join(text.split())


def iter_page_lines(pdf_reader: PyPDF2.PdfReader):
    """Генератор: (page_num_1based, line) по всем страницам."""
    for page_num, page in enumerate(pdf_reader.pages, start=1):
        text = page.extract_text() or ""
        for raw_line in text.split("\n"):
            yield page_num, raw_line


# ---------------------------------------------------------------------------
# Извлечение — режим 1
# ---------------------------------------------------------------------------

def _extract_mode1(pdf_reader: PyPDF2.PdfReader) -> list[Figure]:
    found_nums: set[int] = set()
    figures: list[Figure] = []

    for page_num, raw_line in iter_page_lines(pdf_reader):
        line = normalize(raw_line)
        for pattern in PATTERNS_MODE1:
            match = pattern.search(line)
            if not match:
                continue

            groups = match.groups()
            if len(groups) == 3:
                fig_num = int(groups[2])
                fig_name = groups[1]
            else:
                fig_name = groups[0]
                fig_num = int(groups[1])

            fig_name = normalize(fig_name)
            if (
                len(fig_name) < FIGURE_NAME_MAX_LEN
                and "Рисунок" in fig_name
                and fig_num not in found_nums
            ):
                figures.append(Figure(page=page_num, number=fig_num, name=fig_name))
                found_nums.add(fig_num)
                break  # следующая строка

    figures.sort(key=lambda f: f.number)
    return figures


# ---------------------------------------------------------------------------
# Извлечение — режим 2
# ---------------------------------------------------------------------------

_FIGURE_START = re.compile(r'^(Figure|Рисунок)\s+(\d+)', re.UNICODE)


def _extract_mode2(pdf_reader: PyPDF2.PdfReader) -> list[Figure]:
    grouped: dict[int, list[dict]] = defaultdict(list)

    for page_num, raw_line in iter_page_lines(pdf_reader):
        line = raw_line.strip()
        if not line:
            continue
        if not (line.startswith("Figure") or line.startswith("Рисунок")):
            continue

        match = _FIGURE_START.match(line)
        if match:
            num = int(match.group(2))
            grouped[num].append({"page": page_num, "full_text": normalize(line)})

    figures: list[Figure] = []
    for num, items in grouped.items():
        items.sort(key=lambda x: x["page"])
        names = [item["full_text"] for item in items]
        while len(names) < 2:
            names.append("")
        figures.append(Figure(
            page=items[0]["page"],
            number=num,
            name1=names[0],
            name2=names[1],
        ))

    figures.sort(key=lambda f: f.number)
    return figures


# ---------------------------------------------------------------------------
# Основная функция извлечения
# ---------------------------------------------------------------------------

def extract_figures(pdf_path: Path, mode: int) -> ExtractionResult:
    """Извлекает рисунки из одного PDF файла."""
    result = ExtractionResult(pdf_path=pdf_path, mode=mode)

    if not pdf_path.exists():
        result.errors.append(f"Файл не найден: {pdf_path}")
        logger.error(result.errors[-1])
        return result

    logger.info("Обработка: %s  (режим %d)", pdf_path.name, mode)

    try:
        with pdf_path.open("rb") as fh:
            pdf_reader = PyPDF2.PdfReader(fh)
            logger.info("Страниц в файле: %d", len(pdf_reader.pages))

            if mode == 1:
                result.figures = _extract_mode1(pdf_reader)
            else:
                result.figures = _extract_mode2(pdf_reader)

    except PyPDF2.errors.PdfReadError as exc:
        result.errors.append(f"Повреждённый PDF: {exc}")
        logger.error(result.errors[-1])
    except Exception as exc:  # noqa: BLE001
        result.errors.append(f"Неожиданная ошибка: {exc}")
        logger.exception("Неожиданная ошибка при обработке %s", pdf_path.name)

    logger.info("Найдено рисунков: %d", result.count)
    return result


# ---------------------------------------------------------------------------
# Сохранение в CSV
# ---------------------------------------------------------------------------

_FIELDNAMES = {
    1: ["Страница", "Номер рисунка", "Название рисунка"],
    2: ["Страница", "Номер рисунка", "Название рисунка 1", "Название рисунка 2"],
}


def _figure_to_row(fig: Figure, mode: int) -> dict:
    base = {"Страница": fig.page, "Номер рисунка": fig.number}
    if mode == 1:
        return {**base, "Название рисунка": fig.name}
    return {**base, "Название рисунка 1": fig.name1, "Название рисунка 2": fig.name2}


def _summary_row(count: int, mode: int) -> dict:
    base: dict = {"Страница": "ИТОГО:", "Номер рисунка": ""}
    summary_text = f"Найдено рисунков: {count}"
    if mode == 1:
        return {**base, "Название рисунка": summary_text}
    return {**base, "Название рисунка 1": summary_text, "Название рисунка 2": ""}


def save_to_csv(result: ExtractionResult, output_dir: str = OUTPUT_DIR) -> Optional[Path]:
    """Сохраняет результат в CSV; возвращает путь к файлу или None при ошибке."""
    if not result.figures:
        logger.warning("Нет данных для сохранения: %s", result.pdf_path.name)
        return None

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = result.pdf_path.stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"{stem}_{timestamp}.csv"

    fieldnames = _FIELDNAMES[result.mode]

    try:
        with out_path.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(
                fh, fieldnames=fieldnames, delimiter=";", quotechar='"'
            )
            writer.writeheader()
            for fig in result.figures:
                writer.writerow(_figure_to_row(fig, result.mode))
            writer.writerow({})                                     # пустая строка
            writer.writerow(_summary_row(result.count, result.mode))

        logger.info("CSV сохранён: %s", out_path)
        return out_path

    except OSError as exc:
        logger.error("Не удалось сохранить CSV: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Поиск PDF
# ---------------------------------------------------------------------------

def find_pdf_files(directory: str = ".") -> list[Path]:
    return sorted(Path(directory).glob("*.pdf"))


# ---------------------------------------------------------------------------
# Интерфейс командной строки
# ---------------------------------------------------------------------------

def ask_mode() -> int:
    print("\nВыберите режим извлечения рисунков:")
    print("  1 — одна строка с разделителем '/'")
    print("  2 — отдельные строки на русском и английском")
    while True:
        choice = input("Введите 1 или 2: ").strip()
        if choice in ("1", "2"):
            return int(choice)
        print("Некорректный ввод, попробуйте снова.")


def main() -> None:
    mode = ask_mode()

    pdf_files = find_pdf_files()
    if not pdf_files:
        logger.warning("PDF файлы не найдены в текущей папке.")
        return

    logger.info("Найдено PDF файлов: %d", len(pdf_files))

    total_figures = 0
    saved_files: list[Path] = []
    failed_files: list[Path] = []

    for idx, pdf_path in enumerate(pdf_files, start=1):
        logger.info("[%d/%d] %s", idx, len(pdf_files), pdf_path.name)
        result = extract_figures(pdf_path, mode)

        if result.errors:
            failed_files.append(pdf_path)
            continue

        out = save_to_csv(result)
        if out:
            saved_files.append(out)
            total_figures += result.count
        else:
            failed_files.append(pdf_path)

    # Итоговая сводка
    print("\n" + "=" * 60)
    print(f"  Обработано файлов : {len(pdf_files)}")
    print(f"  Успешно сохранено : {len(saved_files)}")
    print(f"  Всего рисунков    : {total_figures}")
    if failed_files:
        print(f"  Ошибки ({len(failed_files)}):")
        for p in failed_files:
            print(f"    • {p.name}")
    print("=" * 60)


if __name__ == "__main__":
    main()
