from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from filters.filters import UserIsAdmin, AdminChooseDate, DateTimeIsCorrect, AdminChooseTime
from lexicon.lexicon import LEXICON_ADMIN, LEXICON_ADMIN_COMMANDS

from keyboards.other_kb import admin_kb
from keyboards.calendary_kb import (start_calendary_admin_kb, create_admin_calendary_date_kb,
                                    create_admin_times_kb)
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
    keyboard = start_calendary_admin_kb()
    await message.answer(text=LEXICON_ADMIN['/what_you_need'],
                         reply_markup=keyboard)


# Хэндлер для команды "Изменить расписание"
@router.message(F.text == LEXICON_ADMIN_COMMANDS['/edit_calendary'])
async def proccess_edit_calendary_command(message: Message):
    await message.delete()
    status = 'admin_edit_appointment'
    keyboard = create_admin_calendary_date_kb(5, status=status, **database_func.get_datetime_from_db())
    await message.answer(LEXICON_ADMIN['/edit_calendary'],
                         reply_markup=keyboard)


# Хэндлер для обработки колбэков "Изменить расписание"
@router.callback_query(F.data == 'admin_edit_appointment')
async def process_date_is_confirm(callback: CallbackQuery):
    await proccess_edit_calendary_command(callback.message)


# Хэндлер для обработки колбэков "Добавить запись"
@router.callback_query(F.data == 'admin_add_appointment')
async def process_date_is_confirm(callback: CallbackQuery):
    await callback.message.edit_text(text='В разработке...',
                                     reply_markup=None)


# Хэндлер для коллбэков после выбора ДАТЫ на инлайн-клавиатуре
@router.callback_query(AdminChooseDate())
async def process_date_is_confirm(callback: CallbackQuery):
    cb_date, is_admin = callback.data.split('_')
    if ',' in cb_date:
        cb_date, cb_time = cb_date.split(',')
    keyboard = create_admin_times_kb(5, callback)
    await callback.message.edit_text(text=f'Доступные слоты на {cb_date}:',
                                     reply_markup=keyboard)


# Хэндлер для коллбэков после выбора ВРЕМЕНИ на инлайн-клавиатуре
@router.callback_query(AdminChooseTime())
async def process_datetime_is_choose(callback: CallbackQuery):
    user = database_func.admin_change_datetime_status(str(callback.message.chat.id), callback.data)
    cb_date, is_admin = callback.data.split('_')
    cb_date, cb_time = cb_date.split(',')
    keyboard = create_admin_times_kb(5, callback)
    if user:
        await service_func.send_message_to_user(str(callback.message.chat.id),
                                                user,
                                                f'{LEXICON_ADMIN['/admin_delete_appointment']}{cb_date}, {cb_time}')

    await callback.message.edit_text(
        text=f'Вы успешно изменили статус слота {cb_date}, {cb_time}!',
        reply_markup=keyboard
    )


# Хэндлер для обработки кнопки "Назад" в меню выбора времени
@router.callback_query(F.data == 'back_to_calendary_admin')
async def process_back_to_calendary(callback: CallbackQuery):
    await proccess_edit_calendary_command(callback.message)
