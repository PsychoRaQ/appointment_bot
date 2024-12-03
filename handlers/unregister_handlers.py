from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.other_kb import phone_kb
from lexicon.lexicon import LEXICON
from services import database_func
from filters.filters import MessageContact

router = Router()

'''
Обработка всех message'ей
для незарегистрированных пользователей
'''


# Хэндлер для команды Старт (незарегистрированный пользователь)
@router.message(CommandStart())
async def proccess_start_command_unregister_user(message: Message):
    if not database_func.user_is_sign(message.from_user.id):
        keyboard = phone_kb()
        text = LEXICON['/start']
    else:
        keyboard = None
        text = f'{message.from_user.first_name}, {LEXICON['/is_register']}'
    await message.delete()
    await message.answer(text=text,
                         reply_markup=keyboard
                         )

# Хэндлер обработки кнопки отправки телефона (регистрация пользователя в боте + заносим его в БД)
@router.message(MessageContact())
async def process_registration_user(message: Message):
    database_func.new_user_to_db(message.from_user.id, message.from_user.first_name, message.contact.phone_number)
    await message.delete()
    await message.answer(text=LEXICON['/phone_is_add'],
                         reply_markup=ReplyKeyboardRemove())

# Хэндлер для всех остальных сообщений от незарегистрированного пользователя
@router.message()
async def other_unregister_message(message: Message):
    await message.delete()
    keyboard = phone_kb()
    await message.answer(text=LEXICON['/unregister_message'],
                         reply_markup=keyboard)
