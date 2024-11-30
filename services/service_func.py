# from services.database_func import get_user_data_from_db
# from lexicon.lexicon import LEXICON
from config_data.bot_init import bot
import datetime

from lexicon.lexicon import LEXICON
from services.database_func import get_user_appointment

# # получение актуальных записей из профиля пользователя
# def get_user_appointment(user_id: str) -> str:
#     # db = get_user_data_from_db(user_id)['date']
#     # if db != {}:
#     #     date_lst = []
#     #
#     #     for date, time in db.items():
#     #         time = ', '.join(sorted(time))
#     #         text = f'{date} - {time}\n'
#     #         date_lst.append(text)
#     #
#     #     date_lst.sort()
#     #     date_lst.append(f'\n{LEXICON['/user_appointment_end']}')
#     #     date_lst.insert(0, f'\n{LEXICON['/user_appointment']}')
#     #     text = ''.join(date_lst)
#     #
#     # else:
#     #     text = LEXICON['/no_one_appointment']
#     # return text
#     pass

# Создание списка с датами на месяц (month)
def create_date_list(month) -> list:
    years = (2024,2028,2032,2036,2040)
    day = 31 if month in (1,3,5,7,8,10,12) else 30
    if month == 2 and datetime.date.today().year in years:
        day = 29
    elif month == 2 and datetime.date.today().year not in years:
        day = 28
    return [f'{datetime.date.today().year}-{month}-{i}' for i in range(1,day+1)]

# Создание списка со временем (HH:MM) с диапазоном минут (minute_range)
def create_time_in_range_list(minute_range: int) -> list:
    result = [(datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0)) + datetime.timedelta(
        minutes=i)).time().strftime("%H:%M")
           for i in range(0, 24 * 60, minute_range)]
    return result

# Форматирование текста для отображения юзеру его записей
def get_user_appointment_format_text(user_id):
    result = get_user_appointment(user_id)
    if result:
        text = LEXICON['/user_appointment']
        for slot in result:
            date, time = slot
            date = date_from_db_format(date)
            text += f'{date} - {time}\n'
        return text
    else:
        return False

# Форматирование даты для отображения ее пользователю
def date_from_db_format(date):
    year,month,day = date.split('-')
    return f'{day}.{month}.{year}'

# Уведомление ползователя об отмене его записи (администратором)
async def send_message_to_user(admin_id, user_id, message_text):
    try:
        await bot.send_message(user_id, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
        await send_alert_to_admin(admin_id, f"Ошибка при отправке сообщения пользователю {user_id}: {e}")


# Если ошибка при отправке сообщения пользователю - уведомляем админа об этом
# Если ошибка при отправке админу - просто выводим инфу в консоль
async def send_alert_to_admin(user_id, message_text):
    try:
        await bot.send_message(user_id, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения администратору: {e}")
