from __future__ import annotations

import logging  # Модуль для ведения логов приложения
import re  # Регулярные выражения для сортировки файлов
import sys  # Доступ к системным параметрам и функциям
import tempfile  # Создание временных файлов и каталогов
from dataclasses import dataclass  # Декоратор для создания классов-контейнеров
from pathlib import Path  # Работа с путями файловой системы
from typing import List, Optional, Sequence, Tuple  # Типизация для аннотаций

from PIL import Image  # Библиотека обработки изображений (Pillow)

# Попытка импорта опциональной зависимости для улучшенного создания PDF
try:
    import img2pdf  # type: ignore

    HAS_IMG2PDF = True
except ImportError:
    HAS_IMG2PDF = False


@dataclass
class Config:
    """Класс конфигурации приложения. Хранит все постоянные параметры."""

    # Размер A4 при 300 DPI в пикселях (ширина x высота)
    A4_300DPI: Tuple[int, int] = (2480, 3508)

    # Максимальный размер PDF файла (100 МБ)
    MAX_PDF_BYTES: int = 200 * 1024  ** 2

    # Формат промежуточных изображений
    IMAGE_FORMAT: str = "WEBP"

    # Качество сохранения изображений (для WEBP)
    IMAGE_SAVE_QUALITY: int = 90

    # Сжатие без потерь (для WEBP)
    IMAGE_SAVE_LOSSLESS: bool = False

    # Усилие кодирования WEBP (0-6, где 6 = медленнее, но лучше сжатие)
    IMAGE_SAVE_METHOD: int = 6

    # Имя подкаталога для промежуточных результатов (обработанных изображений)
    OUTPUT_SUBDIR: str = "result"

    # Каталог по умолчанию (текущий каталог программы)
    DEFAULT_INPUT_DIR: str = "."

    # Уровни качества для генерации PDF (от 100% до 1%)
    QUALITY_LEVELS: List[Tuple[int, str]] = None

    # Поддерживаемые расширения изображений
    SUPPORTED_PATTERNS: Tuple[str, ...] = (
        " *.png", "*.PNG",
        "*.bmp", "*.BMP",
        "*.tif", "*.TIF", "*.tiff", "*.TIFF"
    )

    def __post_init__(self):
        """Инициализация списка качества после создания объекта."""
        if self.QUALITY_LEVELS is None:
            # Генерация качества от 100% до 10% (шаг 10)
            self.QUALITY_LEVELS = [(i, f"{i}%") for i in range(100, 9, -10)]
            # Добавление качества от 9% до 1% (шаг 1)
            self.QUALITY_LEVELS.extend([(i, f"{i}%") for i in range(9, 0, -1)])


def setup_logger() -> logging.Logger:
    """Настройка системы логирования для всего приложения."""
    logger = logging.getLogger("ImageToPDF")  # Создание логгера с именем
    logger.setLevel(logging.INFO)  # Установка уровня логирования

    # Очистка старых обработчиков (если есть)
    logger.handlers.clear()

    # Обработчик для вывода в консоль
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(message)s'))  # Простой формат вывода

    logger.addHandler(handler)
    return logger


def natural_key(s: str) -> Tuple:
    """
    Генерирует ключ для естественной сортировки строк с числами.
    Например: 'file10' будет идти после 'file2' (человекопонятная сортировка).
    """
    # Разделение строки по числам
    parts = re.split(r"(\d+)", s)
    # Преобразование чисел в int, строк в нижний регистр
    return tuple(int(p) if p.isdigit() else p.lower() for p in parts)


def collect_unique_files(input_dir: Path, patterns: Tuple[str, ...]) -> List[Path]:
    """
    Собирает файлы по заданным паттернам, удаляя дубликаты и сохраняя порядок.
    Возвращает список путей к уникальным файлам.
    """
    found: List[Path] = []  # Список для всех найденных файлов

    # Поиск файлов по каждому паттерну
    for pattern in patterns:
        found.extend(input_dir.glob(pattern))

    # Удаление дубликатов с сохранением порядка (Python 3.7+)
    return list(dict.fromkeys(found))


def resize_to_a4_300dpi(input_path: Path, output_path: Path, config: Config) -> bool:
    """
    Масштабирует изображение под размер A4 при 300 DPI и сохраняет в заданном формате.
    Изображение размещается по центру белого холста.
    Возвращает True при успехе, False при ошибке.
    """
    try:
        # Открытие исходного изображения
        with Image.open(input_path) as img:
            img = img.convert("RGB")  # Конвертация в RGB формат
            original_w, original_h = img.size  # Получение размеров

            # Размеры холста A4
            a4_w, a4_h = config.A4_300DPI

            # Расчет коэффициента масштабирования (сохранение пропорций)
            ratio = min(a4_w / original_w, a4_h / original_h)
            new_size = (int(original_w * ratio), int(original_h * ratio))

            # Масштабирование с использованием качественного фильтра LANCZOS
            resized = img.resize(new_size, Image.Resampling.LANCZOS)

            # Создание белого холста A4
            canvas = Image.new("RGB", config.A4_300DPI, "white")

            # Вычисление смещения для центрирования изображения
            x_offset = (a4_w - new_size[0]) // 2
            y_offset = (a4_h - new_size[1]) // 2

            # Вставка изображения на холст
            canvas.paste(resized, (x_offset, y_offset))

            # Параметры сохранения в зависимости от формата
            save_kwargs = {}
            if config.IMAGE_FORMAT.upper() == "WEBP":
                save_kwargs = {
                    "quality": config.IMAGE_SAVE_QUALITY,
                    "lossless": config.IMAGE_SAVE_LOSSLESS,
                    "method": config.IMAGE_SAVE_METHOD
                }
            else:
                # Для других форматов (например, JPEG) указываем DPI
                save_kwargs = {"quality": 85, "dpi": (300, 300)}

            # Сохранение результата
            canvas.save(output_path, config.IMAGE_FORMAT, **save_kwargs)
            return True

    except Exception as e:
        # Логирование ошибки при обработке файла
        logging.getLogger("ImageToPDF").error(f"Error processing {input_path.name}: {e}")
        return False


def estimate_pdf_size(image_files: Sequence[Path], quality: int,
                      max_bytes: int, conservative: float = 1.1) -> Optional[int]:
    """
    Оценивает размер будущего PDF файла на основе размеров исходных изображений.
    Использует нелинейную аппроксимацию, близкую к реальному поведению сжатия.
    Возвращает размер в байтах, или None если превышает max_bytes.
    """
    if not image_files:
        return 0  # Пустой список = нулевой размер

    # Суммарный размер всех изображений
    total_bytes = sum(p.stat().st_size for p in image_files)

    # Нормализация качества (1-100)
    q = max(1, min(100, quality))

    # Нелинейная аппроксимация коэффициента сжатия
    # Качество 100% → factor ≈ 1.0, качество 1% → factor ≈ 0.35
    factor = 0.35 + 0.65 * ((q / 100.0) ** 0.85)

    # Оценка с консервативным запасом (по умолчанию +10%)
    estimated = int(total_bytes * factor * conservative)

    # Проверка лимита размера
    return estimated if estimated <= max_bytes else None


def format_size(size_bytes: int) -> str:
    """
    Преобразует размер в байтах в человекочитаемую строку (KB, MB, GB и т.д.).
    """
    # Перебор единиц измерения
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0

    return f"{size_bytes:.1f} TB"  # На случай очень больших файлов


def create_pdf(image_paths: List[Path], pdf_path: Path, quality: int,
               use_img2pdf: bool = True) -> Optional[int]:
    """
    Создает PDF файл из списка изображений.
    Приоритет: img2pdf (если доступен), иначе — PIL.
    Возвращает размер файла в байтах при успехе, None при ошибке.
    """
    if not image_paths:
        return None  # Нечего конвертировать

    try:
        # Использование img2pdf (лучшее качество и меньший размер)
        if use_img2pdf and HAS_IMG2PDF:
            # Создание временного каталога для JPEG файлов
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_jpegs: List[str] = []

                # Конвертация каждого изображения в временный JPEG
                for img_path in image_paths:
                    with Image.open(img_path) as im:
                        temp_jpeg = Path(temp_dir) / f"{img_path.stem}.jpg"
                        # Сохранение в JPEG с заданным качеством
                        im.convert("RGB").save(
                            temp_jpeg, "JPEG",
                            quality=quality, optimize=True, progressive=True
                        )
                        temp_jpegs.append(str(temp_jpeg))

                # Создание PDF из временных JPEG файлов
                with open(pdf_path, "wb") as f_pdf:
                    f_pdf.write(img2pdf.convert(temp_jpegs))

        # Резервный метод через PIL (работает всегда, но менее эффективно)
        else:
            # Открытие первого изображения
            with Image.open(image_paths[0]) as first:
                first = first.convert("RGB").copy()

            # Подготовка остальных изображений
            appended = []
            for img_path in image_paths[1:]:
                with Image.open(img_path) as im:
                    appended.append(im.convert("RGB").copy())

            # Сохранение всех изображений в один PDF
            first.save(
                pdf_path, "PDF",
                save_all=True, append_images=appended, optimize=True
            )

            # Освобождение ресурсов (важно для большого количества файлов)
            for im in appended:
                im.close()
            first.close()

        # Возврат размера созданного файла
        return pdf_path.stat().st_size

    except Exception as e:
        # Логирование ошибки при создании PDF
        logging.getLogger("ImageToPDF").error(f"Error creating PDF {pdf_path.name}: {e}")
        return None


def get_input_directory(logger: logging.Logger, default_dir: str = ".") -> Path:
    """
    Запрашивает у пользователя путь к каталогу с изображениями.
    Проверяет существование и валидность введенного пути.
    Возвращает абсолютный путь к каталогу.
    """
    while True:
        # Вывод разделителя для читаемости
        print("\n" + "=" * 60)

        # Запрос ввода от пользователя
        user_input = input(
            f"Введите путь к каталогу с изображениями\n"
            f"(или нажмите Enter для использования текущего каталога): "
        ).strip()

        # Если пользователь ничего не ввел - используем каталог по умолчанию
        if not user_input:
            input_dir = Path(default_dir).resolve()
            logger.info(f"Используется каталог по умолчанию: {input_dir}")
            return input_dir

        # Проверка существования введенного пути
        input_dir = Path(user_input).resolve()

        if not input_dir.exists():
            logger.error(f"Ошибка: каталог '{input_dir}' не существует.")
            continue

        if not input_dir.is_dir():
            logger.error(f"Ошибка: путь '{input_dir}' не является каталогом.")
            continue

        # Успешная валидация
        logger.info(f"Используется каталог: {input_dir}")
        return input_dir


def process_images(input_dir: Path, output_dir: Path, config: Config, logger: logging.Logger) -> List[Path]:
    """
    Основной процесс обработки изображений:
    - Поиск файлов по паттернам
    - Сортировка в естественном порядке
    - Масштабирование и конвертация
    Возвращает список путей к успешно обработанным файлам.
    """
    # Поиск всех поддерживаемых файлов в каталоге
    files = collect_unique_files(input_dir, config.SUPPORTED_PATTERNS)

    # Сортировка файлов в "естественном" порядке (file1, file2, file10, а не file1, file10, file2)
    files.sort(key=lambda p: natural_key(p.stem))

    # Проверка наличия файлов
    if not files:
        logger.error("В каталоге не найдено поддерживаемых изображений.")
        return []

    logger.info(f"Найдено {len(files)} изображений для обработки.")

    # Обработка каждого изображения
    processed_paths: List[Path] = []  # Список успешно обработанных файлов
    skipped = 0  # Счетчик пропущенных файлов
    errors = 0  # Счетчик ошибок

    for idx, src in enumerate(files, 1):
        # Формирование пути выходного файла
        out_path = output_dir / f"{src.stem}_A4.{config.IMAGE_FORMAT.lower()}"

        # Пропуск, если файл уже существует (экономия времени при повторных запусках)
        if out_path.exists():
            skipped += 1
            logger.debug(f"[{idx}/{len(files)}] Пропуск: {out_path.name}")
            processed_paths.append(out_path)  # Добавляем в список для дальнейшего использования
            continue

        # Обработка изображения
        logger.info(f"[{idx}/{len(files)}] Обработка: {src.name}")
        if resize_to_a4_300dpi(src, out_path, config):
            processed_paths.append(out_path)  # Успех
        else:
            errors += 1  # Ошибка при обработке

    # Вывод итоговой статистики
    if skipped:
        logger.info(f"Пропущено существующих файлов: {skipped}")
    if errors:
        logger.error(f"Ошибок при обработке: {errors}")
    if processed_paths:
        logger.info(f"Успешно обработано: {len(processed_paths)} изображений")

    return processed_paths


def create_pdfs(processed_paths: List[Path], output_dir: Path, config: Config, logger: logging.Logger) -> None:
    """
    Создает PDF файлы с различными уровнями качества.
    Для качества > 10% пропускает варианты, превышающие лимит размера.
    Для качества <= 10% создает файлы вне зависимости от лимита.
    PDF файлы сохраняются в подкаталог 'pdf' рядом с 'result'.
    """
    # Проверка наличия обработанных изображений
    if not processed_paths:
        logger.error("Нет обработанных изображений для создания PDF.")
        return

    # Создание каталога для PDF файлов (рядом с result)
    pdf_dir = output_dir.parent / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)

    logger.info("\n" + "=" * 60)
    logger.info("Создание PDF-файлов с различным качеством...")
    logger.info(f"PDF будут сохранены в: {pdf_dir}")
    logger.info("=" * 60)

    results: List[Tuple[int, str, Path, int]] = []  # Список результатов (качество, метка, путь, размер)

    # Перебор всех уровней качества
    for quality, label in config.QUALITY_LEVELS:
        pdf_filename = pdf_dir / f"book_{label}.pdf"  # Имя выходного PDF

        # Оценка размера PDF
        est_size = estimate_pdf_size(processed_paths, quality, config.MAX_PDF_BYTES)

        # Пропуск только для качества > 10% и превышения лимита
        if est_size is None and quality > 10:
            logger.warning(
                f"Пропуск {pdf_filename.name}: оценочный размер превышает лимит "
                f"({format_size(config.MAX_PDF_BYTES)})"
            )
            continue

        # Для качества <= 10% выводим предупреждение, но продолжаем создание
        if est_size is None and quality <= 10:
            logger.warning(
                f"Создание {pdf_filename.name} несмотря на превышение лимита "
                f"(качество {label} создается вне зависимости от размера)"
            )

        # Создание PDF файла
        logger.info(f"Создание {pdf_filename.name} (качество: {label})...")
        created_size = create_pdf(processed_paths, pdf_filename, quality, use_img2pdf=HAS_IMG2PDF)

        # Проверка результата
        if created_size is None:
            logger.error(f"Ошибка создания {pdf_filename.name}")
        else:
            results.append((quality, label, pdf_filename, created_size))
            logger.info(f"{pdf_filename.name:30} | {quality:3}% | {format_size(created_size):>8}")

    # Проверка созданных файлов
    if not results:
        logger.error("PDF-файлы не были созданы.")
        return

    # Сортировка результатов по размеру файла
    results.sort(key=lambda r: r[3])
    logger.info(f"\nСоздано PDF-файлов: {len(results)}")

    # Вывод информации о самом маленьком и большом файлах
    if results:
        smallest = results[0]
        largest = results[-1]
        logger.info(f"Самый маленький: {smallest[2].name} ({format_size(smallest[3])})")
        logger.info(f"Самый большой:  {largest[2].name} ({format_size(largest[3])})")


def main() -> None:
    """Главная точка входа в приложение. Оркестрирует весь процесс."""

    # Инициализация конфигурации и логирования
    config = Config()
    logger = setup_logger()

    print("\n" + "=" * 60)
    print("Конвертер изображений в PDF")
    print("=" * 60)

    # Получение каталога с изображениями от пользователя
    input_dir = get_input_directory(logger, config.DEFAULT_INPUT_DIR)

    # Создание каталога для промежуточных результатов (обработанных изображений)
    output_dir = input_dir / config.OUTPUT_SUBDIR
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Каталог для промежуточных результатов: {output_dir}")

    # Обработка изображений (масштабирование и конвертация)
    processed_paths = process_images(input_dir, output_dir, config, logger)

    # Создание PDF файлов
    create_pdfs(processed_paths, output_dir, config, logger)

    print("\n" + "=" * 60)
    print("Обработка завершена!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем. Выход...")
        sys.exit(1)  # Выход с кодом ошибки
    except Exception as e:
        print(f"\n\nНепредвиденная ошибка: {e}")
        sys.exit(1)  # Выход с кодом ошибки