from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from filters.filters import UserIsAdmin, AdminChooseDate, DateTimeIsCorrect, AdminChooseTime
from lexicon.lexicon import LEXICON_ADMIN, LEXICON_ADMIN_COMMANDS

from keyboards.other_kb import admin_kb
from keyboards.calendary_kb import create_calendary_kb, create_times_kb
from services import database_func, service_func

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
    await message.answer(text='В разработке...')


@router.message(F.text == LEXICON_ADMIN_COMMANDS['/edit_calendary'])
async def proccess_edit_calendary_command(message: Message):
    await message.delete()
    keyboard = create_calendary_kb(5, str(message.chat.id), **database_func.get_datetime_from_db())
    await message.answer(LEXICON_ADMIN['/edit_calendary'],
                         reply_markup=keyboard)


# Хэндлер для коллбэков после выбора ДАТЫ на инлайн-клавиатуре
@router.callback_query(AdminChooseDate())
async def process_date_is_confirm(callback: CallbackQuery):
    cb_date, is_admin = callback.data.split('_')
    if ',' in cb_date:
        cb_date, cb_time = cb_date.split(',')
    keyboard = create_times_kb(5, callback, str(callback.message.chat.id))
    await callback.message.edit_text(text=f'Доступные слоты на {cb_date}:',
                                     reply_markup=keyboard)


# Хэндлер для коллбэков после выбора ВРЕМЕНИ на инлайн-клавиатуре
@router.callback_query(AdminChooseTime())
async def process_datetime_is_choose(callback: CallbackQuery):
    # Здесь админская функция для изменения статуса у даты-времени
    user = database_func.admin_change_datetime_status(str(callback.message.chat.id), callback.data)
    cb_date, is_admin = callback.data.split('_')
    cb_date, cb_time = cb_date.split(',')
    keyboard = create_times_kb(5,callback, str(callback.message.chat.id))
    if user:
        await service_func.send_message_to_user(str(callback.message.chat.id),
                                                user,
                                                f'{LEXICON_ADMIN['/admin_delete_appointment']}{cb_date}, {cb_time}')

    await callback.message.edit_text(
        text=f'Вы успешно изменили статус слота {cb_date}, {cb_time}!',
        reply_markup=keyboard
    )

# Хэндлер для коллбэков после выбора ВРЕМЕНИ на инлайн-клавиатуре
@router.callback_query(F.data_in)
async def process_datetime_is_choose(callback: CallbackQuery):
    # Здесь админская функция для изменения статуса у даты-времени
    database_func.admin_change_datetime_status(str(callback.message.chat.id), callback.data)
    cb_date, is_admin = callback.data.split('_')
    cb_date, cb_time = cb_date.split(',')
    keyboard = create_times_kb(5,callback, str(callback.message.chat.id))
    await callback.message.edit_text(
        text=f'Вы успешно изменили статус слота {cb_date}, {cb_time}!',
        reply_markup=keyboard
    )
# Хэндлер для обработки кнопки "Назад" в меню выбора времени
@router.callback_query(F.data == 'back_to_calendary_admin')
async def process_back_to_calendary(callback: CallbackQuery):
    await proccess_edit_calendary_command(callback.message)