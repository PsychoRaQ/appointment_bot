# аиограм
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select
# состояния
from app.fsm.admin_states import AllAppointments


# Админ выбрал дату для отображения слотов
async def admin_choose_view_date(callback: CallbackQuery, widget: Select,
                                     dialog_manager: DialogManager, data: str):
    if data != 'locked':
        await dialog_manager.update({'date': data})
        await dialog_manager.switch_to(state=AllAppointments.appointments_list)
