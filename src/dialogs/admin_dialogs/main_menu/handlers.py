# аиограм
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select
# состояния
from src.fsm.admin_states import AdminEditCalendary, AllAppointments, Dispatch, Pcode, AllAdmins, AdminSettings
from src.fsm.user_states import UserNewAppointmentSG, UserAppointmentSG
# функции для работы с БД
from src.services.database_func import get_slot_with_user_id

'''
Юзер-стейты используются для открытия диалогов "Ручной записи" и "Отмены ручной записи"
Подробнее расписано в юзер диалогах
'''


# Селектор диалогов из меню, открывает следующие диалоги
async def admin_dialog_selection(callback: CallbackQuery, widget: Select,
                                 dialog_manager: DialogManager, data: str):
    match data:
        case 'edit_calendary':
            await dialog_manager.start(state=AdminEditCalendary.first_month, data={'for_admin': True})
        case 'make_new_appointment':
            await dialog_manager.start(state=UserNewAppointmentSG.calendary_first_month, data={'for_admin': False})
        case 'delete_admin_appointment':
            result = await get_slot_with_user_id(dialog_manager.middleware_data['session'],
                                                 callback.message.chat.id)
            if len(result) == 0:
                await dialog_manager.start(state=UserAppointmentSG.no_one_appointment)
            else:
                await dialog_manager.start(state=UserAppointmentSG.delete_appointment_datetime)
        case 'view_all_appointments':
            await dialog_manager.start(state=AllAppointments.first_month, data={'for_admin': True})
        case 'mass_dispatch':
            await dialog_manager.start(state=Dispatch.edit_dispatch)
        case 'admin_invite':
            await dialog_manager.start(state=Pcode.main_pcode)
        case 'admin_settings':
            await dialog_manager.start(state=AdminSettings.main_menu)
        # старшая админка
        case 'view_all_admins':
            await dialog_manager.start(state=AllAdmins.main_menu)
        case _:
            print(data)
