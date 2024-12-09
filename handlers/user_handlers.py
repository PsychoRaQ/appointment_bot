import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from filters.filters import UserIsRegister
from fsm.states import MainMenuSG

router = Router()
router.message.filter(UserIsRegister())
logger = logging.getLogger(__name__)


# Хэндлер на команду "Старт" для зарегистрированных пользователей
@router.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=MainMenuSG.main_menu, mode=StartMode.RESET_STACK)
