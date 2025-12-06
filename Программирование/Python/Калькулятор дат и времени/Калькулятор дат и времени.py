from datetime import datetime, timedelta, time, date
import re
from typing import Union, List, Tuple, Optional
from decimal import Decimal, getcontext
from dateutil.relativedelta import relativedelta

# Устанавливаем точность вычислений
getcontext().prec = 28


def normalize_separators(input_str: str) -> str:
    """Нормализует разделители в дате: заменяет / на ."""
    return input_str.replace('/', '.')


def parse_number(value_str: str) -> Decimal:
    """Парсит число с запятой или точкой в качестве разделителя"""
    # Заменяем запятую на точку
    normalized = value_str.replace(',', '.')
    return Decimal(normalized)


def parse_datetime_input(input_str: str) -> Tuple[Union[datetime, date, time], bool, bool]:
    """
    Парсит строку ввода в объект datetime, date или time
    Возвращает: (объект, только_время?, только_дата?)
    """
    input_str = normalize_separators(input_str.strip())

    # Определяем возможные форматы
    time_only_formats = ["%H:%M:%S", "%H:%M"]
    date_only_formats = ["%d.%m.%Y"]
    datetime_formats = [
        "%d.%m.%Y %H:%M:%S",  # 01.01.2025 12:00:00
        "%d.%m.%Y %H:%M",  # 01.01.2025 12:00
    ]

    # Пробуем форматы только времени
    for fmt in time_only_formats:
        try:
            t = datetime.strptime(input_str, fmt).time()
            return t, True, False  # только время
        except ValueError:
            continue

    # Пробуем форматы только даты
    for fmt in date_only_formats:
        try:
            dt = datetime.strptime(input_str, fmt)
            return dt.date(), False, True  # только дата
        except ValueError:
            continue

    # Пробуем форматы даты и времени
    for fmt in datetime_formats:
        try:
            dt = datetime.strptime(input_str, fmt)
            return dt, False, False  # дата и время
        except ValueError:
            continue

    raise ValueError(f"Неверный формат: {input_str}")


def parse_time_delta(input_str: str) -> Union[timedelta, relativedelta]:
    """Парсит строку с временным интервалом (1,5d, 2.25h, 3,75m, 4.5s, 1,25y, 1.5mon)"""
    pattern = r'([\d,\.]+)([dhmsy]|mon)'
    match = re.match(pattern, input_str)
    if not match:
        raise ValueError(f"Неверный формат интервала: {input_str}")

    value_str = match.group(1)
    unit = match.group(2)

    try:
        value = parse_number(value_str)
    except Exception as e:
        raise ValueError(f"Неверное число: {value_str}")

    if unit == 'd':
        # Дни: целая часть + дробная часть в часах
        days = int(value)
        fractional_days = value - days
        hours = fractional_days * Decimal('24')
        return timedelta(days=days, hours=float(hours))
    elif unit == 'h':
        # Часы: целая часть + дробная часть в минутах
        total_hours = float(value)
        return timedelta(hours=total_hours)
    elif unit == 'm':
        # Минуты: целая часть + дробная часть в секундах
        total_minutes = float(value)
        return timedelta(minutes=total_minutes)
    elif unit == 's':
        # Секунды
        total_seconds = float(value)
        return timedelta(seconds=total_seconds)
    elif unit == 'y':
        # Годы: используем relativedelta для целых лет + дробная часть в днях
        years = int(value)
        fractional_years = value - years
        days = fractional_years * Decimal('365.2425')  # Среднее количество дней в году

        # Основная часть через relativedelta
        delta = relativedelta(years=years)
        # Добавляем дробную часть через timedelta
        if days != 0:
            delta += timedelta(days=float(days))
        return delta
    elif unit == 'mon':
        # Месяцы: целая часть + дробная часть в днях (приблизительно)
        months = int(value)
        fractional_months = value - months
        days = fractional_months * Decimal('30.436875')  # Среднее количество дней в месяце

        # Основная часть через relativedelta
        delta = relativedelta(months=months)
        # Добавляем дробную часть через timedelta
        if days != 0:
            delta += timedelta(days=float(days))
        return delta


def apply_operation(base: Union[datetime, date, time],
                    delta: Union[timedelta, relativedelta],
                    operation: str) -> Union[datetime, date, time]:
    """Применяет операцию сложения/вычитания с учетом типа данных"""
    if operation == '+':
        if isinstance(base, datetime):
            return base + delta
        elif isinstance(base, date):
            # Для даты без времени добавляем дельту
            temp_dt = datetime.combine(base, datetime.min.time())
            result = temp_dt + delta
            # Если результат не содержит времени, возвращаем дату
            if result.time() == datetime.min.time():
                return result.date()
            return result
        else:  # time
            temp_dt = datetime.combine(datetime.min.date(), base)
            result_dt = temp_dt + delta
            return result_dt.time()
    else:  # '-'
        if isinstance(base, datetime):
            return base - delta
        elif isinstance(base, date):
            temp_dt = datetime.combine(base, datetime.min.time())
            result = temp_dt - delta
            if result.time() == datetime.min.time():
                return result.date()
            return result
        else:  # time
            temp_dt = datetime.combine(datetime.min.date(), base)
            result_dt = temp_dt - delta
            return result_dt.time()


def parse_complex_expression(expression: str) -> List[Tuple[str, str]]:
    """Парсит сложное выражение с множеством операций"""
    tokens = []
    current = ''
    i = 0
    n = len(expression)

    while i < n:
        char = expression[i]

        if char in '+-':
            if current:
                # Сохраняем предыдущий токен
                if not tokens:
                    # Первый токен без оператора
                    tokens.append(('+', current.strip()))
                else:
                    # Определяем оператор для предыдущего токена
                    prev_op = tokens[-1][0] if tokens else '+'
                    tokens.append((prev_op, current.strip()))
                current = ''

            # Сохраняем оператор
            op = char
            i += 1
            # Пропускаем пробелы после оператора
            while i < n and expression[i] == ' ':
                i += 1

            # Начинаем собирать следующий токен
            while i < n and expression[i] not in '+-':
                current += expression[i]
                i += 1

            # Сохраняем токен с оператором
            if current:  # Проверяем, что токен не пустой
                tokens.append((op, current.strip()))
            current = ''
        else:
            current += char
            i += 1

    # Обрабатываем оставшийся токен (если это первый)
    if current and not tokens:
        tokens.append(('+', current.strip()))
    elif current:
        # Если есть остаток и уже есть токены, добавляем с последним оператором
        last_op = tokens[-1][0] if tokens else '+'
        tokens.append((last_op, current.strip()))

    return tokens


def parse_interval_string(interval_str: str, base_date: date) -> Tuple[datetime, datetime]:
    """Парсит строку интервала в формате 'начало + продолжительность' или 'начало - конец'"""
    interval_str = normalize_separators(interval_str.strip())

    # Проверяем формат: начало - конец
    if '-' in interval_str:
        parts = interval_str.split('-')
        if len(parts) != 2:
            raise ValueError(f"Неверный формат интервала: {interval_str}")

        start_str = parts[0].strip()
        end_str = parts[1].strip()

        # Парсим время начала
        try:
            start_time = datetime.strptime(start_str, "%H:%M:%S").time()
        except ValueError:
            try:
                start_time = datetime.strptime(start_str, "%H:%M").time()
            except ValueError:
                raise ValueError(f"Неверный формат времени начала: {start_str}")

        # Парсим время окончания
        try:
            end_time = datetime.strptime(end_str, "%H:%M:%S").time()
        except ValueError:
            try:
                end_time = datetime.strptime(end_str, "%H:%M").time()
            except ValueError:
                raise ValueError(f"Неверный формат времени окончания: {end_str}")

        # Создаем datetime объекты
        start_dt = datetime.combine(base_date, start_time)
        end_dt = datetime.combine(base_date, end_time)

        # Если время окончания меньше времени начала, предполагаем, что это следующий день
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)

        return start_dt, end_dt

    # Формат: начало + продолжительность
    elif '+' in interval_str:
        parts = interval_str.split('+')
        if len(parts) != 2:
            raise ValueError(f"Неверный формат интервала: {interval_str}")

        start_str = parts[0].strip()
        duration_str = parts[1].strip()

        # Парсим время начала
        try:
            start_time = datetime.strptime(start_str, "%H:%M:%S").time()
        except ValueError:
            try:
                start_time = datetime.strptime(start_str, "%H:%M").time()
            except ValueError:
                raise ValueError(f"Неверный формат времени: {start_str}")

        start_dt = datetime.combine(base_date, start_time)

        # Парсим продолжительность
        duration = parse_time_delta(duration_str)
        if isinstance(duration, relativedelta):
            # Для интервалов в днях преобразуем в timedelta
            duration = timedelta(days=duration.days)

        # Конец интервала
        end_dt = start_dt + duration

        return start_dt, end_dt

    else:
        raise ValueError(f"Неверный формат интервала: {interval_str}")


def calculate_time_remaining(base_dt: Union[datetime, date], excluded_intervals: List[str]) -> Tuple[
    timedelta, List[Tuple[datetime, datetime]]]:
    """
    Вычисляет оставшееся время в течение дня, исключая заданные интервалы
    excluded_intervals: список строк вида 'HH:MM:SS + Nd/Nh/Nm/Ns' или 'HH:MM:SS - HH:MM:SS'
    """
    # Если передана только дата, преобразуем в datetime
    if isinstance(base_dt, date):
        base_dt = datetime.combine(base_dt, datetime.min.time())

    base_date = base_dt.date()

    # Начало и конец дня
    day_start = datetime.combine(base_date, datetime.min.time())
    day_end = datetime.combine(base_date, datetime.max.time())

    # Парсим интервалы
    intervals = []
    for interval_str in excluded_intervals:
        try:
            start_dt, end_dt = parse_interval_string(interval_str, base_date)

            # Добавляем интервал, если он попадает в текущий день
            if end_dt > day_start and start_dt < day_end:
                intervals.append((max(start_dt, day_start), min(end_dt, day_end)))
        except ValueError as e:
            print(f"Предупреждение: пропускаем интервал '{interval_str}': {e}")
            continue

    # Сортируем интервалы по времени начала
    intervals.sort(key=lambda x: x[0])

    # Объединяем пересекающиеся интервалы
    merged_intervals = []
    for start, end in intervals:
        if not merged_intervals or start > merged_intervals[-1][1]:
            merged_intervals.append([start, end])
        else:
            merged_intervals[-1][1] = max(merged_intervals[-1][1], end)

    # Вычисляем свободное время
    total_excluded = timedelta()
    for start, end in merged_intervals:
        total_excluded += (end - start)

    total_day = timedelta(days=1)
    remaining_time = total_day - total_excluded

    # Формируем список свободных интервалов
    free_intervals = []
    current_time = day_start

    for start, end in merged_intervals:
        if current_time < start:
            free_intervals.append((current_time, start))
        current_time = max(current_time, end)

    if current_time < day_end:
        free_intervals.append((current_time, day_end))

    return remaining_time, free_intervals


def format_timedelta(td: timedelta) -> str:
    """Форматирует timedelta в читаемый вид"""
    total_seconds = int(td.total_seconds())
    days = total_seconds // 86400
    remaining = total_seconds % 86400
    hours = remaining // 3600
    minutes = (remaining % 3600) // 60
    seconds = remaining % 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


def format_time(t: time) -> str:
    """Форматирует время с секундами только если они не нулевые"""
    if t.second == 0:
        return t.strftime("%H:%M")
    return t.strftime("%H:%M:%S")


def format_result(value: Union[datetime, date, time]) -> str:
    """Форматирует результат для вывода"""
    if isinstance(value, datetime):
        time_part = format_time(value.time())
        return f"{value.strftime('%d.%m.%Y')} {time_part}"
    elif isinstance(value, date):
        return value.strftime("%d.%m.%Y")
    else:  # time
        return format_time(value)


def evaluate_expression(tokens: List[Tuple[str, str]]) -> Union[datetime, date, time, timedelta]:
    """Вычисляет значение выражения из списка токенов"""
    if not tokens:
        raise ValueError("Пустое выражение")

    # Первый токен должен быть датой/временем
    first_op, first_value_str = tokens[0]
    if first_op != '+':
        raise ValueError("Первое значение должно быть датой или временем")

    try:
        base_value, is_time_only, is_date_only = parse_datetime_input(first_value_str)
    except ValueError as e:
        raise ValueError(f"Неверный формат первого значения: {first_value_str}")

    # Применяем все последующие операции
    current_value = base_value

    for i in range(1, len(tokens)):
        op, token_value_str = tokens[i]

        # Пробуем разобрать как интервал
        if re.match(r'^[\d,\.]+[dhmsy]$|^[\d,\.]+mon$', token_value_str):
            # Это интервал
            delta = parse_time_delta(token_value_str)
            current_value = apply_operation(current_value, delta, op)
        else:
            # Пробуем разобрать как дату/время
            try:
                other_value, other_is_time, other_is_date = parse_datetime_input(token_value_str)

                if op == '+':
                    # Для сложения с датой/временем нужен интервал
                    raise ValueError(f"Для сложения нужен интервал времени, а не '{token_value_str}'")
                else:  # '-'
                    # Вычитание даты/времени - вычисляем разницу
                    diff = calculate_difference(current_value, other_value)
                    # Возвращаем разницу как timedelta (особый случай)
                    return diff

            except ValueError:
                raise ValueError(f"Неверный формат значения: '{token_value_str}'")

    return current_value


def calculate_difference(left: Union[datetime, date, time], right: Union[datetime, date, time]) -> timedelta:
    """Вычисляет разницу между двумя значениями"""
    if isinstance(left, datetime) and isinstance(right, datetime):
        return left - right
    elif isinstance(left, date) and isinstance(right, date):
        # Для дат без времени
        left_dt = datetime.combine(left, datetime.min.time())
        right_dt = datetime.combine(right, datetime.min.time())
        return left_dt - right_dt
    elif isinstance(left, time) and isinstance(right, time):
        left_dt = datetime.combine(datetime.min.date(), left)
        right_dt = datetime.combine(datetime.min.date(), right)
        return left_dt - right_dt
    elif isinstance(left, datetime) and isinstance(right, date):
        right_dt = datetime.combine(right, datetime.min.time())
        return left - right_dt
    elif isinstance(left, date) and isinstance(right, datetime):
        left_dt = datetime.combine(left, datetime.min.time())
        return left_dt - right
    else:
        raise ValueError("Несовместимые типы данных для вычитания")


def parse_exclusion_expression(expression: str) -> Tuple[str, List[str]]:
    """Парсит выражение с исключением интервалов"""
    expression = expression.strip()

    # Ищем дату/время и список интервалов
    # Формат: дата [интервалы]
    if '[' not in expression or ']' not in expression:
        raise ValueError("Неверный формат выражения с исключением интервалов")

    # Разделяем на дату и список интервалов
    open_bracket = expression.find('[')
    close_bracket = expression.find(']')

    if open_bracket == -1 or close_bracket == -1:
        raise ValueError("Неверный формат выражения с исключением интервалов")

    date_str = expression[:open_bracket].strip()
    intervals_str = expression[open_bracket + 1:close_bracket].strip()

    # Разделяем интервалы по точкам с запятой
    intervals_list = [interval.strip() for interval in intervals_str.split(';') if interval.strip()]

    return date_str, intervals_list


def calculate():
    while True:
        try:
            print("\nВведите выражение или 'q' для выхода:")
            expression = input("> ").strip()

            if expression.lower() == 'q':
                break

            # Обработка операции с исключением интервалов
            if '[' in expression and ']' in expression:
                try:
                    # Парсим выражение с исключением интервалов
                    date_str, intervals_list = parse_exclusion_expression(expression)

                    # Парсим базовую дату/время
                    base_value, is_time_only, is_date_only = parse_datetime_input(date_str)
                    if is_time_only:
                        raise ValueError("Для этой операции нужна полная дата")

                    # Вычисляем оставшееся время
                    remaining, free_intervals = calculate_time_remaining(base_value, intervals_list)

                    print(f"\n{'=' * 40}")
                    print(f"Результат:")
                    print(f"Оставшееся время в течение дня: {format_timedelta(remaining)}")

                    if free_intervals:
                        print("Свободные интервалы:")
                        for start, end in free_intervals:
                            start_str = format_time(start.time())
                            end_str = format_time(end.time())
                            duration = format_timedelta(end - start)
                            print(f"  • {start_str} - {end_str} ({duration})")
                    else:
                        print("Свободных интервалов нет")

                    print(f"{'=' * 40}")
                    continue

                except Exception as e:
                    print(f"\nОшибка при обработке исключения интервалов: {e}")
                    continue

            # Обработка сложных выражений с множеством операций
            if any(op in expression for op in ['+', '-']) and not ('[' in expression and ']' in expression):
                # Сначала разбираем на токены
                tokens_list = parse_complex_expression(expression)

                # Вычисляем результат
                result = evaluate_expression(tokens_list)

                print(f"\n{'=' * 40}")
                if isinstance(result, timedelta):
                    print(f"Результат: {format_timedelta(result)}")
                else:
                    print(f"Результат: {format_result(result)}")
                print(f"{'=' * 40}")
                continue

            # Обработка простых выражений (для обратной совместимости)
            if '+' in expression:
                parts = expression.split('+', 1)
                operator = '+'
            elif '-' in expression:
                parts = expression.split('-', 1)
                operator = '-'
            else:
                print("Неверный формат выражения. Используйте + или -")
                continue

            left_str = parts[0].strip()
            right_str = parts[1].strip()

            # Парсим левый операнд
            left_val, left_is_time_only, left_is_date_only = parse_datetime_input(left_str)

            if operator == '+':
                # Сложение: дата/время + интервал
                try:
                    delta = parse_time_delta(right_str)
                    result = apply_operation(left_val, delta, '+')
                    print(f"\n{'=' * 40}")
                    print(f"Результат: {format_result(result)}")
                    print(f"{'=' * 40}")

                except ValueError:
                    # Правый операнд не интервал - пробуем как дату/время
                    try:
                        right_val, right_is_time_only, right_is_date_only = parse_datetime_input(right_str)
                        print("\nОшибка: для сложения нужен интервал времени")
                    except ValueError:
                        print("\nОшибка: неверный формат интервала")

            elif operator == '-':
                # Вычитание
                try:
                    # Пробуем правый операнд как интервал
                    delta = parse_time_delta(right_str)
                    result = apply_operation(left_val, delta, '-')
                    print(f"\n{'=' * 40}")
                    print(f"Результат: {format_result(result)}")
                    print(f"{'=' * 40}")

                except ValueError:
                    # Правый операнд - дата/время (разница между двумя датами)
                    right_val, right_is_time_only, right_is_date_only = parse_datetime_input(right_str)
                    diff = calculate_difference(left_val, right_val)

                    print(f"\n{'=' * 40}")
                    print(f"Результат: {format_timedelta(diff)}")
                    print(f"{'=' * 40}")

        except ValueError as e:
            print(f"\nОшибка: {e}")
        except Exception as e:
            print(f"\nНеожиданная ошибка: {type(e).__name__}: {e}")


if __name__ == "__main__":
    calculate()