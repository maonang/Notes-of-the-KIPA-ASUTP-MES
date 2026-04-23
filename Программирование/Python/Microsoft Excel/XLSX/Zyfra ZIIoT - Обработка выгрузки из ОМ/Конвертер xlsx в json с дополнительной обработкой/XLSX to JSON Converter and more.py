import json
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

import pandas as pd

# Отключение предупреждений openpyxl
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')


class DataSorter:
    """Класс для сортировки данных."""

    @staticmethod
    def sort_by_path(data_dict: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Сортирует корневые элементы словаря по параметру Path.

        Args:
            data_dict: Исходный словарь с данными

        Returns:
            Отсортированный словарь
        """
        # Создаем список кортежей (path, id, data)
        items_with_path = []
        items_without_path = []

        for record_id, record_data in data_dict.items():
            path = record_data.get('Path', '')
            if path:
                items_with_path.append((path, record_id, record_data))
            else:
                items_without_path.append((record_id, record_data))

        # Сортируем по Path (лексикографически)
        items_with_path.sort(key=lambda x: x[0])

        # Собираем отсортированный словарь
        sorted_dict = {}

        # Сначала добавляем элементы с Path (отсортированные)
        for path, record_id, record_data in items_with_path:
            sorted_dict[record_id] = record_data

        # Затем добавляем элементы без Path (в исходном порядке)
        for record_id, record_data in items_without_path:
            sorted_dict[record_id] = record_data

        return sorted_dict


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
    ) -> None:
        """
        Инициализация конвертера.

        Args:
            sheet_name: Название листа в Excel файле
            id_column: Название столбца с идентификаторами
            ignore_columns: Список столбцов для игнорирования
            unpack_json_fields: Список полей, содержащих JSON-строки для распаковки
            filter_criteria: Словарь критериев для исключения строк
            exclude_fields: Список полей для исключения из результата
        """
        self.sheet_name: str = sheet_name
        self.id_column: str = id_column
        self.ignore_columns: List[str] = ignore_columns or []
        self.unpack_json_fields: List[str] = unpack_json_fields or []
        self.filter_criteria: Dict[str, List[Any]] = filter_criteria or {}
        self.exclude_fields: List[str] = exclude_fields or []

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
            df: pd.DataFrame = pd.read_excel(file_path, sheet_name=self.sheet_name)
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
        columns_to_drop: List[str] = [
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

        filtered_df: pd.DataFrame = df.copy()
        for column, exclude_values in self.filter_criteria.items():
            if column in filtered_df.columns:
                filtered_df = filtered_df[~filtered_df[column].isin(exclude_values)]

        removed_count: int = len(df) - len(filtered_df)
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
            parsed: Any = json.loads(value)
            return parsed
        except (json.JSONDecodeError, TypeError):
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
        result_dict: Dict[str, Dict[str, Any]] = {}

        for _, row in df.iterrows():
            root_key: str = self.normalize_key(row[self.id_column])

            if root_key not in result_dict:
                result_dict[root_key] = {}

            for col in df.columns:
                if col != self.id_column:
                    if col in self.exclude_fields:
                        continue

                    raw_value: Optional[str] = self.normalize_value(row[col])
                    value: Any = self.process_row_value(col, raw_value)
                    current_value: Any = result_dict[root_key].get(col)

                    if current_value is None and value is not None:
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
        df: pd.DataFrame = self.read_excel_file(file_path)
        self.validate_columns(df)
        df = self.drop_ignored_columns(df)
        df = self.apply_filter(df)

        result: Dict[str, Dict[str, Any]] = self.aggregate_data(df)

        return result


class DataEnricher:
    """Класс для добавления вычисляемых полей из связанных свойств."""

    @staticmethod
    def build_usage_map(data_dict: Dict[str, Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Строит карту использования свойств в расчетах.

        Args:
            data_dict: Словарь с данными

        Returns:
            Словарь вида {path: [список использований]}
        """
        usage_map: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for record_id, record_data in data_dict.items():
            # Проверяем, является ли свойство расчетным
            if record_data.get('DataReference') != 'Calculation Tag':
                continue

            config = record_data.get('Configuration', {})
            if 'variables' not in config:
                continue

            # Получаем путь текущего расчетного свойства
            current_path = record_data.get('Path', '')
            if not current_path:
                continue

            # Получаем tagId текущего расчетного свойства
            current_tag_id = config.get('tagId', '')
            if not current_tag_id or current_tag_id == '':
                current_tag_id = f"SysTag_{record_id}"

            # Получаем expression для текущего расчета
            expression = config.get('expression', '')
            truncated_expression = expression[:2000] + "..." if expression and len(expression) > 2000 else expression

            # Проходим по всем переменным расчета
            for var in config['variables']:
                value_path = var.get('value')
                alias = var.get('alias', '')

                if value_path:
                    usage_map[value_path].append({
                        'param_property_path': current_path,
                        'param_property_tagId': current_tag_id,
                        'param_expression_alias': alias,
                        'param_expression': truncated_expression or ''
                    })

        return usage_map

    @staticmethod
    def enrich_data(data_dict: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Добавляет вычисляемые поля с информацией о связанных свойствах.

        Args:
            data_dict: Исходный словарь с данными

        Returns:
            Словарь с добавленными вычисляемыми полями
        """
        # Создание карты для быстрого поиска по Path
        path_to_data: Dict[str, Dict[str, Any]] = {}

        for record_id, record_data in data_dict.items():
            if 'Path' in record_data and record_data['Path']:
                path_to_data[record_data['Path']] = {
                    'id': record_id,
                    'data': record_data
                }

        usage_map = DataEnricher.build_usage_map(data_dict)

        # Добавление вычисляемых полей для каждой записи
        for record_id, record_data in data_dict.items():
            # Добавляем param_used для всех свойств, которые используются в расчетах
            current_path = record_data.get('Path', '')
            if current_path and current_path in usage_map:
                record_data['param_used'] = usage_map[current_path]
            else:
                record_data['param_used'] = []  # Пустой список, если не используется другими свойствами

            if 'Configuration' not in record_data or not record_data['Configuration']:
                continue

            config: Dict[str, Any] = record_data['Configuration']
            current_data_reference: Optional[str] = record_data.get('DataReference')

            # Добавление полей только для Calculation Tag
            if current_data_reference == 'Calculation Tag':
                # Генерация tagId при отсутствии (только в Configuration)
                if 'tagId' in config:
                    if not config['tagId'] or config['tagId'] == '':
                        config['tagId'] = f"SysTag_{record_id}"

                # Обработка variables для Calculation Tag
                if 'variables' in config:
                    enriched_variables: List[Dict[str, Any]] = []

                    for var in config['variables']:
                        enriched_var: Dict[str, Any] = var.copy()
                        value_path: Optional[str] = var.get('value')

                        if value_path and value_path in path_to_data:
                            linked_data: Dict[str, Any] = path_to_data[value_path]['data']
                            linked_id: str = path_to_data[value_path]['id']
                            linked_config: Dict[str, Any] = linked_data.get('Configuration', {})
                            linked_data_reference: Optional[str] = linked_data.get('DataReference')

                            # Добавление par_type
                            enriched_var['par_type'] = linked_data_reference if linked_data_reference else 'Unknown'

                            # Добавление par_tag
                            if linked_data_reference == 'Calculation Tag':
                                if 'tagId' in linked_config and linked_config['tagId']:
                                    enriched_var['par_tag'] = linked_config['tagId']
                                else:
                                    enriched_var['par_tag'] = f"SysTag_{linked_id}"
                            elif linked_data_reference == 'Constant':
                                enriched_var['par_tag'] = ''
                            else:
                                if 'tagId' in linked_config and linked_config['tagId']:
                                    enriched_var['par_tag'] = linked_config['tagId']
                                else:
                                    enriched_var['par_tag'] = f"SysTag_{linked_id}"

                            # Добавление par_const
                            if linked_data_reference == 'Constant' and 'const' in linked_config:
                                enriched_var['par_const'] = linked_config['const']
                            else:
                                enriched_var['par_const'] = ''

                            # Добавление параметров расчёта связанного свойства
                            enriched_var['par_calc_type'] = linked_config.get('triggerType', '')
                            enriched_var['par_calc_offset'] = linked_config.get('offsetInSeconds', None)
                            enriched_var['par_calc_period'] = linked_config.get('periodInSeconds', None)

                            # Добавление param_expression для связанных расчётных свойств
                            if linked_data_reference == 'Calculation Tag' and 'expression' in linked_config:
                                linked_expression: Optional[str] = linked_config['expression']
                                if linked_expression and len(linked_expression) > 2000:
                                    enriched_var['param_expression'] = linked_expression[:2000] + "..."
                                else:
                                    enriched_var['param_expression'] = linked_expression
                            else:
                                enriched_var['param_expression'] = ''
                        else:
                            # Если связанное свойство не найдено
                            enriched_var['par_type'] = 'Not Found'
                            enriched_var['par_tag'] = ''
                            enriched_var['par_const'] = ''
                            enriched_var['par_calc_type'] = ''
                            enriched_var['par_calc_offset'] = None
                            enriched_var['par_calc_period'] = None
                            enriched_var['param_expression'] = ''

                        enriched_variables.append(enriched_var)

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

        all_fields: set = set()
        filled_count: Dict[str, int] = defaultdict(int)

        for record in data_dict.values():
            for field, value in record.items():
                all_fields.add(field)
                if value is not None:
                    filled_count[field] += 1

        print(f"Всего полей (без учета id): {len(all_fields)}")

        if all_fields:
            print(f"\nСписок всех полей: {sorted(all_fields)}")

        print(f"\nСтатистика заполненности полей:")
        for field in sorted(all_fields):
            filled: int = filled_count[field]
            total: int = len(data_dict)
            percentage: float = (filled / total * 100) if total > 0 else 0
            print(f"  {field}: {filled}/{total} ({percentage:.1f}%)")


class JsonSaver:
    """Класс для сохранения данных в JSON файл."""

    def __init__(self, output_dir: Optional[Union[str, Path]] = None) -> None:
        """
        Инициализация сохранятеля JSON.

        Args:
            output_dir: Директория для сохранения файлов
        """
        if output_dir is None:
            if '__file__' in globals():
                self.output_dir: Path = Path(__file__).parent
            else:
                self.output_dir = Path.cwd()
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)


    def _reorder_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Переупорядочивает словарь, чтобы param_used был последним ключом.

        Args:
            data: Исходный словарь

        Returns:
            Словарь с переупорядоченными ключами
        """
        if not isinstance(data, dict):
            return data

        result = {}

        # Рекурсивно обрабатываем вложенные словари
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self._reorder_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    self._reorder_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value

        # Если есть ключ param_used, удаляем его и добавляем в конец
        if 'param_used' in result:
            param_used_value = result.pop('param_used')
            result['param_used'] = param_used_value

        return result

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
            input_path: Path = Path(input_file)
            filename = f"{input_path.stem}.json"
        elif filename is None:
            filename = "output_data.json"

        output_path: Path = self.output_dir / filename

        # Переупорядочиваем данные, чтобы param_used был последним
        reordered_data = self._reorder_dict(data)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    reordered_data, f,
                    ensure_ascii=False,
                    indent=2,
                    default=self._json_serializer
                )

            file_size: int = output_path.stat().st_size
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
        enable_enrichment: bool = True,
        sort_by_path: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Упрощённая функция для конвертации Excel в JSON.

    Args:
        input_file: Путь к входному Excel файлу
        output_file: Путь к выходному JSON файлу (опционально)
        sheet_name: Название листа
        id_column: Название столбца с ID
        ignore_columns: Список столбцов для игнорирования
        unpack_json_fields: Список полей для распаковки JSON
        filter_criteria: Словарь критериев для исключения строк
        exclude_fields: Список полей для исключения из результата
        show_analysis: Показывать анализ данных
        enable_enrichment: Добавлять вычисляемые поля

    Returns:
        Словарь с обработанными данными
    """
    converter: ExcelToJsonConverter = ExcelToJsonConverter(
        sheet_name=sheet_name,
        id_column=id_column,
        ignore_columns=ignore_columns,
        unpack_json_fields=unpack_json_fields,
        filter_criteria=filter_criteria,
        exclude_fields=exclude_fields
    )

    print(f"Чтение файла: {input_file}")
    print(f"Лист: {sheet_name}")
    if unpack_json_fields:
        print(f"Распаковка JSON в полях: {unpack_json_fields}")

    data: Dict[str, Dict[str, Any]] = converter.convert(input_file)

    if enable_enrichment:
        print("\nДобавление вычисляемых полей по связям...")
        data = DataEnricher.enrich_data(data)
        print("Готово.")

    # Сортировка по Path
    if sort_by_path:
        print("\nСортировка элементов по параметру Path...")
        data = DataSorter.sort_by_path(data)
        print("Сортировка завершена.")

    if show_analysis:
        DataAnalyzer.analyze(data)

    saver: JsonSaver = JsonSaver()
    if output_file:
        output_path: Path = Path(output_file)
        saver.output_dir = output_path.parent
        saver.save(data, output_path.name)
    else:
        saver.save(data, input_file=input_file)

    return data


def main() -> Optional[Dict[str, Dict[str, Any]]]:
    # Конфигурация
    INPUT_FILE: str = "Файл экспорта 22_04_2026.xlsx"
    SHEET_NAME: str = "Models"
    ID_COLUMN: str = "Id"
    IGNORE_COLUMNS: List[str] = ["Delete"]
    UNPACK_JSON_FIELDS: List[str] = ["Configuration"]
    FILTER_CRITERIA: Dict[str, List[str]] = {
        "Type": ["Model", "Object", "ObjectHashTag"]
    }
    EXCLUDE_FIELDS: List[str] = [
        "DataTypePath", "PropertyType", "UomPath", "PropertyPrimitivePath", "Type"
    ]
    ENABLE_ENRICHMENT: bool = True
    SORT_BY_PATH: bool = True  # включить сортировку по Path

    try:
        result: Dict[str, Dict[str, Any]] = process_excel_to_json(
            input_file=INPUT_FILE,
            sheet_name=SHEET_NAME,
            id_column=ID_COLUMN,
            ignore_columns=IGNORE_COLUMNS,
            unpack_json_fields=UNPACK_JSON_FIELDS,
            filter_criteria=FILTER_CRITERIA,
            exclude_fields=EXCLUDE_FIELDS,
            show_analysis=True,
            enable_enrichment=ENABLE_ENRICHMENT,
            sort_by_path=SORT_BY_PATH
        )

        print(f"\n{'=' * 60}")
        print("Готово.")
        print(f"{'=' * 60}")
        print(f"Всего обработано записей: {len(result): }")

        return result

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
