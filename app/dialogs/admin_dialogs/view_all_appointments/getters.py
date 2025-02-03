# аиограм и алхимия
from aiogram.types import User
from aiogram_dialog import DialogManager
# функции для работы с БД
from app.utils.database_func import (get_slots_list_from_db, user_is_register)
# сервисные функции
from app.utils.service_func import datetime_format
# datetime
from datetime import time as tm


# Геттер для отображения всех открытых слотов (занятых и свободных)
async def get_all_slots(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    text_date = dialog_manager.dialog_data.get('date')
    session = dialog_manager.middleware_data.get('session')
    date, text_date = await datetime_format(date=text_date)
    result = []
    admin_id = event_from_user.id
    slots = await get_slots_list_from_db(date, admin_id, session)
    if slots:
        for slot in slots:
            time = f'{tm.strftime(slot.time, '%H:%M')}'
            if slot.user_id == 0:
                result.append(f'{time} - Свободно')
            elif slot.user_id == admin_id:
                comment = slot.comment
                result.append(f'{time} - Ручная запись - {comment}')
            else:
                user = await user_is_register(session, slot.user_id)
                result.append(f'{time} - {user.username} - {user.phone}')
    if result == []:
        result.append('Нет доступных слотов для отображения.')
    return {'date': text_date, 'slot': result}
