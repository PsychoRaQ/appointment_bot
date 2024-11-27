from lexicon.lexicon import LEXICON_COMMANDS
from aiogram import Bot
from aiogram.types import BotCommand

# Функция создания главного меню для пользователя (в зависимости от регистрации его в боте)
async def set_main_menu(bot: Bot):
    main_menu_commands = [BotCommand(command=command,description=description) for command,description
                          in LEXICON_COMMANDS.items()]
    await bot.set_my_commands(main_menu_commands)
