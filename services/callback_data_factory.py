from aiogram.filters.callback_data import CallbackData


class CallbackFactoryForUserCalendary(CallbackData, prefix='UC', sep='_'):
    user_id: int
    date: str
    time: str
    status: str


class CallbackFactoryForAdminCalendary(CallbackData, prefix='AC', sep='_'):
    user_id: int
    date: str
    time: str
    status: str
