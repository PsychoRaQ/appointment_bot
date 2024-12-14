import datetime

from lexicon.lexicon import LEXICON
from services import database_func

import logging

logger = logging.getLogger(__name__)

'''
Разные сервисные функции
'''


# Создание списка с датами на месяц (month)
def create_date_list(month) -> list:
    years = (2024, 2028, 2032, 2036, 2040)
    day = 31 if month in (1, 3, 5, 7, 8, 10, 12) else 30
    year = datetime.datetime.today().year
    if month == 1:
        year += 1
    if month == 2 and year in years:
        day = 29
    elif month == 2 and year not in years:
        day = 28
    date_lst = [f'{i}' for i in range(1, day + 1)]
    date_lst = list((map(lambda x: '0' + x if len(x) == 1 else x, date_lst)))
    date_lst = delete_locked_dates(date_lst, month, year)
    return date_lst


def delete_locked_dates(date_lst, month, year) -> list:
    cur_month = str(month)
    year = str(year)
    cur_month = f'0{cur_month}' if len(cur_month) == 1 else cur_month
    not_locked_dates = database_func.get_two_slots_where('is_locked', False, 'user_id', False, 'date')
    dates_list = []
    if not_locked_dates:
        for slot in not_locked_dates:
            db_year, db_month, db_day = slot[0].split('-')
            date = f'{db_day}.{db_month}'
            if date in dates_list or db_month != cur_month or year != db_year:
                continue
            else:
                dates_list.append(date)
    result = [(i, f'{i}-{cur_month}-{year}') if f'{i}.{cur_month}' in dates_list else (' ', 'locked') for i in date_lst]
    return result


# Создание списка со временем (HH:MM) с диапазоном минут (minute_range)
def create_time_in_range_list(minute_range: int) -> list:
    result = [(datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0)) + datetime.timedelta(
        minutes=i)).time().strftime("%H:%M")
              for i in range(0, 24 * 60, minute_range)]
    return result


# Форматирование текста для отображения юзеру его записей
def get_user_appointment_format_text(user_id) -> str | bool:
    result = database_func.get_user_appointment(user_id)
    if result:
        text = LEXICON['/user_appointment']
        for slot in result:
            date, time = slot
            date = date_from_db_format(date)
            text += f'{date} - {time}\n'
        return text
    else:
        return False


# проверяем превысил ли пользователь максимальное количество занятых слотов
def return_user_is_max_appointment(user_id) -> int:
    appointments = len(database_func.get_one_slots_where('user_id', user_id, 'id'))
    print(appointments)
    user_max_appointment = database_func.get_userdata(user_id)
    user_max_appointment = user_max_appointment[0][4]
    return appointments < user_max_appointment


# Форматирование даты для отображения ее пользователю
def date_from_db_format(date):
    year, month, day = date.split('-')
    return f'{day}.{month}.{year}'


# Уведомление ползователя об отмене его записи (администратором)
async def send_message_to_user(admin_id, user_id, message_text, bot):
    try:
        await bot.send_message(user_id, message_text)
    except Exception as e:
        logger.warning(e)
        await send_alert_to_admin(admin_id, f"Ошибка при отправке сообщения пользователю {user_id}: {e}")


# Если ошибка при отправке сообщения пользователю - уведомляем админа об этом
# Если ошибка при отправке админу - просто выводим инфу в консоль
async def send_alert_to_admin(user_id, message_text, bot):
    try:
        await bot.send_message(user_id, message_text)
    except Exception as e:
        logger.warning(e)


# проверяем имя пользователя при регистрации на корректность
# + форматируем его (отсекая фамилию и отчество)
def username_is_correct(name):
    if ' ' in name:
        name = name.split(' ')[0]
    return name


# форматируем номер телефона для внесения в базу
def refactor_phone_number(number):
    if number[0] == '8':
        return number
    elif number[0] == '+':
        return number.replace('+7', '8', 1)
    else:
        return number.replace('7', '8', 1)