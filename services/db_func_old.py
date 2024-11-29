import json
from pathlib import Path
import config_data.config

USERS_PATH = Path('database/users.json')
DATETIME_PATH = Path('database/datetime.json')
DATABASE_PATH = Path(config_data.config.DATABASE_PATH)
DEFAULT_USER_DATABASE = {'name': None,
                         'phone': None,
                         'date': {},
                         'is_admin': False,
                         'max_appointment': 2
                         }


# СТАНДАРТНОЕ ЗАПОЛНЕНИЕ БАЗЫ ДАТ И ВРЕМЕНИ
# from config_data.config import DATETIME, MONTH
# def date_gen(date):
#     if len(date) == 1:
#         date = f'0{date}'
#     return date
#
# datetime_gen = {f'{date_gen(str(date))}.{MONTH}':{f'{time}':{'lock':True, 'user': None}for time in DATETIME} for date in range(1,32)}
# with open(DATETIME_PATH, 'w') as file:
#     json.dump(datetime_gen, file)


# Проверка регистрации пользователя в боте
def check_user_is_sign(user_id: str) -> bool:
    with open(USERS_PATH, 'r') as file:
        db = json.load(file)
    return user_id in db


# Считывание всей базы данных с пользователями
def get_user_db() -> dict:
    with open(USERS_PATH, 'r') as file:
        db = json.load(file)
    return db


# Если пользователь зарегистрирован, возвращаем все данные о нем
def get_user_data_from_db(user_id: str) -> dict:
    if check_user_is_sign(user_id):
        with open(USERS_PATH, 'r') as file:
            db = json.load(file)
            return db[user_id]


# Если пользователь не зарегистрирован, добавляет его в базу + проверка на номер телефона
def new_user_to_database(user_id: str, name: str) -> bool:
    if check_user_is_sign(user_id) is False:
        with open(USERS_PATH, 'r') as file:
            db = json.load(file)
        db[user_id] = DEFAULT_USER_DATABASE
        db[user_id]['name'] = name
        with open(USERS_PATH, 'w') as file:
            json.dump(db, file)
        return True
    elif check_user_phone(user_id) is None:
        return True
    else:
        return False


# Если пользователь зарегистрирован, добавляет ему номер телефона
def add_phone_to_user(user_id, phone) -> None:
    if check_user_is_sign(user_id):
        with open(USERS_PATH, 'r') as file:
            db = json.load(file)
        db[user_id]['phone'] = phone
        with open(USERS_PATH, 'w') as file:
            json.dump(db, file)


# Если пользователь зарегистрирован, проверяет у него наличие номера телефона
def check_user_phone(user_id) -> bool | str:
    if check_user_is_sign(user_id):
        with open(USERS_PATH, 'r') as file:
            db = json.load(file)
        return db[user_id]['phone']


# Получение словаря с датами и временем из базы
def get_datetime_from_db() -> dict:
    with open(DATETIME_PATH, 'r') as file:
        db = json.load(file)
    return db


# Изменение статуса в базе данных (занять дату/время)
def change_datetime_status(user_id, datetime, status) -> None | Exception:
    # Записываем дату в базу с датами
    db = get_datetime_from_db()

    try:
        date, time = datetime.split(',')
    except Exception as e:
        print(e)
        return e

    # запись даты (если свободна)
    if db[date][time]['user'] is None:
        db[date][time]['user'] = user_id

    #  очистка даты (если занята)
    else:
        db[date][time]['user'] = None

    with open(DATETIME_PATH, 'w') as file:
        json.dump(db, file)

    if status == 'add':
        # Записываем дату в профиль пользователя
        with open(USERS_PATH, 'r') as file:
            db = json.load(file)
        # Пытаемся найти существующую запись с нужной датой у пользователя и добавить время в нее
        try:
            db[user_id]['date'][date].append(time)
        # Если ее нет - создаем дату со списком (чтобы в будущем можно было добавить еще одно время)
        except:
            db[user_id]['date'][date] = [time]
        with open(USERS_PATH, 'w') as file:
            json.dump(db, file)

    elif status == 'clear':
        # Очищаем дату из профиля пользователя
        with open(USERS_PATH, 'r') as file:
            db = json.load(file)
        # Удаляем время из нужной даты
        db[user_id]['date'][date].remove(time)
        # Если у даты больше не осталось привязанного времени - удаляем и её
        if db[user_id]['date'][date] == []:
            del db[user_id]['date'][date]
        with open(USERS_PATH, 'w') as file:
            json.dump(db, file)


# Проверка на максимальное количество записей у пользователя
# True - записаться нельзя, False - записаться можно
def user_max_appointment(user_id) -> bool:
    db = get_user_data_from_db(user_id)
    max_appointment = db['max_appointment']
    datetime_lst = []
    if db['date'] == {}:
        return False
    for i in db['date'].values():
        datetime_lst += i
    return len(datetime_lst) >= max_appointment


# возвращает максимально доступное количество записей у пользователя
def get_user_max_appointment(user_id) -> int:
    db = get_user_data_from_db(user_id)
    max_appointment = db['max_appointment']
    return max_appointment


# проверяем есть ли админка у пользователя, если да - возвращаем "уровень" админки
def user_is_admin(user_id) -> int | bool:
    return get_user_data_from_db(user_id)['is_admin']


# Админ в функции /edit_calendary меняет свое расписание | изменяем статус 'lock' у даты/времени
def admin_change_datetime_status(datetime) -> None | Exception:
    # Записываем дату в базу с датами
    db = get_datetime_from_db()

    try:
        datetime, is_admin = datetime.split('_')
        date, time = datetime.split(',')
    except Exception as e:
        print(e)
        return e

    # Изменяем "доступность" даты на противоположную
    if db[date][time]['lock'] is True:
        db[date][time]['lock'] = False
    #  очистка даты (если занята)
    else:
        db[date][time]['lock'] = True

    user = db[date][time]['user']

    if user is not None:
        user = db[date][time]['user']
        db[date][time]['user'] = None

    with open(DATETIME_PATH, 'w') as file:
        json.dump(db, file)

    if user:
        # Очищаем дату из профиля пользователя
        with open(USERS_PATH, 'r') as file:
            db = json.load(file)
        # Удаляем время из нужной даты
        db[user]['date'][date].remove(time)
        # Если у даты больше не осталось привязанного времени - удаляем и её
        if db[user]['date'][date] == []:
            del db[user]['date'][date]
        with open(USERS_PATH, 'w') as file:
            json.dump(db, file)
    return user

