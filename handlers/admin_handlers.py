from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from filters.filters import UserIsAdmin
from lexicon.lexicon import LEXICON_ADMIN, LEXICON_ADMIN_COMMANDS

from keyboards.admin_calendary_kb import (start_calendary_admin_kb, create_admin_calendary_date_kb, admin_kb)
from services import database_func

router = Router()
router.message.filter(UserIsAdmin())


# Хэндлер для команды "Старт" (если пользователь админ)
@router.message(CommandStart())
async def proccess_start_admin_command_is_register(message: Message):
    await message.delete()
    keyboard = admin_kb()
    await message.answer(LEXICON_ADMIN['/start'],
                         reply_markup=keyboard,
                         )


# Хэндлер для команды "Отобразить календарь" (если пользователь админ)
@router.message(Command('calendary'))
async def proccess_calendary_admin_command(message: Message):
    await message.delete()
    keyboard = start_calendary_admin_kb()
    await message.answer(text=LEXICON_ADMIN['/what_you_need'],
                         reply_markup=keyboard)


# Хэндлер для команды "Изменить расписание"
@router.message(F.text == LEXICON_ADMIN_COMMANDS['/edit_calendary'])
async def proccess_edit_calendary_command(message: Message):
    await message.delete()
    status = 'admin_edit_appointment'
    keyboard = create_admin_calendary_date_kb(4, status=status)
    await message.answer(LEXICON_ADMIN['/edit_calendary'],
                         reply_markup=keyboard)
