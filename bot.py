import asyncio
from aiogram import Dispatcher

from handlers import (user_handlers, unregister_handlers,
                      general_admin_handlers, admin_handlers,
                      user_callback_handlers, admin_callback_handlers)
from keyboards.main_menu import set_main_menu
from config_data import bot_init
from database.database_init import process_checking_database


async def main() -> None:
    bot = bot_init.bot
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_routers(general_admin_handlers.router, admin_handlers.router,
                       user_handlers.router, unregister_handlers.router,
                       admin_callback_handlers.router, user_callback_handlers.router)

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
# ОТДЕЛИТЬ КАЛЕНДАРИ У АДМИНА (разделил, осталось разделить генератор календаря (в идеале)
# + доделать хэндлеры колбэков)


# СДЕЛАТЬ ВОЗМОЖНОСТЬ ИЗМЕНЕНИЯ МАКСИМАЛЬНОГО КОЛИЧЕСТВА ЗАПИСЕЙ У ПОЛЬЗОВАТЕЛЯ
# СДЕЛАТЬ АДМИНУ ВЫВОД ВСЕХ ПОЛЬЗОВАТЕЛЕЙ И ВЕСЬ ФУНКЦИОНАЛ С ЭТИМ СВЯЗАННЫЙ
# Сделать генерацию календаря на 2 месяца (текущий + следующий) с пагинацией
# Вынести логику из получения данных из базы/ обработки хэндлеров в сервисный модуль
# Оформить код

# Разобраться с генерацией дат и времени, исправить ошибку импортов в database_func


# Починить календарь пользователя с макс запсиями ----> исправить сортировку времени при выводе на календарь