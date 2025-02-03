# аиограм
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Select, Group
from aiogram_dialog.widgets.text import Const, Format
# состояния
from app.fsm.user_states import MainMenuSG
# геттеры
from app.dialogs.user_dialogs.main_menu.handlers import user_dialog_selection
# хэндлеры
from app.dialogs.user_dialogs.main_menu.getters import get_main_menu

'''
Главное меню бота (для пользователя).
Кнопки создаются в виде кортежа в геттере, обрабатываются в match/case в хэндлере
'''
main_menu_dialog = Dialog(
    Window(
        Const(text='☰      Главное меню     ☰'),
        Group(
            Select(
                Format('{item[0]}'),
                id='main_menu',
                item_id_getter=lambda x: x[1],
                items='main_menu',
                on_click=user_dialog_selection,
            ),
            width=1
        ),
        state=MainMenuSG.main_menu,
        getter=get_main_menu,
    ),
)
