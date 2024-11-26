import json
from pathlib import Path

USERS_PATH = Path('database/users.json')

DEFAULT_USER_DATABASE = {'name': None,
                         'phone': None,
                         'date': None,
                         'is_admin': False
                         }


# n = {'1.11': {'10:00': {'lock': False, 'user': None},
#               '11:00': {'lock': True, 'user': 'username'}
#               },
#      '2.11': {'10:00': {'lock': False, 'user': None},
#               '11:00': {'lock': True, 'user': 'username'}
#               }

# datetime_gen = {f'{date}.{MONTH}':{f'{time}':{'lock':False, 'user': None}for time in DATETIME} for date in range(1,32)}

# Проверка регистрации пользователя в боте
def check_user_is_sign(user_id: str):
    with open(USERS_PATH, 'r') as file:
        db = json.load(file)
    return user_id in db


# Если пользователь зарегистрирован, возвращаем все данные о нем
def get_user_data_from_db(user_id: str) -> dict:
    if check_user_is_sign(user_id):
        with open(USERS_PATH, 'r') as file:
            db = json.load(file)
            return db[user_id]

# Если пользователь не зарегестрирован, добавляет его в базу + проверка на номер телефона
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

# Если пользователь зарегестрирован, добавляет ему номер телефона
def add_phone_to_user(user_id, phone) -> None:
    if check_user_is_sign(user_id):
        with open(USERS_PATH, 'r') as file:
            db = json.load(file)
        db[user_id]['phone'] = phone
        with open(USERS_PATH, 'w') as file:
            json.dump(db, file)

# Если пользователь зарагистрирован, проверяет у него наличие номера телефона
def check_user_phone(user_id):
    if check_user_is_sign(user_id):
        with open(USERS_PATH, 'r') as file:
            db = json.load(file)
        return db[user_id]['phone']
