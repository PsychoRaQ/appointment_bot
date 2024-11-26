from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from lexicon.lexicon import START_KB_TEXT
from services.database_func import get_user_data_from_db

# Создание инлайн-клавиатуры для команды /start
# СЕЙЧАС НЕ АКТУАЛЬНО
def create_start_kb(user_id):
    kb_builder = InlineKeyboardBuilder()

    user = get_user_data_from_db(user_id) # Достаем данные о пользователе из базы, на их основе строим клавиатуру
    name = 'yes_name' if user['name'] else 'no_name'
    phone = 'yes_phone' if user['phone'] else 'no_phone'

    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=START_KB_TEXT[phone], callback_data=phone),
        InlineKeyboardButton(text=START_KB_TEXT[name], callback_data=name)
    ]

    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()