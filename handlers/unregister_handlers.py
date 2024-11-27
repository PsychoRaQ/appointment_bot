from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.other_kb import phone_kb
from lexicon.lexicon import LEXICON
from services import database_func
from filters.filters import MessageContact


router = Router()


@router.message(CommandStart())
async def proccess_start_command(message: Message):
    if database_func.new_user_to_database(str(message.from_user.id), message.from_user.first_name):
        keyboard = phone_kb()
        text = LEXICON['/start']
    ############################
    else: # Необязательный кусок?
        keyboard = ReplyKeyboardRemove()
        text = f'{message.from_user.first_name}, {LEXICON['/is_register']}'
        ########################
    await message.delete()
    await message.answer(text=text,
                         reply_markup=keyboard
                         )


@router.message(MessageContact())
async def process_add_contact(message: Message):
    database_func.add_phone_to_user(str(message.from_user.id), message.contact.phone_number)
    await message.delete()
    await message.answer(text=LEXICON['/phone_is_add'],
                         reply_markup=ReplyKeyboardRemove())


@router.message()
async def other_unregister_message(message: Message):
    await message.delete()
    keyboard = phone_kb()
    await message.answer(text=LEXICON['/unregister_message'],
                         reply_markup=keyboard)
