from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from services import database_func


# Функционал: у админа для создания клавиатуры редактирования расписания
# У пользователя для записи на конкретную дату и время

# Создание инлайн-клавиатуры календаря (даты)
def create_calendary_kb(width: int, **kwargs) -> InlineKeyboardMarkup | bool:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if kwargs:
        for button, text in kwargs.items():
            date_is_locked = [True if v['user'] or v['lock'] is True else False for i, v in text.items()]
            date_is_locked = False if False in date_is_locked else True
            if date_is_locked is False:
                buttons.append(InlineKeyboardButton(text=button, callback_data=button))

    if len(buttons) == 0:
        return False
    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text='Закрыть', callback_data='close_calendary'))
    return kb_builder.as_markup()


# Создание инлайн-клавиатуры календаря (доступное время)
def create_times_kb(width: int, callback) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    db = database_func.get_datetime_from_db()

    cb_date = callback.data
    if ',' in callback.data:
        cb_date = callback.data.split(',')[0]
    for button, text in db[cb_date].items():
        if db[cb_date][button]['lock'] is False and db[cb_date][button]['user'] is None:
            buttons.append(InlineKeyboardButton(text=button, callback_data=f'{cb_date},{button}'))

    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text="Назад", callback_data='back_to_calendary'), width=1)

    return kb_builder.as_markup()


# Инлайн-клавиатура с ДАТАМИ для удаления записи (пользовательская)
def delete_my_appointment_data_kb(width, user_id):
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    db = database_func.get_user_db()
    button_lst = [button for button in db[user_id]['date'].keys()]
    for button in sorted(button_lst):
        buttons.append(InlineKeyboardButton(text=button, callback_data=f'{user_id}_delete_{button}'))
    if buttons == []:
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
        db = database_func.get_user_data_from_db(user_id)

        button_lst = [button for button in db['date'][date]]
        for button in sorted(button_lst):
            buttons.append(InlineKeyboardButton(text=button, callback_data=f'{user_id}_delete_{date}_delete_{button}'))
        if buttons == []:
            buttons.append(InlineKeyboardButton(text='Назад', callback_data='no_one_appointment'))

    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text="Назад", callback_data='back_to_delete_calendary'), width=1)

    return kb_builder.as_markup()
