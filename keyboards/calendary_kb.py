from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from lexicon.lexicon import DATE_LST
from config_data import config
from services.database_func import get_datetime_from_db

# Создание инлайн-клавиатуры календаря (даты)
def create_calendary_kb(width: int, **kwargs) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(text=button, callback_data=button))

    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup()


# Создание инлайн-клавиатуры календаря (доступное время)
def create_times_kb(width: int, callback) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if callback.data:
        db =  get_datetime_from_db()
        for button, text in db[callback.data].items():
            if db[callback.data][button]['lock'] is False:
                buttons.append(InlineKeyboardButton(text=button, callback_data=f'{callback.data},{button}'))

    kb_builder.row(*buttons, width=width)
    kb_builder.row(InlineKeyboardButton(text="Назад", callback_data='back_to_calendary'), width=1)

    return kb_builder.as_markup()
