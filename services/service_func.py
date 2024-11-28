from services.database_func import get_user_data_from_db
from lexicon.lexicon import LEXICON
from config_data.bot_init import bot

# получение актуальных записей из профиля пользователя
def get_user_appointment(user_id: str) -> str:
    db = get_user_data_from_db(user_id)['date']
    if db != {}:
        date_lst = []

        for date, time in db.items():
            time = ', '.join(sorted(time))
            text = f'{date} - {time}\n'
            date_lst.append(text)

        date_lst.sort()
        date_lst.append(f'\n{LEXICON['/user_appointment_end']}')
        date_lst.insert(0, f'\n{LEXICON['/user_appointment']}')
        text = ''.join(date_lst)

    else:
        text = LEXICON['/no_one_appointment']
    return text

# Уведомление ползователя об отмене его записи (администратором)
async def send_message_to_user(admin_id, user_id, message_text):
    try:
        await bot.send_message(user_id, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
        await send_alert_to_admin(admin_id, f"Ошибка при отправке сообщения пользователю {user_id}: {e}" )

# Если ошибка при отправке сообщения пользователю - уведомляем админа об этом
# Если ошибка при отправке админу - просто выводим инфу в консоль
async def send_alert_to_admin(user_id, message_text):
    try:
        await bot.send_message(user_id, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения администратору: {e}")