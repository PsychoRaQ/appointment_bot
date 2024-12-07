import asyncio
from aiogram import Dispatcher, Bot
from aiogram_dialog import setup_dialogs

from handlers import (user_handlers, unregister_handlers,
                      general_admin_handlers, admin_handlers,
                      user_callback_handlers, admin_callback_handlers)
from keyboards.main_menu import set_main_menu
from database.database_init import process_checking_database
import logging
from aiogram.fsm.storage.redis import DefaultKeyBuilder, Redis, RedisStorage
from config_data import config
from dialogs import registration_dialogs

async def main() -> None:
    # настраиваем логгирование
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # подключаем редис
    storage = RedisStorage(redis=Redis(host='localhost'), key_builder=DefaultKeyBuilder(with_destiny=True))

    # инициализация бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    # Подключаем роутеры
    dp.include_routers(registration_dialogs.router,registration_dialogs.start_dialog, general_admin_handlers.router, admin_handlers.router,
                       user_handlers.router,
                       admin_callback_handlers.router, user_callback_handlers.router)

    setup_dialogs(dp)

    # инициализация базы данных
    await process_checking_database()

    # устанавливаем меню для бота
    await set_main_menu(bot)
    # пропускаем накопившиеся апдейты
    await bot.delete_webhook(drop_pending_updates=True)
    # запускаем поллинг
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

# ######################

# СДЕЛАТЬ ВОЗМОЖНОСТЬ ИЗМЕНЕНИЯ МАКСИМАЛЬНОГО КОЛИЧЕСТВА ЗАПИСЕЙ У ПОЛЬЗОВАТЕЛЯ
# СДЕЛАТЬ АДМИНУ ВЫВОД ВСЕХ ПОЛЬЗОВАТЕЛЕЙ И ВЕСЬ ФУНКЦИОНАЛ С ЭТИМ СВЯЗАННЫЙ
# Сделать генерацию календаря на 2 месяца (текущий + следующий) с пагинацией

# Разобраться с генерацией дат и времени, исправить ошибку импортов в database_func
