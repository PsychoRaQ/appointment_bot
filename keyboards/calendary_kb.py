from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from services.database_func import get_datetime_from_db, user_is_admin


# Функционал: у админа для создания клавиатуры редактирования расписания
# У пользователя для записи на конкретную дату и время

# Создание инлайн-клавиатуры календаря (даты)
def create_calendary_kb(width: int, **kwargs) -> InlineKeyboardMarkup | bool:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if kwargs:
        for button, text in kwargs.items():
            date_is_locked = [v['lock'] for i, v in text.items()]
            print(date_is_locked)
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
    db = get_datetime_from_db()

    cb_date = callback.data
    if ',' in callback.data:
        cb_date = callback.data.split(',')[0]
    for button, text in db[cb_date].items():
        if db[cb_date][button]['lock'] is False:
            buttons.append(InlineKeyboardButton(text=button, callback_data=f'{cb_date},{button}'))

    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text="Назад", callback_data='back_to_calendary'), width=1)

    return kb_builder.as_markup()


def start_calendary_admin_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text='Добавить запись', callback_data='admin_add_appointment'),
               InlineKeyboardButton(text='Изменить расписание', callback_data='admin_edit_appointment'),
               InlineKeyboardButton(text='Закрыть', callback_data='close_calendary')]
    kb_builder.row(*buttons, width=2)
    return kb_builder.as_markup()


def create_admin_calendary_date_kb(width: int, status, **kwargs) -> InlineKeyboardMarkup | bool:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    if kwargs:
        for button, text in kwargs.items():
            date_is_locked = [v['lock'] for i, v in text.items()]
            date_is_locked = '✅' if False in date_is_locked else '❌'
            if status == 'admin_edit_appointment':
                buttons.append(InlineKeyboardButton(text=button + date_is_locked, callback_data=f'{button}_admin'))
            elif status == 'admin_add_appointment':
                pass
    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text='Закрыть', callback_data='close_calendary'))
    return kb_builder.as_markup()


# Создание инлайн-клавиатуры календаря (доступное время)
def create_admin_times_kb(width: int, callback) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    db = get_datetime_from_db()

    cb_date = callback.data.split('_')[0]
    if ',' in cb_date:
        cb_date = cb_date.split(',')[0]
    for button, text in db[cb_date].items():
        date_is_locked = db[cb_date][button]['lock']
        date_is_locked = '✅' if date_is_locked is False else '❌'
        buttons.append(
            InlineKeyboardButton(text=button + date_is_locked, callback_data=f'{cb_date},{button}_admin'))
    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text="Назад", callback_data='back_to_calendary_admin'), width=1)

    return kb_builder.as_markup()
