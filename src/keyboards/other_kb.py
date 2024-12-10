from aiogram.types import KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from services import callback_data_factory
from lexicon.lexicon import LEXICON_COMMANDS

'''
Функции связанные с генерацией
разных inline-клавиатур для пользователей
'''


# Кнопка для отправки телефона при регистрации в боте
def phone_kb() -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()
    contact_btn = KeyboardButton(text='Отправить телефон',
                                 request_contact=True,
                                 )
    kb_builder.row(contact_btn, width=1)
    return kb_builder.as_markup(resize_keyboard=True)


# Создание инлайн-клавиатуры главного меню бота
def create_main_menu_kb() -> InlineKeyboardMarkup | bool:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    buttons.append(InlineKeyboardButton(text=LEXICON_COMMANDS['/help'],
                                        callback_data=callback_data_factory.CallbackFactoryForUserMenu(user_id=0,
                                                                                                       status='Help').pack(
                                        )))
    buttons.append(InlineKeyboardButton(text=LEXICON_COMMANDS['/calendary'],
                                        callback_data=callback_data_factory.CallbackFactoryForUserMenu(user_id=0,
                                                                                                       status='Calendary').pack(
                                        )))
    buttons.append(InlineKeyboardButton(text=LEXICON_COMMANDS['/my_appointment'],
                                        callback_data=callback_data_factory.CallbackFactoryForUserMenu(user_id=0,
                                                                                                       status='MyAppoint').pack(
                                        )))
    buttons.append(InlineKeyboardButton(text=LEXICON_COMMANDS['/delete_my_appointment'],
                                        callback_data=callback_data_factory.CallbackFactoryForUserMenu(user_id=0,
                                                                                                       status='DelMyAppoint').pack(
                                        )))
    kb_builder.row(*buttons, width=2)
    kb_builder.row(
        InlineKeyboardButton(text='Закрыть', callback_data=callback_data_factory.CallbackFactoryForUserCalendary(
            user_id=0,
            date='',
            time='',
            status='CloseDateKeyboard'
        ).pack()))

    return kb_builder.as_markup()


# Создание инлайн-клавиатуры с кнопкой "закрыть"
def create_back_button_kb() -> InlineKeyboardMarkup | bool:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(text='Назад в главное меню',
                             callback_data=callback_data_factory.CallbackFactoryForUserMenu(
                                 user_id=0,
                                 status='BackMenu'
                             ).pack()))

    return kb_builder.as_markup()

# Создание инлайн-клавиатуры для подтверждения регистрации пользователя
def create_confirm_registration_keyboard() -> InlineKeyboardMarkup | bool:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(text='Подтвердить данные',
                             callback_data=callback_data_factory.CallbackFactoryForUserMenu(
                                 user_id=0,
                                 status='RegConfirm'
                             ).pack()),
        InlineKeyboardButton(text='Начать регистрацию сначала',
                             callback_data=callback_data_factory.CallbackFactoryForUserMenu(
                                 user_id=0,
                                 status='NoReg'
                             ).pack()), width=1)

    return kb_builder.as_markup()

