from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from services.database_func import get_datetime_from_db
from lexicon.lexicon import LEXICON_ADMIN_COMMANDS, LEXICON_GENERAL_ADMIN_COMMANDS


# Кнопки для админки (главный админ)
def general_admin_kb():
    kb_builder = ReplyKeyboardBuilder()
    buttons_admin = [KeyboardButton(text=LEXICON_ADMIN_COMMANDS[text]) for text in LEXICON_ADMIN_COMMANDS]
    buttons_gen_admin = [KeyboardButton(text=LEXICON_GENERAL_ADMIN_COMMANDS[text]) for text in
                         LEXICON_GENERAL_ADMIN_COMMANDS]
    kb_builder.row(*buttons_admin + buttons_gen_admin, width=1)
    return kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


# Кнопки для админки (обычный админ)
def admin_kb():
    kb_builder = ReplyKeyboardBuilder()
    buttons_admin = [KeyboardButton(text=LEXICON_ADMIN_COMMANDS[text]) for text in LEXICON_ADMIN_COMMANDS]
    kb_builder.row(*buttons_admin, width=1)
    return kb_builder.as_markup(resize_keyboard=True)


# Создание инлайн-клавиатуры выбора действий при кнопке календаря в меню (у админа)
def start_calendary_admin_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text='Добавить запись', callback_data='admin_add_appointment'),
               InlineKeyboardButton(text='Изменить расписание', callback_data='admin_edit_appointment'),
               InlineKeyboardButton(text='Закрыть', callback_data='close_calendary')]
    kb_builder.row(*buttons, width=2)
    return kb_builder.as_markup()


# Создание инлайн-клавиатуры календаря (в зависимости от выбора - изменение расписания или редактирование записей)
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


# Создание инлайн-клавиатуры админ-календаря (доступное время) для изменения расписания
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
