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
    print("<command> create_table <имя_таблицы> "
    "<столбец1:тип> ... - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def run():
    filepath = "db_meta.json"
    print_help()

    while True:
        # подгружаем актуальные данные
        metadata = load_metadata(filepath)
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
        save_metadata(filepath, metadata)