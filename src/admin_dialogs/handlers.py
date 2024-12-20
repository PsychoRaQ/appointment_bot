import datetime

from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select

from src.config_data.config import load_config
from src.fsm.admin_states import AdminEditCalendary
from src.services.database_func import (get_slot_from_db, admin_change_slot_data, add_new_time_slot)
from src.services.service_func import datetime_format

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
    bot = None
    if user_id:
        # создаем экземпляр бота для отправки уведомления пользователю
        config = load_config('.env')
        bot_token = config.token  # токен бота
        bot = Bot(token=bot_token)
        await bot.send_message(user_id,
                               f'Администратор отменил Вашу запись {text_date} - {text_time}')
    await admin_change_slot_data(date, time, 0, True, session)
    if bot:
        await bot.session.close()
    await dialog_manager.switch_to(state=AdminEditCalendary.choose_time)
