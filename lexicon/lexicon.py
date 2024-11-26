from config_data import config

LEXICON = {
    '/start': 'Старт',
    '/help': 'Помощь',
    '/beginning': 'Начало работы',
}

LEXICON_COMMANDS = {
    '/start': 'Старт',
    '/help': 'Помощь',
    '/beginning': 'Записаться',
    '/calendary': 'Отобразить календарь',
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
