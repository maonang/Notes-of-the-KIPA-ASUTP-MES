import pandas as pd
import numpy as np
import os
from typing import Tuple, Dict, List
from decimal import Decimal, getcontext

# Устанавливаем высокую точность для Decimal
getcontext().prec = 50


def find_excel_file() -> str:
    """
    Автоматически находит файл Excel в текущем каталоге.

    Returns:
        str: Имя найденного файла Excel

    Raises:
        FileNotFoundError: Если файл Excel не найден
    """
    # Получаем список всех файлов в текущем каталоге
    files = os.listdir('.')
    # Ищем файлы с расширением .xlsx
    excel_files = [f for f in files if f.endswith('.xlsx')]

    if not excel_files:
        raise FileNotFoundError("Файл таблицы в формате *.xlsx не найден в текущем каталоге")

    # Берем первый найденный файл Excel
    excel_file = excel_files[0]
    return excel_file


def select_columns(df: pd.DataFrame) -> Tuple[str, str]:
    """
    Предлагает пользователю выбрать колонки для уровня и объема.

    Args:
        df: DataFrame с данными

    Returns:
        Tuple[str, str]: Имена выбранных колонок для уровня и объема
    """
    print("\nДоступные колонки в файле:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i}. {col}")

    print("\nПожалуйста, укажите какие колонки использовать:")

    # Запрашиваем выбор колонки для уровня
    while True:
        try:
            level_choice = int(input("Введите номер колонки для 'Уровень' (в мм): "))
            if 1 <= level_choice <= len(df.columns):
                level_column = df.columns[level_choice - 1]
                break
            else:
                print(f"Неверный номер. Введите число от 1 до {len(df.columns)}.")
        except ValueError:
            print("Введите целое число.")

    # Запрашиваем выбор колонки для объема
    while True:
        try:
            volume_choice = int(input("Введите номер колонки для 'Объем' (в литрах): "))
            if 1 <= volume_choice <= len(df.columns):
                volume_column = df.columns[volume_choice - 1]
                break
            else:
                print(f"Неверный номер. Введите число от 1 до {len(df.columns)}.")
        except ValueError:
            print("Введите целое число.")

    print(f"\nВыбраны колонки:")
    print(f"Уровень: '{level_column}'")
    print(f"Объем: '{volume_column}'")

    return level_column, volume_column


def calculate_level_step(df: pd.DataFrame, level_col: str) -> float:
    """
    Автоматически определяет шаг уровня из данных.

    Args:
        df: DataFrame с данными
        level_col: Колонка с уровнями

    Returns:
        float: Определенный шаг уровня
    """
    # Сортируем данные по уровню и убираем пустые значения
    df_sorted = df.dropna(subset=[level_col]).sort_values(level_col)
    levels = df_sorted[level_col].values

    if len(levels) < 2:
        raise ValueError("Недостаточно данных для определения шага уровня")

    # Вычисляем разницы между соседними уровнями
    level_diffs = np.diff(levels)

    # Находим наиболее часто встречающуюся разницу (шаг)
    unique_diffs, counts = np.unique(level_diffs, return_counts=True)
    most_common_step = unique_diffs[np.argmax(counts)]

    # Проверяем, что шаг стабилен (более 80% записей имеют этот шаг)
    step_ratio = (level_diffs == most_common_step).mean()

    if step_ratio > 0.8:
        return most_common_step
    else:
        # Если шаг нестабилен, используем среднее значение
        avg_step = np.mean(level_diffs)
        return avg_step


def calculate_base_coefficient_robust(df: pd.DataFrame, level_col: str, volume_col: str, level_step: float) -> float:
    """
    Улучшенный метод вычисления базового коэффициента, устойчивый к шуму.
    """
    # Сортируем данные по уровню
    df_sorted = df.sort_values(level_col).dropna(subset=[level_col, volume_col])

    # Нормализуем уровни с использованием level_step
    X = df_sorted[level_col].values.reshape(-1, 1) / level_step
    y = df_sorted[volume_col].values

    # Метод 1: Линейная регрессия через наименьшие квадраты
    coeff_lr = (X.T @ y) / (X.T @ X)
    coeff_lr = coeff_lr[0, 0]

    # Метод 2: Анализ разностей с правильной нормализацией
    volume_diffs = df_sorted[volume_col].diff().dropna()
    level_diffs_actual = df_sorted[level_col].diff().dropna()

    # Правильная нормализация - учитываем level_step
    normalized_diffs = volume_diffs / (level_diffs_actual / level_step)

    # Фильтрация выбросов с использованием межквартильного размаха (более устойчивый метод)
    Q1 = normalized_diffs.quantile(0.25)
    Q3 = normalized_diffs.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    filtered_diffs = normalized_diffs[
        (normalized_diffs >= lower_bound) &
        (normalized_diffs <= upper_bound)
        ]

    if len(filtered_diffs) > len(normalized_diffs) * 0.5:  # Если осталось больше 50% данных
        coeff_median = filtered_diffs.median()
    else:
        coeff_median = normalized_diffs.median()

    # Сравниваем два методы - они должны быть близки
    discrepancy = abs(coeff_lr - coeff_median) / min(coeff_lr, coeff_median)

    if discrepancy > 0.1:  # Если расхождение больше 10%
        # Используем медиану, так как она более устойчива к выбросам
        return coeff_median
    else:
        # Используем среднее взвешенное
        final_coeff = 0.5 * coeff_lr + 0.5 * coeff_median
        return final_coeff


def optimize_coefficient_high_precision(data_dict: Dict[float, List[float]], base_coeff: float,
                                        n_len: int, level_step: float) -> Tuple[float, float]:
    """
    Оптимизирует коэффициент для заданной точности с высокой точностью.
    """
    # Используем Decimal для высокоточной арифметики
    base_coeff_dec = Decimal(str(base_coeff))
    level_step_dec = Decimal(str(level_step))

    # Динамический диапазон перебора в зависимости от точности
    if n_len <= 5:
        range_size = 20  # ±10 шагов для низкой точности
    elif n_len <= 10:
        range_size = 15  # ±7 шагов для средней точности
    elif n_len <= 15:
        range_size = 10  # ±5 шагов для высокой точности
    else:
        range_size = 8  # ±4 шага для сверхвысокой точности

    step = Decimal('10') ** Decimal(f'-{n_len}')
    coefficients = [float(base_coeff_dec + i * step) for i in range(-range_size // 2, range_size // 2 + 1)]

    best_coeff = base_coeff
    best_total_diff = float('inf')

    for coeff in coefficients:
        total_diff = 0
        max_single_diff = 0

        for level, (true_volume, _, _, _) in data_dict.items():
            # Используем Decimal для высокоточных вычислений
            level_dec = Decimal(str(level))
            coeff_dec = Decimal(str(coeff))
            true_volume_dec = Decimal(str(true_volume))

            calculated_volume = (level_dec / level_step_dec) * coeff_dec
            diff = abs(true_volume_dec - calculated_volume)
            total_diff += float(diff)
            max_single_diff = max(max_single_diff, float(diff))

        # Учитываем не только сумму, но и максимальное отклонение
        weighted_diff = total_diff + max_single_diff * 0.1

        if weighted_diff < best_total_diff:
            best_total_diff = weighted_diff
            best_coeff = coeff

    return best_coeff, best_total_diff


def main():
    """Основная функция программы."""
    try:
        print("=" * 60)
        print("АНАЛИЗ ГРАДУИРОВОЧНОЙ ТАБЛИЦЫ")
        print("=" * 60)

        # 1. Автоматически находим файл Excel
        excel_file = find_excel_file()
        print(f"Найден файл: {excel_file}")

        # 2. Загружаем данные с первого листа
        data = pd.read_excel(excel_file, sheet_name=0)
        print(f"Загружено строк: {len(data)}")

        # 3. Предлагаем пользователю выбрать колонки
        level_col, volume_col = select_columns(data)

        # 4. Автоматически определяем шаг уровня
        level_step = calculate_level_step(data, level_col)
        print(f"Определен шаг уровня: {level_step} мм")

        # 5. Создаем основной словарь данных
        data_dict = {
            level: [volume, None, None, None]  # [реальный объем, расчетный объем, коэффициент, отклонение]
            for level, volume in zip(data[level_col], data[volume_col])
            if pd.notna(level) and pd.notna(volume)
        }

        print(f"Обработано записей: {len(data_dict)}")

        # 6. Вычисляем базовый коэффициент улучшенным методом
        print("\nВычисление коэффициента...")
        base_coeff = calculate_base_coefficient_robust(data, level_col, volume_col, level_step)

        # 7. Постепенно увеличиваем точность коэффициента до 20 знаков
        current_coeff = base_coeff
        previous_total_diff = float('inf')

        print("Оптимизация точности...")
        for n_len in range(1, 21):  # n_len от 1 до 20
            current_coeff, total_diff = optimize_coefficient_high_precision(data_dict, current_coeff, n_len, level_step)

            if total_diff < previous_total_diff or n_len == 1:
                # Обновляем данные в словаре
                for level in data_dict:
                    true_volume = data_dict[level][0]
                    calculated_volume = (level / level_step) * current_coeff
                    diff = true_volume - calculated_volume

                    data_dict[level][1] = calculated_volume
                    data_dict[level][2] = current_coeff
                    data_dict[level][3] = diff

        # 8. Выводим результат
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ РАСЧЕТА")
        print("=" * 60)
        print(f"[15 знаков]: {current_coeff:.15f}")
        print(f"[20 знаков]: {current_coeff:.20f}")

    except Exception as e:
        print(f"\nОшибка выполнения программы: {str(e)}")
        raise


if __name__ == "__main__":
    main()