# системное
import asyncio
import logging
import sys
# аиограм и алхихия
from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import DefaultKeyBuilder, Redis, RedisStorage
from aiogram_dialog import setup_dialogs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
# диалоги для подключения
from admin_dialogs import dialogs as admin_dg

from dialogs import user_dialogs as user_dg
# from user_dialogs import dialogs as user_dg

# конфигурация бота
from config_data.config import load_config, load_database, load_nats
# хэндлеры для команд
from handlers import user_handlers, unregister_handlers, admin_handlers
# мидлвари
from middlewares.session import DbSessionMiddleware
from middlewares.user_role import UserRoleMiddlware
# функция для внесения всех пользователей из базы в кэш
from src.services.database_func import get_all_users_from_db
# меню бота
from src.services.service_func import set_main_menu
# натс
from src.nats.nats_connect import connect_to_nats
from src.services.start_consumers import start_delayed_consumer, start_dispatch_consumer, start_subscribe_consumer


async def main() -> None:
    # настраиваем логгирование
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # подключаем редис
    redis = Redis(host='localhost', port=6380)
    storage = RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True))

    # Настройка конфига
    config = load_config('.env')
    bot_token = config.token  # токен бота
    admin_ids = config.admin_id  # id телеграмм-аккаунта админа
    description = config.description  # описание бота / текст кнопки "помощь"
    admin_url = config.admin_url  # ссылка на тг админа для обратной связи

    database_config = load_database()  # загрузка конфигурации базы данных

    # настройка nats
    nats_cfg = load_nats()
    nc, js = await connect_to_nats(servers=nats_cfg.nats.servers)
    delayed_bucket = await js.create_key_value(bucket='kv_storage')
    subscribe_bucket = await js.create_key_value(bucket='subscribe_storage')

    # создаем движок Алхимии с параметрами из конфига
    engine = create_async_engine(url=database_config.dsn, echo=database_config.is_echo)
    Sessionmaker = async_sessionmaker(engine, expire_on_commit=False)  # noqa

    # инициализация бота и диспетчера
    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage, db_engine=engine)

    # Проверка соединения с СУБД
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
        # передача в диспетчер id всех пользователей из базы
        registered_users = await get_all_users_from_db(conn)
        dp.workflow_data.update({'registered_users': registered_users, })

    # передача переменных из конфига в диспетчер
    dp.workflow_data.update({'admin_ids': admin_ids, 'description': description, 'admin_url': admin_url,
                             'js': js, 'delay_del_subject': nats_cfg.delayed_consumer.subject,
                             'dispatch_subject': nats_cfg.dispatch_consumer.subject,
                             'subscribe_subject': nats_cfg.subscribe_consumer.subject, 'storage': delayed_bucket,
                             'subscribe_storage': subscribe_bucket})

    # подключаем мидлвари
    dp.update.outer_middleware(DbSessionMiddleware(Sessionmaker))
    dp.update.outer_middleware(UserRoleMiddlware())

    # Подключаем роутеры для хэндлеров
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(unregister_handlers.router)

    # Подключаем роутеры для диалогов админки
    dp.include_router(admin_dg.main_menu_dialog)
    dp.include_router(admin_dg.edit_calendary)
    dp.include_router(admin_dg.all_appointments)
    dp.include_router(admin_dg.dispatch_dialog)
    dp.include_router(admin_dg.new_pcode)
    dp.include_router(admin_dg.all_admins)
    dp.include_router(admin_dg.admin_settings)

    # Подключаем роутеры для диалогов пользователей
    dp.include_router(user_dg.registration_dialog)
    dp.include_router(user_dg.main_menu_dialog)
    dp.include_router(user_dg.make_appointment_dialog)
    dp.include_router(user_dg.view_user_appointments_dialog)

    # Подключаем диалоги
    setup_dialogs(dp)

    # устанавливаем кнопку Меню
    await set_main_menu(bot)
    # пропускаем накопившиеся апдейты
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        # запуск поллинга и консьюмера отложенных сообщений
        await asyncio.gather(
            dp.start_polling(bot),
            start_delayed_consumer(
                nc=nc,
                js=js,
                bot=bot,
                subject=nats_cfg.delayed_consumer.subject,
                stream=nats_cfg.delayed_consumer.stream,
                durable_name=nats_cfg.delayed_consumer.durable_name,
            ),
            start_dispatch_consumer(
                nc=nc,
                js=js,
                bot=bot,
                subject=nats_cfg.dispatch_consumer.subject,
                stream=nats_cfg.dispatch_consumer.stream,
                durable_name=nats_cfg.dispatch_consumer.durable_name,
            ),
            start_subscribe_consumer(
                nc=nc,
                js=js,
                bot=bot,
                subject=nats_cfg.subscribe_consumer.subject,
                stream=nats_cfg.subscribe_consumer.stream,
                durable_name=nats_cfg.subscribe_consumer.durable_name,
            )
        )

    except Exception as e:
        print(e)
    finally:
        await nc.close()
        print('Connection to NATS closed')


if __name__ == '__main__':
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
