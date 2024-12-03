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
        cb_date = service_func.date_from_db_format(cb_date)
    keyboard = create_admin_times_kb(4, callback)
    if keyboard:
        await callback.message.edit_text(text=f'Доступные слоты на {cb_date}:',
                                         reply_markup=keyboard)
    else:
        await callback.message.edit_text(text=f'Ошибка отображения клавиатуры.',
                                         reply_markup=None)


# Хэндлер для коллбэков после выбора ВРЕМЕНИ на инлайн-клавиатуре
@router.callback_query(AdminChooseTime())
async def process_datetime_is_choose(callback: CallbackQuery):
    cb_date, is_admin = callback.data.split('_')
    cb_date, cb_time = cb_date.split(',')
    slot = database_func.get_two_slots_where('date', cb_date, 'time', cb_time, 'user_id, is_locked')
    if slot:
        slot = slot[0]
        user, current_status = slot
        current_status = 0 if current_status == 1 else 1
        database_func.admin_change_is_locked_status(cb_date, cb_time, current_status)

        if user:
            await service_func.send_message_to_user(str(callback.message.chat.id), user,
                                                    f'{LEXICON_ADMIN['/admin_delete_appointment']}{cb_date}, {cb_time}')
    else:
        database_func.add_new_slot(cb_date, cb_time)

    keyboard = create_admin_times_kb(4, callback)
    await callback.message.edit_text(
        text=f'Вы успешно изменили статус слота {cb_date}, {cb_time}!',
        reply_markup=keyboard
    )


# Хэндлер для обработки кнопки "Назад" в меню выбора времени
@router.callback_query(F.data == 'back_to_calendary_admin')
async def process_back_to_calendary(callback: CallbackQuery):
    await proccess_edit_calendary_command(callback.message)
