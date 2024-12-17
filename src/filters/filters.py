from aiogram.filters import BaseFilter

from src.services import database_func
from sqlalchemy.ext.asyncio import AsyncSession

'''
Фильтры для хэндлеров
'''


# Проверяем есть ли пользователь в базе данных (зарегистрирован)
class UserIsRegister(BaseFilter):
    async def __call__(self, message, session: AsyncSession) -> bool:
        result = await database_func.user_is_register(session, message.from_user.id)
        return result is not None
