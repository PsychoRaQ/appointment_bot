from aiogram import Router, F
from aiogram.filters import CommandStart, MagicData, or_f
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from src.filters.filters import UserIsRegister
from src.fsm.user_states import MainMenuSG

router = Router()
router.message.filter(or_f(MagicData(F.event.chat.id.in_(F.registered_users)), UserIsRegister()))

'''
Обработка message'ей всех зарегистрированных пользователей
'''


# Хэндлер на команду "Старт" для зарегистрированных пользователей
# Открывает главное меню бота
@router.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=MainMenuSG.main_menu, mode=StartMode.RESET_STACK)
