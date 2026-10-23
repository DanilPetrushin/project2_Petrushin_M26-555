# Для вспомогательных функций (например, работа с файлами).

import json
import os


def load_metadata(filepath):
    '''
    Загружает данные из JSON-файла. 
    Если файл не найден, возвращает пустой словарь {}
    '''
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load (f)
    except FileNotFoundError:
        return {}

def save_metadata(filepath, data):
    '''
    Сохраняет переданные данные в JSON-файл.
    '''
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)  # ensure_ascii для кириллицы 

def load_table_data(table_name):
    filepath = os.path.join("data", f"{table_name}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [] # возвращает пустой список, чтобы не прерывать работу ошибкой

def save_table_data(table_name, data):
    try:
        os.mkdir("data")
    except FileExistsError:
        pass
    filepath = os.path.join("data", f"{table_name}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)