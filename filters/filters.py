from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery
from services import database_func


# Проверяем наличие "контакта" в сообщении
class MessageContact(BaseFilter):
    async def __call__(self, message) -> bool:
        return message.contact


class UserIsRegister(BaseFilter):
    async def __call__(self, message) -> bool:
        return database_func.user_is_sign(message.from_user.id)


class UserIsGeneralAdmin(BaseFilter):
    async def __call__(self, message) -> bool:
        users = database_func.get_userdata(message.from_user.id)
        if users:
            for user in users:
                print(user)
                return user[5] == 2
        return False


class UserIsAdmin(BaseFilter):
    async def __call__(self, message) -> bool:
        users = database_func.get_userdata(message.from_user.id)
        if users:
            for user in users:
                return user[5] == 1
        return False


class AdminChooseDate(BaseFilter):
    async def __call__(self, callback) -> bool:
        try:
            cb_date, is_admin = callback.data.split('_')
            return callback.data == f'{cb_date}_admin' and ',' not in cb_date
        except:
            return False


class AdminChooseTime(BaseFilter):
    async def __call__(self, callback) -> bool:
        try:
            cb_date, is_admin = callback.data.split('_')
            return callback.data == f'{cb_date}_admin' and ',' in cb_date
        except:
            return False
