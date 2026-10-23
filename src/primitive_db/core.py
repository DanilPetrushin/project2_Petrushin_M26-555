#Здесь будет основная логика работы с таблицами и данными.

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