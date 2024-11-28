from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.calendary_kb import create_calendary_kb, create_times_kb
from keyboards.other_kb import delete_my_appointment_data_kb, delete_my_appointment_time_kb
from lexicon.lexicon import LEXICON
from filters.filters import (DateTimeIsCorrect, UserIsRegister, UserIsDeleteAppointment,
                             UserIsDeleteAppointmentTime, UserIsAdmin)
from services import database_func, service_func

router = Router()
router.message.filter(UserIsRegister())


# Хэндлер для команды "Старт" (если пользователь уже зарегистрирован и не админ)
@router.message(CommandStart())
async def proccess_start_user_command_is_register(message: Message):
    await message.delete()
    await message.answer(LEXICON['/is_register'],
                         keyboard=ReplyKeyboardRemove())


# Хэндлер для команды "Помощь"
@router.message(Command(commands='help'))
async def proccess_help_command(message: Message):
    await message.delete()
    await message.answer(LEXICON['/help'])


# Хэндлер для команды "Начало работы"
@router.message(Command(commands='beginning'))
async def proccess_beginning_command(message: Message):
    await message.delete()
    await message.answer(LEXICON['/beginning'])


# Хэндлер для отображения календаря (и дальнейшая запись)
@router.message(Command(commands='calendary'))
async def proccess_calendary_command(message: Message):
    await message.delete()
    if database_func.user_max_appointment(str(message.chat.id)):
        await message.answer(text=LEXICON['/user_is_max_appointment'],
                             reply_markup=ReplyKeyboardRemove())
    else:
        keyboard = create_calendary_kb(5, **database_func.get_datetime_from_db())
        if keyboard:
            await message.answer(text=LEXICON['/user_is_not_max_appointment'],
                                 reply_markup=keyboard)
        else:
            await message.answer(text=LEXICON['/no_one_available_date'],
                                 show_alert=True,
                                 reply_markup=ReplyKeyboardRemove())


# Хэндлер для команды "Мои записи"
@router.message(Command(commands='my_appointment'))
async def process__my_appointment(message: Message):
    await message.delete()
    text = service_func.get_user_appointment(str(message.from_user.id))
    await message.answer(text=text,
                         reply_markup=None)


# Хэндлер для команды "Удалить запись"
@router.message(Command(commands='delete_my_appointment'))
async def process_delete_my_appointment(message: Message):
    await message.delete()
    keyboard = delete_my_appointment_data_kb(3, str(message.chat.id))
    if keyboard == 'no_one_appointment':
        await message.answer(
            text=LEXICON['/no_one_appointment'],
            show_alert=True,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(text=LEXICON['/choose_date_to_delete'],
                             reply_markup=keyboard)


# Хэндлер для всех неопознанных сообщений
@router.message()
async def test_other_handlers(message: Message):
    await message.delete()
    print('Сообщение не распознано')
    await message.answer(text=LEXICON['/unknown_message'])
