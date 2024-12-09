import sqlite3
from config_data.config import DATABASE_PATH
from pathlib import Path

DATABASE_PATH = Path(DATABASE_PATH)

'''
Инициализация базы данных
(проверка её наличия и создание таблиц, в случае отсутствия)
'''


# Проверка на наличие таблицы в БД, если ее нет - создает пустую (принимает соединение с БД)
async def process_checking_database() -> bool:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = connection.cursor()
        # Создаем таблицу Users
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY UNIQUE,
        username TEXT NOT NULL,
        phone TEXT DEFAULT NULL,
        date TEXT DEFAULT NULL,
        max_appointment INTEGER NOT NULL DEFAULT 2,
        is_admin INTEGER DEFAULT NULL
        )
        ''')
        cursor.execute(f'''
                        CREATE TABLE IF NOT EXISTS Slots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL,
                        time TIME NOT NULL,
                        is_locked BOOLEAN NOT NULL DEFAULT FALSE,
                        user_id INT DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES Users (user_id)
                        )
                               ''')



        # Сохраняем изменения и закрываем соединение
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(e)
        connection.close()
        return False
