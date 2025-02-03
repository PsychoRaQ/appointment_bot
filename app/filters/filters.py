# аиограм и алхимия
from aiogram.filters import BaseFilter
from sqlalchemy.ext.asyncio import AsyncSession
# функция для получения объекта "Пользователь" из базы данных
from app.utils.database_func import user_is_register

'''
Фильтры для хэндлеров
'''


# Проверяем есть ли пользователь в базе данных (зарегистрирован)
class UserIsRegister(BaseFilter):
    async def __call__(self, message, session: AsyncSession) -> bool:
        result = await user_is_register(session, message.from_user.id)
        return result is not None


class UserIsAdmin(BaseFilter):
    async def __call__(self, message, **data) -> bool:
        role = data.get('user_role')
        return role in ('admin', 'grand_admin')