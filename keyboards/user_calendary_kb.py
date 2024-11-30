from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from services import database_func, service_func


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
        buttons.append(InlineKeyboardButton(text=text_date, callback_data=callback_date))
    if len(buttons) == 0:
        return False
    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text='Закрыть', callback_data='close_calendary'))
    return kb_builder.as_markup()


# Создание инлайн-клавиатуры календаря (доступное время)
def create_times_kb(width: int, callback) -> InlineKeyboardMarkup | bool:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    not_locked_times = database_func.get_open_times_with_date(callback.data)
    if not_locked_times:
        for slot in not_locked_times:
            callback_date = slot[0]
            callback_time = slot[1]
            buttons.append(InlineKeyboardButton(text=callback_time, callback_data=f'{callback_date},{callback_time}'))

    buttons = sorted(buttons, key=lambda x: x.text)
    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text="Назад", callback_data='back_to_calendary'), width=1)
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
            buttons.append(InlineKeyboardButton(text=text_date, callback_data=f'{user_id}_delete_{date}'))
    if not buttons:
        return 'no_one_appointment'
    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text='Закрыть', callback_data='close_delete_calendary'))
    return kb_builder.as_markup()


# Инлайн-клавиатура с ВРЕМЕНЕМ для удаления записи(пользовательская)
def delete_my_appointment_time_kb(width, callback):
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if callback.data:
        callback_data = callback.data.split('_delete_')
        user_id, date = callback_data[0], callback_data[1]
        slots = database_func.get_two_slots_where('date', date, 'user_id', user_id, 'date, time')
        if slots:
            for slot in slots:
                date, time = slot
                buttons.append(InlineKeyboardButton(text=time, callback_data=f'{user_id}_delete_{date}_delete_{time}'))
        if not buttons:
            buttons.append(InlineKeyboardButton(text='Назад', callback_data='no_one_appointment'))

    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text="Назад", callback_data='back_to_delete_calendary'), width=1)

    return kb_builder.as_markup()
