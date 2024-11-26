from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from pyexpat.errors import messages

from keyboards.calendary_kb import create_calendary_kb, create_times_kb
from keyboards.other_kb import delete_my_appointment_data_kb, delete_my_appointment_time_kb

from lexicon.lexicon import LEXICON, DATE_LST

from filters.filters import DateTimeIsCorrect, MessageContact, UserIsRegister, UserIsDeleteAppointment

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
    keyboard = create_calendary_kb(7, **database_func.get_datetime_from_db())
    await message.answer(text='Календарь',
                         reply_markup=keyboard)

# Хэндлер для команды "Удалить запись"
@router.message(Command(commands='delete_my_appointment'))
async def process_delete_my_appointment(message: Message):
    keyboard = delete_my_appointment_data_kb(3, str(message.from_user.id))
    await message.answer(text='Выберите дату для удаления:',
                         reply_markup=keyboard)


# Хэндлер для всех неопознанных сообщений
@router.message()
async def test_other_handlers(message: Message):
    print('Без хэндлера')
    await message.answer(text=LEXICON['/unknown_message'])


# Хэндлер для коллбэков после выбора ДАТЫ на инлайн-клавиатуре
@router.callback_query(F.data.in_(database_func.get_datetime_from_db()))
async def process_date_is_confirm(callback: CallbackQuery):
    keyboard = create_times_kb(5, callback)
    await callback.message.edit_text(text='Время:',
                                     reply_markup=keyboard)


# Хэндлер для коллбэков после выбора ВРЕМЕНИ на инлайн-клавиатуре
@router.callback_query(DateTimeIsCorrect())
async def process_datetime_is_choose(callback: CallbackQuery):
    print(callback.message.chat.id)
    await database_func.change_datetime_status(str(callback.message.chat.id), callback.data)
    await callback.message.edit_text(
        text=f'Отлично! Вы записаны на {callback.data}!',
        show_alert=True,
        reply_markup=None
    )

# Хэндлер для колбэков после выбора ДАТЫ удаления записи
@router.callback_query(UserIsDeleteAppointment())
async def process_delete_date_appointment(callback: CallbackQuery):

    # ДЕЛАТЬ ПОКАЗ ВРЕМЕНИ ПОСЛЕ ВЫБОРА ДАТЫ В ВИДЕ КАЛЕНДАРЯ ИЛИ КНОПКИ НАЗАД


    keyboard = delete_my_appointment_time_kb(4, callback)
    await callback.message.edit_text(
        text=f'Выберите время:',
        reply_markup=keyboard
    )


# Хэндлер для обработки кнопки "Назад" в меню выбора времени
@router.callback_query(F.data == 'back_to_calendary')
async def process_back_to_calendary(callback: CallbackQuery):
    await callback.message.delete()
    await proccess_calendary_command(callback.message)


# Хэндлер для всех оставшихся колбэков, для теста
@router.callback_query()
async def process_datetime_is_choose(callback: CallbackQuery):
    print(callback.data)
    await callback.answer()
