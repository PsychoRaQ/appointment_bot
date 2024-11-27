import asyncio
from aiogram import Bot, Dispatcher
from config_data import config
from handlers import (user_handlers, unregister_handlers, general_admin_handlers, admin_handlers, user_callback_handlers)
from keyboards.main_menu import set_main_menu

async def main() -> None:
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_routers(general_admin_handlers.router, admin_handlers.router,
                       user_handlers.router, unregister_handlers.router, user_callback_handlers.router)

    # устанавливаем меню для бота
    await set_main_menu(bot)
    # пропускаем накопившиеся апдейты
    await bot.delete_webhook(drop_pending_updates=True)
    # запускаем поллинг
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())



# ######################
# УДАЛИТЬ ПРИНТЫ
# ИСПРАВИТЬ КНОПКИ НАЗАД И ЗАКРЫТЬ
# ОТДЕЛИТЬ КАЛЕНДАРИ У АДМИНА
# ДЕЛАТЬ УВЕДОМЛЕНИЕ ПОЛЬЗОВАТЕЛЮ ЕСЛИ ЕГО ЗАПИСЬ ОТМЕНЕНА
