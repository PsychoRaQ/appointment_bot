from aiogram.types import User
from aiogram_dialog import DialogManager
from services.database_func import get_user_appointment, get_open_times_with_date
from services.service_func import create_date_list
import datetime


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
        # ('Отменить запись ❌', 'delete_appointment'),
        ('Мои записи 📖', 'my_appointment'),
        ('Помощь ❓', 'help'),
        ('Обратная связь 💬', 'feedback'),
    ]
    return {'main_menu': main_menu}


# Геттер для отображения пользователю его записей
async def get_user_appointments(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    user_appointment = get_user_appointment(event_from_user.id)
    return {'user_appointment': user_appointment}


# Геттер для отображения пользователю календаря на первый месяц
async def get_free_dates_on_current_month(**kwargs) -> dict:
    MONTH_LIST = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
                  'Ноябрь',
                  'Декабрь']
    current_month = datetime.date.today().month
    next_month = current_month + 1 if current_month != 12 else current_month - 12 + 1
    current_month_dates = create_date_list(current_month)
    first_weekday = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, 1).weekday()
    if first_weekday:
        for _ in range(first_weekday):
            current_month_dates.insert(0, (' ', 'locked'))
    for _ in range(42 - len(current_month_dates)):
        current_month_dates.append((' ', 'locked'))
    return {'current_month_dates': current_month_dates, 'current_month': MONTH_LIST[current_month - 1],
            'next_month': MONTH_LIST[next_month - 1], 'current_month_int': current_month}


# Геттер для отображения пользователю календаря на следующий месяц
async def get_free_dates_on_next_month(**kwargs) -> dict:
    MONTH_LIST = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
                  'Ноябрь',
                  'Декабрь']
    month = datetime.date.today().month
    current_month = month + 1 if month != 12 else month - 12 + 1
    current_month_dates = create_date_list(current_month)
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
    date = dialog_manager.dialog_data.get('date')
    date_lst = date.split('-')
    new_date = f'{date_lst[2]}-{date_lst[1]}-{date_lst[0]}'
    time_list = get_open_times_with_date(new_date)
    return {'open_time': time_list, 'date': date}


# Геттер для подтверждения записи
async def get_confirm_datetime(dialog_manager: DialogManager, **kwargs) -> dict:
    date = dialog_manager.dialog_data.get('date')
    time = dialog_manager.dialog_data.get('time')

    return {'time': time, 'date': date}
