# аиограм и алхимия
from aiogram.types import User
from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession
# для работы с datetime
import datetime
# функции для работы с БД
from src.services.database_func import get_slots_list_from_db, get_slot_from_db, user_is_register
# сервисные функции
from src.services.service_func import create_admin_date_list, create_time_slots, datetime_format

'''
Геттеры для диалогов (админка)
'''


# Геттер для отображения главного меню
async def get_admin_menu(**kwargs) -> dict:
    main_menu = [
        ('Изменить расписание 🗓️', 'edit_calendary'),
        ('Записать пользователя 🖊️', 'add_user_appointment'),
        ('Отменить ручную запись ❌', 'delete_admin_appointment'),
        ('Посмотреть все записи 📑', 'all_appointments'),
        ('Настройка рассылки ✉️', 'dispatch'),
    ]
    return {'main_menu': main_menu}


# Геттер для отображения админу календаря на первый месяц
async def get_free_dates_on_current_month(session: AsyncSession, **kwargs) -> dict:
    MONTH_LIST = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
                  'Ноябрь',
                  'Декабрь']
    current_month = datetime.date.today().month
    next_month = current_month + 1 if current_month != 12 else current_month - 12 + 1

    current_month_dates = await create_admin_date_list(current_month, session)

    first_weekday = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, 1).weekday()
    if first_weekday:
        for _ in range(first_weekday):
            current_month_dates.insert(0, (' ', 'locked'))
    for _ in range(42 - len(current_month_dates)):
        current_month_dates.append((' ', 'locked'))

    return {'current_month_dates': current_month_dates, 'current_month': MONTH_LIST[current_month - 1],
            'next_month': MONTH_LIST[next_month - 1], 'current_month_int': current_month}


# Геттер для отображения админу календаря на следующий месяц
async def get_free_dates_on_next_month(session: AsyncSession, **kwargs) -> dict:
    MONTH_LIST = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
                  'Ноябрь',
                  'Декабрь']
    month = datetime.date.today().month
    year = datetime.date.today().year
    current_month = month + 1 if month != 12 else month - 12 + 1
    current_year = year if current_month != 1 else year + 1
    current_month_dates = await create_admin_date_list(current_month, session)
    first_weekday = datetime.datetime(current_year, current_month, 1).weekday()
    if first_weekday:
        for _ in range(first_weekday):
            current_month_dates.insert(0, (' ', 'locked'))
    for _ in range(42 - len(current_month_dates)):
        current_month_dates.append((' ', 'locked'))
    return {'current_month_dates': current_month_dates, 'current_month': MONTH_LIST[current_month - 1],
            'current_month_int': current_month, 'prev_month': MONTH_LIST[month - 1]}


# Геттер для отображения слотов на выбранную дату
async def get_free_times_from_date(dialog_manager: DialogManager, **kwargs) -> dict:
    text_date = dialog_manager.dialog_data.get('date')
    if text_date == 'locked':
        return {}
    session = dialog_manager.middleware_data['session']

    date, text_date = await datetime_format(date=text_date)

    times_scalar = await get_slots_list_from_db(date, session)
    slots = await create_time_slots(6, 23)

    result_text = []
    result_data = []

    for i in slots:
        result_text.append(i[0])
        result_data.append(i[1])

    for i in times_scalar:
        if i.time in result_data:
            index = result_data.index(i.time)
            if i.user_id == 0:
                result_text[index] = f'{datetime.time.strftime(i.time, '%H:%M')} ✅'
                result_data[index] = i.time
            else:
                result_text[index] = f'{datetime.time.strftime(i.time, '%H:%M')} 👩'
                result_data[index] = i.time
    result = list(zip(result_text, result_data))
    return {'open_time': result, 'date': date, 'text_date': text_date}


# Геттер для инфы о занятом слоте который пытается закрыть админ
async def slot_info_for_user(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    text_date = dialog_manager.dialog_data.get('date')
    session = dialog_manager.middleware_data['session']

    date, text_date, time, text_time = await datetime_format(date=text_date,
                                                             time=dialog_manager.dialog_data.get('time'))

    slot = await get_slot_from_db(date, time, session)
    comment = slot.comment if slot.comment else '-'
    user = await user_is_register(session, slot.user_id)
    username = user.username
    user_phone = user.phone

    is_admin = user.telegram_id == event_from_user.id

    return {'date': date, 'time': time, 'text_date': text_date, 'text_time': text_time, 'username': username,
            'phone': user_phone, 'comment': comment, 'is_admin': is_admin}


# Геттер для отображения всех открытых слотов (занятых и свободных)
async def get_all_slots(dialog_manager: DialogManager, **kwargs):
    text_date = dialog_manager.dialog_data.get('date')
    session = dialog_manager.middleware_data['session']
    date, text_date = await datetime_format(date=text_date)
    result = []
    slots = await get_slots_list_from_db(date, session)
    admin_ids = dialog_manager.middleware_data.get('admin_ids')
    if slots:
        for slot in slots:
            time = f'{datetime.time.strftime(slot.time, '%H:%M')}'
            if slot.user_id == 0:
                result.append(f'{time} - Свободно')
            elif slot.user_id in admin_ids:
                comment = slot.comment
                result.append(f'{time} - Ручная запись - {comment}')
            else:
                user = await user_is_register(session, slot.user_id)
                result.append(f'{time} - {user.username} - {user.phone}')
    if result == []:
        result.append('Нет доступных слотов для отображения.')
    return {'date': text_date, 'slot': result}
