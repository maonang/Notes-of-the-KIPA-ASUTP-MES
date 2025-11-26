#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Программа копирования файлов с расширенным логированием в CSV.
Поддержка Windows, обработка ошибок, интерактивный CLI.
"""

import csv
import os
import shutil
import platform
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple

try:
    from tqdm import tqdm
except Exception:
    tqdm = None


# ------------------------------------------------------------------------------
# Конфигурация
# ------------------------------------------------------------------------------

@dataclass
class CopyConfig:
    """Настройки поведения копирования."""
    individual_processing: bool = True
    replace_existing: bool = False
    skip_all_existing: bool = False
    replace_all_existing: bool = False


# ------------------------------------------------------------------------------
# Логирование CSV
# ------------------------------------------------------------------------------

class CsvLogger:
    """Логирование в отдельные CSV-файлы."""

    def __init__(self, file_path: str, fieldnames: List[str]):
        self.file_path = Path(file_path)
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
# Основной класс копирования
# ------------------------------------------------------------------------------

class Copier:

    def __init__(self, src_root: str, dst_root: str, config: Optional[CopyConfig] = None):
        self.src_root = Path(src_root)
        self.dst_root = Path(dst_root)
        self.config = config or CopyConfig()
        self.platform = platform.system()

        base = Path.cwd() / "logs_csv"
        base.mkdir(parents=True, exist_ok=True)

        fields = [
            "timestamp", "full_path", "path_length", "size_bytes",
            "owner", "creation_time", "modification_time", "message", "status"
        ]

        self.l_error = CsvLogger(base / "error.csv", fields)
        self.l_owner = CsvLogger(base / "error_owner.csv", fields)
        self.l_length = CsvLogger(base / "error_length.csv", fields)
        self.l_info = CsvLogger(base / "info.csv", fields)
        self.l_skip = CsvLogger(base / "skipped.csv", fields)
        self.l_owner_chg = CsvLogger(base / "owner_changed.csv", fields)

    # ------------------------------------------------------------------
    # Вспомогательные методы
    # ------------------------------------------------------------------

    @staticmethod
    def now() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_file_owner(self, path: Path) -> str:
        """Получение владельца (Windows, если доступен pywin32)."""
        try:
            if self.platform == "Windows":
                import win32security  # type: ignore
                sd = win32security.GetFileSecurity(str(path), win32security.OWNER_SECURITY_INFORMATION)
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
        info.update({
            "timestamp": self.now(),
            "message": message,
            "status": status,
        })
        logger.log(info)

    # ------------------------------------------------------------------
    # Решение о замене
    # ------------------------------------------------------------------

    def ask_replace(self, src: Path, dst: Path) -> bool:
        """Интерактивный выбор: заменить файл, пропустить, выбрать режим на будущее."""
        if not dst.exists():
            return True

        if not self.config.individual_processing:
            if self.config.replace_all_existing:
                return True
            if self.config.skip_all_existing:
                return False

        print("\nОбнаружен существующий файл:")
        print("Источник:", src)
        print("Цель    :", dst)

        while True:
            print("\nВыберите действие:")
            print("[1] Заменить файл")
            print("[2] Пропустить файл")
            print("[3] Всегда заменять (без вопросов)")
            print("[4] Всегда пропускать (без вопросов)")

            c = input("Ваш выбор: ").strip()
            if c == "1":
                return True
            if c == "2":
                self.log(self.l_skip, src, "Пропущен пользователем", "SKIPPED")
                return False
            if c == "3":
                self.config.replace_all_existing = True
                return True
            if c == "4":
                self.config.skip_all_existing = True
                self.log(self.l_skip, src, "Пользователь выбрал пропуск всех", "SKIPPED")
                return False
            print("Неверный ввод.")

    # ------------------------------------------------------------------
    # Копирование
    # ------------------------------------------------------------------

    def copy_file(self, src: Path, dst: Path) -> bool:
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)

            if dst.exists():
                if not self.ask_replace(src, dst):
                    return False

            shutil.copy2(src, dst)
            self.log(self.l_info, src, f"Скопирован → {dst}", "OK")
            return True

        except PermissionError as e:
            self.log(self.l_owner, src, f"Ошибка доступа: {e}", "OWNER_ERROR")
            return False

        except OSError as e:
            if "File name too long" in str(e):
                self.log(self.l_length, src, "Слишком длинный путь", "PATH_LONG")
                return False
            self.log(self.l_error, src, f"OSError: {e}", "ERROR")
            return False

        except Exception as e:
            self.log(self.l_error, src, f"Unexpected: {e}", "ERROR")
            return False

    # ------------------------------------------------------------------

    def copy_all(self):
        files = []
        for root, _, fs in os.walk(self.src_root):
            for f in fs:
                files.append(Path(root) / f)

        print("\nВсего файлов:", len(files))

        iterator = tqdm(files, ncols=100, unit="файл") if tqdm else files

        for src in iterator:
            rel = src.relative_to(self.src_root)
            dst = self.dst_root / rel
            self.copy_file(src, dst)

        print("\nГотово. Логи в папке logs_csv.")

    # ------------------------------------------------------------------

    def verify(self):
        if not self.src_root.exists():
            print("Исходная директория не существует.")
            return False
        self.dst_root.mkdir(parents=True, exist_ok=True)
        return True


# ------------------------------------------------------------------------------
# Интерактивный CLI
# ------------------------------------------------------------------------------

def main():
    print("=== Копировщик файлов v2.0 ===")

    src = input("\nУкажите путь ИСТОЧНИКА: ").strip().strip('"')
    dst = input("Укажите путь НАЗНАЧЕНИЯ: ").strip().strip('"')

    mode = input("\nИспользовать индивидуальные запросы при конфликте файлов? (y/n): ").lower()
    individual = (mode != "n")

    copier = Copier(src, dst, CopyConfig(individual_processing=individual))

    if not copier.verify():
        return

    copier.copy_all()


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
