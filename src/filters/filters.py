# аиограм и алхимия
from aiogram.filters import BaseFilter
from sqlalchemy.ext.asyncio import AsyncSession
# функция для получения объекта "Пользователь" из базы данных
from src.services.database_func import user_is_register

'''
Фильтры для хэндлеров
'''


# Проверяем есть ли пользователь в базе данных (зарегистрирован)
class UserIsRegister(BaseFilter):
    async def __call__(self, message, session: AsyncSession) -> bool:
        result = await user_is_register(session, message.from_user.id)
        return result is not None
