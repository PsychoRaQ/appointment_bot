# аиограм
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Row, Back, Next, Cancel
from aiogram_dialog.widgets.text import Const, Format
# состояния
from src.fsm.user_states import StartSG
# геттеры
from src.dialogs.user_dialogs.user_registration.getters import get_userdata
# хэндлеры
from src.dialogs.user_dialogs.user_registration.handlers import (confirm_registration, correct_input, check_phone,
                                                                 check_username, check_pcode, error_input)

'''
Регистрация нового пользователя в боте.
Открывается при команде /start, если пользователя нет в базе данных.

При регистрации - проверяется промокод или реферальная ссылка.
Если ссылка (или промокод) от Старшего админа - регистрируем как "администратора" и выдаем N дней пробной подписки.
Если ссылка (или промокод) от администратора - регистрируем как "пользователя" и привязываем его к пригласившему админу.
'''

registration_dialog = Dialog(
    # окно открывается если пользователь просто написал /start не переходя по ссылке или отменил регистрацию в процессе
    Window(
        Const(
            'Добро пожаловать!\nПожалуйста, введите промокод пригласившего Вас администратора или пройдите по его персональной ссылке.'),
        TextInput(
            id='input_pcode',
            on_success=check_pcode,
        ),
        state=StartSG.start
    ),
    # окно при неверном вводе промокода или при переходе по устаревшей ссылки
    Window(
        Const(
            'Промокод не найден!\nПожалуйста, введите правильный промокод или пройдите по персональной ссылке администратора.'),
        TextInput(
            id='input_pcode',
            on_success=check_pcode,
        ),
        state=StartSG.wrong_pcode
    ),
    # окно при корректном вводе промокода или переходе по актуальной ссылке
    Window(
        Const('Добро пожаловать!\nПеред тем как записаться, нужно пройти регистрацию'),
        Next(Const('Зарегистрироваться')),
        state=StartSG.start_with_pcode
    ),
    # окно ввода никнейма
    Window(
        Const(
            'Давайте познакомимся?\nПожалуйста, отправьте в чат Ваше имя.\n(Не более 10 символов)\n\nЕсли хотите взять Ваше имя из телеграмма - просто нажмите "Продолжить"'),
        TextInput(
            id='name_input',
            type_factory=check_username,
            on_success=correct_input,
            on_error=error_input,
        ),
        Row(
            Back(Const('← Назад')),
            Next(Const('Продолжить →')),
        ),
        state=StartSG.get_name,
    ),
    # окно ввода номера телефона
    Window(
        Format(
            'Отлично, {username}!\n Пожалуйста, отправьте в чат свой номер телефона для связи\n(на всякий случай)\n\nПримечание: Вы можете ввести свой номер в любом формате (8, +7, 7)'),
        TextInput(
            id='phone_input',
            type_factory=check_phone,
            on_success=correct_input,
            on_error=error_input,
        ),
        Back(Const('← Назад')),
        state=StartSG.get_phone
    ),
    # окно подтверждения введенных данных
    # при подтверждении - пользователь вносится в базу данных
    Window(
        Format('Пожалуйста, проверьте Ваши данные.\nИмя: {username}\nТелефон: {phone}\n\nВсе верно?'),
        Cancel(Const('Пройти регистрацию сначала')),
        Button(Const('Подтвердить регистрацию'), id='b_confirm', on_click=confirm_registration),
        state=StartSG.confirm
    ),
    getter=get_userdata,
)
