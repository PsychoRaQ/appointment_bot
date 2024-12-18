import datetime

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select

from src.fsm.admin_states import AdminEditCalendary

from src.services.database_func import (get_slot_from_db, admin_change_slot_data, add_new_time_slot)

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
            print(data)
        case 'delete_user_appointment':
            print(data)
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


# Админ выбрал время слота
async def admin_choose_time_slot_for_edit(callback: CallbackQuery, widget: Select,
                                          dialog_manager: DialogManager, data: str):
    await dialog_manager.update({'time': data})
    date_convert = list(map(int, dialog_manager.dialog_data.get('date').split('-')))
    time_convert = list(map(int, data.split(':')))

    date = datetime.date(date_convert[2], date_convert[1], date_convert[0])
    time = datetime.time(time_convert[0], time_convert[1])

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
    date = list(map(int, dialog_manager.dialog_data.get('date').split('-')))
    date = datetime.date(date[2], date[1], date[0])
    time = datetime.time(*list(map(int, dialog_manager.dialog_data.get('time').split(':'))))

    slot = await get_slot_from_db(date, time, session)

    await admin_change_slot_data(date, time, 0, True, session)

    user_id = slot.user_id
    # здесь сделать уведомление пользователя об отмене его записи

    await dialog_manager.switch_to(state=AdminEditCalendary.choose_time)
