import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import User
from aiogram_dialog import DialogManager

from src.services.database_func import (get_free_time_on_date_from_db, get_slot_with_user_id)
from src.services.service_func import create_date_list

'''
Геттеры для диалогов
'''


# Геттер получения данных пользователя, для регистрации
async def get_userdata(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    if dialog_manager.dialog_data.get('username'):
        username = dialog_manager.dialog_data.get('username')
    else:
        username = event_from_user.first_name
    phone = dialog_manager.dialog_data.get('phone')
    return {'username': username, 'phone': phone}


# Геттер для отображения главного меню
async def get_main_menu(**kwargs) -> dict:
    main_menu = [
        ('Записаться 🖊️', 'new_appointment'),
        ('Мои записи 📖', 'my_appointment'),
        ('Помощь ❓', 'help'),
        ('Обратная связь 💬', 'feedback'),
    ]
    return {'main_menu': main_menu}


# Геттер для отображения пользователю его записей
async def get_user_appointments(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    user_appointment_list = await get_slot_with_user_id(dialog_manager.middleware_data['session'], event_from_user.id)
    user_appointment = [(datetime.date.strftime(slot.date, '%d.%m.%Y'), datetime.time.strftime(slot.time, '%H:%M')) for
                        slot in user_appointment_list]
    date = dialog_manager.dialog_data.get('date')
    time = dialog_manager.dialog_data.get('time')
    datetime_for_user = dialog_manager.dialog_data.get('datetime_for_user')

    return {'user_appointment': user_appointment, 'datetime_for_user': datetime_for_user, 'date': date, 'time': time}


# Геттер для отображения пользователю календаря на первый месяц
async def get_free_dates_on_current_month(session: AsyncSession, **kwargs) -> dict:
    MONTH_LIST = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
                  'Ноябрь',
                  'Декабрь']
    current_month = datetime.date.today().month
    next_month = current_month + 1 if current_month != 12 else current_month - 12 + 1

    current_month_dates = await create_date_list(current_month, session)

    first_weekday = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, 1).weekday()
    if first_weekday:
        for _ in range(first_weekday):
            current_month_dates.insert(0, (' ', 'locked'))
    for _ in range(42 - len(current_month_dates)):
        current_month_dates.append((' ', 'locked'))
    return {'current_month_dates': current_month_dates, 'current_month': MONTH_LIST[current_month - 1],
            'next_month': MONTH_LIST[next_month - 1], 'current_month_int': current_month}


# Геттер для отображения пользователю календаря на следующий месяц
async def get_free_dates_on_next_month(session: AsyncSession, **kwargs) -> dict:
    MONTH_LIST = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
                  'Ноябрь',
                  'Декабрь']
    month = datetime.date.today().month
    current_month = month + 1 if month != 12 else month - 12 + 1
    current_month_dates = await create_date_list(current_month, session)
    first_weekday = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, 1).weekday()
    if first_weekday:
        for _ in range(first_weekday):
            current_month_dates.insert(0, (' ', 'locked'))
    for _ in range(42 - len(current_month_dates)):
        current_month_dates.append((' ', 'locked'))
    return {'current_month_dates': current_month_dates, 'current_month': MONTH_LIST[current_month - 1],
            'current_month_int': current_month, 'prev_month': MONTH_LIST[month - 1]}


# Геттер для отображения доступного времени на выбранную дату
async def get_free_times_from_date(dialog_manager: DialogManager, **kwargs) -> dict:
    session = dialog_manager.middleware_data['session']
    date = list(map(int, dialog_manager.dialog_data.get('date').split('-')))
    date = datetime.date(date[2], date[1], date[0])
    times_scalar = await get_free_time_on_date_from_db(date, session)
    time_list = [(datetime.time.strftime(slot.time, '%H:%M'),) for slot in times_scalar]
    return {'open_time': time_list, 'date': date}


# Геттер для подтверждения записи
async def get_confirm_datetime(dialog_manager: DialogManager, **kwargs) -> dict:
    date = dialog_manager.dialog_data.get('date')
    time = dialog_manager.dialog_data.get('time')
    return {'time': time, 'date': date}