from aiogram import F, Router
from aiogram.types import CallbackQuery
from keyboards.calendary_kb import create_times_kb
from keyboards.other_kb import delete_my_appointment_time_kb
from filters.filters import (DateTimeIsCorrect, UserIsRegister, UserIsDeleteAppointment,
    UserIsDeleteAppointmentTime)
from services import database_func
from handlers import user_handlers


router = Router()
router.message.filter(UserIsRegister())


# Хэндлер для коллбэков после выбора ДАТЫ на инлайн-клавиатуре
@router.callback_query(F.data.in_(database_func.get_datetime_from_db()))
async def process_date_is_confirm(callback: CallbackQuery):
    keyboard = create_times_kb(5, callback)
    await callback.message.edit_text(text=f'Доступное время записи на {callback.data}:',
                                     reply_markup=keyboard)


# Хэндлер для коллбэков после выбора ВРЕМЕНИ на инлайн-клавиатуре
@router.callback_query(DateTimeIsCorrect())
async def process_datetime_is_choose(callback: CallbackQuery):
    database_func.change_datetime_status(str(callback.message.chat.id), callback.data, 'add')
    await callback.message.edit_text(
        text=f'Отлично! Вы записаны на {''.join(callback.data.split('_')[0])}!',
        show_alert=True,
        reply_markup=None
    )


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
    database_func.change_datetime_status(user_id,f'{cb_date},{cb_time}', 'clear')
    await callback.message.edit_text(
        text=f'Вы удалили запись на {cb_date}, {cb_time}!',
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
async def process_datetime_is_choose(callback: CallbackQuery):
    print(callback.data, 'Колбэк не распознан')
    await callback.answer()