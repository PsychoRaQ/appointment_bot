# аиограм и алхимия
from aiogram.types import User
from aiogram_dialog import DialogManager
# функции для работы с базой данных
from app.utils.database_func import get_slot_with_user_id
# datetime
from datetime import date, time


# Геттер для отображения пользователю его записей
async def get_user_appointments(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    session = dialog_manager.middleware_data.get('session')
    slots = await get_slot_with_user_id(session, event_from_user.id)

    # делаем список кортежей с записями пользователя в формате "(ДАТА, ВРЕМЯ)" из списка полученного из БД
    user_appointments_lst = [(date.strftime(slot.date, '%d.%m.%Y'), time.strftime(slot.time, '%H:%M')) for
                             slot in slots]

    role = dialog_manager.middleware_data.get('user_role')
    is_admin = True if role == 'admin' else False

    text_date = dialog_manager.dialog_data.get('text_date')
    text_time = dialog_manager.dialog_data.get('text_time')
    comment = dialog_manager.dialog_data.get('comment')

    return {'user_appointment': user_appointments_lst, 'text_date': text_date,
            'text_time': text_time, 'is_admin': is_admin, 'comment': comment}
