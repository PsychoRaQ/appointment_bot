from aiogram.filters.callback_data import CallbackData

'''
Фабрики колбэков
'''


# Фабрика для колбэков связанных с инлайн-календарями для пользователя
class CallbackFactoryForUserCalendary(CallbackData, prefix='UC', sep='_'):
    user_id: int
    date: str
    time: str
    status: str


# Фабрика для колбэков связанных с главным меню для пользователя
class CallbackFactoryForUserMenu(CallbackData, prefix='UM', sep='_'):
    user_id: int
    status: str


# Фабрика для колбэков связанных с инлайн-календарями для администратора
class CallbackFactoryForAdminCalendary(CallbackData, prefix='AC', sep='_'):
    user_id: int
    date: str
    time: str
    status: str
