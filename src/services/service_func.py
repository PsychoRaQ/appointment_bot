# типизация
from aiogram.types import BotCommand
# функции для работы с базой данных
from src.services.database_func import get_free_dates_from_db, user_is_register, get_slot_with_user_id
# для работы с datetime
import datetime
# логирование
import logging

logger = logging.getLogger(__name__)

'''
Разные сервисные функции
'''


####### ПОЛЬЗОВАТЕЛИ

# Создание списка с датами на месяц (month)
# Основная функция, здесь работа с датами и заготовка под конечный результат
async def create_date_list(month, session, status, admin_id) -> list:
    years = (2024, 2028, 2032, 2036, 2040)
    day = 31 if month in (1, 3, 5, 7, 8, 10, 12) else 30
    year = datetime.datetime.today().year
    if month == 1 and datetime.datetime.today().month == 12:
        year += 1
    if month == 2 and year in years:
        day = 29
    elif month == 2 and year not in years:
        day = 28

    if status == 'current':
        current_day = datetime.datetime.today().day
    else:
        current_day = 1

    date_lst = [f'{i}' for i in range(current_day, day + 1)]
    date_lst = list((map(lambda x: '0' + x if len(x) == 1 else x, date_lst)))
    date_lst = await delete_locked_dates(date_lst, month, year, session, False, admin_id)
    return date_lst


# Вспомогательная функция для создания списка с датами, здесь получение данных из БД и подстановка их
# в кортеж для отправки в геттер
async def delete_locked_dates(date_lst, month, year, session, for_admin: bool, admin_id) -> list:
    cur_month = str(month)
    year = str(year)
    cur_month = f'0{cur_month}' if len(cur_month) == 1 else cur_month

    dates_scalar = await get_free_dates_from_db(session, for_admin, admin_id)

    dates_list = []
    if dates_scalar:
        for slot in dates_scalar:
            date = slot.date

            if (date in dates_list or str(datetime.date.strftime(date, '%m')) != cur_month
                    or year != str(datetime.date.strftime(date, '%Y'))):
                continue
            else:
                dates_list.append(str(datetime.date.strftime(date, '%d.%m')))
    if for_admin:
        result = [(f'{i} ✅', f'{i}-{cur_month}-{year}') if f'{i}.{cur_month}' in dates_list else (
            f'{i} ❌', f'{i}-{cur_month}-{year}') for i in date_lst]
    else:
        result = [(i, f'{i}-{cur_month}-{year}') if f'{i}.{cur_month}' in dates_list else (' ', 'locked') for i in
                  date_lst]
    return result


# проверяем превысил ли пользователь максимальное количество занятых слотов
async def return_user_is_max_appointment(session, user_id) -> int:
    user = await user_is_register(session, user_id)
    user_max_appointment = user.max_appointment  # noqa
    current_user_appoointments = await get_slot_with_user_id(session, user_id)
    return len(current_user_appoointments) < user_max_appointment


# форматируем номер телефона для внесения в базу
async def refactor_phone_number(number):
    if number[0] == '8':
        return number
    elif number[0] == '+':
        return number.replace('+7', '8', 1)
    else:
        return number.replace('7', '8', 1)


############### АДМИНКА

# Создание списка с датами на месяц (month)
# Основная функция, здесь работа с датами и заготовка под конечный результат
async def create_admin_date_list(month, session, admin_id) -> list:
    years = (2024, 2028, 2032, 2036, 2040)
    day = 31 if month in (1, 3, 5, 7, 8, 10, 12) else 30
    year = datetime.datetime.today().year
    if month == 1 and datetime.datetime.today().month == 12:
        year += 1
    if month == 2 and year in years:
        day = 29
    elif month == 2 and year not in years:
        day = 28
    date_lst = [f'{i}' for i in range(1, day + 1)]
    date_lst = list((map(lambda x: '0' + x if len(x) == 1 else x, date_lst)))
    date_lst = await delete_locked_dates(date_lst, month, year, session, True, admin_id)
    return date_lst


# создание списка временных слотов для изменения админом
async def create_time_slots(start, stop):
    result = []
    for i in range(start, stop + 1):
        result.append(datetime.time(i))
        result.append(datetime.time(i, 30))

    result = [(f'{datetime.time.strftime(time, '%H:%M')} ❌', time) for time in result]
    return result


##### Общее

# Форматирует дату и время во все нужные виды
async def datetime_format(date=None, time=None):
    result = ()
    if date:
        date_for_format = list(map(int, date.split('-')))
        new_date = datetime.date(date_for_format[2], date_for_format[1], date_for_format[0])
        result += (new_date, date)  # noqa
    if time:
        time = time.split(':')
        if not time[1].isdigit():
            time[1] = time[1].split(' ')[0]
        new_time = datetime.time(*list(map(int, time)))
        text_time = f'{datetime.time.strftime(new_time, '%H:%M')}'
        result += (new_time, text_time)
    return result


# Функция для настройки кнопки Menu бота
async def set_main_menu(bot):
    main_menu_commands = [
        BotCommand(
            command='/start',
            description='Главное меню',
        ),
    ]
    await bot.set_my_commands(main_menu_commands)
