from aiogram import Bot
from aiogram.types import BotCommand

from lexicon.lexicon import LEXICON_COMMANDS

'''
Генерация кнопки menu у бота
'''


# Функция создания главного меню для пользователя (в зависимости от регистрации его в боте)
async def set_main_menu(bot: Bot):
    main_menu_commands = [BotCommand(command='/start', description=LEXICON_COMMANDS['/start'])]
    await bot.set_my_commands(main_menu_commands)
