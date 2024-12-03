from pathlib import Path
import sqlite3
import config_data.config

DATABASE_PATH = Path(config_data.config.DATABASE_PATH)

import logging

logger = logging.getLogger(__name__)

'''
Функции обеспечивающие связь с базой данных и
выполнение SQL запросов
'''


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
        logger.warning(e)
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
        logger.warning(e)
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
        logger.warning(e)
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
        logger.warning(e)
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
        logger.warning(e)
        connection.close()
        return False


# Выборка из базы Slots по двум полям key1 = value1, key2 = value2
def get_two_slots_where(key1, value1, key2, value2, what) -> list | None:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(f'SELECT {what} FROM Slots WHERE {key1} = ? AND {key2} = ? ORDER BY date, time',
                       (value1, value2))
        result = cursor.fetchall()
        connection.close()
        return result
    except Exception as e:
        logger.warning(e)
        connection.close()
        return None


# Выборка из базы Slots по одному полю key1 = value1
def get_one_slots_where(key1, value1, what) -> list | None:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(f'SELECT {what} FROM Slots WHERE {key1} = ? ORDER BY date, time', (value1,))
        result = cursor.fetchall()
        connection.close()
        return result
    except Exception as e:
        logger.warning(e)
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
        logger.warning(e)
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
        logger.warning(e)
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
        logger.warning(e)
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
        logger.warning(e)
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
        logger.warning(e)
        connection.close()
        return None


# Блокируем слот и очищаем его от пользователя
# или разблокируем его
def admin_change_is_locked_status(date, time, status) -> bool:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(f'UPDATE Slots SET user_id = 0, is_locked = ?  WHERE date = ? AND time = ?',
                       (status, date, time))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        logger.warning(e)
        return False
