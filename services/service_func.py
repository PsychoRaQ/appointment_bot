from services.database_func import get_user_data_from_db
from lexicon.lexicon import LEXICON

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