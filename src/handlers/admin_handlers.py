# аиограм
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
# фильтры
from src.filters.filters import UserIsAdmin
# состояния (админ меню)
from src.fsm.admin_states import AdminMenuSG

# подключаем и настраиваем роутер (id в списке админов)
router = Router()
router.message.filter(UserIsAdmin())

'''
Обработка message'ей админов
проверка по telegram id из конфига
'''


# Хэндлер на команду "Старт"
# Открывает главное меню бота для администратора
@router.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=AdminMenuSG.admin_menu, mode=StartMode.RESET_STACK)
