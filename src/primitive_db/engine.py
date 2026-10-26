# Файл отвечает за запуск, игровой цикл и парсинг команд.
import shlex

import prompt

from primitive_db.constants import CANCEL_OPERATION
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
    validate_data,
)
from primitive_db.parser import parser_clause, parser_value
from primitive_db.utils import (
    load_metadata,
    print_table,
    save_metadata,
    save_table_data,
)


# src/primitive_db/engine.py
def print_help():
    """Prints the help message for the current mode."""
    ## нужно требовать кавычки и пробелы рядом с =
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    # операции с таблицами из 2-го блока
    print("<command> create_table <имя_таблицы> <столбец1:тип> ... - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    # операции с таблицами из 3-го блока
    print(
        "<command> insert into <имя_таблицы> values (<значение1> "
        "<значение2> ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = "
        "<значение> - прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> - "
        "удалить запись."
    )
    # общие команды
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")
    print(
        "*При вводе команды строки заключайте в двойные кавычки, "
        "а вокруг = ставьте пробелы."
    )


def run():
    meta_filepath = "db_meta.json"
    print_help()

    while True:
        try:
            # Загрузка, ввод, обработка и сохранение.
            metadata = load_metadata(meta_filepath)
            user_input = prompt.string("Введите команду: ").strip()
            args = shlex.split(user_input, posix=False)
            if not args:
                continue
            command = args[0]
            # перебираем команды
            if command == "exit":
                break
            elif command == "help":
                print_help()
            elif command == "create_table":
                if len(args) < 3:
                    print(
                        "Команда create_table должна содержать "
                        "<имя_таблицы> <столбец1:тип>..."
                    )
                    continue
                result = create_table(metadata, args[1], args[2:])
                if result == CANCEL_OPERATION:
                    continue
                metadata = result
            elif command == "list_tables":
                if len(args) != 1:
                    print("Команда list_tables не должна содержать аргументы")
                    continue  # досрочно завершаем цикл
                list_tables(metadata)
            elif command == "drop_table":
                if len(args) != 2:
                    print("Команда drop_table должна содержать только <имя_таблицы>")
                    continue
                result = drop_table(metadata, args[1])
                if result == CANCEL_OPERATION:
                    continue
                metadata = result
            # далее более сложные команды
            elif command == "insert":
                if len(args) < 5 or args[1] != "into" or args[3] != "values":
                    raise ValueError(
                        "Использование: insert into <имя_таблицы> "
                        "values <значение1> <значение2>..."
                    )
                table_name = args[2]
                values = [parser_value(value) for value in args[4:]]
                table_data = insert(metadata, table_name, values)
                if table_data == CANCEL_OPERATION:
                    continue
                save_table_data(table_name, table_data)
                print("Добавлена новая запись.")
                ## Что если вставляем в неусществующую таблицу?
            elif command == "select":
                if len(args) not in (3, 7) or args[1] != "from":
                    raise ValueError(
                        "Использование: select from <имя_таблицы> "
                        "where <столбец> = <значение>"
                    )
                table_name = args[2]
                where_clause = None
                if table_name not in metadata:
                    raise ValueError(f"Таблица '{table_name}' не существует")
                if len(args) == 7:
                    if args[3] != "where" or args[5] != "=":
                        raise ValueError("Условие должно иметь вид: where age = 22")
                    where_clause = parser_clause(" ".join(args[4:]))
                    validate_data(metadata, table_name, where_clause)
                records = select(table_name, where_clause)

                if records == CANCEL_OPERATION:
                    continue

                print_table(metadata, table_name, records)
            elif command == "update":
                if (
                    len(args) != 10
                    or args[2] != "set"
                    or args[4] != "="
                    or args[6] != "where"
                    or args[8] != "="
                ):
                    raise ValueError(
                        "Использование: update <имя_таблицы> "
                        "set <столбец1> = <новое_значение1> "
                        "where <столбец_условия> = <значение_условия>"
                    )
                table_name = args[1]
                # if table_name not in metadata:
                #     raise ValueError(f"Таблица '{table_name}' не существует")
                set_clause = parser_clause(" ".join(args[3:6]))
                where_clause = parser_clause(" ".join(args[7:]))
                validate_data(metadata, table_name, set_clause)
                validate_data(metadata, table_name, where_clause)
                table_data = update(table_name, set_clause, where_clause)
                if table_data == CANCEL_OPERATION:
                    continue
                save_table_data(table_name, table_data)
                print("Операция выполнена.")
            elif command == "delete":
                if (
                    len(args) != 7
                    or args[1] != "from"
                    or args[3] != "where"
                    or args[5] != "="
                ):
                    raise ValueError("Использование: delete from users where ID = 1")
                # if table_name not in metadata:
                #     raise ValueError(f"Таблица '{table_name}' не существует")
                table_name = args[2]
                where_clause = parser_clause(" ".join(args[4:]))
                validate_data(metadata, table_name, where_clause)
                table_data = delete(table_name, where_clause)
                if table_data == CANCEL_OPERATION:
                    continue
                save_table_data(table_name, table_data)
                print("Удаление выполнено.")
            else:
                print(f"Функции <{command}> нет. Попробуйте снова.")
            save_metadata(meta_filepath, metadata)
        except ValueError as error:
            print(f"Ошибка: {error}")
