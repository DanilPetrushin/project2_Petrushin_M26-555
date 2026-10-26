import time
from functools import wraps

from primitive_db.constants import CANCEL_OPERATION


def handle_db_errors(func):
    '''
    Декоратор для перехвата ошибок
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
        return CANCEL_OPERATION

    return wrapper


def confirm_action(func_name):
    '''
    Декоратор для подтверждения действий
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(f'Вы уверены, что хотите выполнить "{func_name}"? [y/n]: ')
            # уберем пробелы и сделаем строчной
            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return CANCEL_OPERATION
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    '''
    Декоратор для счёта времени потраченного на операцию
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            op_time = time.monotonic() - start_time
            print(f"Функция {func.__name__} выполнилась за {op_time:.3f} секунд.")

    return wrapper


# очень хотелось реализовать cache из functools, но по заданию
# требуется другое решение
def create_cacher():
    '''
    Кэш.
    '''
    cache = {}

    def cache_result(key, value_func):
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    return cache_result
