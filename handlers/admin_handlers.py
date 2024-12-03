from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from filters.filters import UserIsAdmin
from lexicon.lexicon import LEXICON_ADMIN

from keyboards.admin_calendary_kb import (start_calendary_admin_kb, admin_kb)

router = Router()
router.message.filter(UserIsAdmin())

'''
Обработка message'ей
от администраторов
'''


# Хэндлер для команды "Старт"
@router.message(CommandStart())
async def proccess_start_admin_command_is_register(message: Message):
    await message.delete()
    keyboard = admin_kb()
    await message.answer(LEXICON_ADMIN['/start'],
                         reply_markup=keyboard,
                         )


# Хэндлер для команды "Отобразить календарь"
@router.message(Command('calendary'))
async def proccess_calendary_admin_command(message: Message):
    await message.delete()
    keyboard = start_calendary_admin_kb()
    await message.answer(text=LEXICON_ADMIN['/what_you_need'],
                         reply_markup=keyboard)