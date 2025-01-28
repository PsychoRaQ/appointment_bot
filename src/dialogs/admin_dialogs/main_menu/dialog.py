# аиограм
from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Back, Next, Select, Group
from aiogram_dialog.widgets.text import Const, Format
# состояния
from src.fsm.admin_states import AdminMenuSG
# геттеры
from src.dialogs.admin_dialogs.main_menu.getters import get_admin_menu, get_admin_role, get_admin_feedback
# хэндлеры
from src.dialogs.admin_dialogs.main_menu.handlers import admin_dialog_selection

'''
Главное меню бота для администратора
Кнопки создаются в виде кортежа в геттере, обрабатываются в match/case в хэндлере.

Во время каждого открытия окна меню происходит проверка на наличие подписки у админа а также
проверка на роль (админ/старший админ).
В зависимости от наличия подписки и роли, выбирается вариант окна для отображения.
'''

# Главное меню
main_menu_dialog = Dialog(
    Window(
        # основное окно главного меню (есть подписка)
        Const(text='☰           Админка          ☰'),
        Group(
            Select(
                Format('{item[0]}'),
                id='main_menu',
                item_id_getter=lambda x: x[1],
                items='main_menu',
                on_click=admin_dialog_selection,
            ),
            width=1,
            when=F['user_role'] == 'admin' and F['subscribe'] == 'paid'
        ),
        Group(
            Select(
                Format('{item[0]}'),
                id='grand_admin_menu',
                item_id_getter=lambda x: x[1],
                items='grand_admin_main_menu',
                on_click=admin_dialog_selection,
            ),
            width=1,
            when=F['user_role'] == 'grand_admin'
        ),
        Next(Const(text='Продлить подписку'), id='pay_btn',
             when=F['user_role'] == 'admin' and F['subscribe'] == 'unpaid'),
        state=AdminMenuSG.admin_menu,
        getter=get_admin_menu
    ),
    Window(
        # окно кнопки обратной связи (нужно перенести)
        Format(text='Для продления подписки напишите администратору:'),
        Format(text='{url}'),
        Back(Const(text='← Назад'),
             id='b_button'),
        state=AdminMenuSG.unpaid_menu,
        getter=get_admin_feedback,
    ),
    getter=get_admin_role
)
