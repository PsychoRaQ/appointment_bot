# аиограм и алхимия
from aiogram.types import User
from aiogram_dialog import DialogManager
# функции для работы с БД
from src.services.database_func import get_all_admins_from_db


# получение списка админов
async def get_all_admins(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    session = dialog_manager.middleware_data.get('session')
    admins = await get_all_admins_from_db(session)
    kv_storage = dialog_manager.middleware_data.get('subscribe_storage')
    if admins:
        result_lst = []
        for admin in admins:
            data = await kv_storage.get(admin.telegram_id)
            result = {'admin_id': admin.telegram_id,
                      'username': admin.username,
                      'phone': admin.phone,
                      'sub_days': int(data.value.decode("utf-8"))}
            result_lst.append(result)
    else:
        result_lst = ['Нет доступных администраторов для отображения']

    return {'admins': result_lst}


# получение данных администратора по id
async def get_admin_data(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    admin_id = dialog_manager.dialog_data.get('admin_id')
    if not admin_id:
        admin_id = event_from_user.id
    kv_storage = dialog_manager.middleware_data.get('subscribe_storage')
    data = await kv_storage.get(admin_id)
    sub_days = int(data.value.decode("utf-8"))

    admin_data = {'admin_id': admin_id, 'sub_days': sub_days}

    return {'admin_data': admin_data}
