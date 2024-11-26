from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from lexicon.lexicon import DATE_LST
from config_data import config


# Создание инлайн-клавиатуры календаря (даты)
def create_calendary_kb(width: int, *args, **kwargs) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []

    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(text=DATE_LST[button] if button in DATE_LST else button,
                                                callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(text=button, callback_data=button))

    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup()

# Создание инлайн-клавиатуры календаря (доступное время)
def create_times_kb(width: int, obj) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    date = f'{obj.date}.{config.MONTH}'
    print(date)
    for t in obj.times:
        if obj.times[t].lock is False:
            buttons.append(InlineKeyboardButton(text=t, callback_data=f'{date},{obj.times[t].time}'))

    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup()
