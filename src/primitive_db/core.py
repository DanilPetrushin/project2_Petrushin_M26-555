#Здесь будет основная логика работы с таблицами и данными.
from primitive_db.utils import load_table_data


def create_table(metadata, table_name, columns):
    '''
    Она должна принимать текущие метаданные, имя таблицы и список столбцов.
    Автоматически добавлять столбец ID:int в начало списка столбцов.
    Проверять, не существует ли уже таблица с таким именем. Если да, выводить ошибку.
    Проверять корректность типов данных (только int, str, bool).
    В случае успеха, обновлять словарь metadata и возвращать его.
    '''
    # есть ли таблица с таким именем?
    if table_name in metadata:
        print(f"Ошибка: таблица '{table_name}' уже существует.")
        return metadata

    # в result формируем таблицу для её дальнешего переноса в metadata
    # сразу заносим ID:int
    result = ["ID:int"] 
    names = {"ID"}

    for column in columns:
        split_data = column.split(":")

        if len(split_data) != 2: # проверка на наличие двух слов (имя и тип)
            print(f"Ошибка: '{column}' должен иметь формат имя:тип.")
            return metadata

        name, data_type = split_data # имя и тип переход в две разные переменные

        # 1) ЕСТЬ ЛИ ИМЯ
        # 2) соотвествует ли доступному
        if not name or data_type not in ("int", "str", "bool"):
            print(f"Ошибка: некорректные данные в столбце '{column}'.")
            return metadata
        # не повторяется ли имя столбца?
        if name in names:
            print(f"Ошибка: столбец с именем'{name}' уже существует.")
            return metadata

        # names нужен для проверки дубликации имён
        names.add(name)
        # result хранит все корректные столбцы
        result.append(column)

    metadata[table_name] = result
    print(f"Таблица '{table_name}' создана.")
    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f"Ошибка: таблица с именен '{table_name}' не найдена.")
        return metadata

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
        #columns хранят несколько значений, тк это список, поэтому склеиваем их
        print(f"{table_name}: {', '.join(columns)}") 

# валидация вынесена в отдельную функцию из-за сложности
def validate_data(metadata, table_name, real_data):
    # есть ли метаданные по такой таблице?
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не обнаружена")
    # создаём словарь типа name : str...
    template = dict(column.split(":") for column in metadata)
    types = {"int":int, "str":str, "bool":bool}
    for name, value in real_data.items:
        if name not in template:
            raise ValueError(f"Столбец '{name}' не обнаружен")
        required_type = types[template[name]]
        if type(value) is not required_type:
            raise ValueError(f"Значения столбца '{name}' должны принадлежать"
                             f"типу {template[name]}")

        
def insert(metadata, table_name, values):
    if table_name not in metadata:
        raise ValueError(f'Таблица {table_name} не обнаружена')
    
    columns = metadata[table_name][1:]
    
    if len(values) != len(columns):
        raise ValueError(
            f"Ожидается значений: {len(columns)}, "
            f"получено: {len(values)}."
        )
    # создаём словарь, в котором сначала указываем название колонки, а потом значение
    real_data = {column.split(":")[0]:value for column, value in zip(columns, values)}
    validate_data(metadata, table_name, real_data)

    table_data = load_table_data(table_name)
    #создание нового id, default на случай, если это первая запись
    next_id = max((record["ID"] for record in table_data), default=0) + 1
    table_data.append({"ID": next_id, **real_data})
    return table_data

def select(table_data, where_clause=None):
    pass
def update(table_data, set_clause, where_clause):
    pass
def delete(table_data, where_clause):
    pass