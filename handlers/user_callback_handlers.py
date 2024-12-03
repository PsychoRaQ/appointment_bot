from aiogram import F, Router
from aiogram.types import CallbackQuery
from keyboards.user_calendary_kb import create_times_kb, delete_my_appointment_time_kb
from filters.filters import UserIsRegister

from services import database_func, service_func, callback_data_factory
from handlers import user_handlers


router = Router()
router.message.filter(UserIsRegister())


# Хэндлер для коллбэков после выбора ВРЕМЕНИ на инлайн-клавиатуре
@router.callback_query(callback_data_factory.CallbackFactoryForUserCalendary.filter(F.status == 'UserChooseTime'))
async def process_datetime_is_choose(callback: CallbackQuery, callback_data: callback_data_factory.CallbackFactoryForUserCalendary):
    date = callback_data.date
    time = callback_data.time
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
@router.callback_query(callback_data_factory.CallbackFactoryForUserCalendary.filter(F.status == 'UserChooseDate'))
async def process_date_is_confirm(callback: CallbackQuery, callback_data: callback_data_factory.CallbackFactoryForUserCalendary):
    keyboard = create_times_kb(5, callback_data)
    text_date = service_func.date_from_db_format(callback_data.date)
    await callback.message.edit_text(text=f'Доступное время записи на {text_date}:',
                                     reply_markup=keyboard)


# Хэндлер для колбэков после выбора ДАТЫ удаления записи
@router.callback_query(callback_data_factory.CallbackFactoryForUserCalendary.filter(F.status == 'UserDelDate'))
async def process_delete_date_appointment(callback: CallbackQuery, callback_data: callback_data_factory.CallbackFactoryForUserCalendary):
    keyboard = delete_my_appointment_time_kb(4, callback_data)
    await callback.message.edit_text(
        text=f'Выберите время:',
        reply_markup=keyboard
    )


# Хэндлер для колбэков после выбора ВРЕМЕНИ удаления записи
@router.callback_query(callback_data_factory.CallbackFactoryForUserCalendary.filter(F.status == 'UserDelTime'))
async def process_delete_time_appointment(callback: CallbackQuery, callback_data = callback_data_factory.CallbackFactoryForUserCalendary):
    date = callback_data.date
    time = callback_data.time
    text_date = service_func.date_from_db_format(date)
    if database_func.user_take_datetime(date, time, 0):
        text = f'Вы отменили свою запись на {text_date} - {time}!'
    else:
        text = 'Ошибка удаления записи.'
    await callback.message.edit_text(
        text=text,
        show_alert=True,
        reply_markup=None
    )


# Хэндлер для обработки кнопки "Закрыть" в меню выбора ДАТЫ КАЛЕНДАРЯ
@router.callback_query(callback_data_factory.CallbackFactoryForUserCalendary.filter(F.status == 'CloseDeleteKeyboard'))
async def process_close_calendary(callback: CallbackQuery):
    await callback.message.delete()


# Хэндлер для обработки кнопки "Назад" в меню выбора времени
@router.callback_query(callback_data_factory.CallbackFactoryForUserCalendary.filter(F.status == 'BackToDateKeyboard'))
async def process_back_to_calendary(callback: CallbackQuery):
    await user_handlers.proccess_calendary_command(callback.message)


# Хэндлер для обработки кнопки "Назад" в меню выбора удаления времени записи
@router.callback_query(callback_data_factory.CallbackFactoryForUserCalendary.filter(F.status == 'BackToDeleteCalendary'))
async def process_back_to_delete_calendary(callback: CallbackQuery):
    await user_handlers.process_delete_my_appointment(callback.message)


# Хэндлер для обработки события "no_one_appointment" при удалении времени записи
@router.callback_query(callback_data_factory.CallbackFactoryForUserCalendary.filter(F.status == 'NoOneAppointment'))
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
