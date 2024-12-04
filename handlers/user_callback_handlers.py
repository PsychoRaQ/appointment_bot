from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery
from keyboards.user_calendary_kb import create_times_kb, delete_my_appointment_time_kb, create_calendary_kb, \
    delete_my_appointment_data_kb
from keyboards.other_kb import create_back_button_kb, create_main_menu_kb
from filters.filters import UserIsRegister
from lexicon.lexicon import LEXICON

from services import database_func, service_func, callback_data_factory
import logging

router = Router()
router.message.filter(UserIsRegister(), StateFilter(default_state))
logger = logging.getLogger(__name__)

'''
Обработка всех callback'ов
обычных зарегистрированных пользователей
(в т.ч. администраторов)
'''


# Хэндлер для пункта в главном меню "Открыть календарь"
@router.callback_query(callback_data_factory.CallbackFactoryForUserMenu.filter(F.status == 'Calendary'))
async def proccess_calendary_command(callback: CallbackQuery,
                                     callback_data: callback_data_factory.CallbackFactoryForUserMenu):
    if service_func.return_user_is_max_appointment(callback.message.chat.id):
        keyboard = create_back_button_kb()
        await callback.message.edit_text(text=LEXICON['/user_is_max_appointment'],
                                         reply_markup=keyboard)
    else:
        keyboard = create_calendary_kb(5)
        if keyboard:
            await callback.message.edit_text(text=LEXICON['/user_is_not_max_appointment'],
                                             reply_markup=keyboard)
        else:
            keyboard = create_back_button_kb()
            await callback.message.edit_text(text=LEXICON['/no_one_available_date'],
                                             show_alert=True,
                                             reply_markup=keyboard)


# Хэндлер для пункта в главном меню "Помощь"
@router.callback_query(callback_data_factory.CallbackFactoryForUserMenu.filter(F.status == 'Help'))
async def proccess_help_command(callback: CallbackQuery,
                                callback_data: callback_data_factory.CallbackFactoryForUserMenu):
    keyboard = create_back_button_kb()
    await callback.message.edit_text(text=LEXICON['/help'],
                                     reply_markup=keyboard)


# Хэндлер для "Отменить запись"
@router.callback_query(callback_data_factory.CallbackFactoryForUserMenu.filter(F.status == 'DelMyAppoint'))
async def proccess_delete_appointment_command(callback: CallbackQuery,
                                              callback_data: callback_data_factory.CallbackFactoryForUserMenu):
    keyboard = keyboard = delete_my_appointment_data_kb(3, str(callback.message.chat.id))
    if keyboard == 'no_one_appointment':
        keyboard = create_back_button_kb()
        await callback.message.edit_text(
            text=LEXICON['/no_one_appointment'],
            show_alert=True,
            reply_markup=keyboard
        )
    else:
        await callback.message.edit_text(text=LEXICON['/choose_date_to_delete'],
                                         reply_markup=keyboard)


# Хэндлер для пункта в главном меню "Помощь"
@router.callback_query(callback_data_factory.CallbackFactoryForUserMenu.filter(F.status == 'MyAppoint'))
async def proccess_my_appointment_command(callback: CallbackQuery,
                                          callback_data: callback_data_factory.CallbackFactoryForUserMenu):
    keyboard = create_back_button_kb()
    text = service_func.get_user_appointment_format_text(callback.message.chat.id)
    if not text:
        text = LEXICON['/no_one_appointment']
    else:
        text += f'\n{LEXICON['/user_appointment_end']}'
    await callback.message.edit_text(text=text,
                                     reply_markup=keyboard)


# Хэндлер для кнопок "назад"
@router.callback_query(callback_data_factory.CallbackFactoryForUserMenu.filter(F.status == 'BackMenu'))
async def proccess_backmenu_command(callback: CallbackQuery,
                                    callback_data: callback_data_factory.CallbackFactoryForUserMenu):
    keyboard = create_main_menu_kb()
    await callback.message.edit_text(text='Что делаем?',
                                     reply_markup=keyboard)


# Хэндлер для коллбэков после выбора ВРЕМЕНИ на инлайн-клавиатуре
@router.callback_query(callback_data_factory.CallbackFactoryForUserCalendary.filter(F.status == 'UserChooseTime'))
async def process_datetime_is_choose(callback: CallbackQuery,
                                     callback_data: callback_data_factory.CallbackFactoryForUserCalendary):
    date = callback_data.date
    time = callback_data.time
    keyboard = create_main_menu_kb()
    if database_func.user_take_datetime(date, time, callback.message.chat.id):
        text_date = service_func.date_from_db_format(date)
        await callback.message.edit_text(
            text=f'Отлично! Вы записаны на {text_date} - {time}!',
            show_alert=True,
            reply_markup=keyboard
        )
    else:
        await callback.message.edit_text(
            text=f'Ошибка записи!',
            show_alert=True,
            reply_markup=keyboard
        )


# Хэндлер для коллбэков после выбора ДАТЫ на инлайн-клавиатуре
@router.callback_query(callback_data_factory.CallbackFactoryForUserCalendary.filter(F.status == 'UserChooseDate'))
async def process_date_is_confirm(callback: CallbackQuery,
                                  callback_data: callback_data_factory.CallbackFactoryForUserCalendary):
    keyboard = create_times_kb(5, callback_data)
    text_date = service_func.date_from_db_format(callback_data.date)
    await callback.message.edit_text(text=f'Доступное время записи на {text_date}:',
                                     reply_markup=keyboard)


# Хэндлер для колбэков после выбора ДАТЫ удаления записи
@router.callback_query(callback_data_factory.CallbackFactoryForUserCalendary.filter(F.status == 'UserDelDate'))
async def process_delete_date_appointment(callback: CallbackQuery,
                                          callback_data: callback_data_factory.CallbackFactoryForUserCalendary):
    keyboard = delete_my_appointment_time_kb(4, callback_data)
    await callback.message.edit_text(
        text=f'Выберите время:',
        reply_markup=keyboard
    )


# Хэндлер для колбэков после выбора ВРЕМЕНИ удаления записи
@router.callback_query(callback_data_factory.CallbackFactoryForUserCalendary.filter(F.status == 'UserDelTime'))
async def process_delete_time_appointment(callback: CallbackQuery,
                                          callback_data=callback_data_factory.CallbackFactoryForUserCalendary):
    date = callback_data.date
    time = callback_data.time
    text_date = service_func.date_from_db_format(date)
    if database_func.user_take_datetime(date, time, 0):
        text = f'Вы отменили свою запись на {text_date} - {time}!'
    else:
        text = 'Ошибка удаления записи.'
    keyboard = create_main_menu_kb()
    await callback.message.edit_text(
        text=text,
        show_alert=True,
        reply_markup=keyboard
    )


# Хэндлер для обработки кнопки "Закрыть" в меню выбора ДАТЫ КАЛЕНДАРЯ
@router.callback_query(callback_data_factory.CallbackFactoryForUserCalendary.filter(F.status == 'CloseDateKeyboard'))
async def process_close_calendary(callback: CallbackQuery):
    await callback.message.delete()


# Хэндлер для обработки события "no_one_appointment" при удалении времени записи
@router.callback_query(callback_data_factory.CallbackFactoryForUserCalendary.filter(F.status == 'NoOneAppointment'))
async def process_back_to_calendary(callback: CallbackQuery):
    keyboard = create_back_button_kb()
    await callback.message.edit_text(text=LEXICON['/no_one_available_date'],
                                     reply_markup=keyboard)


# Хэндлер для всех оставшихся колбэков, для теста
@router.callback_query()
async def process_exception_callback(callback: CallbackQuery):
    logger.info(callback, 'Колбэк не распознан')
    await callback.message.edit_text(
        text=f'Произошла ошибка. Пожалуйста, повторите позже.',
        show_alert=True,
        reply_markup=None
    )
