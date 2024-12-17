import asyncio
import sys
import logging
from aiogram import Dispatcher, Bot
from aiogram_dialog import setup_dialogs
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from aiogram.fsm.storage.redis import DefaultKeyBuilder, Redis, RedisStorage
from dialogs import dialogs
from config_data.config import load_config, load_database
from middlewares.session import DbSessionMiddleware
from handlers import (user_handlers, unregister_handlers)


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
    admin_ids = config.admin_id  # id телеграмм-аккаунта главного админа (через него настраиваем функционал)

    database_config = load_database()  # загрузка конфигурации базы данных

    # создаем движок Алхимии с параметрами из конфига
    engine = create_async_engine(url=database_config.dsn, echo=database_config.is_echo)
    Sessionmaker = async_sessionmaker(engine, expire_on_commit=False)  # noqa

    # Проверка соединения с СУБД
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

    # инициализация бота и диспетчера
    bot = Bot(token=bot_token)
    dp = Dispatcher(storage=storage, db_engine=engine)

    # передача переменных из конфига в диспетчер
    dp.workflow_data.update({'admin_ids': admin_ids, })

    # подключаем мидлвари
    dp.update.outer_middleware(DbSessionMiddleware(Sessionmaker))

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

    # пропускаем накопившиеся апдейты
    await bot.delete_webhook(drop_pending_updates=True)
    # запускаем поллинг
    await dp.start_polling(bot)


if __name__ == '__main__':
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
