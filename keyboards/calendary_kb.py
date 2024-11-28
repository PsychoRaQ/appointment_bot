from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from services.database_func import get_datetime_from_db, user_is_admin


# Функционал: у админа для создания клавиатуры редактирования расписания
# У пользователя для записи на конкретную дату и время

# Создание инлайн-клавиатуры календаря (даты)
def create_calendary_kb(width: int, user_id: str, **kwargs) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if kwargs:
        for button, text in kwargs.items():
            date_is_locked = [v['lock'] for i, v in text.items()]
            date_is_locked = '✅' if False in date_is_locked else '❌'
            if user_is_admin(user_id):
                buttons.append(InlineKeyboardButton(text=button + date_is_locked, callback_data=button + '_admin'))
            else:
                if date_is_locked == '✅':
                    buttons.append(InlineKeyboardButton(text=button, callback_data=button))

    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text='Закрыть', callback_data='close_calendary'))

    return kb_builder.as_markup()


# Создание инлайн-клавиатуры календаря (доступное время)
def create_times_kb(width: int, callback, user_id: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    db = get_datetime_from_db()
    try:
        cb_date, is_admin = callback.data.split('_')
        if ',' in cb_date:
            cb_date = cb_date.split(',')[0]
    except Exception as e:
        cb_date, is_admin = False, False
        print(e)
    if user_is_admin(user_id) and cb_date and is_admin:
        back_button = 'back_to_calendary_admin'
        for button, text in db[cb_date].items():
            date_is_locked = db[cb_date][button]['lock']
            date_is_locked = '✅' if date_is_locked is False else '❌'
            buttons.append(
                InlineKeyboardButton(text=button + date_is_locked, callback_data=f'{cb_date},{button}_admin'))
    else:
        back_button = 'back_to_calendary'
        for button, text in db[callback.data].items():
            if db[callback.data][button]['lock'] is False:
                buttons.append(InlineKeyboardButton(text=button, callback_data=f'{callback.data},{button}'))

    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text="Назад", callback_data=back_button), width=1)

    return kb_builder.as_markup()
