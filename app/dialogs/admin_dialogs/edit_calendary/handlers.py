# аиограм
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select
# состояния
from app.fsm.admin_states import AdminEditCalendary
# для рассылки
# функции для работы с БД
from app.utils.database_func import (get_slot_from_db, admin_change_slot_data, add_new_time_slot)
# сервисная функция для форматирования даты/времени
from app.utils.service_func import datetime_format


# Админ выбрал дату для изменения слотов
async def admin_choose_date_for_edit(callback: CallbackQuery, widget: Select,
                                     dialog_manager: DialogManager, data: str):
    if data != 'locked':
        await dialog_manager.update({'date': data})
        await dialog_manager.switch_to(state=AdminEditCalendary.choose_time, show_mode=ShowMode.AUTO)


# Админ выбрал время слота
async def admin_choose_time_slot_for_edit(callback: CallbackQuery, widget: Select,
                                          dialog_manager: DialogManager, data: str):
    await dialog_manager.update({'time': data})
    date, text_date, time, text_time = await datetime_format(date=dialog_manager.dialog_data.get('date'), time=data)
    session = dialog_manager.middleware_data.get('session')
    admin_id = callback.from_user.id
    slot = await get_slot_from_db(date, time, admin_id, session)
    if slot:
        if slot.user_id == 0:
            status = 0 if slot.is_locked else 1
            await admin_change_slot_data(date, time, 0, status, admin_id, session)
        else:
            await dialog_manager.switch_to(state=AdminEditCalendary.user_on_date, show_mode=ShowMode.AUTO)
    else:
        await add_new_time_slot(date, time, admin_id, session)


# Админ решил закрыть слот на который записан пользователь
async def admin_close_slot(callback: CallbackQuery, widget: Select,
                           dialog_manager: DialogManager):
    session = dialog_manager.middleware_data.get('session')
    date, text_date, time, text_time = await datetime_format(date=dialog_manager.dialog_data.get('date'),
                                                             time=dialog_manager.dialog_data.get('time'))
    admin_id = callback.from_user.id
    slot = await get_slot_from_db(date, time, admin_id, session)

    if slot.user_id != admin_id:
        bot = dialog_manager.middleware_data.get('bot')
        await bot.send_message(slot.user_id,
                               f'Администратор отменил Вашу запись {text_date} - {text_time}')
    await admin_change_slot_data(date, time, 0, True, admin_id, session)
    await dialog_manager.switch_to(state=AdminEditCalendary.choose_time, show_mode=ShowMode.AUTO)
