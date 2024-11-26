from config_data import config

LEXICON = {
    '/start': 'Добро пожаловать в бота.\n'
              'Перед началом работы необходимо зарегистрироваться.\n'
              'Пожалуйста, добавьте добавьте свой номер телефона при помощи кнопки снизу.\n',
    '/is_register':'Вы уже зарегистрированы.\n'
                   'Чтобы узнать о возможностях бота, напишите /help или выберите раздел "Помощь" в главном меню',
    '/help': 'Помощь - в разработке',
    '/beginning': 'Начало работы - в разработке',
    '/phone_is_add': 'Номер телефона добавлен!\n'
                     'Теперь Вы можете пользоваться всеми функциями бота.\n\n'
                     'Чтобы узнать о возможностях бота, напишите /help или выберите раздел "Помощь" в главном меню',
    '/unregister_message': 'Вы не зарегистрированы.\n'
                           'Перед началом работы необходимо зарегистрироваться.\n'
              'Пожалуйста, добавьте добавьте свой номер телефона при помощи кнопки снизу.\n',
    '/unknown_message': 'Команда не распознана.\n'
                        'Чтобы узнать о возможностях бота, напишите /help или выберите раздел "Помощь" в главном меню',
}

LEXICON_COMMANDS = {
    '/start': 'Зарегистрироваться',
    '/help': 'Помощь - в разработке',
    '/beginning': 'Записаться - в разработке',
    '/calendary': 'Отобразить календарь - в разработке',
    '/delete_my_appointment': 'Удалить свою запись - в разработке',
}

START_KB_TEXT = {
    'no_phone': 'Добавить телефон ❌',
    'yes_phone': 'Телефон добавлен ✅',
    'no_name': 'Добавить ФИО ❌',
    'yes_name': 'Имя добавлено ✅'
}


# CALENDARY = {str(i):f'{i}.{config.MONTH}' for i in range(1,32)}
# TIME = {i:i for i in config.DATETIME}

class Time:
    def __init__(self, time):
        self.time = time
        self.lock = False


class Date:
    def __init__(self, date, times):
        self.times: dict = times
        self.date = date


DATE_LST = {f'{i}.{config.MONTH}': Date(str(i), {j: Time(j) for j in config.DATETIME}) for i in range(1, 32)}

# DATE_LST['1.11'].times['11:00'].lock
