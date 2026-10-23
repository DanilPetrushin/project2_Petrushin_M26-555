# Файл отвечает за запуск, игровой цикл и парсинг команд.

import shlex

import prompt

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata


# src/primitive_db/engine.py
def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    # операции с таблицами из 2-го блока
    print("<command> create_table <имя_таблицы> "
    "<столбец1:тип> ... - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    # операции с таблицами из 3-го блока
    print("<command> insert into <имя_таблицы> values (<значение1>, "
    "<значение2>, ...) - создать запись.")
    print("<command> select from <имя_таблицы> where <столбец> = "
    "<значение> - прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> " \
    "where <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - " \
    "удалить запись.")
    # общие команды
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def run():
    meta_filepath = "db_meta.json"
    print_help()

    while True:
        # подгружаем актуальные данные
        metadata = load_metadata(meta_filepath)
        user_input = prompt.string("Введите команду: ")
        args = shlex.split(user_input) # разделяем ввод на отдельные слова
        command = args[0] 
        if command == "exit":
            break
        elif command == "help":
            print_help()
        elif command == "create_table":
            if len(args) < 3:
                print ("Команда create_table должна содержать "
                "<имя_таблицы> <столбец1:тип>...")
                continue
            metadata = create_table(metadata, args[1], args[2:])
        elif command == "list_tables":
            if len(args) != 1:
                print("Команда list_tables не должна содержать аргументы")
                continue # досрочно завершаем цикл
            list_tables(metadata)
        elif command == "drop_table":
            if len(args) > 2:
                    print ("Команда create_table должна содержать только <имя_таблицы>")
                    continue
            drop_table(metadata, args[1])
        else:
            print(f"Функции <{command}> нет. Попробуйте снова.")

        # в конце цикла сохраняем данные
        save_metadata(meta_filepath, metadata)