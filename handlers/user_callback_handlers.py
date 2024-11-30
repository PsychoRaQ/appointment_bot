from aiogram import F, Router
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from keyboards.user_calendary_kb import create_times_kb, delete_my_appointment_time_kb
from filters.filters import (DateTimeIsCorrect, UserIsRegister, UserIsDeleteAppointment,
                             UserIsDeleteAppointmentTime, DateIsCorrect)
from services import database_func, service_func
from handlers import user_handlers

router = Router()
router.message.filter(UserIsRegister())


# Хэндлер для коллбэков после выбора ВРЕМЕНИ на инлайн-клавиатуре
@router.callback_query(DateTimeIsCorrect())
async def process_datetime_is_choose(callback: CallbackQuery):
    date, time = callback.data.split(',')
    if database_func.user_take_datetime(date, time, callback.message.chat.id):
        text_date = service_func.date_from_db_format(date)
        await callback.message.edit_text(
            text=f'Отлично! Вы записаны на {text_date} - {time}!',
            show_alert=True,
            reply_markup=None
        )
    else:
        await callback.message.edit_text(
            text=f'Ошибка записи!',
            show_alert=True,
            reply_markup=None
        )


# Хэндлер для коллбэков после выбора ДАТЫ на инлайн-клавиатуре
@router.callback_query(DateIsCorrect())
async def process_date_is_confirm(callback: CallbackQuery):
    keyboard = create_times_kb(5, callback)
    text_date = service_func.date_from_db_format(callback.data)
    await callback.message.edit_text(text=f'Доступное время записи на {text_date}:',
                                     reply_markup=keyboard)


# Хэндлер для колбэков после выбора ДАТЫ удаления записи
@router.callback_query(UserIsDeleteAppointment())
async def process_delete_date_appointment(callback: CallbackQuery):
    keyboard = delete_my_appointment_time_kb(4, callback)
    await callback.message.edit_text(
        text=f'Выберите время:',
        reply_markup=keyboard
    )


# Хэндлер для колбэков после выбора ВРЕМЕНИ удаления записи
@router.callback_query(UserIsDeleteAppointmentTime())
async def process_delete_time_appointment(callback: CallbackQuery):
    user_id, cb_date, cb_time = callback.data.split('_delete_')
    text_date = service_func.date_from_db_format(cb_date)
    if database_func.user_take_datetime(cb_date, cb_time, 0):
        text = f'Вы отменили свою запись на {text_date} - {cb_time}!'
    else:
        text = 'Ошибка удаления записи.'
    await callback.message.edit_text(
        text=text,
        show_alert=True,
        reply_markup=None
    )


# Хэндлер для обработки кнопки "Закрыть" в меню выбора ДАТЫ КАЛЕНДАРЯ
@router.callback_query(F.data == 'close_calendary')
async def process_close_calendary(callback: CallbackQuery):
    await callback.message.delete()


# Хэндлер для обработки кнопки "Назад" в меню выбора времени
@router.callback_query(F.data == 'back_to_calendary')
async def process_back_to_calendary(callback: CallbackQuery):
    await user_handlers.proccess_calendary_command(callback.message)


# Хэндлер для обработки кнопки "Назад" в меню выбора удаления времени записи
@router.callback_query(F.data == 'back_to_delete_calendary')
async def process_back_to_delete_calendary(callback: CallbackQuery):
    await user_handlers.process_delete_my_appointment(callback.message)


# Хэндлер для обработки события "no_one_appointment" при удалении времени записи
@router.callback_query(F.data == 'close_delete_calendary')
async def process_back_to_calendary(callback: CallbackQuery):
    await callback.message.delete()


# Хэндлер для всех оставшихся колбэков, для теста
@router.callback_query()
async def process_exception_callback(callback: CallbackQuery):
    print(callback.data, 'Колбэк не распознан')
    await callback.message.edit_text(
        text=f'Произошла ошибка. Пожалуйста, повторите позже.',
        show_alert=True,
        reply_markup=None
    )
