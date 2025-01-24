# аиограм и алхимия
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import User
from aiogram_dialog import DialogManager
# для работы с datetime
import datetime
# функции для работы с базой данных
from src.services.database_func import (get_free_time_on_date_from_db, get_slot_with_user_id, get_pcode_with_name,
                                        user_is_register)
# сервисные функции (список доступных дат, форматирование даты/времени)
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
    pcode = dialog_manager.dialog_data.get('pcode')
    if pcode:
        session = dialog_manager.middleware_data['session']
        pcode_from_db = await get_pcode_with_name(pcode, session)
        admin_id = pcode_from_db.admin_id
    else:
        admin_id = dialog_manager.dialog_data.get('admin_id')
    return {'username': username, 'phone': phone, 'admin_id': admin_id}


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
async def get_feedback(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    user_id = event_from_user.id
    session = dialog_manager.middleware_data['session']
    user = await user_is_register(session, user_id)
    admin_id = user.admin_id
    admin_url = 123
    return {'url': admin_url}


# Геттер для отображения пользователю его записей
async def get_user_appointments(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    session = dialog_manager.middleware_data['session']
    user_appointment_list = await get_slot_with_user_id(session, event_from_user.id)
    user_appointment = [(datetime.date.strftime(slot.date, '%d.%m.%Y'), datetime.time.strftime(slot.time, '%H:%M')) for
                        slot in user_appointment_list]

    admin_id = dialog_manager.dialog_data.get('admin_id')
    if not admin_id:
        user = await user_is_register(session, event_from_user.id)
        admin_id = user.admin_id
        dialog_manager.dialog_data.update({'admin_id': admin_id})

    text_date = dialog_manager.dialog_data.get('text_date')
    text_time = dialog_manager.dialog_data.get('text_time')
    comment = dialog_manager.dialog_data.get('comment')

    is_admin = event_from_user.id in dialog_manager.middleware_data['admin_ids']
    return {'user_appointment': user_appointment, 'text_date': text_date, 'text_time': text_time, 'is_admin': is_admin,
            'comment': comment, 'admin_id': admin_id}


# Геттер для отображения пользователю календаря на первый месяц
async def get_free_dates_on_current_month(dialog_manager: DialogManager, event_from_user: User, session: AsyncSession,
                                          **kwargs) -> dict:
    MONTH_LIST = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
                  'Ноябрь',
                  'Декабрь']

    admin_id = dialog_manager.dialog_data.get('admin_id')
    if not admin_id:
        user = await user_is_register(session, event_from_user.id)
        admin_ids = dialog_manager.middleware_data.get('admin_ids')
        if user.admin_id in admin_ids:
            admin_id = user.telegram_id
        else:
            admin_id = user.admin_id
        dialog_manager.dialog_data.update({'admin_id': admin_id})
        # проверка на админку через кв бакет

    current_month = datetime.date.today().month
    next_month = current_month + 1 if current_month != 12 else current_month - 12 + 1
    current_month_dates = await create_date_list(current_month, session, 'current', admin_id)
    first_weekday = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month,
                                      1).weekday() + datetime.datetime.today().day - 1
    if first_weekday:
        for _ in range(first_weekday):
            current_month_dates.insert(0, (' ', 'locked'))
    for _ in range(42 - len(current_month_dates)):
        current_month_dates.append((' ', 'locked'))
    return {'current_month_dates': current_month_dates, 'current_month': MONTH_LIST[current_month - 1],
            'next_month': MONTH_LIST[next_month - 1], 'current_month_int': current_month, 'admin_id': admin_id}


# Геттер для отображения пользователю календаря на следующий месяц
async def get_free_dates_on_next_month(dialog_manager: DialogManager, event_from_user: User, session: AsyncSession,
                                       **kwargs) -> dict:
    MONTH_LIST = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
                  'Ноябрь',
                  'Декабрь']

    admin_id = dialog_manager.dialog_data.get('admin_id')

    month = datetime.date.today().month
    current_month = month + 1 if month != 12 else month - 12 + 1
    year = datetime.date.today().year
    current_month_dates = await create_date_list(current_month, session, 'next', admin_id)
    current_year = year if current_month != 1 else year + 1
    first_weekday = datetime.datetime(current_year, current_month, 1).weekday()
    if first_weekday:
        for _ in range(first_weekday):
            current_month_dates.insert(0, (' ', 'locked'))
    for _ in range(42 - len(current_month_dates)):
        current_month_dates.append((' ', 'locked'))
    return {'current_month_dates': current_month_dates, 'current_month': MONTH_LIST[current_month - 1],
            'current_month_int': current_month, 'prev_month': MONTH_LIST[month - 1], 'admin_id': admin_id}


# Геттер для отображения доступного времени на выбранную дату
async def get_free_times_from_date(dialog_manager: DialogManager, **kwargs) -> dict:
    session = dialog_manager.middleware_data['session']
    admin_id = dialog_manager.dialog_data.get('admin_id')
    date, text_date = await datetime_format(date=dialog_manager.dialog_data.get('date'))
    times_scalar = await get_free_time_on_date_from_db(date, admin_id, session)
    time_list = [(datetime.time.strftime(slot.time, '%H:%M'),) for slot in times_scalar]
    return {'open_time': time_list, 'date': date, 'text_date': text_date}


# Геттер для подтверждения записи
async def get_confirm_datetime(dialog_manager: DialogManager, **kwargs) -> dict:
    date = dialog_manager.dialog_data.get('date')
    time = dialog_manager.dialog_data.get('time')
    comment = dialog_manager.dialog_data.get('comment')
    return {'time': time, 'date': date, 'comment': comment}
