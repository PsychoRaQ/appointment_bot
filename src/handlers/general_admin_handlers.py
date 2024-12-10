from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from filters.filters import UserIsGeneralAdmin
from lexicon.lexicon import LEXICON_GENERAL_ADMIN

from keyboards.admin_calendary_kb import general_admin_kb

router = Router()
router.message.filter(UserIsGeneralAdmin())

'''
Обработка message'ей 
для супер-администратора
'''


# Хэндлер для команды "Старт"
@router.message(CommandStart())
async def proccess_start_user_command_is_register(message: Message):
    await message.delete()
    keyboard = general_admin_kb()
    await message.answer(LEXICON_GENERAL_ADMIN['/start'],
                         reply_markup=keyboard)