# аиограм и алхимия
from aiogram.types import User
from aiogram_dialog import DialogManager
# функции для работы с базой данных
from app.utils.database_func import get_slots_list_from_db, user_is_register, get_slot_from_db
# сервисные функции
from app.utils.service_func import datetime_format, create_time_slots
# datetime
from datetime import time as tm


# Геттер для отображения "слотов" на выбранную дату
# + радиокнопки для выбора нужного промежутка между "слотами"
async def get_free_times_from_date(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    checked = dialog_manager.find('radio_times').get_checked()
    slot_times = {
        # '1': 5,
        # '2': 10,
        '3': 15,
        '4': 20,
        '5': 30,
    }
    chosen_time = slot_times['5' if not checked else checked]

    text_date = dialog_manager.dialog_data.get('date')
    if text_date == 'locked':
        return {}
    session = dialog_manager.middleware_data.get('session')

    date, text_date = await datetime_format(date=text_date)

    admin_id = event_from_user.id
    times_scalar = await get_slots_list_from_db(date, admin_id, session)
    slots = await create_time_slots(6, 23, chosen_time)  # создание временных "слотов"

    result_text = []
    result_data = []

    for i in slots:
        result_text.append(i[0])
        result_data.append(i[1])

    for i in times_scalar:
        if i.time in result_data:
            index = result_data.index(i.time)
            if i.user_id == 0:
                result_text[index] = f'{tm.strftime(i.time, '%H:%M')} ✅'
                result_data[index] = i.time
            else:
                result_text[index] = f'{tm.strftime(i.time, '%H:%M')} 👩'
                result_data[index] = i.time
    result = list(zip(result_text, result_data))
    slot_times = [
        # (':05', '1'),
        # (':10', '2'),
        (':15', '3'),
        (':20', '4'),
        (':30', '5'),
    ]
    return {'open_time': result, 'date': date, 'text_date': text_date, 'slot_times': slot_times}


# Геттер для информации о занятом "слоте", который пытается закрыть админ
async def slot_info_for_user(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    text_date = dialog_manager.dialog_data.get('date')
    session = dialog_manager.middleware_data.get('session')

    date, text_date, time, text_time = await datetime_format(date=text_date,
                                                             time=dialog_manager.dialog_data.get('time'))

    admin_id = event_from_user.id
    slot = await get_slot_from_db(date, time, admin_id, session)
    comment = slot.comment if slot.comment else '-'
    user = await user_is_register(session, slot.user_id)
    username = user.username
    user_phone = user.phone

    is_admin = user.telegram_id == event_from_user.id

    return {'date': date, 'time': time, 'text_date': text_date, 'text_time': text_time, 'username': username,
            'phone': user_phone, 'comment': comment, 'is_admin': is_admin}
