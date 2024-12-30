import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import User
from aiogram_dialog import DialogManager

from src.services.database_func import (get_free_time_on_date_from_db, get_slot_with_user_id)
from src.services.service_func import create_date_list, datetime_format

'''
Геттеры для диалогов (пользователь)
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


# Геттер для окна помощь
async def get_help_menu(dialog_manager: DialogManager, **kwargs) -> dict:
    text = dialog_manager.middleware_data['description']
    return {'help': text}


# Геттер для окна обратной связи
async def get_feedback(dialog_manager: DialogManager, **kwargs) -> dict:
    admin_url = dialog_manager.middleware_data.get('admin_url')
    return {'url': admin_url}


# Геттер для отображения пользователю его записей
async def get_user_appointments(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    user_appointment_list = await get_slot_with_user_id(dialog_manager.middleware_data['session'], event_from_user.id)
    user_appointment = [(datetime.date.strftime(slot.date, '%d.%m.%Y'), datetime.time.strftime(slot.time, '%H:%M')) for
                        slot in user_appointment_list]

    text_date = dialog_manager.dialog_data.get('text_date')
    text_time = dialog_manager.dialog_data.get('text_time')
    comment = dialog_manager.dialog_data.get('comment')

    is_admin = event_from_user.id in dialog_manager.middleware_data['admin_ids']
    return {'user_appointment': user_appointment, 'text_date': text_date, 'text_time': text_time, 'is_admin': is_admin,
            'comment': comment}


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
    year = datetime.date.today().year
    current_month_dates = await create_date_list(current_month, session)
    current_year = year if current_month != 1 else year + 1
    first_weekday = datetime.datetime(current_year, current_month, 1).weekday()
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
    date, text_date = await datetime_format(date=dialog_manager.dialog_data.get('date'))
    times_scalar = await get_free_time_on_date_from_db(date, session)
    time_list = [(datetime.time.strftime(slot.time, '%H:%M'),) for slot in times_scalar]
    return {'open_time': time_list, 'date': date, 'text_date': text_date}


# Геттер для подтверждения записи
async def get_confirm_datetime(dialog_manager: DialogManager, **kwargs) -> dict:
    date = dialog_manager.dialog_data.get('date')
    time = dialog_manager.dialog_data.get('time')
    comment = dialog_manager.dialog_data.get('comment')
    return {'time': time, 'date': date, 'comment': comment}
