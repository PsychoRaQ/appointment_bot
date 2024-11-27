from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from services import database_func

# Кнопка для отправки телефона при регистрации в боте
def phone_kb():
    kb_builder = ReplyKeyboardBuilder()
    contact_btn = KeyboardButton(text='Отправить телефон',
                                 request_contact=True)
    kb_builder.row(contact_btn, width=1)

    return kb_builder.as_markup()


# Инлайн-клавиатура с ДАТАМИ для удаления записи
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

# Инлайн-клавиатура с ВРЕМЕНЕМ для удаления записи
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
