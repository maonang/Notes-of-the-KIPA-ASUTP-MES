"""
Модуль для преобразования Excel-файлов в структурированный JSON-словарь.
Обрабатывает повторяющиеся ID, заполняя поля только если они были пустыми.
Автоматически распаковывает JSON-строки в поле Configuration.
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd


class ExcelToJsonConverter:
    """Конвертер Excel файлов в JSON словарь с агрегацией по ID."""

    def __init__(
            self,
            sheet_name: str = 'Models',
            id_column: str = 'Id',
            ignore_columns: Optional[List[str]] = None,
            unpack_json_fields: Optional[List[str]] = None,
            filter_criteria: Optional[Dict[str, List[Any]]] = None,
            exclude_fields: Optional[List[str]] = None
    ):
        """
        Инициализация конвертера.

        Args:
            sheet_name: Название листа в Excel файле
            id_column: Название столбца с идентификаторами
            ignore_columns: Список столбцов для игнорирования
            unpack_json_fields: Список полей, содержащих JSON-строки для распаковки
        """
        self.sheet_name = sheet_name
        self.id_column = id_column
        self.ignore_columns = ignore_columns or []
        self.unpack_json_fields = unpack_json_fields or []
        self.filter_criteria = filter_criteria or {}
        self.exclude_fields = exclude_fields or []

    def read_excel_file(self, file_path: str) -> pd.DataFrame:
        """
        Читает Excel файл и возвращает DataFrame.

        Args:
            file_path: Путь к Excel файлу

        Returns:
            DataFrame с данными

        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если указанный лист не существует
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Файл '{file_path}' не найден")

        try:
            df = pd.read_excel(file_path, sheet_name=self.sheet_name)
        except ValueError as e:
            raise ValueError(
                f"Лист '{self.sheet_name}' не найден в файле. "
                f"Доступные листы: {pd.ExcelFile(file_path).sheet_names}"
            ) from e

        return df

    def validate_columns(self, df: pd.DataFrame) -> None:
        """
        Проверяет наличие обязательных столбцов в DataFrame.

        Args:
            df: DataFrame для проверки

        Raises:
            ValueError: Если обязательный столбец отсутствует
        """
        if self.id_column not in df.columns:
            raise ValueError(
                f"Столбец '{self.id_column}' не найден. "
                f"Доступные столбцы: {list(df.columns)}"
            )

    def drop_ignored_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Удаляет игнорируемые столбцы из DataFrame.

        Args:
            df: Исходный DataFrame

        Returns:
            DataFrame без игнорируемых столбцов
        """
        columns_to_drop = [
            col for col in self.ignore_columns if col in df.columns
        ]

        if columns_to_drop:
            df = df.drop(columns=columns_to_drop)

        return df

    def apply_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Применяет фильтр к DataFrame, исключая строки с указанными значениями.

        Args:
            df: Исходный DataFrame

        Returns:
            Отфильтрованный DataFrame
        """
        if not self.filter_criteria:
            return df

        filtered_df = df.copy()
        for column, exclude_values in self.filter_criteria.items():
            if column in filtered_df.columns:
                # Исключаем строки, где значение столбца входит в exclude_values
                filtered_df = filtered_df[~filtered_df[column].isin(exclude_values)]

        removed_count = len(df) - len(filtered_df)
        if removed_count > 0:
            print(f"Применен фильтр: исключено {removed_count} строк")
            print(f"  Критерии: {self.filter_criteria}")

        return filtered_df

    @staticmethod
    def normalize_value(value: Any) -> Optional[str]:
        """
        Нормализует значение в строку для JSON-сериализации.

        Args:
            value: Исходное значение

        Returns:
            Строковое значение или None
        """
        if pd.isna(value):
            return None
        # Все значения преобразуем в строки
        return str(value)

    @staticmethod
    def normalize_key(key: Any) -> str:
        """
        Нормализует ключ для использования в JSON.

        Args:
            key: Исходный ключ

        Returns:
            Ключ в виде строки
        """
        return str(key)

    @staticmethod
    def unpack_json_string(value: Optional[str]) -> Any:
        """
        Распаковывает JSON-строку в объект Python.

        Args:
            value: JSON-строка или None

        Returns:
            Распакованный объект или исходное значение
        """
        if value is None:
            return None

        try:
            # Пробуем распарсить JSON
            parsed = json.loads(value)
            return parsed
        except (json.JSONDecodeError, TypeError):
            # Если не JSON, возвращаем исходное значение
            return value

    def process_row_value(self, field_name: str, value: Optional[str]) -> Any:
        """
        Обрабатывает значение поля, распаковывая JSON если необходимо.

        Args:
            field_name: Название поля
            value: Значение поля

        Returns:
            Обработанное значение
        """
        if value is None:
            return None

        # Распаковываем JSON для указанных полей
        if field_name in self.unpack_json_fields:
            return self.unpack_json_string(value)

        return value

    def aggregate_data(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Агрегирует данные по ID.
        При повторении ID заполняет только пустые поля.

        Args:
            df: DataFrame с данными

        Returns:
            Словарь с агрегированными данными
        """
        # Словарь для хранения результата
        result_dict: Dict[str, Dict[str, Any]] = {}

        # Проходим по каждой строке DataFrame
        for _, row in df.iterrows():
            root_key = self.normalize_key(row[self.id_column])

            # Если ID еще нет в результате, создаем пустой словарь
            if root_key not in result_dict:
                result_dict[root_key] = {}

            # Проходим по всем полям строки
            for col in df.columns:
                if col != self.id_column:
                    # Пропускаем исключаемые поля
                    if col in self.exclude_fields:
                        continue

                    raw_value = self.normalize_value(row[col])
                    # Обрабатываем значение (распаковываем JSON если нужно)
                    value = self.process_row_value(col, raw_value)

                    # Получаем текущее значение поля для этого ID
                    current_value = result_dict[root_key].get(col)

                    # Заполняем поле только если:
                    # 1. Поле еще не установлено (None или отсутствует)
                    # 2. И новое значение не пустое (не None)
                    if (current_value is None and value is not None):
                        result_dict[root_key][col] = value

        return result_dict

    def convert(self, file_path: str) -> Dict[str, Dict[str, Any]]:
        """
        Основной метод конвертации Excel файла в словарь.

        Args:
            file_path: Путь к Excel файлу

        Returns:
            Словарь с данными
        """
        # Чтение и подготовка данных
        df = self.read_excel_file(file_path)
        self.validate_columns(df)
        df = self.drop_ignored_columns(df)
        df = self.apply_filter(df)

        # Агрегация данных
        result = self.aggregate_data(df)

        return result


class DataEnricher:
    """Класс для добавления дополнительных полей из связанных свойств."""

    @staticmethod
    def enrich_data(data_dict: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Добавляет данные с информацией о связанных свойствах.

        Args:
            data_dict: Исходный словарь с данными

        Returns:
            Обогащенный словарь
        """
        # Создаем карту для быстрого поиска по Path и по ID
        path_to_data = {}
        id_to_path = {}

        for record_id, record_data in data_dict.items():
            if 'Path' in record_data and record_data['Path']:
                path_to_data[record_data['Path']] = {
                    'id': record_id,
                    'data': record_data
                }
                id_to_path[record_id] = record_data['Path']

        # Дополняем каждую запись
        for record_id, record_data in data_dict.items():
            # Пропускаем, если нет Configuration
            if 'Configuration' not in record_data or not record_data['Configuration']:
                continue

            config = record_data['Configuration']

            # Проверяем DataReference текущего свойства
            current_data_reference = record_data.get('DataReference')

            # Добавляем новые параметры ТОЛЬКО для Calculation Tag
            if current_data_reference == 'Calculation Tag':
                # 1. Заполняем tagId если он пустой
                if 'tagId' in config:
                    if not config['tagId'] or config['tagId'] == '':
                        config['tagId'] = f"SysTag_{record_id}"
                        print(f"  Для ID {record_id} сгенерирован tagId: {config['tagId']}")

                # Добавляем par_tag из tagId для текущего свойства (на верхний уровень)
                record_data['par_tag'] = config.get('tagId', '')

                # Добавляем param_expression из expression (с обрезанием при длине > 2000)
                if 'expression' in config:
                    expression = config['expression']
                    if expression and len(expression) > 2000:
                        record_data['param_expression'] = expression[:2000] + "..."
                        print(f"  Для ID {record_id} выражение обрезано (было {len(expression)} символов)")
                    else:
                        record_data['param_expression'] = expression
                else:
                    record_data['param_expression'] = ''

                # Добавляем информацию о периоде расчета для текущего свойства
                if 'triggerType' in config:
                    record_data['par_calc_type'] = config['triggerType']
                else:
                    record_data['par_calc_type'] = ''

                if 'offsetInSeconds' in config:
                    record_data['par_calc_offset'] = config['offsetInSeconds']
                else:
                    record_data['par_calc_offset'] = None

                if 'periodInSeconds' in config:
                    record_data['par_calc_period'] = config['periodInSeconds']
                else:
                    record_data['par_calc_period'] = None

                # Обрабатываем variables для Calculation Tag
                if 'variables' in config:
                    enriched_variables = []

                    for var in config['variables']:
                        enriched_var = var.copy()

                        # Ищем связанное свойство по value (пути)
                        value_path = var.get('value')
                        if value_path and value_path in path_to_data:
                            linked_data = path_to_data[value_path]['data']
                            linked_id = path_to_data[value_path]['id']
                            linked_config = linked_data.get('Configuration', {})

                            # Добавляем par_type - берем DataReference связанного свойства
                            linked_data_reference = linked_data.get('DataReference')
                            if linked_data_reference:
                                enriched_var['par_type'] = linked_data_reference
                            else:
                                enriched_var['par_type'] = 'Unknown'

                            # Добавляем par_tag
                            if linked_data_reference == 'Calculation Tag':
                                # Для расчетных свойств берем tagId или генерируем из ID
                                if 'tagId' in linked_config and linked_config['tagId']:
                                    enriched_var['par_tag'] = linked_config['tagId']
                                else:
                                    # Генерируем SysTag_ + ID
                                    enriched_var['par_tag'] = f"SysTag_{linked_id}"
                            elif linked_data_reference == 'Constant':
                                # Для констант par_tag пустой
                                enriched_var['par_tag'] = ''
                            else:
                                # Для Tag и других типов также генерируем SysTag_ + ID если нет tagId
                                if 'tagId' in linked_config and linked_config['tagId']:
                                    enriched_var['par_tag'] = linked_config['tagId']
                                else:
                                    enriched_var['par_tag'] = f"SysTag_{linked_id}"

                            # Добавляем par_const - берем const из Configuration связанного свойства
                            if linked_data_reference == 'Constant' and 'const' in linked_config:
                                enriched_var['par_const'] = linked_config['const']
                            else:
                                enriched_var['par_const'] = ''

                            # Добавляем par_calc_type - берем triggerType связанного свойства
                            if 'triggerType' in linked_config:
                                enriched_var['par_calc_type'] = linked_config['triggerType']
                            else:
                                enriched_var['par_calc_type'] = ''

                            # Добавляем par_calc_offset - берем offsetInSeconds связанного свойства
                            if 'offsetInSeconds' in linked_config:
                                enriched_var['par_calc_offset'] = linked_config['offsetInSeconds']
                            else:
                                enriched_var['par_calc_offset'] = None

                            # Добавляем par_calc_period - берем periodInSeconds связанного свойства
                            if 'periodInSeconds' in linked_config:
                                enriched_var['par_calc_period'] = linked_config['periodInSeconds']
                            else:
                                enriched_var['par_calc_period'] = None

                            # Добавляем param_expression для связанных расчетных свойств
                            if linked_data_reference == 'Calculation Tag' and 'expression' in linked_config:
                                linked_expression = linked_config['expression']
                                if linked_expression and len(linked_expression) > 2000:
                                    enriched_var['param_expression'] = linked_expression[:2000] + "..."
                                else:
                                    enriched_var['param_expression'] = linked_expression
                            else:
                                enriched_var['param_expression'] = ''
                        else:
                            # Если связанное свойство не найдено, заполняем пустыми значениями
                            enriched_var['par_type'] = 'Not Found'
                            enriched_var['par_tag'] = ''
                            enriched_var['par_const'] = ''
                            enriched_var['par_calc_type'] = ''
                            enriched_var['par_calc_offset'] = None
                            enriched_var['par_calc_period'] = None
                            enriched_var['param_expression'] = ''

                        enriched_variables.append(enriched_var)

                    # Заменяем variables на обогащенные
                    config['variables'] = enriched_variables

        return data_dict


class DataAnalyzer:
    """Класс для анализа структуры данных."""

    @staticmethod
    def analyze(data_dict: Dict[str, Dict[str, Any]]) -> None:
        """
        Анализирует структуру полученных данных.

        Args:
            data_dict: Словарь с данными для анализа
        """
        if not data_dict:
            print("Нет данных для анализа")
            return

        print(f"\n{'=' * 60}")
        print("АНАЛИЗ СТРУКТУРЫ ДАННЫХ")
        print(f"{'=' * 60}")
        print(f"Всего уникальных ID: {len(data_dict): }")

        # Статистика по полям
        all_fields = set()
        filled_count = defaultdict(int)

        for record in data_dict.values():
            for field, value in record.items():
                all_fields.add(field)
                if value is not None:
                    filled_count[field] += 1

        print(f"Всего полей (без учета id): {len(all_fields)}")

        if all_fields:
            print(f"\nСписок всех полей: {sorted(all_fields)}")

        # Статистика заполненности полей
        print(f"\nСтатистика заполненности полей:")
        for field in sorted(all_fields):
            filled = filled_count[field]
            total = len(data_dict)
            percentage = (filled / total * 100) if total > 0 else 0
            print(f"  {field}: {filled}/{total} ({percentage:.1f}%)")



class JsonSaver:
    """Класс для сохранения данных в JSON файл."""

    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """
        Инициализация сохранятеля JSON.

        Args:
            output_dir: Директория для сохранения файлов
        """
        if output_dir is None:
            # Если директория не указана, используем директорию скрипта
            if '__file__' in globals():
                self.output_dir = Path(__file__).parent
            else:
                self.output_dir = Path.cwd()
        else:
            self.output_dir = Path(output_dir)

        # Создаем директорию, если её нет
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _json_serializer(obj: Any) -> Any:
        """
        Сериализатор для специальных типов данных.

        Args:
            obj: Объект для сериализации

        Returns:
            Сериализованное значение
        """
        if pd.isna(obj):
            return None
        if isinstance(obj, (pd.Timestamp, pd.Timedelta)):
            return str(obj)
        if isinstance(obj, (set, tuple)):
            return list(obj)
        if hasattr(obj, '__dict__'):
            return str(obj)
        return obj

    def save(
            self,
            data: Dict[str, Any],
            filename: Optional[str] = None,
            input_file: Optional[str] = None
    ) -> Path:
        """
        Сохраняет словарь в JSON файл.

        Args:
            data: Словарь для сохранения
            filename: Имя выходного файла
            input_file: Исходный файл (для генерации имени)

        Returns:
            Путь к сохраненному файлу
        """
        if filename is None and input_file is not None:
            # Генерируем имя на основе входного файла
            input_path = Path(input_file)
            filename = f"{input_path.stem}.json"
        elif filename is None:
            filename = "output_data.json"

        output_path = self.output_dir / filename

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    data, f,
                    ensure_ascii=False,
                    indent=2,
                    default=self._json_serializer
                )

            file_size = output_path.stat().st_size
            print(f"\nJSON файл успешно сохранен: {output_path}")
            print(f"  Размер файла: {file_size: } байт")

            return output_path

        except Exception as e:
            print(f"\nОшибка при сохранении JSON: {e}")
            raise


def process_excel_to_json(
        input_file: str,
        output_file: Optional[str] = None,
        sheet_name: str = 'Models',
        id_column: str = 'Id',
        ignore_columns: Optional[List[str]] = None,
        unpack_json_fields: Optional[List[str]] = None,
        filter_criteria: Optional[Dict[str, List[Any]]] = None,
        exclude_fields: Optional[List[str]] = None,
        show_analysis: bool = True,
        enable_enrichment: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Упрощенная функция для конвертации Excel в JSON.

    Args:
        input_file: Путь к входному Excel файлу
        output_file: Путь к выходному JSON файлу (опционально)
        sheet_name: Название листа
        id_column: Название столбца с ID
        ignore_columns: Список столбцов для игнорирования
        unpack_json_fields: Список полей для распаковки JSON
        show_analysis: Показывать анализ данных

    Returns:
        Словарь с обработанными данными
    """
    # Конвертация данных
    converter = ExcelToJsonConverter(
        sheet_name=sheet_name,
        id_column=id_column,
        ignore_columns=ignore_columns,
        unpack_json_fields=unpack_json_fields,
        filter_criteria=filter_criteria,
        exclude_fields = exclude_fields
    )

    print(f"Чтение файла: {input_file}")
    print(f"Лист: {sheet_name}")
    if unpack_json_fields:
        print(f"Распаковка JSON в полях: {unpack_json_fields}")

    data = converter.convert(input_file)

    # Добавление новых параметров
    if enable_enrichment:
        print("\nДобавление данных связями...")
        data = DataEnricher.enrich_data(data)
        print("Готово.")

    # Анализ данных
    if show_analysis:
        DataAnalyzer.analyze(data)

    # Сохранение в JSON
    saver = JsonSaver()
    if output_file:
        # Если указан полный путь, используем его директорию
        output_path = Path(output_file)
        saver.output_dir = output_path.parent
        saver.save(data, output_path.name)
    else:
        saver.save(data, input_file=input_file)

    return data


def main() -> Optional[Dict[str, Dict[str, Any]]]:
    """Основная функция для запуска из командной строки."""

    # Конфигурация
    INPUT_FILE = "Файл экспорта 22_04_2026.xlsx"
    SHEET_NAME = "Models"
    ID_COLUMN = "Id"
    IGNORE_COLUMNS = ["Delete"]
    UNPACK_JSON_FIELDS = ["Configuration"]  # Поля, содержащие JSON-строки
    FILTER_CRITERIA = {
        "Type": ["Model", "Object", "ObjectHashTag"]  # Исключаем эти значения
    }
    EXCLUDE_FIELDS = [
        "DataTypePath", "PropertyType", "UomPath", "PropertyPrimitivePath", "Type"] # Эти поля не попадут в JSON
    ENABLE_ENRICHMENT = True  # Включить дополнение данными

    try:
        # Обработка данных
        result = process_excel_to_json(
            input_file=INPUT_FILE,
            sheet_name=SHEET_NAME,
            id_column=ID_COLUMN,
            ignore_columns=IGNORE_COLUMNS,
            unpack_json_fields=UNPACK_JSON_FIELDS,
            filter_criteria=FILTER_CRITERIA,
            exclude_fields=EXCLUDE_FIELDS,
            show_analysis=True,
            enable_enrichment = ENABLE_ENRICHMENT
        )

        print(f"\n{'=' * 60}")
        print("Готово.")
        print(f"{'=' * 60}")
        print(f"Всего обработано записей: {len(result): }")

    except FileNotFoundError as e:
        print(f"\nОшибка: {e}")
        print(f"Текущая директория: {Path.cwd()}")
        return None

    except Exception as e:
        print(f"\nОшибка при обработке: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()