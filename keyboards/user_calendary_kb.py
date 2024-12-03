from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from services import database_func, service_func, callback_data_factory

# Создание инлайн-клавиатуры календаря (даты)
def create_calendary_kb(width: int) -> InlineKeyboardMarkup | bool:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    not_locked_dates = database_func.get_two_slots_where('is_locked', False, 'user_id', False, '*')
    dates_list = []
    for slot in not_locked_dates:
        callback_date = slot[1]
        if callback_date in dates_list:
            continue
        else:
            dates_list.append(callback_date)
        date = slot[1].split('-')
        text_date = f'{date[2]}.{date[1]}'
        buttons.append(InlineKeyboardButton(text=text_date, callback_data=callback_data_factory.CallbackFactoryForUserCalendary(
            user_id=0,
            date=callback_date,
            time='',
            status='UserChooseDate'
        ).pack()))
    if len(buttons) == 0:
        return False
    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text='Закрыть', callback_data=callback_data_factory.CallbackFactoryForUserCalendary(
            user_id=0,
            date='',
            time='',
            status='CloseDateKeyboard'
        ).pack()))
    return kb_builder.as_markup()


# Создание инлайн-клавиатуры календаря (доступное время)
def create_times_kb(width: int, callback_data) -> InlineKeyboardMarkup | bool:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    not_locked_times = database_func.get_open_times_with_date(callback_data.date)
    if not_locked_times:
        for slot in not_locked_times:
            callback_date = slot[0]
            callback_time = slot[1]
            buttons.append(InlineKeyboardButton(text=callback_time, callback_data=callback_data_factory.CallbackFactoryForUserCalendary(
                user_id=0,
                date=callback_date,
                time=callback_time,
                status='UserChooseTime'
            ).pack()))

    buttons = sorted(buttons, key=lambda x: x.text)
    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text="Назад", callback_data=callback_data_factory.CallbackFactoryForUserCalendary(
        user_id = 0,
        date='',
        time='',
        status='BackToDateKeyboard'
    ).pack()), width=1)
    return kb_builder.as_markup()


# Инлайн-клавиатура с ДАТАМИ для удаления записи (пользовательская)
def delete_my_appointment_data_kb(width, user_id):
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    slots = database_func.get_user_appointment(user_id)
    dates_list = []
    if slots:
        for slot in slots:
            date, time = slot
            if date in dates_list:
                continue
            dates_list.append(date)
            text_date = service_func.date_from_db_format(date)
            buttons.append(InlineKeyboardButton(text=text_date, callback_data=callback_data_factory.CallbackFactoryForUserCalendary(
                user_id=user_id,
                date=date,
                time='',
                status='UserDelDate'
            ).pack()))
    if not buttons:
        return 'no_one_appointment'
    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text='Закрыть', callback_data=callback_data_factory.CallbackFactoryForUserCalendary(
                user_id=user_id,
                date='',
                time='',
                status='CloseDeleteKeyboard'
            ).pack()), width=1)
    return kb_builder.as_markup()


# Инлайн-клавиатура с ВРЕМЕНЕМ для удаления записи(пользовательская)
def delete_my_appointment_time_kb(width, callback_data):
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    user_id = callback_data.user_id
    date = callback_data.date
    slots = database_func.get_two_slots_where('date', date, 'user_id', user_id, 'date, time')
    if slots:
        for slot in slots:
                date, time = slot
                buttons.append(InlineKeyboardButton(text=time, callback_data=callback_data_factory.CallbackFactoryForUserCalendary(
                user_id=user_id,
                date=date,
                time=time,
                status='UserDelTime'
            ).pack()))
        if not buttons:
            buttons.append(InlineKeyboardButton(text='Назад', callback_data=callback_data_factory.CallbackFactoryForUserCalendary(
                user_id=0,
                date='',
                time='',
                status='NoOneAppointment'
            ).pack()))

    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text="Назад", callback_data=callback_data_factory.CallbackFactoryForUserCalendary(
                user_id=0,
                date='',
                time='',
                status='BackToDeleteCalendary'
            ).pack()), width=1)

    return kb_builder.as_markup()
