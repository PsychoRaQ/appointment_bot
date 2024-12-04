from aiogram import Router, F, Bot

from aiogram.types import CallbackQuery

from filters.filters import UserIsAdmin
from lexicon.lexicon import LEXICON_ADMIN

from keyboards.admin_calendary_kb import create_admin_times_kb, create_admin_calendary_date_kb
from services import database_func, service_func, callback_data_factory
import logging

router = Router()
router.message.filter(UserIsAdmin())

logger = logging.getLogger(__name__)

'''
Обработка callback'ов
связанных с администраторами
'''


# Хэндлер для обработки колбэков "Изменить расписание"
@router.callback_query(callback_data_factory.CallbackFactoryForAdminCalendary.filter(F.status == 'EditAppoint'))
async def process_date_is_confirm(callback: CallbackQuery,
                                  callback_data: callback_data_factory.CallbackFactoryForAdminCalendary):
    keyboard = create_admin_calendary_date_kb(4, callback_data)
    await callback.message.edit_text(text=LEXICON_ADMIN['/edit_calendary'],
                                     reply_markup=keyboard)


# Хэндлер для обработки колбэков "Добавить запись"
@router.callback_query(callback_data_factory.CallbackFactoryForAdminCalendary.filter(F.status == 'AddAppoint'))
async def process_date_is_confirm(callback: CallbackQuery):
    await callback.message.edit_text(text='В разработке...',
                                     reply_markup=None)


# Хэндлер для коллбэков после выбора ДАТЫ на инлайн-клавиатуре
@router.callback_query(callback_data_factory.CallbackFactoryForAdminCalendary.filter(F.status == 'AdmDate'))
async def process_date_is_confirm(callback: CallbackQuery,
                                  callback_data: callback_data_factory.CallbackFactoryForAdminCalendary):
    date = callback_data.date
    text_date = service_func.date_from_db_format(date)
    keyboard = create_admin_times_kb(4, callback_data)
    if keyboard:
        await callback.message.edit_text(text=f'Доступные слоты на {text_date}:',
                                         reply_markup=keyboard)


# Хэндлер для коллбэков после выбора ВРЕМЕНИ на инлайн-клавиатуре
@router.callback_query(callback_data_factory.CallbackFactoryForAdminCalendary.filter(F.status == 'AdmDateTime'))
async def process_datetime_is_choose(callback: CallbackQuery,
                                     callback_data: callback_data_factory.CallbackFactoryForAdminCalendary, bot: Bot):
    date = callback_data.date
    time = callback_data.time
    slot = database_func.get_two_slots_where('date', date, 'time', time, 'user_id, is_locked')
    if slot:
        slot = slot[0]
        user, current_status = slot
        current_status = 0 if current_status == 1 else 1
        database_func.admin_change_is_locked_status(date, time, current_status)
        if user:
            await service_func.send_message_to_user(str(callback.message.chat.id), user,
                                                    f'{LEXICON_ADMIN['/admin_delete_appointment']}{date}, {time}', bot)
    else:
        database_func.add_new_slot(date, time)

    keyboard = create_admin_times_kb(4, callback_data)
    await callback.message.edit_text(
        text=f'Вы успешно изменили статус слота {date}, {time}!',
        reply_markup=keyboard
    )
