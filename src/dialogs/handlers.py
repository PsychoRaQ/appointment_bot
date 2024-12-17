import datetime

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select

from src.fsm.states import (StartSG, MainMenuSG, UserAppointmentSG, UserNewAppointmentSG)
from src.services.database_func import add_new_user, user_confirm_datetime, get_slot_with_user_id
from src.services.service_func import return_user_is_max_appointment, refactor_phone_number

'''
Хэндлеры для всех диалогов и геттеров
'''


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
    session = dialog_manager.middleware_data['session']

    await add_new_user(session, user_id, username, phone)
    await dialog_manager.done()
    await dialog_manager.start(MainMenuSG.main_menu)


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
        phone = await refactor_phone_number(text)
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
            result = await return_user_is_max_appointment(dialog_manager.middleware_data['session'],
                                                          callback.message.chat.id)
            if result:
                await dialog_manager.start(state=UserNewAppointmentSG.calendary_first_month)
            else:
                await dialog_manager.start(state=UserNewAppointmentSG.user_max_appointment)
        case 'my_appointment':
            result = await get_slot_with_user_id(dialog_manager.middleware_data['session'],
                                                 callback.message.chat.id)
            if len(result) == 0:
                await dialog_manager.start(state=UserAppointmentSG.no_one_appointment)
            else:
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

        convert_time = list(map(int, data.split(':')))
        convert_date = list(map(int, dialog_manager.dialog_data.get('date').split('-')))

        time = datetime.time(*convert_time)
        date = datetime.date(convert_date[2], convert_date[1], convert_date[0])
        session = dialog_manager.middleware_data['session']
        status = 'confirm'
        result = await user_confirm_datetime(callback.message.chat.id, date, time, status, session)
        if result:
            await dialog_manager.switch_to(state=UserNewAppointmentSG.confirm_datetime)
        else:
            await dialog_manager.switch_to(state=UserNewAppointmentSG.error_confirm)


################################################################################
# ПОЛЬЗОВАТЕЛЬ ХОЧЕТ ОТМЕНИТЬ ЗАПИСЬ

# пользователь выбрал "слот" для отмены
async def user_delete_appointment(callback: CallbackQuery, widget: Select,
                                  dialog_manager: DialogManager, data: str):
    date, time = data.split('-')
    date = list(map(int, date.split('.')))
    time = list(map(int, time.split(':')))

    await dialog_manager.update({'date': date, 'time': time, 'datetime_for_user': data})
    await dialog_manager.next(show_mode=ShowMode.EDIT)


# пользователь подтвердил удаление выбранного слота
async def user_is_confirm_delete_appointment(callback: CallbackQuery, widget: Select,
                                             dialog_manager: DialogManager):
    convert_date = dialog_manager.dialog_data.get('date')
    user_id = callback.message.chat.id
    session = dialog_manager.middleware_data['session']
    date = datetime.date(convert_date[2], convert_date[1], convert_date[0])
    time = datetime.time(*dialog_manager.dialog_data.get('time'))
    status = 'delete'

    await user_confirm_datetime(user_id, date, time, status, session)
    await dialog_manager.next(show_mode=ShowMode.EDIT)
