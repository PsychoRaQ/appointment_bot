# аиограм
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Next, Cancel
from aiogram_dialog.widgets.text import Const, Format, List
# состояния
from src.fsm.admin_states import AllAdmins
# геттеры
from src.dialogs.admin_dialogs.view_all_admins.getters import get_all_admins, get_admin_data
# хэндлеры
from src.dialogs.admin_dialogs.view_all_admins.handlers import correct_id, edit_admin_data, edit_sub_days

'''
Диалог для отображения (и управления) списка из всех администраторов для Старшего админа.
Для управления администратором - нужно ввести его id.
После этого доступны следующие возможности:
    - установить время подписки для администратора (дни)
    - ...
'''

# список всех админов
view_all_admins_dialog = Dialog(
    # окно с отображением списка администраторов (все их данные) и вводе id админа для настройки
    Window(
        Format(text='Введите id администратора для управления.\n'
                    'Список админов: \n'),
        List(field=Format(
            '<b>{item[username]}</b>\nid - {item[admin_id]}\nТелефон - {item[phone]}\nПодписка - {item[sub_days]}\n'),
            items='admins'),
        TextInput(
            id='input_admin_id',
            type_factory=correct_id,
            on_success=edit_admin_data
        ),
        Cancel(Const(text='☰ Главное меню')),
        getter=get_all_admins,
        state=AllAdmins.main_menu
    ),
    # окно с данными выбранного администратора и кнопками для настройки
    Window(
        Format(text='Администратор: <b>{admin_data[admin_id]}</b>'),
        Format(text='Дней подписки: <b>{admin_data[sub_days]}</b>'),
        Next(Const(text='Изменить время подписки')),
        Back(Const(text='← Назад')),
        getter=get_admin_data,
        state=AllAdmins.edit_admin_data
    ),
    # окно для ввода количества дней подписки для выбранного администратора
    Window(
        Format(text='Администратор: <b>{admin_data[admin_id]}</b>'),
        Format(text='Дней подписки: <b>{admin_data[sub_days]}</b>\n'
                    'Введите новое количество дней подписки.'),
        TextInput(
            id='input_sub_days',
            type_factory=correct_id,
            on_success=edit_sub_days
        ),
        Back(Const(text='← Назад')),
        getter=get_admin_data,
        state=AllAdmins.edit_sub_days
    ),
)
