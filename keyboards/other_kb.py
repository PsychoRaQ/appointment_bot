from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonPollType
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def phone_kb():
    kb_builder = ReplyKeyboardBuilder()
    contact_btn = KeyboardButton(text='Отправить телефон',
                                 request_contact=True)
    kb_builder.row(contact_btn,width=1)

    return kb_builder.as_markup()

