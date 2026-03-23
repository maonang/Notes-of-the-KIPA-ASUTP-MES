#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Программа копирования файлов с расширенным логированием в CSV.
"""

import csv
import os
import shutil
import platform
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List

try:
    from tqdm import tqdm
except Exception:
    tqdm = None


# ------------------------------------------------------------------------------
# Конфигурационные файлы (создаются при старте)
# ------------------------------------------------------------------------------

EXCLUDE_EXTENSIONS_FILE = Path("exclude_extensions.txt")
EXCLUDE_DIRS_FILE = Path("exclude_dirs.txt")

EXCLUDE_EXTENSIONS_DEFAULT = """\
# Файл исключений по расширению.
# Укажите расширения файлов (по одному на строку), которые НЕ нужно копировать.
# Регистр не важен. Знак # в начале строки — комментарий.
# Примеры:
# .tmp
# .log
# .bak
# .thumb
"""

EXCLUDE_DIRS_DEFAULT = """\
# Файл исключений по каталогам.
# Укажите корневые каталоги (по одному на строку), из которых файлы копировать НЕ нужно.
# Регистр пути зависит от операционной системы. Знак # — комментарий.
# Примеры:
# C:\\Users\\User\\AppData
# D:\\Temp
# /home/user/.cache
"""


def ensure_config_files():
    """Создаёт конфигурационные файлы, если они не существуют."""
    if not EXCLUDE_EXTENSIONS_FILE.exists():
        EXCLUDE_EXTENSIONS_FILE.write_text(EXCLUDE_EXTENSIONS_DEFAULT, encoding="utf-8")
        print(f"  [+] Создан файл исключений расширений: {EXCLUDE_EXTENSIONS_FILE.resolve()}")

    if not EXCLUDE_DIRS_FILE.exists():
        EXCLUDE_DIRS_FILE.write_text(EXCLUDE_DIRS_DEFAULT, encoding="utf-8")
        print(f"  [+] Создан файл исключений каталогов: {EXCLUDE_DIRS_FILE.resolve()}")


def load_exclude_extensions() -> set:
    """Загружает расширения для исключения из txt-файла."""
    result = set()
    if not EXCLUDE_EXTENSIONS_FILE.exists():
        return result
    for line in EXCLUDE_EXTENSIONS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            ext = line.lower()
            if not ext.startswith("."):
                ext = "." + ext
            result.add(ext)
    return result


def load_exclude_dirs() -> List[Path]:
    """Загружает каталоги для исключения из txt-файла."""
    result = []
    if not EXCLUDE_DIRS_FILE.exists():
        return result
    for line in EXCLUDE_DIRS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            result.append(Path(line))
    return result


def is_excluded_by_dir(path: Path, exclude_dirs: List[Path]) -> bool:
    """Возвращает True, если путь находится внутри одного из исключённых каталогов."""
    for excl in exclude_dirs:
        try:
            path.relative_to(excl)
            return True
        except ValueError:
            pass
    return False


# ------------------------------------------------------------------------------
# Конфигурация копирования
# ------------------------------------------------------------------------------

@dataclass
class CopyConfig:
    """Настройки поведения копирования."""
    replace_existing: bool = False      # True = заменять все дубли, False = пропускать все
    delay_between_files: float = 0.0    # Пауза между файлами (секунды)
    speed_limit_bytes: int = 0          # Ограничение скорости (байт/сек), 0 = без ограничения


# ------------------------------------------------------------------------------
# Статистика
# ------------------------------------------------------------------------------

@dataclass
class Stats:
    copied: int = 0
    skipped: int = 0
    errors: int = 0
    owner_errors: int = 0
    path_too_long: int = 0
    excluded_ext: int = 0
    excluded_dir: int = 0


# ------------------------------------------------------------------------------
# Логирование CSV
# ------------------------------------------------------------------------------

class CsvLogger:
    """Логирование в отдельные CSV-файлы."""

    def __init__(self, file_path: Path, fieldnames: List[str]):
        self.file_path = file_path
        self.fieldnames = fieldnames
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_header()

    def _ensure_header(self) -> None:
        need_header = not self.file_path.exists() or self.file_path.stat().st_size == 0
        with self.file_path.open("a", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            if need_header:
                writer.writeheader()

    def log(self, record: dict) -> None:
        with self.file_path.open("a", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(record)


# ------------------------------------------------------------------------------
# Копирование с ограничением скорости
# ------------------------------------------------------------------------------

def copy_with_speed_limit(src: Path, dst: Path, speed_limit_bytes: int):
    """
    Копирует файл чанками с соблюдением ограничения скорости.
    Если speed_limit_bytes == 0, использует стандартный shutil.copy2.
    """
    if speed_limit_bytes <= 0:
        shutil.copy2(src, dst)
        return

    chunk_size = max(65536, speed_limit_bytes // 10)  # ~10 итераций в секунду
    with src.open("rb") as fsrc, dst.open("wb") as fdst:
        while True:
            t0 = time.monotonic()
            chunk = fsrc.read(chunk_size)
            if not chunk:
                break
            fdst.write(chunk)
            elapsed = time.monotonic() - t0
            expected = len(chunk) / speed_limit_bytes
            if expected > elapsed:
                time.sleep(expected - elapsed)

    # Сохраняем метаданные (время изменения/доступа)
    shutil.copystat(src, dst)


# ------------------------------------------------------------------------------
# Основной класс копирования
# ------------------------------------------------------------------------------

class Copier:

    def __init__(
        self,
        src_root: str,
        dst_root: str,
        config: Optional[CopyConfig] = None,
        exclude_extensions: Optional[set] = None,
        exclude_dirs: Optional[List[Path]] = None,
    ):
        self.src_root = Path(src_root)
        self.dst_root = Path(dst_root)
        self.config = config or CopyConfig()
        self.exclude_extensions = exclude_extensions or set()
        self.exclude_dirs = exclude_dirs or []
        self.platform = platform.system()
        self.stats = Stats()

        base = Path.cwd() / "logs_csv"
        base.mkdir(parents=True, exist_ok=True)

        fields = [
            "timestamp", "full_path", "path_length", "size_bytes",
            "owner", "creation_time", "modification_time", "message", "status"
        ]

        self.l_error     = CsvLogger(base / "error.csv",         fields)
        self.l_owner     = CsvLogger(base / "error_owner.csv",   fields)
        self.l_length    = CsvLogger(base / "error_length.csv",  fields)
        self.l_info      = CsvLogger(base / "info.csv",          fields)
        self.l_skip      = CsvLogger(base / "skipped.csv",       fields)
        self.l_excluded  = CsvLogger(base / "excluded.csv",      fields)

        print(f"  [+] Папка логов: {base.resolve()}")

    # ------------------------------------------------------------------
    # Вспомогательные методы
    # ------------------------------------------------------------------

    @staticmethod
    def now() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_file_owner(self, path: Path) -> str:
        try:
            if self.platform == "Windows":
                import win32security  # type: ignore
                sd = win32security.GetFileSecurity(
                    str(path), win32security.OWNER_SECURITY_INFORMATION
                )
                owner_sid = sd.GetSecurityDescriptorOwner()
                name, domain, _ = win32security.LookupAccountSid(None, owner_sid)
                return f"{domain}\\{name}" if domain else name
        except Exception:
            pass
        try:
            return f"UID:{path.stat().st_uid}"
        except Exception:
            return "Unknown"

    def file_info(self, path: Path) -> dict:
        try:
            st = path.stat()
            return {
                "full_path": str(path),
                "size_bytes": st.st_size,
                "path_length": len(str(path)),
                "owner": self.get_file_owner(path),
                "creation_time": datetime.fromtimestamp(st.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                "modification_time": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            }
        except Exception:
            return {
                "full_path": str(path),
                "size_bytes": "",
                "path_length": len(str(path)),
                "owner": "N/A",
                "creation_time": "",
                "modification_time": "",
            }

    # ------------------------------------------------------------------
    # Логирование
    # ------------------------------------------------------------------

    def log(self, logger: CsvLogger, path: Path, message: str, status: str):
        info = self.file_info(path)
        info.update({"timestamp": self.now(), "message": message, "status": status})
        logger.log(info)

    # ------------------------------------------------------------------
    # Копирование одного файла
    # ------------------------------------------------------------------

    def copy_file(self, src: Path, dst: Path) -> bool:
        # Фильтр по расширению
        if src.suffix.lower() in self.exclude_extensions:
            self.log(self.l_excluded, src, f"Исключён по расширению: {src.suffix}", "EXCLUDED_EXT")
            self.stats.excluded_ext += 1
            return False

        # Фильтр по каталогу
        if is_excluded_by_dir(src, self.exclude_dirs):
            self.log(self.l_excluded, src, "Исключён по каталогу", "EXCLUDED_DIR")
            self.stats.excluded_dir += 1
            return False

        try:
            dst.parent.mkdir(parents=True, exist_ok=True)

            if dst.exists():
                if not self.config.replace_existing:
                    self.log(self.l_skip, src, "Дубль пропущен (режим: пропускать)", "SKIPPED")
                    self.stats.skipped += 1
                    return False
                # replace_existing == True: файл будет перезаписан

            copy_with_speed_limit(src, dst, self.config.speed_limit_bytes)
            self.log(self.l_info, src, f"Скопирован → {dst}", "OK")
            self.stats.copied += 1
            return True

        except PermissionError as e:
            self.log(self.l_owner, src, f"Ошибка доступа: {e}", "OWNER_ERROR")
            self.stats.owner_errors += 1
            return False

        except OSError as e:
            if "File name too long" in str(e) or "path too long" in str(e).lower():
                self.log(self.l_length, src, "Слишком длинный путь", "PATH_LONG")
                self.stats.path_too_long += 1
                return False
            self.log(self.l_error, src, f"OSError: {e}", "ERROR")
            self.stats.errors += 1
            return False

        except Exception as e:
            self.log(self.l_error, src, f"Unexpected: {e}", "ERROR")
            self.stats.errors += 1
            return False

    # ------------------------------------------------------------------
    # Обход и копирование
    # ------------------------------------------------------------------

    def copy_all(self):
        print("\nСканирование источника...")
        files = []
        for root, dirs, fs in os.walk(self.src_root):
            root_path = Path(root)
            # Исключаем подкаталоги прямо в os.walk, чтобы не заходить в них
            dirs[:] = [
                d for d in dirs
                if not is_excluded_by_dir(root_path / d, self.exclude_dirs)
            ]
            for f in fs:
                files.append(root_path / f)

        print(f"Всего файлов для обработки: {len(files)}")
        if self.config.delay_between_files > 0:
            print(f"Пауза между файлами: {self.config.delay_between_files} сек.")
        if self.config.speed_limit_bytes > 0:
            print(f"Ограничение скорости: {self.config.speed_limit_bytes // 1024} КБ/сек")

        iterator = tqdm(files, ncols=100, unit="файл") if tqdm else files

        for src in iterator:
            rel = src.relative_to(self.src_root)
            dst = self.dst_root / rel
            self.copy_file(src, dst)
            if self.config.delay_between_files > 0:
                time.sleep(self.config.delay_between_files)

        self._print_summary()

    # ------------------------------------------------------------------
    # Итоговый отчёт
    # ------------------------------------------------------------------

    def _print_summary(self):
        s = self.stats
        total = s.copied + s.skipped + s.errors + s.owner_errors + s.path_too_long + s.excluded_ext + s.excluded_dir
        print("\n" + "=" * 50)
        print("  ИТОГ КОПИРОВАНИЯ")
        print("=" * 50)
        print(f"  Всего обработано файлов : {total}")
        print(f"  Скопировано успешно     : {s.copied}")
        print(f"  Пропущено (дубли)       : {s.skipped}")
        print(f"  Исключено по расширению : {s.excluded_ext}")
        print(f"  Исключено по каталогу   : {s.excluded_dir}")
        print(f"  Ошибки доступа          : {s.owner_errors}")
        print(f"  Путь слишком длинный    : {s.path_too_long}")
        print(f"  Прочие ошибки           : {s.errors}")
        print("=" * 50)
        print("  Логи сохранены в папке: logs_csv/")
        print("=" * 50)

    # ------------------------------------------------------------------

    def verify(self) -> bool:
        if not self.src_root.exists():
            print("Ошибка: исходная директория не существует.")
            return False
        self.dst_root.mkdir(parents=True, exist_ok=True)
        return True


# ------------------------------------------------------------------------------
# Вспомогательный ввод с валидацией
# ------------------------------------------------------------------------------

def ask_float(prompt: str, default: float, min_val: float = 0.0) -> float:
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return default
        try:
            val = float(raw)
            if val < min_val:
                print(f"  Введите значение >= {min_val}.")
                continue
            return val
        except ValueError:
            print("  Неверный формат. Введите число.")


def ask_int(prompt: str, default: int, min_val: int = 0) -> int:
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return default
        try:
            val = int(raw)
            if val < min_val:
                print(f"  Введите значение >= {min_val}.")
                continue
            return val
        except ValueError:
            print("  Неверный формат. Введите целое число.")


# ------------------------------------------------------------------------------
# Интерактивный CLI
# ------------------------------------------------------------------------------

def main():
    print("=" * 50)
    print("  Копировщик файлов v4.0")
    print("=" * 50)

    # ── Шаг 1: создать все файлы ──────────────────────────────────────
    print("\n[1/5] Подготовка рабочих файлов...")
    ensure_config_files()

    # CSV-логи будут созданы внутри Copier, но информируем заранее
    logs_path = Path.cwd() / "logs_csv"
    print(f"  [i] CSV-логи будут в: {logs_path.resolve()}")

    # ── Шаг 2: вопросы о дублях (ДО указания путей) ───────────────────
    print("\n[2/5] Настройка обработки дублей")
    print("  Что делать, если файл в папке назначения уже существует?")
    print("  [1] Пропускать все дубли")
    print("  [2] Заменять все дубли")
    while True:
        choice = input("  Ваш выбор [1/2]: ").strip()
        if choice == "1":
            replace_existing = False
            print("  → Режим: пропускать дубли.")
            break
        elif choice == "2":
            replace_existing = True
            print("  → Режим: заменять дубли.")
            break
        print("  Введите 1 или 2.")

    # ── Шаг 3: настройки нагрузки ─────────────────────────────────────
    print("\n[3/5] Настройка нагрузки на диск / сеть")
    print("  Нажмите Enter, чтобы принять значение по умолчанию.")

    delay = ask_float(
        "  Пауза между файлами в секундах (0 = без паузы) [по умолчанию: 0]: ",
        default=0.0,
        min_val=0.0,
    )

    speed_kb = ask_int(
        "  Ограничение скорости копирования в КБ/сек (0 = без ограничения) [по умолчанию: 0]: ",
        default=0,
        min_val=0,
    )
    speed_bytes = speed_kb * 1024

    # ── Шаг 4: пути ───────────────────────────────────────────────────
    print("\n[4/5] Укажите пути")
    print("  Сейчас вы можете отредактировать файлы исключений, затем продолжить.")
    print(f"  Расширения : {EXCLUDE_EXTENSIONS_FILE.resolve()}")
    print(f"  Каталоги   : {EXCLUDE_DIRS_FILE.resolve()}")
    input("  Нажмите Enter, когда будете готовы продолжить...")

    src = input("\n  Укажите путь ИСТОЧНИКА : ").strip().strip('"')
    dst = input("  Укажите путь НАЗНАЧЕНИЯ: ").strip().strip('"')

    # ── Шаг 5: загрузка исключений и запуск ───────────────────────────
    print("\n[5/5] Загрузка конфигурации и запуск")
    exclude_exts = load_exclude_extensions()
    exclude_dirs = load_exclude_dirs()

    if exclude_exts:
        print(f"  Исключены расширения ({len(exclude_exts)}): {', '.join(sorted(exclude_exts))}")

    if exclude_dirs:
        print(f"  Исключены каталоги ({len(exclude_dirs)}):")
        for d in exclude_dirs:
            print(f"    - {d}")

    config = CopyConfig(
        replace_existing=replace_existing,
        delay_between_files=delay,
        speed_limit_bytes=speed_bytes,
    )

    copier = Copier(src, dst, config, exclude_exts, exclude_dirs)

    if not copier.verify():
        return

    print("\nЗапуск копирования...\n")
    copier.copy_all()


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
