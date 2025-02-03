# аиограм и алхимия
from aiogram.types import User
from aiogram.utils.deep_linking import create_start_link
from aiogram_dialog import DialogManager
# функции для работы с БД
from app.utils.database_func import get_admin_pcode


# Геттер для отображения промокода и рефералки (получаем из базы данных)
async def get_pcode_from_db(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    admin_id = event_from_user.id
    link = await create_start_link(dialog_manager.middleware_data.get('bot'), str(admin_id))
    session = dialog_manager.middleware_data.get('session')
    pcode = await get_admin_pcode(admin_id, session)
    if not pcode:
        pcode = admin_id
    else:
        pcode = pcode.pcode
    return {'link': link, 'pcode': pcode}


# Геттер для отображения промокода и рефералки (получаем из диалог даты)
async def get_pcode_from_dialog(dialog_manager: DialogManager, **kwargs) -> dict:
    pcode = dialog_manager.dialog_data.get('pcode')
    return {'pcode': pcode}
