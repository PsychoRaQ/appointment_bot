from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards.other_kb import create_main_menu_kb
from lexicon.lexicon import LEXICON
from filters.filters import UserIsRegister
import logging

router = Router()
router.message.filter(UserIsRegister())
logger = logging.getLogger(__name__)

'''
Обработка message'ей
обычных зарегистрированных пользователей
(в т.ч. администраторов)
'''


# Хэндлер для команды "Старт" (пользователь уже зарегистрирован и не админ)
@router.message(CommandStart())
async def proccess_start_command_user_is_register(message: Message):
    await message.delete()
    keyboard = create_main_menu_kb()
    await message.answer(text='Что делаем?',
                         reply_markup=keyboard)


# Хэндлер для всех неопознанных сообщений
@router.message()
async def test_other_handlers(message: Message):
    await message.delete()
    logger.info('Сообщение не распознано')
    await message.answer(text=LEXICON['/unknown_message'])
