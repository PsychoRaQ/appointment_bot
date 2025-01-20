# типизация
from typing import Callable, Awaitable, Dict, Any
# аиограм и алхимия
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
# функции базы данных
from src.services.database_func import user_is_register

'''
Мидлварь создания сессии для работы с базой данных
Подключается как внешняя мидлварь
'''


# создание сессии
class UserRoleMiddlware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        session = data.get('session')
        user_id = data["event_from_user"].id
        user = await user_is_register(session, user_id)
        if user:
            data["user_role"] = user.role
            if user.role == 'admin':
                kv = data.get('subscribe_storage')
                kv_data = await kv.get(str(user_id))
                days = int(kv_data.value.decode("utf-8"))
                if days <= 0:
                    data["subscribe"] = 'unpaid'
                else:
                    data["subscribe"] = 'paid'
        return await handler(event, data)
