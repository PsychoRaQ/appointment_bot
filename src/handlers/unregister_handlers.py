from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from filters.filters import UserIsRegister
from fsm.states import StartSG

router = Router()
router.message.filter(~UserIsRegister())

'''
Обработка всех message'ей
для незарегистрированных пользователей
'''


# Хэндлер на команду "Старт" для незарегистрированных пользователей
@router.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)
