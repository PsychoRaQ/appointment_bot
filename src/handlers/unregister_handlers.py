# аиограм
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

# состояния (меню регистрации)
from src.fsm.user_states import StartSG
# функции базы данных
from src.services.database_func import get_admin_pcode

# подключаем роутер
router = Router()

'''
Обработка всех message'ей
для незарегистрированных пользователей
(незарегистрированный - id пользователя нет в таблице Users)
'''


# Хэндлер на команду "Старт" для незарегистрированных пользователей
# Запуск процесса регистрации пользователя
@router.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    text_lst = message.text.split()
    if len(text_lst) > 1:
        admin_id = int(text_lst[1])
        session = dialog_manager.middleware_data['session']
        pcode_in_database = await get_admin_pcode(admin_id, session)
        if pcode_in_database:
            await dialog_manager.start(state=StartSG.start_with_pcode, mode=StartMode.RESET_STACK)
            dialog_manager.dialog_data.update({'admin_id': admin_id})
        else:
            await dialog_manager.start(state=StartSG.wrong_pcode, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)
