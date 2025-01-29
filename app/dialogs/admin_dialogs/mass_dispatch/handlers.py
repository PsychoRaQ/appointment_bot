# аиограм
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput
# паблишер натс для рассылки
from app.services.nats_service.publishers.publishers import send_dispatch
# функции для работы с БД
from app.utils.database_func import get_all_users_with_admin_id


# админ ввел текст для рассылки
async def edit_dispatch_text(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    await dialog_manager.update({'text': text})
    await dialog_manager.next(show_mode=ShowMode.EDIT)


# запуск рассылки(получаем всех юзеров конкретного админа и отправляем сообщения в натс)
async def start_mass_dispatch(callback: CallbackQuery,
                              widget: ManagedTextInput,
                              dialog_manager: DialogManager) -> None:
    session = dialog_manager.middleware_data.get('session')
    user_ids = await get_all_users_with_admin_id(session, callback.from_user.id)
    message_text = bytes(dialog_manager.dialog_data.get('text'), encoding='utf-8')
    js = dialog_manager.middleware_data.get('js')
    subject = dialog_manager.middleware_data.get('dispatch_subject')

    for id in user_ids:
        await send_dispatch(js=js,
                            subject=subject,
                            delay=1,
                            user_id=id,
                            payload=message_text)

    await dialog_manager.next(show_mode=ShowMode.EDIT)
