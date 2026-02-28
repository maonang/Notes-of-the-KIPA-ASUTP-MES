#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, time, date
from decimal import Decimal, getcontext
from typing import (
    Union,
    Tuple,
    List,
    Sequence,
    Optional,
    Iterable,
    Callable,
    Any,
)
import re
from dateutil.relativedelta import relativedelta


# --------------------------
# Типы
# --------------------------

DateLike = date | datetime
TimeLike = time
DateTimeLike = datetime | date | time
TimeDeltaLike = timedelta | relativedelta

Token = Tuple[str, str]                     # оператор, строковое значение токена
ParsedDT = Tuple[DateTimeLike, bool, bool]  # значение, только_время?, только_дата?

Interval = Tuple[datetime, datetime]


# --------------------------
# Настройки
# --------------------------

getcontext().prec = 28


# --------------------------
# Утилиты
# --------------------------

def normalize_separators(input_str: str) -> str:
    """Нормализует разделители / → ."""
    return input_str.replace('/', '.')


def parse_number(value_str: str) -> Decimal:
    normalized = value_str.replace(',', '.')
    return Decimal(normalized)


# --------------------------
# Парсинг дат, времени
# --------------------------

def parse_datetime_input(input_str: str) -> ParsedDT:
    """
    Парсит строку в datetime/date/time.
    Поддерживает: now
    """
    clean = normalize_separators(input_str.strip())

    # now
    if clean.lower() == "now":
        return datetime.now(), False, False

    # время
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            t = datetime.strptime(clean, fmt).time()
            return t, True, False
        except ValueError:
            pass

    # дата
    for fmt in ("%d.%m.%Y",):
        try:
            d = datetime.strptime(clean, fmt).date()
            return d, False, True
        except ValueError:
            pass

    # datetime
    for fmt in ("%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M"):
        try:
            dt = datetime.strptime(clean, fmt)
            return dt, False, False
        except ValueError:
            pass

    raise ValueError(f"Неверный формат: {input_str}")


# --------------------------
# Парсинг интервалов
# --------------------------

def parse_time_delta(input_str: str) -> TimeDeltaLike:
    """
    Парсит интервалы:
    - Новый формат: "Xd HH:MM[:SS]"
    - Старые форматы: "1d", "2h", "1.5m", "1y", "2mon"
    """
    s = input_str.strip()

    # Новый формат
    complex_match = re.match(
        r'(?:(\d+)[dD]\s+)?(\d{1,2}):(\d{2})(?::(\d{2}))?$',
        s
    )
    if complex_match:
        days = int(complex_match.group(1) or 0)
        hours = int(complex_match.group(2))
        minutes = int(complex_match.group(3))
        seconds = int(complex_match.group(4) or 0)
        return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    # Старый формат
    match = re.match(r'([\d,\.]+)([dhmsy]|mon)$', s)
    if not match:
        raise ValueError(f"Неверный формат интервала: {input_str}")

    value = parse_number(match.group(1))
    unit = match.group(2)

    if unit == 'd':
        days = int(value)
        frac_hours = float(value - days) * 24
        return timedelta(days=days, hours=frac_hours)

    if unit == 'h':
        return timedelta(hours=float(value))

    if unit == 'm':
        return timedelta(minutes=float(value))

    if unit == 's':
        return timedelta(seconds=float(value))

    if unit == 'y':
        years = int(value)
        remainder = float(value - years) * 365.2425
        delta = relativedelta(years=years)
        if remainder:
            delta += timedelta(days=remainder)
        return delta

    if unit == 'mon':
        months = int(value)
        remainder = float(value - months) * 30.436875
        delta = relativedelta(months=months)
        if remainder:
            delta += timedelta(days=remainder)
        return delta

    raise ValueError(f"Неизвестная единица: {unit}")


# --------------------------
# Операции над датами/временем
# --------------------------

def apply_operation(base: DateTimeLike, delta: TimeDeltaLike, op: str) -> DateTimeLike:
    if op not in ('+', '-'):
        raise ValueError(f"Неизвестный оператор: {op}")

    sign = 1 if op == '+' else -1

    if isinstance(base, datetime):
        return base + delta * sign

    if isinstance(base, date):
        tmp = datetime.combine(base, time.min) + delta * sign
        return tmp.date() if tmp.time() == time.min else tmp

    if isinstance(base, time):
        tmp = datetime.combine(date.min, base) + delta * sign
        return tmp.time()

    raise TypeError("Неподдерживаемый тип")


# --------------------------
# Разница дат/времени
# --------------------------

def calculate_difference(left: DateTimeLike, right: DateTimeLike) -> timedelta:
    if isinstance(left, datetime) and isinstance(right, datetime):
        return left - right

    if isinstance(left, date) and isinstance(right, date):
        return datetime.combine(left, time.min) - datetime.combine(right, time.min)

    if isinstance(left, time) and isinstance(right, time):
        return datetime.combine(date.min, left) - datetime.combine(date.min, right)

    if isinstance(left, datetime) and isinstance(right, date):
        return left - datetime.combine(right, time.min)

    if isinstance(left, date) and isinstance(right, datetime):
        return datetime.combine(left, time.min) - right

    raise ValueError("Несовместимые типы для вычитания")


# --------------------------
# Разбор комплексных выражений
# --------------------------

def parse_complex_expression(expression: str) -> List[Token]:
    tokens: List[Token] = []
    cur = ""
    s = expression
    n = len(s)
    i = 0

    while i < n:
        c = s[i]

        if c in "+-":
            if cur:
                if not tokens:
                    tokens.append(("+", cur.strip()))
                else:
                    tokens.append((tokens[-1][0], cur.strip()))
                cur = ""
            op = c
            i += 1
            while i < n and s[i] == " ":
                i += 1
            while i < n and s[i] not in "+-":
                cur += s[i]
                i += 1
            if cur:
                tokens.append((op, cur.strip()))
            cur = ""
        else:
            cur += c
            i += 1

    if cur:
        if not tokens:
            tokens.append(("+", cur.strip()))
        else:
            tokens.append((tokens[-1][0], cur.strip()))

    return tokens


# --------------------------
# Вычисление комплексного выражения
# --------------------------

def evaluate_expression(tokens: Sequence[Token]) -> DateTimeLike | timedelta:
    if not tokens:
        raise ValueError("Пустое выражение")

    op0, first_val = tokens[0]
    if op0 != '+':
        raise ValueError("Первое значение должно быть датой")

    base, is_t, is_d = parse_datetime_input(first_val)
    cur: DateTimeLike = base

    for op, val in tokens[1:]:

        # интервал?
        is_simple_interval = re.match(r'^[\d,\.]+[dhmsy]$|^[\d,\.]+mon$', val)
        is_complex_interval = re.match(r'(?:(\d+)[dD]\s+)?\d{1,2}:\d{2}(?::\d{2})?$', val)

        if is_simple_interval or is_complex_interval:
            delta = parse_time_delta(val)
            cur = apply_operation(cur, delta, op)
            continue

        # дата/время
        other, _, _ = parse_datetime_input(val)

        if op == '+':
            raise ValueError(f"Нельзя складывать даты: {val}")

        return calculate_difference(cur, other)

    return cur


# --------------------------
# Форматирование
# --------------------------

def format_timedelta(td: timedelta) -> str:
    total = int(td.total_seconds())
    days = total // 86400
    total %= 86400
    hours = total // 3600
    total %= 3600
    minutes = total // 60
    seconds = total % 60

    parts: List[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


def format_time(t: time) -> str:
    return t.strftime("%H:%M") if t.second == 0 else t.strftime("%H:%M:%S")


def format_result(v: DateTimeLike) -> str:
    if isinstance(v, datetime):
        return f"{v:%d.%m.%Y} {format_time(v.time())}"
    if isinstance(v, date):
        return f"{v:%d.%m.%Y}"
    return format_time(v)


# --------------------------
# Основной цикл
# --------------------------

def calculate() -> None:
    while True:
        print("\nВведите выражение или 'q' для выхода:")
        expression = normalize_separators(input("> ").strip())

        if expression.lower() == "q":
            break

        if not any(op in expression for op in "+-"):
            print("Неверный ввод")
            continue

        tokens = parse_complex_expression(expression)

        result = evaluate_expression(tokens)

        print("=" * 40)
        if isinstance(result, timedelta):
            print("Результат:", format_timedelta(result))
        else:
            print("Результат:", format_result(result))
        print("=" * 40)


if __name__ == "__main__":
    calculate()