from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from PIL import Image

A4_300DPI: Tuple[int, int] = (2480, 3508)
QUALITY_LEVELS: List[Tuple[int, str]] = [
    (100, "100%"),
    (90, "90%"),
    (80, "80%"),
    (70, "70%"),
    (60, "60%"),
    (50, "50%"),
    (40, "40%"),
    (30, "30%"),
    (20, "20%"),
    (10, "10%"),
    (9, "9%"),
    (8, "8%"),
    (7, "7%"),
    (6, "6%"),
    (5, "5%"),
    (4, "4%"),
    (3, "3%"),
    (2, "2%"),
    (1, "1%"),
]

IMAGE_FORMAT: str = "WEBP"
IMAGE_SAVE_QUALITY: int = 90
IMAGE_SAVE_LOSSLESS: bool = False
IMAGE_SAVE_METHOD: int = 6  # webp encoding effort (0..6)
MAX_PDF_BYTES = 100 * 1024**2  # 100 MB

try:
    import img2pdf  # type: ignore
    HAS_IMG2PDF = True
except Exception:
    HAS_IMG2PDF = False


def natural_key(s: str) -> Tuple:
    """Естественная сортировка с учетом чисел в именах."""
    parts = re.split(r"(\d+)", s)
    key = [int(p) if p.isdigit() else p.lower() for p in parts]
    return tuple(key)


def collect_unique_files(input_dir: Path, patterns: Tuple[str, ...]) -> List[Path]:
    """Собирает файлы по паттернам, убирает дубликаты, сохраняет порядок."""
    found: List[Path] = []
    for pat in patterns:
        found.extend(input_dir.glob(pat))
    unique = list(dict.fromkeys(found))
    return unique


def resize_to_a4_300dpi(input_path: Path, output_path: Path) -> None:
    """Масштабирует изображение под A4 (300 DPI) и сохраняет в .webp"""
    a4_w, a4_h = A4_300DPI
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        w, h = img.size
        ratio = min(a4_w / w, a4_h / h)
        new_size = (int(w * ratio), int(h * ratio))
        resized = img.resize(new_size, Image.Resampling.LANCZOS)

        canvas = Image.new("RGB", A4_300DPI, "white")
        x_off = (a4_w - new_size[0]) // 2
        y_off = (a4_h - new_size[1]) // 2
        canvas.paste(resized, (x_off, y_off))

        save_kwargs = (
            {"quality": IMAGE_SAVE_QUALITY, "lossless": IMAGE_SAVE_LOSSLESS, "method": IMAGE_SAVE_METHOD}
            if IMAGE_FORMAT.upper() == "WEBP"
            else {"quality": 85, "dpi": (300, 300)}
        )
        canvas.save(output_path, IMAGE_FORMAT, **save_kwargs)


def estimate_pdf_size_from_images(image_files: Sequence[Path], quality: int, conservative: float = 1.1) -> int:
    """
    Оценка размера PDF.
    f(quality) — нелинейная аппроксимация, ближе к реальному поведению JPEG/PDF.
    """
    total_bytes = sum(p.stat().st_size for p in image_files)
    q = max(1, min(100, quality))
    factor = 0.35 + 0.65 * ((q / 100.0) ** 0.85)
    return int(total_bytes * factor * conservative)


def format_size(size_bytes: int) -> str:
    mb = 1024 ** 2
    kb = 1024
    if size_bytes >= mb:
        return f"{size_bytes / mb:.1f} MB"
    if size_bytes >= kb:
        return f"{size_bytes / kb:.1f} KB"
    return f"{size_bytes} B"


def create_pdf_with_quality(image_paths: List[Path], pdf_path: Path, quality: int) -> Optional[int]:
    """
    Создаёт PDF из списка изображений.
    Использует img2pdf (если доступен), иначе — безопасный PIL-режим.
    """
    if not image_paths:
        return None

    try:
        if HAS_IMG2PDF:
            with tempfile.TemporaryDirectory() as td:
                tmp_paths: List[str] = []
                for p in image_paths:
                    with Image.open(p) as im:
                        rgb = im.convert("RGB")
                        tmp_jpeg = Path(td) / (p.stem + ".jpg")
                        rgb.save(tmp_jpeg, "JPEG", quality=quality, optimize=True, progressive=True)
                        tmp_paths.append(str(tmp_jpeg))

                with open(pdf_path, "wb") as f_pdf:
                    f_pdf.write(img2pdf.convert(tmp_paths))
            return pdf_path.stat().st_size

        with Image.open(image_paths[0]) as first:
            first = first.convert("RGB").copy()

        appended = []
        for p in image_paths[1:]:
            with Image.open(p) as im:
                appended.append(im.convert("RGB").copy())

        first.save(pdf_path, "PDF", save_all=True, append_images=appended, optimize=True)

        for im in appended:
            im.close()
        first.close()

        return pdf_path.stat().st_size

    except Exception as e:
        print(f"Ошибка при создании PDF {pdf_path.name}: {e}")
        return None

def process_all_image_files(input_folder: str = ".", output_folder: str = "result") -> None:
    input_dir = Path(input_folder)
    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    patterns = ("*.png", "*.PNG", "*.bmp", "*.BMP")
    files = collect_unique_files(input_dir, patterns)
    files = sorted(files, key=lambda p: natural_key(p.stem))

    if not files:
        print("Ошибка: PNG/BMP файлы не найдены.")
        return

    print(f"Найдено {len(files)} исходных изображений.")

    processed_paths_all: List[Path] = [output_dir / f"{src.stem}_a4.{IMAGE_FORMAT.lower()}" for src in files]
    all_exist = all(p.exists() for p in processed_paths_all)

    if all_exist:
        print("Все .webp уже существуют - пропускаем обработку изображений.\n")
    else:
        print("Создание .webp файлов...\n")
        skipped = 0
        for i, src in enumerate(files, start=1):
            out_path = output_dir / f"{src.stem}_A4.{IMAGE_FORMAT.lower()}"
            if out_path.exists():
                skipped += 1
                print(f"[{i}/{len(files)}] Пропуск: {out_path.name}")
                continue
            try:
                resize_to_a4_300dpi(src, out_path)
                print(f"[{i}/{len(files)}] {src.name} → {out_path.name}")
            except Exception as e:
                print(f"[{i}/{len(files)}] Ошибка {src.name}: {e}")
        print(f"\nПропущено существующих: {skipped}")

    processed_paths = [p for p in dict.fromkeys(processed_paths_all) if p.exists()]

    if not processed_paths:
        print("Ошибка: не найдено готовых .webp файлов.")
        return

    print("\nСоздание PDF с разным качеством...\n" + "=" * 60)
    pdf_results: List[Tuple[int, str, Path, int]] = []

    for quality, label in QUALITY_LEVELS:
        pdf_filename = output_dir / f"book_{label}.pdf"
        est_size = estimate_pdf_size_from_images(processed_paths, quality)
        if est_size > MAX_PDF_BYTES:
            print(f"Пропуск {pdf_filename.name}: оценка {format_size(est_size)} > {format_size(MAX_PDF_BYTES)}")
            continue

        created_size = create_pdf_with_quality(processed_paths, pdf_filename, quality)
        if created_size is None:
            print(f"Ошибка при создании {pdf_filename.name}")
        else:
            pdf_results.append((quality, label, pdf_filename, created_size))
            print(f"{pdf_filename.name:30} | {quality:3}% | {format_size(created_size):>8}")

    if not pdf_results:
        print("\nPDF не созданы")
        return

    pdf_results.sort(key=lambda r: r[3])
    print(f"\nОбработка завершена.")

if __name__ == "__main__":
    process_all_image_files()
