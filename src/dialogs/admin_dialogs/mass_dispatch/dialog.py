# аиограм
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Back, Cancel
from aiogram_dialog.widgets.text import Const, Format
# состояния
from src.fsm.admin_states import Dispatch
# геттеры
from src.dialogs.admin_dialogs.mass_dispatch.getters import get_dispatch_text
# хэндлдеры
from src.dialogs.admin_dialogs.mass_dispatch.handlers import start_mass_dispatch, edit_dispatch_text

'''
Диалог для функционала массовой рассылки.
Администраторы могу сделать рассылку по всем привязанным к ним пользователям.
Старший администратор делает рассылку по всем администраторам.

В данный момент доступна только рассылка текста.
'''

# рассылка
mass_dispatch_dialog = Dialog(
    # окно ввода текста рассылки
    Window(
        Const(text='Отправьте текст рассылки (форматирование будет сохранено):'),
        TextInput(
            id='input_dispatch',
            on_success=edit_dispatch_text
        ),
        Cancel(Const(text='☰ Главное меню')),
        state=Dispatch.edit_dispatch
    ),
    # окно отправки рассылки
    Window(
        Const(text='Подтвердите рассылку:\n'),
        Format('{text}'),
        Button(Const(text='Запустить рассылку'), id='b_next', on_click=start_mass_dispatch),
        Back(Const(text='← Назад')),
        state=Dispatch.confirm_dispatch
    ),
    # окно с подтверждением успешной отправки рассылки
    Window(
        Const(text='Рассылка успешно отправлена!\n'
                   'Текст рассылки:\n'),
        Format('{text}'),
        Cancel(Const(text='☰ Главное меню')),
        state=Dispatch.dispatch_is_successfull
    ),
    getter=get_dispatch_text
)
