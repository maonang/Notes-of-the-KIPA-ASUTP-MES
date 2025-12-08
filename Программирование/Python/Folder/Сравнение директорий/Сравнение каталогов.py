#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pip install aiofiles aiosqlite tqdm

"""
Асинхронное сравнение директорий
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from tqdm import tqdm
from typing import TypeAlias
import aiofiles
import aiosqlite
import asyncio
import os
import tempfile


# ===== Windows: поддержка длинных путей =====

def win_long_path(path: str | Path) -> str:
    """Преобразует путь в формат Windows \\?\ для длинных путей."""
    p = str(path)
    if os.name == "nt":
        p = os.path.abspath(p)
        if not p.startswith("\\\\?\\"):
            if p.startswith("\\\\"):  # UNC
                p = "\\\\?\\UNC\\" + p[2:]
            else:
                p = "\\\\?\\" + p
    return p


PathLike: TypeAlias = str | os.PathLike
DB_BATCH = 1024


@dataclass(slots=True, frozen=True)
class Config:
    source: Path
    target: Path
    out_prefix: Path
    recursive: bool


async def normalize_path_async(path: PathLike) -> Path:
    """Асинхронная нормализация пути (но фактически синхронная — через to_thread)."""
    def _resolve():
        p = Path(path).expanduser().resolve()
        return Path(win_long_path(p))

    resolved = await asyncio.to_thread(_resolve)
    return resolved


# ===== Сканирование =====

def walk_sync_recursive(root: Path):
    root = Path(root)
    root_str = str(root).rstrip(os.sep)
    root_len = len(root_str) + 1

    stack = [root]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                for entry in it:
                    path_obj = Path(entry.path)
                    rel = str(path_obj)[root_len:] if str(path_obj).startswith(root_str) else entry.name
                    if entry.is_dir(follow_symlinks=False):
                        yield rel, True
                        stack.append(path_obj)
                    else:
                        yield rel, False
        except PermissionError:
            continue


def walk_sync_flat(root: Path):
    try:
        with os.scandir(root) as it:
            for entry in it:
                yield entry.name, entry.is_dir(follow_symlinks=False)
    except PermissionError:
        return


async def produce_paths(root: Path, queue: asyncio.Queue, recursive: bool):
    loop = asyncio.get_running_loop()
    scan_func = walk_sync_recursive if recursive else walk_sync_flat

    # Весь обход синхронный → выносим в поток
    iterator = await loop.run_in_executor(None, lambda: list(scan_func(root)))

    pbar = tqdm(desc=f"Scanning {root}", unit="items", dynamic_ncols=True)

    batch = []
    for rel, isdir in iterator:
        batch.append((rel, 1 if isdir else 0))
        if len(batch) >= DB_BATCH:
            await queue.put(batch)
            pbar.update(len(batch))
            batch = []
    if batch:
        await queue.put(batch)
        pbar.update(len(batch))

    pbar.close()
    await queue.put(None)


async def consume_paths(queue: asyncio.Queue, db: str, table: str):
    async with aiosqlite.connect(db) as conn:
        await conn.execute("PRAGMA journal_mode=WAL;")
        await conn.execute("PRAGMA synchronous=NORMAL;")
        await conn.execute(
            f"CREATE TABLE IF NOT EXISTS {table} (path TEXT PRIMARY KEY, is_dir INTEGER);"
        )
        await conn.commit()

        insert_sql = f"INSERT OR IGNORE INTO {table}(path, is_dir) VALUES (?, ?);"

        while True:
            batch = await queue.get()
            if batch is None:
                break
            async with conn.executemany(insert_sql, batch):
                pass
            await conn.commit()


async def build_db(root: Path, db: str, table: str, recursive: bool):
    queue = asyncio.Queue(maxsize=10)
    prod = asyncio.create_task(produce_paths(root, queue, recursive))
    cons = asyncio.create_task(consume_paths(queue, db, table))
    await asyncio.gather(prod, cons)


async def query_missing(db_src: str, table_src: str, db_tgt: str, table_tgt: str):
    missing_files = []
    missing_dirs = []

    async with aiosqlite.connect(db_src) as src:
        await src.execute(f"ATTACH DATABASE '{db_tgt}' AS tgt;")

        qf = f"""
            SELECT s.path FROM {table_src} s
            LEFT JOIN tgt.{table_tgt} t ON s.path=t.path
            WHERE s.is_dir=0 AND t.path IS NULL;
        """

        qd = f"""
            SELECT s.path FROM {table_src} s
            LEFT JOIN tgt.{table_tgt} t ON s.path=t.path
            WHERE s.is_dir=1 AND t.path IS NULL;
        """

        async with src.execute(qf) as cur:
            async for row in cur:
                missing_files.append(row[0])

        async with src.execute(qd) as cur:
            async for row in cur:
                missing_dirs.append(row[0])

        await src.execute("DETACH DATABASE tgt;")

    return missing_files, missing_dirs


async def write_results(prefix: Path, missing_files, missing_dirs):
    mf = prefix.with_name(prefix.name + "_missing_files.txt")
    md = prefix.with_name(prefix.name + "_missing_dirs.txt")

    async with aiofiles.open(mf, "w", encoding="utf-8") as f:
        for x in missing_files:
            await f.write(x + "\n")

    async with aiofiles.open(md, "w", encoding="utf-8") as f:
        for x in missing_dirs:
            await f.write(x + "\n")


async def run_comparison(cfg: Config):
    tmp = tempfile.TemporaryDirectory(prefix="cmp_dirs_")
    db_src = Path(tmp.name) / "src.db"
    db_tgt = Path(tmp.name) / "tgt.db"
    table = "paths"

    print("\nСканирование исходного каталога...")
    await build_db(cfg.source, str(db_src), table, cfg.recursive)

    print("\nСканирование проверяемого каталога...")
    await build_db(cfg.target, str(db_tgt), table, cfg.recursive)

    print("\nОпределение различий...")
    missing_files, missing_dirs = await query_missing(str(db_src), table, str(db_tgt), table)

    print("\nЗапись результатов...")
    await write_results(cfg.out_prefix, missing_files, missing_dirs)

    print(f"\nОтсутствует файлов: {len(missing_files):,d}")
    print(f"Отсутствует директорий: {len(missing_dirs):,d}")
    print("\nГотово.")

    tmp.cleanup()


# =========== Ввод данных пользователем ============

def ask_path(prompt: str) -> Path:
    while True:
        p = input(prompt).strip().strip('"').strip("'")
        if not p:
            print("Введите путь.")
            continue
        p = Path(p)
        if p.exists() and p.is_dir():
            return p
        print("Каталог не найден. Повторите ввод.")


def ask_recursive() -> bool:
    while True:
        a = input("Сканировать рекурсивно? (y/n): ").strip().lower()
        if a in ("y", "yes", "д", "да"):
            return True
        if a in ("n", "no", "н", "нет"):
            return False
        print("Введите y или n.")


async def main():
    print("=== Сравнение каталогов ===\n")

    src = ask_path("Исходный каталог: ")
    tgt = ask_path("Проверяемый каталог: ")

    recursive = ask_recursive()

    cfg = Config(
        source=await normalize_path_async(src),
        target=await normalize_path_async(tgt),
        out_prefix=Path("compare_result"),
        recursive=recursive,
    )

    await run_comparison(cfg)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nПрервано пользователем.")