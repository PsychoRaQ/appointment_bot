from aiogram.types import Message, CallbackQuery, User
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select

from fsm.states import (StartSG, MainMenuSG, UserAppointmentSG, UserNewAppointmentSG)
from services.database_func import new_user_to_db, user_take_datetime
from services.service_func import refactor_phone_number, return_user_is_max_appointment


#########################################################
# РЕГИСТРАЦИЯ НОВОГО ПОЛЬЗОВАТЕЛЯ


# Хэндлер для обработки кнопки "Продолжить" в меню выбора имени (берем имя пользователя из ТГ)
async def go_next(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await dialog_manager.update({'username': callback.message.chat.first_name})
    await dialog_manager.next()


# Хэндлер для кнопки "Пройти регистрацию сначала" в меню подтверждения данных
async def cancel_registration(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(StartSG.start)


# Хэндлер для кнопки "Подтвердить регистрацию" в меню подтверждения данных
async def confirm_registration(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    user_id = callback.message.chat.id
    username = dialog_manager.dialog_data.get('username')
    phone = dialog_manager.dialog_data.get('phone')
    if new_user_to_db(user_id, username, phone):
        await dialog_manager.done()
        # await callback.message.answer(
        #     text=f'{username}, Вы успешно зарегистрировались и можете использовать весь функционал бота.\n\n'
        #          f'Если меню не открылось автоматически - пожалуйста, откройте его при помощи кнопки слева от чата, или'
        #          f'отправьте команду "/start" в чат.')
        await dialog_manager.start(state=MainMenuSG.main_menu)
    else:
        print('Ошибка при регистрации')


# Обработчик-фильтр для проверки корректности имени пользователя
def check_username(data: str) -> str:
    if data.isalpha() and len(data) < 10:
        return data
    raise ValueError


# Обработчик-фильтр для проверки корректности телефона пользователя
def check_phone(data: str) -> str:
    if len(data) == 12:
        if data[0] == '+' and data[1] == '7' and data[1:].isdigit():
            return data
    else:
        if (data[0] == '8' or data[0] == '7') and len(data) == 11:
            return data
    raise ValueError


# Хэндлер, который сработает, если пользователь ввел корректное имя/телефон
async def correct_input(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    if text.isalpha():
        await dialog_manager.update({'username': text})
    else:
        phone = refactor_phone_number(text)
        await dialog_manager.update({'phone': phone})
    await dialog_manager.next(show_mode=ShowMode.EDIT)


# Хэндлер, который сработает на ввод некорректного имени/телефона
async def error_input(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError) -> None:
    await message.answer(
        text='Вы ввели некорректное значение.\n Пожалуйста, введите правильно.'
    )


##########################################################################
# ГЛАВНОЕ МЕНЮ БОТА

# Селектор диалогов из главного меню, открывает следующие диалоги
async def user_dialog_selection(callback: CallbackQuery, widget: Select,
                                dialog_manager: DialogManager, data: str):
    match data:
        case 'new_appointment':
            print(callback.message.chat.id)
            if return_user_is_max_appointment(callback.message.chat.id):
                await dialog_manager.start(state=UserNewAppointmentSG.calendary_first_month)
            else:
                print('Чет многовато')
        case 'delete_appointment':
            print(data)
        case 'my_appointment':
            await dialog_manager.start(state=UserAppointmentSG.main)
        case 'help':
            print(data)
        case 'feedback':
            print(data)
        case _:
            print(data)


##############################################################################
# ВЫБОР ДАТЫ И ВРЕМЕНИ ДЛЯ ЗАПИСИ ПОЛЬЗОВАТЕЛЯ

# Пользователь выбрал дату для записи
async def user_new_date_appointment(callback: CallbackQuery, widget: Select,
                                    dialog_manager: DialogManager, data: str):
    if data != 'locked':
        await dialog_manager.update({'date': data})
        await dialog_manager.switch_to(state=UserNewAppointmentSG.choose_time)


# Пользователь выбрал время для записи
async def user_new_time_appointment(callback: CallbackQuery, widget: Select,
                                    dialog_manager: DialogManager, data: str):
    if data:
        await dialog_manager.update({'time': data})
        time = data
        date = dialog_manager.dialog_data.get('date').split('-')
        new_date = f'{date[2]}-{date[1]}-{date[0]}'
        if user_take_datetime(new_date, time, callback.message.chat.id):
            await dialog_manager.switch_to(state=UserNewAppointmentSG.confirm_datetime)
        else:
            await dialog_manager.switch_to(state=UserNewAppointmentSG.error_confirm)
