# аиограм и алхимия
from aiogram.types import User
from aiogram_dialog import DialogManager
# функции для работы с базой данных
from app.utils.database_func import (get_pcode_with_name)


# Геттер получения данных пользователя
async def get_userdata(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    if dialog_manager.dialog_data.get('username'):
        username = dialog_manager.dialog_data.get('username')
    else:
        username = event_from_user.first_name
    phone = dialog_manager.dialog_data.get('phone')
    pcode = dialog_manager.dialog_data.get('pcode')
    if pcode:
        session = dialog_manager.middleware_data.get('session')
        pcode_from_db = await get_pcode_with_name(pcode, session)
        admin_id = pcode_from_db.admin_id
    else:
        admin_id = dialog_manager.dialog_data.get('admin_id')
    return {'username': username, 'phone': phone, 'admin_id': admin_id}
