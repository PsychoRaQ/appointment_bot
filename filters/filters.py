from aiogram.filters import BaseFilter
from services import database_func

'''
Фильтры для хэндлеров
'''


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


# проверяем имя пользователя при регистрации на корректность
class UsernameIsCorrect(BaseFilter):
    async def __call__(self, message):
        name = message.text.split(' ')[0] if ' ' in message.text else message.text
        return name.isalpha()

# проверяем телефон пользователя при регистрации на корректность
class PhoneNumberIsCorrect(BaseFilter):
    async def __call__(self, message):
        phone = message.text
        if phone[0] == '8':
            return phone.isdigit() and len(phone[1:]) == 10
        elif phone[0] == '+' and phone[1] == '7':
            return phone[2:].isdigit() and len(phone[2:]) == 10
        elif phone[0] == '7':
            return phone.isdigit() and len(phone[1:]) == 10
        else:
            return False

