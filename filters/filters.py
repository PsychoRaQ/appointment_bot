from aiogram.filters import BaseFilter
from services import database_func


# Проверяем наличие "контакта" в сообщении
class MessageContact(BaseFilter):
    async def __call__(self, message) -> bool:
        return message.contact

# Проверяем есть ли пользователь в базе данных (зарегистрирован)
class UserIsRegister(BaseFilter):
    async def __call__(self, message) -> bool:
        return database_func.user_is_sign(message.from_user.id)

# Проверяем является ли пользователь старшим админом
class UserIsGeneralAdmin(BaseFilter):
    async def __call__(self, message) -> bool:
        users = database_func.get_userdata(message.from_user.id)
        if users:
            for user in users:
                return user[5] == 2
        return False

# Проверяем является ли пользователь обычным админом
class UserIsAdmin(BaseFilter):
    async def __call__(self, message) -> bool:
        users = database_func.get_userdata(message.from_user.id)
        if users:
            for user in users:
                return user[5] == 1
        return False