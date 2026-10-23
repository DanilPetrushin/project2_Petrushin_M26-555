# Управление таблицами

Запуск базы данных (через bash):

project

## Создание таблицы со столбцами типов int, str и bool:

create_table users name:str age:int active:bool

Столбец ID:int добавляется автоматически.

## Просмотр таблиц и их структуры:

list_tables

## Удаление таблицы:

drop_table users

## Дополнительные команды:

- help — справка.
- exit — выход.

Метаданные автоматически сохраняются в db_meta.json.