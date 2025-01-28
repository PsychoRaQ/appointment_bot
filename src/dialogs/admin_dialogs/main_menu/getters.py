# аиограм и алхимия
from aiogram.types import User
from aiogram_dialog import DialogManager


# Геттер для отображения главного меню
async def get_admin_menu(**kwargs) -> dict:
    main_menu = [
        ('🗓️ Изменить расписание 🗓️', 'edit_calendary'),
        ('🖊️ Записать пользователя 🖊️', 'make_new_appointment'),
        ('❌ Отменить ручную запись ❌', 'delete_admin_appointment'),
        ('📑 Посмотреть все записи 📑', 'view_all_appointments'),
        ('✉️ Запустить рассылку ✉️', 'mass_dispatch'),
        ('💬 Реферальная ссылка 💬', 'admin_invite'),
        ('⚙ Настройки админки ⚙', 'admin_settings'),
    ]
    grand_admin_main_menu = [
        ('Реферальная ссылка', 'admin_invite'),
        ('Список всех админов', 'view_all_admins'),
        ('Запустить рассылку', 'mass_dispatch'),
    ]
    return {'main_menu': main_menu, 'grand_admin_main_menu': grand_admin_main_menu}


# Геттер для получения роли админа и наличия у него подписки
async def get_admin_role(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    user_role = dialog_manager.middleware_data.get('user_role')
    subscribe = dialog_manager.middleware_data.get('subscribe')
    return {'user_role': user_role, 'subscribe': subscribe}


# Геттер для окна обратной связи (потом перенести в отдельный диалог)
async def get_admin_feedback(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    url = dialog_manager.middleware_data.get('admin_url')
    return {'url': url}
