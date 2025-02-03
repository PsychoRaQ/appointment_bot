# аиограм и алхимия
from aiogram.types import User
from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession
# функции для работы с базой данных
from app.utils.database_func import get_free_time_on_date_from_db, user_is_register
# сервисные функции (список доступных дат, форматирование даты/времени)
from app.utils.service_func import create_date_list, datetime_format
# datetime
from datetime import date, datetime, time as tm


# Геттер для отображения пользователю календаря на текущий месяц
async def get_free_dates(dialog_manager: DialogManager, event_from_user: User, session: AsyncSession,
                         **kwargs) -> dict:
    MONTH_LIST = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

    # получаем id администратора к которому привязан пользователь
    # если это админ - берем его id
    admin_id = dialog_manager.dialog_data.get('admin_id')
    if not admin_id:
        role = dialog_manager.middleware_data.get('user_role')
        if role == 'admin':
            admin_id = event_from_user.id
        else:
            user = await user_is_register(session, event_from_user.id)
            admin_id = user.admin_id
        dialog_manager.dialog_data.update({'admin_id': admin_id})

    # получаем порядковый номер текущего месяца и следующего
    current_month = date.today().month
    next_month = current_month + 1 if current_month != 12 else current_month - 12 + 1

    # получаем стартовый параметр из контекста (для кого генерируем календарь)
    for_admin = dialog_manager.middleware_data.get('aiogd_context').start_data.get('for_admin')
    # создаем список с датами на текущий месяц
    current_month_dates = await create_date_list(current_month, session, 'current', for_admin, admin_id)
    first_weekday_on_current_month = datetime(datetime.today().year, datetime.today().month,
                                              1).weekday() + datetime.today().day - 1
    for _ in range(first_weekday_on_current_month):
        current_month_dates.insert(0, (' ', 'locked'))
    for _ in range(42 - len(current_month_dates)):
        current_month_dates.append((' ', 'locked'))

    # создаем список с датами на следующий месяц
    next_month_dates = await create_date_list(next_month, session, 'next', for_admin, admin_id)
    first_weekday_on_next_month = datetime(datetime.today().year, next_month, 1).weekday()
    for _ in range(first_weekday_on_next_month):
        next_month_dates.insert(0, (' ', 'locked'))
    for _ in range(42 - len(next_month_dates)):
        next_month_dates.append((' ', 'locked'))

    return {
        'current_month_dates': current_month_dates,
        'next_month_dates': next_month_dates,
        'current_month': MONTH_LIST[current_month - 1],
        'next_month': MONTH_LIST[next_month - 1],
        'current_month_int': current_month,
        'admin_id': admin_id
    }


# Геттер для отображения доступных для записи временных "слотов" на выбранную дату
async def get_free_times_from_date(dialog_manager: DialogManager, **kwargs) -> dict:
    session = dialog_manager.middleware_data.get('session')
    admin_id = dialog_manager.dialog_data.get('admin_id')
    date, text_date = await datetime_format(date=dialog_manager.dialog_data.get('date'))
    slots = await get_free_time_on_date_from_db(date, admin_id, session)
    time_list = [(tm.strftime(slot.time, '%H:%M'),) for slot in slots]
    return {'open_time': time_list, 'date': date, 'text_date': text_date}


# Геттер для получения информации о слоте во время записи
async def get_confirm_datetime(dialog_manager: DialogManager, **kwargs) -> dict:
    date = dialog_manager.dialog_data.get('date')
    time = dialog_manager.dialog_data.get('time')
    comment = dialog_manager.dialog_data.get('comment')
    return {'time': time, 'date': date, 'comment': comment}
