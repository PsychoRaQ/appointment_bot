# аиограм и алхимия
from aiogram.types import User
from aiogram_dialog import DialogManager


# Геттер для окна обратной связи
async def get_admin_feedback(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    url = dialog_manager.middleware_data.get('admin_url')
    return {'url': url}
