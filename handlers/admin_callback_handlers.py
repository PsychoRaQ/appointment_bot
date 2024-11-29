from aiogram import Router, F

from aiogram.types import CallbackQuery

from filters.filters import UserIsAdmin, AdminChooseDate, AdminChooseTime
from handlers.admin_handlers import proccess_edit_calendary_command
from lexicon.lexicon import LEXICON_ADMIN

from keyboards.admin_calendary_kb import create_admin_times_kb
from services import database_func, service_func

router = Router()
router.message.filter(UserIsAdmin())


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
    user = database_func.admin_change_datetime_status(callback.data)
    cb_date, is_admin = callback.data.split('_')
    cb_date, cb_time = cb_date.split(',')
    keyboard = create_admin_times_kb(5, callback)
    if user:
        await service_func.send_message_to_user(str(callback.message.chat.id), user,
                                                f'{LEXICON_ADMIN['/admin_delete_appointment']}{cb_date}, {cb_time}')
    await callback.message.edit_text(
        text=f'Вы успешно изменили статус слота {cb_date}, {cb_time}!',
        reply_markup=keyboard
    )


# Хэндлер для обработки кнопки "Назад" в меню выбора времени
@router.callback_query(F.data == 'back_to_calendary_admin')
async def process_back_to_calendary(callback: CallbackQuery):
    await proccess_edit_calendary_command(callback.message)
