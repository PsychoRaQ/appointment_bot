import asyncio
import sys

from aiogram import Dispatcher, Bot
from aiogram_dialog import setup_dialogs

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import create_engine

from handlers import (user_handlers, unregister_handlers,
                      general_admin_handlers, admin_handlers,
                      user_callback_handlers, admin_callback_handlers)
from keyboards.main_menu import set_main_menu
import db
from db import database_init

import logging
from aiogram.fsm.storage.redis import DefaultKeyBuilder, Redis, RedisStorage
from dialogs import dialogs
from config_data.config import load_config, load_database


async def main() -> None:
    # настраиваем логгирование
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # подключаем редис
    storage = RedisStorage(redis=Redis(host='localhost'), key_builder=DefaultKeyBuilder(with_destiny=True))

    # Настройка конфига
    config = load_config('.env')
    bot_token = config.token  # токен бота
    grand_admin_id = config.admin_id  # id телеграмм-аккаунта главного админа (через него настраиваем функционал)

    database_config = load_database()  # загрузка конфигурации базы данных

    # создаем движок Алхимии с параметрами из конфига
    engine = create_engine(url=database_config.dsn, echo=database_config.is_echo)

    # # Открытие нового соединение с базой
    # async with engine.begin() as conn:
    #     # Выполнение обычного текстового запроса
    #     await conn.execute(text("SELECT 1"))

    # Удаление предыдущей версии базы
    # и создание таблиц заново
    db.Base.metadata.drop_all(engine)
    db.Base.metadata.create_all(engine)

    # инициализация бота и диспетчера
    bot = Bot(token=bot_token)
    dp = Dispatcher(storage=storage, db_engine=engine)

    # Печатает на экран SQL-запрос для создания таблицы в PostgreSQL
    print(CreateTable(db.Users.__table__).compile(dialect=postgresql.dialect()))

    # передача переменных из конфига в диспетчер
    dp.workflow_data.update({'grand_admin_id': grand_admin_id, })

    # Подключаем роутеры для хэндлеров
    dp.include_router(user_handlers.router)
    dp.include_router(unregister_handlers.router)

    # Подключаем роутеры для диалогов
    dp.include_router(dialogs.main_menu_dialog)
    dp.include_router(dialogs.start_dialog)
    dp.include_router(dialogs.user_appointment_dialog)
    dp.include_router(dialogs.user_new_appointment_dialog)

    # Подключаем диалоги
    setup_dialogs(dp)

    # инициализация базы данных
    await db.database_init.process_checking_database()

    # устанавливаем меню для бота
    await set_main_menu(bot)
    # пропускаем накопившиеся апдейты
    await bot.delete_webhook(drop_pending_updates=True)
    # запускаем поллинг
    await dp.start_polling(bot)


if __name__ == '__main__':
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

# ######################
### Новое
# Перенести функционал бота на диалоги


# Запись +
# Мои записи +-
# Отмена записи (в моих записях) -
# Главное меню +
# Админка -


#### Старое

# СДЕЛАТЬ ВОЗМОЖНОСТЬ ИЗМЕНЕНИЯ МАКСИМАЛЬНОГО КОЛИЧЕСТВА ЗАПИСЕЙ У ПОЛЬЗОВАТЕЛЯ
# СДЕЛАТЬ АДМИНУ ВЫВОД ВСЕХ ПОЛЬЗОВАТЕЛЕЙ И ВЕСЬ ФУНКЦИОНАЛ С ЭТИМ СВЯЗАННЫЙ
# Сделать генерацию календаря на 2 месяца (текущий + следующий) с пагинацией

# Разобраться с генерацией дат и времени, исправить ошибку импортов в database_func
