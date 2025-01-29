# аиограм
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Back, Next, Cancel
from aiogram_dialog.widgets.text import Const, Format
# импорт состояний
from app.fsm.admin_states import Pcode
# геттеры
from app.dialogs.admin_dialogs.admin_invite.getters import get_pcode_from_db, get_pcode_from_dialog
# хэндлеры
from app.dialogs.admin_dialogs.admin_invite.handlers import check_pcode, edit_pcode, confirm_pcode

'''
Диалог для создания реферальных ссылок администратора и/или промокодов для регистрации.
Используются для привязки пользователя к администратору в момент регистрации.
Промокод по умолчанию - id администратора, создается в момент регистрации администратора.

Для старшего администратора - функционал идентичен, если во время регистрации указать промокод или id 
старшего админа - пользователь регистрируется как администратор.
'''

# диалог для рефералок и промокодов
admin_invite_dialog = Dialog(
    # окно отображения актуальных данных о промокоде и реф. ссылке
    Window(
        Format(text='Ваша реферальная ссылка: <code>{link}</code>\n'),
        Format(text='Ваш промокод: <code>{pcode}</code>\n'),
        Const(text='(нажмите чтобы скопировать)'),
        Next(Const(text='Изменить промокод')),
        Cancel(Const(text='☰ Главное меню')),
        state=Pcode.main_pcode,
        getter=get_pcode_from_db
    ),
    # окно ввода нового промокода
    Window(
        Const(text='Отправьте новый промокод:\n'
                   '(2 - 10 символов, регистр не учитывается)'),
        TextInput(
            id='input_pcode',
            type_factory=check_pcode,
            on_success=edit_pcode
        ),
        Back(Const(text='← Назад')),
        state=Pcode.edit_pcode,
    ),
    # окно изменения промокода
    Window(
        Format(text='Подтвердите изменение промокода:\n'),
        Format(text='Новый промокод: {pcode}\n'),
        Button(Const(text='Подтвердить'), id='next_button', on_click=confirm_pcode),
        Back(Const(text='← Назад')),
        state=Pcode.confirm_pcode,
    ),
    # окно с уведомлением об успешном изменении промокода
    Window(
        Const(text='Промокод успешно изменен!\n'),
        Format(text='Новый промокод: {pcode}\n'),
        Cancel(Const(text='☰ Главное меню')),
        state=Pcode.pcode_edit_successfull,
    ),
    # окно с уведомлением о неудачном изменении промокода или неправильном вводе
    Window(
        Const(text='Ошибка: не выполнены требования или такой промокод уже занят. '
                   'Пожалуйста, введите другой промокод\n'
                   '(2 - 10 символов, регистр не учитывается)'),
        TextInput(
            id='input_pcode',
            type_factory=check_pcode,
            on_success=edit_pcode
        ),
        Cancel(Const(text='☰ Главное меню')),
        state=Pcode.error_pcode,
    ),
    getter=get_pcode_from_dialog
)
