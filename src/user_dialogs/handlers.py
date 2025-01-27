# аиограм
# системное
import datetime

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select

from src.fsm.admin_states import AdminMenuSG
# состояния
from src.fsm.user_states import StartSG, MainMenuSG, UserAppointmentSG, UserNewAppointmentSG, HelpSG, FeedbackSG
# импорт паблишера для отпавки отложенного сообщения
from src.nats.publishers import send_delay_message_publisher, new_subscribe
# функции для работы с базой данных
from src.services.database_func import (add_new_user, user_confirm_datetime, get_slot_with_user_id, user_is_register,
                                        get_slot_from_db, get_pcode_with_name, edit_admin_pcode)
# сервисные функции
from src.services.service_func import return_user_is_max_appointment, refactor_phone_number, datetime_format

'''
Хэндлеры для всех диалогов и геттеров (пользователь)
'''


#########################################################
# РЕГИСТРАЦИЯ НОВОГО ПОЛЬЗОВАТЕЛЯ


# Хэндлер для обработки кнопки "Продолжить" в меню выбора имени (берем имя пользователя из ТГ)
async def go_next(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await dialog_manager.update({'username': callback.message.chat.first_name})
    await dialog_manager.next()


# Хэндлер для кнопки "Пройти регистрацию сначала" в меню подтверждения данных
async def cancel_registration(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(StartSG.start_with_pcode)


# Хэндлер для кнопки "Подтвердить регистрацию" в меню подтверждения данных
async def confirm_registration(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    user_id = callback.message.chat.id
    username = dialog_manager.dialog_data.get('username')
    phone = dialog_manager.dialog_data.get('phone')
    session = dialog_manager.middleware_data['session']
    admin_id = dialog_manager.dialog_data.get('admin_id')
    grand_admin_id = dialog_manager.middleware_data.get('admin_ids')

    if admin_id in grand_admin_id:
        role = 'admin'
        next_state = AdminMenuSG.admin_menu
        await edit_admin_pcode(user_id, str(user_id), session)

        js = dialog_manager.middleware_data.get('js')
        subject = dialog_manager.middleware_data.get('subscribe_subject')
        kv = dialog_manager.middleware_data.get('subscribe_storage')

        days = 30
        await kv.put(str(user_id), bytes(str(days), encoding='utf-8'))
        await new_subscribe(js=js, subject=subject, delay=1, user_id=user_id, days=days)
    else:
        role = 'user'
        next_state = MainMenuSG.main_menu
    await add_new_user(session, user_id, username, phone, admin_id, role)
    await dialog_manager.start(state=next_state, mode=StartMode.RESET_STACK)


# проверка промокода
async def check_pcode(message: Message,
                      widget: ManagedTextInput,
                      dialog_manager: DialogManager,
                      text: str):
    session = dialog_manager.middleware_data['session']
    pcode_in_database = await get_pcode_with_name(text.upper(), session)
    if pcode_in_database:
        admin_id = pcode_in_database.admin_id
        pcode = pcode_in_database.pcode
        dialog_manager.dialog_data.update({'admin_id': admin_id, 'pcode': pcode})
        await dialog_manager.switch_to(state=StartSG.start_with_pcode)
    else:
        await dialog_manager.switch_to(state=StartSG.wrong_pcode)


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
            if result or callback.message.chat.id in dialog_manager.middleware_data.get('admin_ids'):
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
            await dialog_manager.start(state=HelpSG.help_menu)
        case 'feedback':
            await dialog_manager.start(state=FeedbackSG.feedback)
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
        role = dialog_manager.middleware_data.get('user_role')
        if role == 'admin':
            await dialog_manager.switch_to(state=UserNewAppointmentSG.write_admin_comment)
        else:
            session = dialog_manager.middleware_data.get('session')
            status = 'confirm'
            date, text_date, time, text_time = await datetime_format(date=dialog_manager.dialog_data.get('date'),
                                                                     time=data)
            admin_id = dialog_manager.dialog_data.get('admin_id')
            result = await user_confirm_datetime(callback.message.chat.id, date, time, status, admin_id, session)

            # настройка отложенного уведомления пользователю (за 24ч до записи)
            timestamp = datetime.datetime.now()
            time_to_send_notification = datetime.datetime.combine(date, time)

            delay = int((time_to_send_notification - timestamp).total_seconds()) - 3600 * 24

            js = dialog_manager.middleware_data.get('js')
            subject = dialog_manager.middleware_data.get('delay_del_subject')

            message_id = text_date + text_time

            kv = dialog_manager.middleware_data['storage']
            await kv.put(f'{message_id}', bytes(str(callback.message.chat.id), encoding='utf-8'))
            # отправляем сообщение в натс
            await send_delay_message_publisher(
                js=js,
                subject=subject,
                delay=delay,
                message_id=message_id,
                date=text_date,
                time=text_time,
            )

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
    date = date.replace('.', '-')
    date, text_date, time, text_time = await datetime_format(date, time)
    session = dialog_manager.middleware_data['session']
    role = dialog_manager.middleware_data.get('user_role')
    if role == 'admin':
        admin_id = callback.message.chat.id
    else:
        admin_id = dialog_manager.dialog_data.get('admin_id')
    slot = await get_slot_from_db(date, time, admin_id, session)
    comment = slot.comment
    await dialog_manager.update(
        {'text_date': text_date, 'text_time': text_time, 'comment': comment})
    await dialog_manager.next(show_mode=ShowMode.EDIT)

    # пользователь подтвердил удаление выбранного слота


async def user_is_confirm_delete_appointment(callback: CallbackQuery, widget: Select,
                                             dialog_manager: DialogManager):
    user_id = callback.message.chat.id
    session = dialog_manager.middleware_data['session']

    text_date = dialog_manager.dialog_data.get('text_date')
    text_time = dialog_manager.dialog_data.get('text_time')
    date, text_date, time, text_time = await datetime_format(text_date, text_time)
    role = dialog_manager.middleware_data.get('user_role')
    if role == 'admin':
        admin_id = callback.message.chat.id
    else:
        admin_id = dialog_manager.dialog_data.get('admin_id')

    status = 'delete'
    # отправляем в кв бакет состояние слота (отмена уведомления)
    message_id = text_date + text_time
    kv = dialog_manager.middleware_data['storage']
    await kv.put(f'{message_id}', b'0')

    user = await user_is_register(session, user_id)
    bot = dialog_manager.middleware_data['bot']
    if role == 'user':
        try:
            await bot.send_message(admin_id,
                                   f'Пользователь {user.username} отменил свою запись {text_date} - {text_time}\n'
                                   f'Телефон: {user.phone}')
        except:
            pass

    await user_confirm_datetime(user_id, date, time, status, admin_id, session)
    await dialog_manager.next(show_mode=ShowMode.EDIT)

    ###### ЗАПИСЬ ОТ ЛИЦА АДМИНА


async def new_appointment_from_admin(callback: CallbackQuery, widget: Select,
                                     dialog_manager: DialogManager):
    session = dialog_manager.middleware_data.get('session')
    status = 'confirm'
    date, text_date, time, text_time = await datetime_format(date=dialog_manager.dialog_data.get('date'),
                                                             time=dialog_manager.dialog_data.get('time'))
    comment = dialog_manager.dialog_data.get('comment')
    admin_id = callback.message.chat.id
    result = await user_confirm_datetime(admin_id, date, time, status, admin_id, session, comment)
    if result:
        await dialog_manager.switch_to(state=UserNewAppointmentSG.confirm_admin_datetime)
    else:
        await dialog_manager.switch_to(state=UserNewAppointmentSG.error_confirm)

    # функция если фильтр выше пройден


async def confirmed_admin_appointment(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    await dialog_manager.update({'comment': text})
    await dialog_manager.next(show_mode=ShowMode.EDIT)

    # обработчик кнопки "назад" из написания админ коммента


async def back_btn_adm_appointment(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(UserNewAppointmentSG.choose_time)
