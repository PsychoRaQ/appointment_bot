# аиограм
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
# состояния
from src.fsm.admin_states import AllAdmins
# для рассылки
# функции для работы с БД
from src.services.database_func import get_all_admins_from_db


# обработчик-фильтр для проверки корректности id и введенного числа дней подписки
def correct_id(data: str):
    if data.isdigit():
        return data
    raise ValueError


# переходим в меню управления админом с указанным id (если id есть в базе)
async def edit_admin_data(message: Message,
                          widget: ManagedTextInput,
                          dialog_manager: DialogManager,
                          data: str) -> None:
    session = dialog_manager.middleware_data.get('session')
    admins = await get_all_admins_from_db(session)
    admin_ids = [admin.telegram_id for admin in admins]
    if int(data) in admin_ids:
        dialog_manager.dialog_data.update({'admin_id': data})
        await dialog_manager.next()
    else:
        pass


# изменение количества дней подписки
async def edit_sub_days(message: Message,
                        widget: ManagedTextInput,
                        dialog_manager: DialogManager,
                        data: str) -> None:
    admin_id = dialog_manager.dialog_data.get('admin_id')
    kv_storage = dialog_manager.middleware_data.get('subscribe_storage')
    days = int(data)
    await kv_storage.put(str(admin_id), bytes(str(days), encoding='utf-8'))
    await dialog_manager.switch_to(AllAdmins.main_menu)
