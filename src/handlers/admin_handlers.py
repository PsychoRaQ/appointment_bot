# аиограм
from aiogram import Router, F
from aiogram.filters import CommandStart, MagicData
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
# состояния (админ меню)
from src.fsm.admin_states import AdminMenuSG

# подключаем и настраиваем роутер (id в списке админов)
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
    await dialog_manager.start(state=AdminMenuSG.admin_menu, mode=StartMode.RESET_STACK)
