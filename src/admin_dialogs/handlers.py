from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select

from src.fsm.admin_states import AdminEditCalendary, AllAppointments
from src.services.database_func import (get_slot_from_db, admin_change_slot_data, add_new_time_slot,
                                        get_slot_with_user_id)
from src.services.service_func import datetime_format
from src.fsm.user_states import UserNewAppointmentSG, UserAppointmentSG

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
            print(data)
        case _:
            print(data)


##### Изменение расписания

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
    slot = await get_slot_from_db(date, time, session)
    if slot:
        if slot.user_id == 0:
            status = 0 if slot.is_locked else 1
            await admin_change_slot_data(date, time, 0, status, session)
        else:
            await dialog_manager.switch_to(state=AdminEditCalendary.user_on_date)
    else:
        await add_new_time_slot(date, time, session)


# Админ решил закрыть слот на который записан пользователь
async def admin_close_slot(callback: CallbackQuery, widget: Select,
                           dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    date, text_date, time, text_time = await datetime_format(date=dialog_manager.dialog_data.get('date'),
                                                             time=dialog_manager.dialog_data.get('time'))
    slot = await get_slot_from_db(date, time, session)
    user_id = slot.user_id
    is_admin = user_id in dialog_manager.middleware_data['admin_ids']
    if user_id and is_admin is False:
        bot = dialog_manager.middleware_data['bot']
        await bot.send_message(user_id,
                               f'Администратор отменил Вашу запись {text_date} - {text_time}')
    await admin_change_slot_data(date, time, 0, True, session)
    await dialog_manager.switch_to(state=AdminEditCalendary.choose_time)
