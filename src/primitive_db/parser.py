import json
import re
import shlex


'''
Проблема:
У простых функций по типу create, list и drop лишь один аргумент 
после названий, но у insert into, select и update их больше. 
Таким образом требуется разделять их после ключевых слов:
values, where, set
Опционально настроить from и into, хотя их можно просто сделать 
частью команды.
'''

#Работает только для одного значения типа 42, "Петрушин Данил"
def parser_value(value):
    value = value.strip() #выкидываем начальные и конечные пробелы
    # Обработка строк
    #(!!!) Запрашиваем строки именно в КАВЫЧКАХ
    if value[0] == '"' and value[-1] == '"':
        return value[1:-1].strip #проверка, вдруг внутри кавычек пробелы
    # Обработка true, false (bool)
    if value == "true":
        return True
    if value == "false":
        return False
    # Обработка int
    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"Некорректное значение: {value}. "
            "Строки заключайте в двойные кавычки."
        ) from None
    # from None нужно, чтобы выдавало только нашу ошибку 
    # без ошибки от int
    # https://ru.stackoverflow.com/questions/1485541/%D0%A7%D1%82%D0%BE-%D0%B7%D0%B0-%D0%BA%D0%BE%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%86%D0%B8%D1%8F-raise-from-%D0%B2-python # noqa: E501