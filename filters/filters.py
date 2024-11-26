from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery
from lexicon.lexicon import DATE_LST
from services.database_func import check_user_is_sign,check_user_phone

class DateTimeIsCorrect(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        try:
            date, time = callback.data.split(',')
            return date in DATE_LST and DATE_LST[date].times[time].lock is False
        except:
            return False

class MessageContact(BaseFilter):
    async def __call__(self, message) -> bool:
        return message.contact


class UserIsRegister(BaseFilter):
    async def __call__(self, message) -> bool:
        return check_user_is_sign(str(message.from_user.id)) and check_user_phone(str(message.from_user.id))