# Здесь будет основная логика работы с таблицами и данными.
import json
from copy import deepcopy

from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import load_table_data, save_table_data

cache = create_cacher()


@handle_db_errors
def create_table(metadata, table_name, columns):
    """
    Она должна принимать текущие метаданные, имя таблицы и список столбцов.
    Автоматически добавлять столбец ID:int в начало списка столбцов.
    Проверять, не существует ли уже таблица с таким именем. Если да, выводить ошибку.
    Проверять корректность типов данных (только int, str, bool).
    В случае успеха, обновлять словарь metadata и возвращать его.
    """
    # есть ли таблица с таким именем?
    if table_name in metadata:
        raise ValueError(f"Таблица '{table_name}' уже существует.")

    # в result формируем таблицу для её дальнешего переноса в metadata
    # сразу заносим ID:int
    result = ["ID:int"]
    names = {"ID"}

    for column in columns:
        split_data = column.split(":")

        if len(split_data) != 2:  # проверка на наличие двух слов (имя и тип)
            raise ValueError(f"Столбец '{column}' должен иметь формат имя:тип.")

        name, data_type = split_data  # имя и тип переход в две разные переменные

        # 1) ЕСТЬ ЛИ ИМЯ
        # 2) соотвествует ли доступному
        if not name or data_type not in ("int", "str", "bool"):
            raise ValueError(f"Некорректные данные в столбце '{column}'.")
        # не повторяется ли имя столбца?
        if name in names:
            raise ValueError(f"Столбец '{name}' уже существует.")

        # names нужен для проверки дубликации имён
        names.add(name)
        # result хранит все корректные столбцы
        result.append(column)

    save_table_data(table_name, [])
    metadata[table_name] = result
    print(f"Таблица '{table_name}' создана.")
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не найдена.")

    del metadata[table_name]
    print(f"Таблица '{table_name}' удалена.")
    return metadata


def list_tables(metadata):
    # проверка на пустые таблицы: чтобы не выглядело, будто очень долгая загрузка
    if not metadata:
        print("Таблицы отсутствуют")
        return

    # через .items извлекаем пары ключ-значение в две разные переменные
    for table_name, columns in metadata.items():
        # columns хранят несколько значений, тк это список, поэтому склеиваем их
        print(f"{table_name}: {', '.join(columns)}")


# валидация вынесена в отдельную функцию из-за сложности
def validate_data(metadata, table_name, real_data):
    # есть ли метаданные по такой таблице?
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не обнаружена")
    # создаём словарь типа name : str...
    template = dict(column.split(":") for column in metadata[table_name])
    types = {"int": int, "str": str, "bool": bool}
    for name, value in real_data.items():
        if name not in template:
            raise ValueError(f"Столбец '{name}' не обнаружен")
        required_type = types[template[name]]
        if type(value) is not required_type:
            raise ValueError(
                f"Значения столбца '{name}' должны принадлежать типу {template[name]}"
            )


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    if table_name not in metadata:
        raise ValueError(f"Таблица {table_name} не обнаружена")

    columns = metadata[table_name][1:]

    if len(values) != len(columns):
        raise ValueError(
            f"Ожидается значений: {len(columns)}, получено: {len(values)}."
        )
    # создаём словарь, в котором сначала указываем название колонки, а потом значение
    real_data = {column.split(":")[0]: value for column, value in zip(columns, values)}
    validate_data(metadata, table_name, real_data)

    table_data = load_table_data(table_name)
    # создание нового id, default на случай, если это первая запись
    next_id = max((record["ID"] for record in table_data), default=0) + 1
    table_data.append({"ID": next_id, **real_data})
    return table_data


@handle_db_errors
@log_time
def select(table_name, where_clause=None):
    # подгрузка данных
    table_data = load_table_data(table_name)

    # формируем ключ для обращения к кэшу
    key = (
        table_name,
        json.dumps(table_data, sort_keys=True, ensure_ascii=False),
        json.dumps(where_clause, sort_keys=True, ensure_ascii=False),
    )

    # (!) найти ссылка на youtube с данным решением
    # создаём функцию, чтобы cache её вызывал
    # только если она не вызывалась раннее
    def get_result():
        if where_clause is None:
            return table_data

        if len(where_clause) != 1:
            raise ValueError("Укажите ровно одно условие.")

        name, value = next(iter(where_clause.items()))
        data = []

        for record in table_data:
            if record.get(name) == value:
                data.append(record)

        return data

    return deepcopy(cache(key, get_result))


@handle_db_errors
def update(table_name, set_clause, where_clause=None):
    if where_clause is None:
        raise ValueError("Условие не задано")
    if "ID" in set_clause:
        raise ValueError("Изменять ID нельзя")
    table_data = load_table_data(table_name)
    if where_clause is None or len(where_clause) != 1:
        raise ValueError("Укажите ровно одно условие.")
    name, value = next(iter(where_clause.items()))
    for record in table_data:
        if record.get(name) == value:
            record.update(set_clause)
    return table_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_name, where_clause):
    table_data = load_table_data(table_name)
    if where_clause is None or len(where_clause) != 1:
        raise ValueError("Укажите ровно одно условие.")
    name, value = next(iter(where_clause.items()))
    data = []

    for record in table_data:
        if record.get(name) != value:
            data.append(record)

    return data
