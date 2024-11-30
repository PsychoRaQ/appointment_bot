import json
from pathlib import Path
import sqlite3
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


########################


# Добавляем пользователя в БД (если его там нет)
def new_user_to_db(user_id, username, phone) -> bool:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(f'INSERT INTO Users(user_id, username, phone) Values(?,?,?)', (user_id, username, phone))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(e)
        connection.close()
        return False


# Проверяем наличие пользователя в БД
def user_is_sign(user_id) -> bool:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(f'SELECT user_id FROM Users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        connection.close()
        return user_id in result
    except Exception as e:
        print(e)
        connection.close()
        return False


# Возвращаем все данные пользователя по его user_id
def get_userdata(user_id) -> list | None:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM Users WHERE user_id = ?', (user_id,))
        result = cursor.fetchall()
        connection.close()
        return result
    except Exception as e:
        print(e)
        connection.close()
        return None


# Добавляет в таблицу Date все даты из указанного месяца
def add_new_month_to_db(month: int) -> bool:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.executemany('INSERT INTO Dates(Date) Values (?)', zip(service_func.create_date_list(month)))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(e)
        connection.close()
        return False


# Добавляет в таблицу Times время в диапазоне minute_range. (00:00 - 00:15 - 00:30 - ... - 23:45)
def add_new_time_to_db(minute_range: int) -> bool:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.executemany('INSERT INTO Times(Time) Values (?)',
                           zip(service_func.create_time_in_range_list(minute_range)))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(e)
        connection.close()
        return False


# Выборка из базы Slots по двум полям key1 = value1, key2 = value2
def get_two_slots_where(key1, value1, key2, value2, what) -> list | None:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(f'SELECT {what} FROM Slots WHERE {key1} = ? AND {key2} = ?', (value1, value2))
        result = cursor.fetchall()
        connection.close()
        return result
    except Exception as e:
        print(e)
        connection.close()
        return None


# Выборка из базы Slots по одному полю key1 = value1
def get_one_slots_where(key1, value1, what) -> list | None:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(f'SELECT {what} FROM Slots WHERE {key1} = ? ORDER BY time', (value1,))
        result = cursor.fetchall()
        connection.close()
        return result
    except Exception as e:
        print(e)
        connection.close()
        return None


# Выборка из базы Slots свободных доступных для записи дат
def get_open_times_with_date(date) -> list | None:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(f'SELECT date, time FROM Slots WHERE date = ? AND is_locked = ? AND user_id = ?',
                       (date, False, False))
        result = cursor.fetchall()
        connection.close()
        return result
    except Exception as e:
        print(e)
        connection.close()
        return None


# Добавляем в базу Slots новый слот, если в нем нет такой же связки Дата-Время
def add_new_slot(date, time) -> bool:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM Slots WHERE date = ? AND time = ?', (date, time))
        result = cursor.fetchall()
        if result:
            return False
        cursor.execute(f'INSERT INTO Slots(date,time) Values (?,?)', (date, time))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(e)
        connection.close()
        return False


# Изменение "слота" в таблице Slots, юзер занимает/освобождает
def user_take_datetime(date, time, user_id) -> bool:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(f'UPDATE Slots SET user_id = ? WHERE date = ? AND time = ?', (user_id, date, time))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(e)
        return False


# Выборка слотов юзера по его id, возвращает время/дату для отображения и дальнейшего изменения через функцию выше
def get_user_appointment(user_id) -> list | None:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(f'SELECT date, time FROM Slots WHERE user_id = ? ORDER BY date, time', (user_id,))
        result = cursor.fetchall()
        connection.close()
        return result
    except Exception as e:
        print(e)
        connection.close()
        return None


# Возвращаем все Даты или Время из таблиц Dates, Times (по выбору аргумента)
# Для отображения админ-календаря изменения слотов
def return_dates_or_times_to_admin_calendary(table_name) -> list | None:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM {table_name}')
        result = cursor.fetchall()
        connection.close()
        return result
    except Exception as e:
        print(e)
        connection.close()
        return None


# Блокируем слот и очищаем его от пользователя
# или разблокируем его
def admin_change_is_locked_status(date, time, status) -> bool:
    print(status)
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(f'UPDATE Slots SET user_id = 0, is_locked = ?  WHERE date = ? AND time = ?',
                       (status, date, time))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(e)
        return False
