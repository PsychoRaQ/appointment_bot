# аиограм и алхимия
from aiogram_dialog import DialogManager


# Геттер для отображения данных о рассылке
async def get_dispatch_text(dialog_manager: DialogManager, **kwargs) -> dict:
    text = dialog_manager.dialog_data.get('text')
    return {'text': text}
