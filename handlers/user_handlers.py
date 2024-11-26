
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from pyexpat.errors import messages

from keyboards.calendary_kb import create_calendary_kb, create_times_kb
from keyboards.other_kb import phone_kb

from lexicon.lexicon import LEXICON, DATE_LST

from filters.filters import DateTimeIsCorrect, MessageContact, UserIsRegister

from services.service_func import change_datetime_status
from services import database_func


router = Router()
router.message.filter(UserIsRegister())

# Хэндлер для команды "Помощь"
@router.message(Command(commands='help'))
async def proccess_help_command(message: Message):
    await message.answer(LEXICON['/help'])

# Хэндлер для команды "Начало работы"
@router.message(Command(commands='beginning'))
async def proccess_beginning_command(message: Message):
    await message.answer(LEXICON['/beginning'])

# Хэндлер для отображения календаря (и дальнейшая запись)
@router.message(Command(commands='calendary'))
async def proccess_calendary_command(message: Message):
    keyboard = create_calendary_kb(7, **DATE_LST)
    await message.answer(text='Календарь',
                         reply_markup=keyboard)

# Хэндлер для всех оставшихся сообщений
@router.message()
async def test_other_handlers(message: Message):
    print('Без хэндлера')
    await message.answer(text='123')







#########################
# Старые хэндлеры для колбэков-записи
@router.callback_query(F.data.in_(DATE_LST))
async def process_date_is_confirm(callback: CallbackQuery):
    keyboard = create_times_kb(5, DATE_LST[callback.data])
    await callback.message.edit_text(text='Время:',
                                     reply_markup=keyboard)

@router.callback_query(DateTimeIsCorrect())
async def process_datetime_is_choose(callback: CallbackQuery):
    await change_datetime_status(callback.data)
    await callback.message.edit_text(
        text=f'Отлично! Вы записаны на {callback.data}!',
        show_alert=True,
        reply_markup=None
    )

# @router.callback_query(F.data == 'no_phone')
# async def process_add_phone(callback: CallbackQuery):
#
#     keyboard = phone_kb()
#     await callback.message.edit_text(text='Добавить телефон:',
#                                      reply_markup=keyboard)
#
#
#

#################################

# Хэндлер для всех оставшихся колбэков, для теста
@router.callback_query()
async def process_datetime_is_choose(callback: CallbackQuery):
    print('callback.data')
    await callback.answer()