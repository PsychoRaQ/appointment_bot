from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from services import database_func, callback_data_factory
from lexicon.lexicon import LEXICON_ADMIN_COMMANDS, LEXICON_GENERAL_ADMIN_COMMANDS

'''
Функции связанные с генерацией
inline-клавиатур для администратора
'''


# Кнопки для админки (главный админ)
def general_admin_kb() -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()
    buttons_admin = [KeyboardButton(text=LEXICON_ADMIN_COMMANDS[text]) for text in LEXICON_ADMIN_COMMANDS]
    buttons_gen_admin = [KeyboardButton(text=LEXICON_GENERAL_ADMIN_COMMANDS[text]) for text in
                         LEXICON_GENERAL_ADMIN_COMMANDS]
    kb_builder.row(*buttons_admin + buttons_gen_admin, width=1)
    return kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


# Кнопки для админки (обычный админ)
def admin_kb() -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()
    buttons_admin = [KeyboardButton(text=LEXICON_ADMIN_COMMANDS[text]) for text in LEXICON_ADMIN_COMMANDS]
    kb_builder.row(*buttons_admin, width=1)
    return kb_builder.as_markup(resize_keyboard=True)


# Создание инлайн-клавиатуры выбора действий при кнопке календаря в меню (у админа)
def start_calendary_admin_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text='Добавить запись',
                                    callback_data=callback_data_factory.CallbackFactoryForAdminCalendary(
                                        user_id=0,
                                        date='',
                                        time='',
                                        status='AddAppoint'
                                    ).pack()),
               InlineKeyboardButton(text='Изменить расписание',
                                    callback_data=callback_data_factory.CallbackFactoryForAdminCalendary(
                                        user_id=0,
                                        date='',
                                        time='',
                                        status='EditAppoint'
                                    ).pack()),
               InlineKeyboardButton(text='Закрыть',
                                    callback_data=callback_data_factory.CallbackFactoryForUserCalendary(
                                        user_id=0,
                                        date='',
                                        time='',
                                        status='CloseDateKeyboard'
                                    ).pack())]
    kb_builder.row(*buttons, width=2)
    return kb_builder.as_markup()


# Создание инлайн-клавиатуры календаря (в зависимости от выбора - изменение расписания или редактирование записей)
def create_admin_calendary_date_kb(width: int,
                                   callback_data: callback_data_factory.CallbackFactoryForAdminCalendary) -> InlineKeyboardMarkup | bool:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    dates = database_func.return_dates_or_times_to_admin_calendary('Dates')
    if callback_data.status == 'EditAppoint':
        for date in dates:
            date = date[0]
            slots = database_func.get_two_slots_where('date', date, 'is_locked', False, '*')
            date_is_locked = '✅' if slots else '❌'
            year, month, day = date.split('-')
            buttons.append(InlineKeyboardButton(text=f'{day}.{month}' + date_is_locked,
                                                callback_data=callback_data_factory.CallbackFactoryForAdminCalendary(
                                                    user_id=0,
                                                    date=date,
                                                    time='',
                                                    status='AdmDate'
                                                ).pack()))

        kb_builder.row(*buttons, width=width)
        kb_builder.row(
            InlineKeyboardButton(text='Закрыть', callback_data=callback_data_factory.CallbackFactoryForUserCalendary(
                user_id=0,
                date='',
                time='',
                status='CloseDateKeyboard'
            ).pack()))
        return kb_builder.as_markup()


# Создание инлайн-клавиатуры админ-календаря (доступное время) для изменения расписания
def create_admin_times_kb(width: int,
                          callback_data: callback_data_factory.CallbackFactoryForAdminCalendary) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    cb_date = callback_data.date
    all_times = database_func.return_dates_or_times_to_admin_calendary('Times')
    for time in all_times:
        time = time[0]
        buttons.append(
            InlineKeyboardButton(text=time + '❌', callback_data=callback_data_factory.CallbackFactoryForAdminCalendary(
                user_id=0,
                date=cb_date,
                time=time,
                status='AdmDateTime'
            ).pack()))
    slots = database_func.get_one_slots_where('date', cb_date, '*')
    if slots:
        for slot in slots:
            id, date, time, is_locked, user_id = slot
            date_is_locked = '✅' if is_locked == 0 else '❌'
            if date_is_locked == '✅' and user_id:
                date_is_locked += '🙋‍'
            for i, v in enumerate(buttons):
                if v.text == time + '❌':
                    buttons[i] = InlineKeyboardButton(text=time + date_is_locked,
                                                      callback_data=callback_data_factory.CallbackFactoryForAdminCalendary(
                                                          user_id=0,
                                                          date=cb_date,
                                                          time=time,
                                                          status='AdmDateTime'
                                                      ).pack())

    kb_builder.row(*buttons, width=width)
    kb_builder.row(
        InlineKeyboardButton(text="Назад", callback_data=callback_data_factory.CallbackFactoryForAdminCalendary(
            user_id=0,
            date='',
            time='',
            status='EditAppoint'
        ).pack(), width=1))
    return kb_builder.as_markup()
