# аиограм
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
# состояния
from app.fsm.admin_states import Pcode
# функции для работы с БД
from app.utils.database_func import edit_admin_pcode, get_pcode_with_name


# Обработчик-фильтр для проверки корректности промокода
def check_pcode(data: str) -> str:
    if 11 > len(data) > 1:
        return data
    raise ValueError


# изменение текста промокода (после прохождения фильтра)
async def edit_pcode(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        data: str) -> None:
    dialog_manager.dialog_data.update({'pcode': data.upper()})
    await dialog_manager.next()


# подтверждение изменения промокода (изменяем его в базе данных)
async def confirm_pcode(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager) -> None:
    pcode = dialog_manager.dialog_data.get('pcode')
    session = dialog_manager.middleware_data.get('session')
    admin_id = message.from_user.id
    unique = await get_pcode_with_name(pcode, session)
    if unique:
        await dialog_manager.switch_to(state=Pcode.error_pcode)
    else:
        await edit_admin_pcode(admin_id, pcode, session)
        await dialog_manager.next()
