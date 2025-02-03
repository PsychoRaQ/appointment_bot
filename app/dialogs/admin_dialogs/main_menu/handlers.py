# аиограм
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select
# состояния
from app.fsm.admin_states import AdminEditCalendary, AllAppointments, Dispatch, Pcode, AllAdmins, AdminSettings
from app.fsm.user_states import UserNewAppointmentSG, UserAppointmentSG
# функции для работы с БД
from app.utils.database_func import get_slot_with_user_id

'''
Юзер-стейты используются для открытия диалогов "Ручной записи" и "Отмены ручной записи"
Подробнее расписано в юзер диалогах
'''


# Селектор диалогов из меню, открывает следующие диалоги
async def admin_dialog_selection(callback: CallbackQuery, widget: Select,
                                 dialog_manager: DialogManager, data: str):
    match data:
        case 'edit_calendary':
            await dialog_manager.start(state=AdminEditCalendary.first_month, data={'for_admin': True},
                                       show_mode=ShowMode.AUTO)
        case 'make_new_appointment':
            await dialog_manager.start(state=UserNewAppointmentSG.calendary_first_month, data={'for_admin': False},
                                       show_mode=ShowMode.AUTO)
        case 'delete_admin_appointment':
            result = await get_slot_with_user_id(dialog_manager.middleware_data.get('session'),
                                                 callback.message.chat.id)
            if len(result) == 0:
                await dialog_manager.start(state=UserAppointmentSG.no_one_appointment, show_mode=ShowMode.AUTO)
            else:
                await dialog_manager.start(state=UserAppointmentSG.delete_appointment_datetime, show_mode=ShowMode.AUTO)
        case 'view_all_appointments':
            await dialog_manager.start(state=AllAppointments.first_month, data={'for_admin': True},
                                       show_mode=ShowMode.AUTO)
        case 'mass_dispatch':
            await dialog_manager.start(state=Dispatch.edit_dispatch, show_mode=ShowMode.AUTO)
        case 'admin_invite':
            await dialog_manager.start(state=Pcode.main_pcode, show_mode=ShowMode.AUTO)
        case 'admin_settings':
            await dialog_manager.start(state=AdminSettings.main_menu, show_mode=ShowMode.AUTO)
        # старшая админка
        case 'view_all_admins':
            await dialog_manager.start(state=AllAdmins.main_menu, show_mode=ShowMode.AUTO)
        case _:
            print(data)
