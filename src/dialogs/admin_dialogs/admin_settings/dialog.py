# аиограм
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Back, Next, Cancel
from aiogram_dialog.widgets.text import Const, Format
# состояния
from src.fsm.admin_states import AdminSettings
# геттеры
from src.dialogs.admin_dialogs.view_all_admins.getters import get_admin_data
from src.dialogs.admin_dialogs.admin_settings.getters import get_admin_feedback

'''
Диалог для настройки админки у администратора.
На данный момент реализовано только управление подпиской.
'''

# настройки админки
admin_settings_dialog = Dialog(
    # окно с отображением оставшихся дней подписки и кнопками настроек
    Window(
        Format(text='Настройки админки:\n\n'
                    'Ваша подписка заканчивается через {admin_data[sub_days]} дней.'),
        Next(Const(text='Продлить подписку')),
        Cancel(Const(text='☰ Главное меню')),
        getter=get_admin_data,
        state=AdminSettings.main_menu
    ),
    # окно для продления подписки
    Window(
        Format(text='Для продления подписки напишите администратору:'),
        Format(text='{url}'),
        Back(Const(text='← Назад')),
        state=AdminSettings.feedback,
        getter=get_admin_feedback,
    ),
)
