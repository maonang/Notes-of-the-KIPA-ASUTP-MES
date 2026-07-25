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
    TypeVar,
    overload,
)
import re
from dateutil.relativedelta import relativedelta

# ============================================================================
# Типы и константы
# ============================================================================

# Основные типы
DateTimeLike = Union[datetime, date, time]
TimeDeltaLike = Union[timedelta, relativedelta]
Token = Tuple[str, str]  # (оператор, значение)
ParsedDT = Tuple[DateTimeLike, bool, bool]  # (значение, флаг только_время?, флаг только_дата?)

# Настройки точности
getcontext().prec = 28

# Регулярные выражения для парсинга
RE_TIME_INTERVAL = re.compile(r'(?:(\d+)[dD]\s+)?(\d{1,2}):(\d{2})(?::(\d{2}))?$')
RE_SIMPLE_INTERVAL = re.compile(r'^[\d,\.]+[dhmsy]$|^[\d,\.]+mon$')
RE_COMPOSITE_INTERVAL = re.compile(r'^[\d,\.]+\s*[dhms](\s+[\d,\.]+\s*[dhms])+$')
RE_INTERVAL_PARTS = re.compile(r'([\d,\.]+)\s*([dhms])\b')
RE_SINGLE_INTERVAL = re.compile(r'([\d,\.]+)([dhmsy]|mon)$')
RE_INTERVAL_ONLY = re.compile(r'^[\d,\.]+\s*[dhmsy](\s+[\d,\.]+\s*[dhmsy])*$|^[\d,\.]+mon$')


# ============================================================================
# Утилиты
# ============================================================================

def normalize_separators(input_str: str) -> str:
    """
    Нормализует разделители в строке.
    Заменяет '/' на '.' для единообразия формата дат.

    Args:
        input_str: Исходная строка

    Returns:
        Строка с нормализованными разделителями
    """
    return input_str.replace('/', '.')


def parse_number(value_str: str) -> Decimal:
    """
    Парсит строку в Decimal.
    Поддерживает запятые как десятичный разделитель.

    Args:
        value_str: Строка с числом

    Returns:
        Decimal значение

    Raises:
        ValueError: Если строка не является числом
    """
    normalized = value_str.replace(',', '.')
    return Decimal(normalized)


def is_interval_string(s: str) -> bool:
    """
    Проверяет, является ли строка интервалом времени.
    Поддерживаемые форматы:
    - "HH:MM[:SS]" или "Xd HH:MM[:SS]"
    - "1d", "2h", "1.5m", "1y", "2mon"
    - "2h 15m", "1d 2h 30m"

    Args:
        s: Проверяемая строка

    Returns:
        True если строка является интервалом, иначе False
    """
    s = s.strip()

    # Формат времени как интервал: "HH:MM" или "Xd HH:MM"
    if RE_TIME_INTERVAL.match(s):
        return True

    # Одиночный интервал: "1d", "2h" и т.д.
    if RE_SIMPLE_INTERVAL.match(s):
        return True

    # Составной интервал: "2h 15m", "1h 3m", "1d 2h 30m"
    if RE_COMPOSITE_INTERVAL.match(s):
        return True

    return False


def is_time_string(s: str) -> bool:
    """
    Проверяет, является ли строка временем.

    Args:
        s: Проверяемая строка

    Returns:
        True если строка является временем, иначе False
    """
    return bool(re.match(r'^\d{1,2}:\d{2}(?::\d{2})?$', s.strip()))


def is_date_string(s: str) -> bool:
    """
    Проверяет, является ли строка датой.

    Args:
        s: Проверяемая строка

    Returns:
        True если строка является датой, иначе False
    """
    return bool(re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}$', s.strip()))


def is_interval_only(s: str) -> bool:
    """
    Проверяет, является ли строка только интервалом (без операторов + или -).

    Args:
        s: Проверяемая строка

    Returns:
        True если строка является интервалом без операторов
    """
    s = s.strip()
    return bool(RE_INTERVAL_ONLY.match(s)) and '+' not in s and '-' not in s


# ============================================================================
# Парсинг дат и времени
# ============================================================================

def parse_datetime_input(input_str: str) -> ParsedDT:
    """
    Парсит строку в datetime/date/time.
    Поддерживаемые форматы:
    - "now" - текущее время
    - "HH:MM" или "HH:MM:SS" - время
    - "DD.MM.YYYY" - дата
    - "DD.MM.YYYY HH:MM" или "DD.MM.YYYY HH:MM:SS" - дата и время

    Args:
        input_str: Строка для парсинга

    Returns:
        Кортеж (значение, только_время?, только_дата?)

    Raises:
        ValueError: Если формат строки не распознан
    """
    clean = normalize_separators(input_str.strip())

    # Специальные значения
    if clean.lower() == "now":
        return datetime.now(), False, False

    # Время
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            t = datetime.strptime(clean, fmt).time()
            return t, True, False
        except ValueError:
            pass

    # Дата
    try:
        d = datetime.strptime(clean, "%d.%m.%Y").date()
        return d, False, True
    except ValueError:
        pass

    # Дата и время
    for fmt in ("%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M"):
        try:
            dt = datetime.strptime(clean, fmt)
            return dt, False, False
        except ValueError:
            pass

    raise ValueError(f"Неверный формат: {input_str}")


def parse_time_delta(input_str: str) -> TimeDeltaLike:
    """
    Парсит строку интервала времени.
    Поддерживаемые форматы:
    - "Xd HH:MM[:SS]" или "HH:MM[:SS]"
    - "1d", "2h", "1.5m", "1y", "2mon"
    - "2h 15m", "1d 2h 30m", "1h 3m"

    Args:
        input_str: Строка интервала

    Returns:
        timedelta или relativedelta объект

    Raises:
        ValueError: Если формат интервала не распознан
    """
    s = input_str.strip()

    # Формат времени как интервал: "HH:MM[:SS]" или "Xd HH:MM[:SS]"
    time_match = RE_TIME_INTERVAL.match(s)
    if time_match:
        days = int(time_match.group(1) or 0)
        hours = int(time_match.group(2))
        minutes = int(time_match.group(3))
        seconds = int(time_match.group(4) or 0)
        return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    # Составной формат: "2h 15m", "1d 2h 30m", "1h 3m" и т.д.
    parts = RE_INTERVAL_PARTS.findall(s)
    if parts:
        result = timedelta(0)
        for value_str, unit in parts:
            value = parse_number(value_str)

            if unit == 'd':
                days = int(value)
                frac_hours = float(value - days) * 24
                result += timedelta(days=days, hours=frac_hours)
            elif unit == 'h':
                result += timedelta(hours=float(value))
            elif unit == 'm':
                result += timedelta(minutes=float(value))
            elif unit == 's':
                result += timedelta(seconds=float(value))
        return result

    # Одиночный формат: "1d", "2h", "1.5m", "1y", "2mon"
    match = RE_SINGLE_INTERVAL.match(s)
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


def parse_interval_to_components(input_str: str) -> Tuple[int, int, int, int, int, int]:
    """
    Парсит интервал и разбивает его на компоненты: годы, месяцы, дни, часы, минуты, секунды.

    Args:
        input_str: Строка интервала

    Returns:
        Кортеж (годы, месяцы, дни, часы, минуты, секунды)
    """
    delta = parse_time_delta(input_str)

    if isinstance(delta, relativedelta):
        years = delta.years or 0
        months = delta.months or 0
        days = delta.days or 0
        hours = 0
        minutes = 0
        seconds = 0
    else:
        years = 0
        months = 0
        total_seconds = int(delta.total_seconds())
        days = total_seconds // 86400
        total_seconds %= 86400
        hours = total_seconds // 3600
        total_seconds %= 3600
        minutes = total_seconds // 60
        seconds = total_seconds % 60

    return years, months, days, hours, minutes, seconds


def format_interval_components(years: int, months: int, days: int, hours: int, minutes: int, seconds: int) -> str:
    """
    Форматирует компоненты интервала в читаемый вид.

    Args:
        years: Годы
        months: Месяцы
        days: Дни
        hours: Часы
        minutes: Минуты
        seconds: Секунды

    Returns:
        Строка с отформатированным интервалом
    """
    parts = []
    if years:
        parts.append(f"{years} лет" if years > 1 else f"{years} год" if years == 1 else f"{years} года")
    if months:
        parts.append(f"{months} мес" if months > 1 else f"{months} мес")
    if days:
        parts.append(f"{days} дн" if days > 1 else f"{days} дн")
    if hours:
        parts.append(f"{hours} ч" if hours > 1 else f"{hours} ч")
    if minutes:
        parts.append(f"{minutes} мин" if minutes > 1 else f"{minutes} мин")
    if seconds:
        parts.append(f"{seconds} с" if seconds > 1 else f"{seconds} с")

    return " ".join(parts) if parts else "0 с"


# ============================================================================
# Операции с датами и временем
# ============================================================================

def apply_operation(base: DateTimeLike, delta: TimeDeltaLike, op: str) -> DateTimeLike:
    """
    Применяет операцию (+ или -) к дате/времени с интервалом.

    Args:
        base: Исходное значение (datetime, date или time)
        delta: Интервал для применения
        op: Оператор ('+' или '-')

    Returns:
        Результат операции того же типа, что и base

    Raises:
        ValueError: Если оператор неизвестен
        TypeError: Если тип base не поддерживается
    """
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

    raise TypeError(f"Неподдерживаемый тип: {type(base)}")


def calculate_difference(left: DateTimeLike, right: DateTimeLike) -> timedelta:
    """
    Вычисляет разницу между двумя значениями даты/времени.

    Args:
        left: Левое значение
        right: Правое значение

    Returns:
        Разница как timedelta

    Raises:
        ValueError: Если типы несовместимы для вычитания
    """
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


# ============================================================================
# Парсинг и вычисление выражений
# ============================================================================

def parse_complex_expression(expression: str) -> List[Token]:
    """
    Разбирает сложное выражение на токены.

    Args:
        expression: Строка выражения

    Returns:
        Список токенов (оператор, значение)
    """
    tokens: List[Token] = []
    current = ""
    s = expression
    n = len(s)
    i = 0

    while i < n:
        c = s[i]

        if c in "+-":
            # Сохраняем предыдущий токен
            if current:
                if not tokens:
                    tokens.append(("+", current.strip()))
                else:
                    tokens.append((tokens[-1][0], current.strip()))
                current = ""

            op = c
            i += 1

            # Пропускаем пробелы
            while i < n and s[i] == " ":
                i += 1

            # Собираем значение
            while i < n and s[i] not in "+-":
                current += s[i]
                i += 1

            if current:
                tokens.append((op, current.strip()))
            current = ""
        else:
            current += c
            i += 1

    # Сохраняем последний токен
    if current:
        if not tokens:
            tokens.append(("+", current.strip()))
        else:
            tokens.append((tokens[-1][0], current.strip()))

    return tokens


def evaluate_expression(tokens: Sequence[Token]) -> Union[DateTimeLike, TimeDeltaLike]:
    """
    Вычисляет выражение из токенов.

    Args:
        tokens: Список токенов

    Returns:
        Результат вычисления (DateTimeLike или TimeDeltaLike)

    Raises:
        ValueError: Если выражение некорректно
    """
    if not tokens:
        raise ValueError("Пустое выражение")

    op0, first_val = tokens[0]

    # Определяем тип первого значения
    if is_interval_string(first_val):
        # Выражение начинается с интервала
        current: TimeDeltaLike = timedelta(0)
        delta = parse_time_delta(first_val)
        if op0 == '+':
            current += delta
        else:
            current -= delta
    else:
        # Выражение начинается с даты/времени
        if op0 != '+':
            raise ValueError("Первое значение должно быть датой")
        base, is_t, is_d = parse_datetime_input(first_val)
        current: DateTimeLike = base

    # Обрабатываем остальные токены
    for op, val in tokens[1:]:
        if is_interval_string(val):
            # Токен - интервал
            delta = parse_time_delta(val)
            if isinstance(current, (datetime, date, time)):
                current = apply_operation(current, delta, op)
            else:
                # current - это timedelta
                if op == '+':
                    current += delta
                else:
                    current -= delta
        else:
            # Токен - дата/время
            other, _, _ = parse_datetime_input(val)

            if op == '+':
                raise ValueError(f"Нельзя складывать даты: {val}")

            return calculate_difference(current, other)

    return current


# ============================================================================
# Форматирование результатов
# ============================================================================

def format_timedelta(td: timedelta) -> str:
    """
    Форматирует timedelta в читаемый вид.

    Args:
        td: timedelta объект

    Returns:
        Строка в формате "Xd Xh Xm Xs"
    """
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


def format_as_time_string(td: timedelta) -> str:
    """
    Форматирует timedelta как время HH:MM[:SS].

    Args:
        td: timedelta объект

    Returns:
        Строка в формате "HH:MM" или "HH:MM:SS"
    """
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    total_seconds %= 3600
    minutes = total_seconds // 60
    seconds = total_seconds % 60

    if seconds > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{hours:02d}:{minutes:02d}"


def format_as_decimal_hours(value: Union[timedelta, time]) -> str:
    """
    Форматирует timedelta или time как десятичные часы.

    Args:
        value: timedelta или time объект

    Returns:
        Строка с количеством часов (4 знака после запятой)
    """
    if isinstance(value, timedelta):
        total_seconds = value.total_seconds()
    elif isinstance(value, time):
        total_seconds = value.hour * 3600 + value.minute * 60 + value.second
    else:
        return "Невозможно преобразовать"

    hours = total_seconds / 3600
    return f"{hours:.4f} ч"


def format_interval(td: TimeDeltaLike) -> str:
    """
    Форматирует timedelta или relativedelta как интервал.

    Args:
        td: timedelta или relativedelta объект

    Returns:
        Строка с интервалом
    """
    if isinstance(td, relativedelta):
        parts = []
        if td.years:
            parts.append(f"{td.years}y")
        if td.months:
            parts.append(f"{td.months}mon")
        if td.days:
            parts.append(f"{td.days}d")
        return " ".join(parts) if parts else "0s"
    return format_timedelta(td)


def format_time(t: time) -> str:
    """
    Форматирует время.

    Args:
        t: time объект

    Returns:
        Строка в формате "HH:MM" или "HH:MM:SS"
    """
    return t.strftime("%H:%M") if t.second == 0 else t.strftime("%H:%M:%S")


def format_result(v: DateTimeLike) -> str:
    """
    Форматирует результат (datetime, date или time).

    Args:
        v: DateTimeLike объект

    Returns:
        Отформатированная строка
    """
    if isinstance(v, datetime):
        return f"{v:%d.%m.%Y} {format_time(v.time())}"
    if isinstance(v, date):
        return f"{v:%d.%m.%Y}"
    return format_time(v)


# ============================================================================
# Основной цикл
# ============================================================================

def calculate() -> None:
    while True:
        print("\nВведите выражение или 'q' для выхода:")
        expression = normalize_separators(input("> ").strip())

        if expression.lower() == "q":
            break

        # Проверка: если введен только интервал без операторов
        if is_interval_only(expression):
            try:
                years, months, days, hours, minutes, seconds = parse_interval_to_components(expression)
                print("=" * 40)
                print("Результат:", format_interval_components(years, months, days, hours, minutes, seconds))
                print("=" * 40)
                continue
            except ValueError as e:
                print(f"Ошибка: {e}")
                continue

        if not any(op in expression for op in "+-"):
            print("Неверный ввод")
            continue

        tokens = parse_complex_expression(expression)

        try:
            result = evaluate_expression(tokens)
        except ValueError as e:
            print(f"Ошибка: {e}")
            continue

        print("=" * 40)

        if isinstance(result, timedelta):
            print("Результат:", format_timedelta(result))
            print("Время (HH:MM):", format_as_time_string(result))
            print("Десятичные часы:", format_as_decimal_hours(result))
        elif isinstance(result, relativedelta):
            print("Результат:", format_interval(result))
        else:
            print("Результат:", format_result(result))
            if isinstance(result, time):
                print("Десятичные часы:", format_as_decimal_hours(result))

        print("=" * 40)


if __name__ == "__main__":
    calculate()