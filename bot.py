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
from dialogs import dialogs


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

    # Подключаем роутеры для хэндлеров
    dp.include_routers(user_handlers.router,
                       unregister_handlers.router,
                       )

    # Подключаем роутеры для диалогов
    dp.include_routers(dialogs.main_menu_dialog,
                       dialogs.start_dialog,
                       dialogs.user_appointment_dialog,
                       dialogs.user_new_appointment_dialog,
                       )

    # Подключаем диалоги
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
