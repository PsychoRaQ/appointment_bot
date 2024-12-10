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
from dialogs import dialogs
from config_data.config import load_config


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
    bot_token = config.tg_bot.token  # токен бота
    grand_admin_id = config.tg_bot.admin_id  # id телеграмм-аккаунта главного админа (через него настраиваем функционал)

    # инициализация бота и диспетчера
    bot = Bot(token=bot_token)
    dp = Dispatcher(storage=storage)

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
