from config_data import config

LEXICON = {
    '/start': 'Добро пожаловать в бота.\n'
              'Перед началом работы необходимо добавить свои данные в базу.\n'
              'Пожалуйста, добавьте добавьте свой номер телефона при помощи кнопки снизу.\n',
    '/is_register':'Вы уже зарегестрированы.',
    '/help': 'Помощь',
    '/beginning': 'Начало работы',
    '/phone_is_add': 'Номер телефона добавлен!\n'
                     'Теперь Вы можете пользоваться всеми функциями бота.'
}

LEXICON_COMMANDS = {
    '/start': 'Старт',
    '/help': 'Помощь',
    '/beginning': 'Записаться',
    '/calendary': 'Отобразить календарь',
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
