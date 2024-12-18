from aiogram import Router, F
from aiogram.filters import CommandStart, MagicData
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from src.filters.filters import UserIsRegister
from src.fsm.user_states import MainMenuSG

router = Router()
router.message.filter(MagicData(F.event.chat.id.in_(F.admin_ids)))

'''
Обработка message'ей админов
проверка по telegram id из конфига
'''


# Хэндлер на команду "Старт"
# Открывает главное меню бота для администратора
@router.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=MainMenuSG.main_menu, mode=StartMode.RESET_STACK)
