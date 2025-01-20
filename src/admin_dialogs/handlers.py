# аиограм
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Select
# состояния
from src.fsm.admin_states import AdminEditCalendary, AllAppointments, Dispatch, Pcode
from src.fsm.user_states import UserNewAppointmentSG, UserAppointmentSG
# функции для работы с БД
from src.services.database_func import (get_slot_from_db, admin_change_slot_data, add_new_time_slot,
                                        get_slot_with_user_id, get_all_users_from_db, edit_admin_pcode,
                                        get_pcode_with_name, get_all_users_with_admin_id)
# сервисная функция для форматирования даты/времени
from src.services.service_func import datetime_format
# для рассылки
from src.nats.publishers import send_dispatch

'''
Хэндлеры для диалогов и геттеров (админка)
'''


##### АДМИН МЕНЮ

# Селектор диалогов из меню, открывает следующие диалоги
async def admin_dialog_selection(callback: CallbackQuery, widget: Select,
                                 dialog_manager: DialogManager, data: str):
    match data:
        case 'edit_calendary':
            await dialog_manager.start(state=AdminEditCalendary.first_month)
        case 'add_user_appointment':
            await dialog_manager.start(state=UserNewAppointmentSG.calendary_first_month)
        case 'delete_admin_appointment':
            result = await get_slot_with_user_id(dialog_manager.middleware_data['session'],
                                                 callback.message.chat.id)
            if len(result) == 0:
                await dialog_manager.start(state=UserAppointmentSG.no_one_appointment)
            else:
                await dialog_manager.start(state=UserAppointmentSG.delete_appointment_datetime)
        case 'all_appointments':
            await dialog_manager.start(state=AllAppointments.first_month)
        case 'dispatch':
            await dialog_manager.start(state=Dispatch.edit_dispatch)
        case 'pcodes':
            await dialog_manager.start(state=Pcode.main_pcode)
        case 'admin_settings':
            pass
        # старшая админка
        case 'all_admins_list':
            pass
        case _:
            print(data)


##### РАСПИСАНИЕ

# Админ выбрал дату для изменения слотов
async def admin_choose_date_for_edit(callback: CallbackQuery, widget: Select,
                                     dialog_manager: DialogManager, data: str):
    if data != 'locked':
        await dialog_manager.update({'date': data})
        await dialog_manager.switch_to(state=AdminEditCalendary.choose_time)


# Админ выбрал дату для отображения слотов
async def admin_choose_date_for_look(callback: CallbackQuery, widget: Select,
                                     dialog_manager: DialogManager, data: str):
    if data != 'locked':
        await dialog_manager.update({'date': data})
        await dialog_manager.switch_to(state=AllAppointments.appointments_list)


# Админ выбрал время слота
async def admin_choose_time_slot_for_edit(callback: CallbackQuery, widget: Select,
                                          dialog_manager: DialogManager, data: str):
    await dialog_manager.update({'time': data})
    date, text_date, time, text_time = await datetime_format(date=dialog_manager.dialog_data.get('date'), time=data)
    session = dialog_manager.middleware_data['session']
    admin_id = callback.from_user.id
    slot = await get_slot_from_db(date, time, admin_id, session)
    if slot:
        if slot.user_id == 0:
            status = 0 if slot.is_locked else 1
            await admin_change_slot_data(date, time, 0, status, admin_id, session)
        else:
            await dialog_manager.switch_to(state=AdminEditCalendary.user_on_date)
    else:
        await add_new_time_slot(date, time, admin_id, session)


# Админ решил закрыть слот на который записан пользователь
async def admin_close_slot(callback: CallbackQuery, widget: Select,
                           dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    date, text_date, time, text_time = await datetime_format(date=dialog_manager.dialog_data.get('date'),
                                                             time=dialog_manager.dialog_data.get('time'))
    admin_id = callback.from_user.id
    slot = await get_slot_from_db(date, time, admin_id, session)
    user_id = slot.user_id
    is_admin = user_id in dialog_manager.middleware_data['admin_ids']
    if user_id and is_admin is False:
        bot = dialog_manager.middleware_data['bot']
        await bot.send_message(user_id,
                               f'Администратор отменил Вашу запись {text_date} - {text_time}')
    await admin_change_slot_data(date, time, 0, True, admin_id, session)
    await dialog_manager.switch_to(state=AdminEditCalendary.choose_time)


##### РАССЫЛКА

# админ ввел текст для рассылки
async def edit_dispatch(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    await dialog_manager.update({'text': text})
    await dialog_manager.next(show_mode=ShowMode.EDIT)


# запуск рассылки
async def start_dispatch(callback: CallbackQuery,
                         widget: ManagedTextInput,
                         dialog_manager: DialogManager) -> None:
    session = dialog_manager.middleware_data['session']
    admin_ids = dialog_manager.middleware_data['admin_ids']
    user_ids = await get_all_users_with_admin_id(session, callback.from_user.id)
    message_text = bytes(dialog_manager.dialog_data.get('text'), encoding='utf-8')
    js = dialog_manager.middleware_data.get('js')
    subject = dialog_manager.middleware_data.get('dispatch_subject')

    for id in user_ids:
        if id not in admin_ids:
            await send_dispatch(js=js,
                                subject=subject,
                                delay=1,
                                user_id=id,
                                payload=message_text)

    await dialog_manager.next(show_mode=ShowMode.EDIT)


##### ПРОМОКОДЫ АДМИНОВ

# Обработчик-фильтр для проверки корректности промокода
def check_pcode(data: str) -> str:
    if 11 > len(data) > 1:
        return data
    raise ValueError


# изменение промокода
async def edit_pcode(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        data: str) -> None:
    dialog_manager.dialog_data.update({'pcode': data.upper()})
    await dialog_manager.next()


# изменение промокода
async def confirm_pcode(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager) -> None:
    pcode = dialog_manager.dialog_data.get('pcode')
    session = dialog_manager.middleware_data['session']
    admin_id = message.from_user.id
    unique = await get_pcode_with_name(pcode, session)
    if unique:
        await dialog_manager.switch_to(state=Pcode.error_pcode)
    else:
        await edit_admin_pcode(admin_id, pcode, session)
        await dialog_manager.next()
