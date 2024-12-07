from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, User, CallbackQuery
from aiogram_dialog import DialogManager, StartMode, Dialog, Window, ShowMode
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Row, Back, Next
from aiogram_dialog.widgets.text import Const, Format

from filters.filters import UserIsRegister
from keyboards.other_kb import create_main_menu_kb
from lexicon.lexicon import LEXICON
from services.service_func import refactor_phone_number
from services.database_func import new_user_to_db

router = Router()
router.message.filter(~UserIsRegister())


class StartSG(StatesGroup):
    start = State()
    get_name = State()
    get_phone = State()
    confirm = State()


# Хэндлер для обработки кнопки "Продолжить" в меню выбора имени (берем имя пользователя из ТГ)
async def go_next(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await dialog_manager.update({'username': callback.message.chat.first_name})
    await dialog_manager.next()


# Хэндлер для кнопки "Пройти регистрацию сначала" в меню подтверждения данных
async def cancel_registration(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(StartSG.start)


# Хэндлер для кнопки "Подтвердить регистрацию" в меню подтверждения данных
async def confirm_registration(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    user_id = callback.message.chat.id
    username = dialog_manager.dialog_data.get('username')
    phone = dialog_manager.dialog_data.get('phone')
    if new_user_to_db(user_id, username, phone):
        await dialog_manager.done()
        await callback.message.edit_text(text=LEXICON['/registration_is_done'], reply_markup=create_main_menu_kb())
    else:
        print('Ошибка при регистрации')


# Обработчик-фильтр для проверки корректности имени пользователя
def check_username(data: str) -> str:
    if data.isalpha() and len(data) < 10:
        return data
    raise ValueError


# Обработчик-фильтр для проверки корректности телефона пользователя
def check_phone(data: str) -> str:
    if len(data) == 12:
        if data[0] == '+' and data[1] == '7' and data[1:].isdigit():
            return data
    else:
        if (data[0] == '8' or data[0] == '7') and len(data) == 11:
            return data
    raise ValueError


# Хэндлер, который сработает, если пользователь ввел корректное имя/телефон
async def correct_input(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    if text.isalpha():
        await dialog_manager.update({'username': text})
    else:
        phone = refactor_phone_number(text)
        await dialog_manager.update({'phone': phone})
    await dialog_manager.next(show_mode=ShowMode.EDIT)


# Хэндлер, который сработает на ввод некорректного имени/телефона
async def error_input(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError) -> None:
    await message.answer(
        text='Вы ввели некорректное значение.\n Пожалуйста, введите правильно.'
    )


# Геттер
async def get_userdata(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    if dialog_manager.dialog_data.get('username'):
        username = dialog_manager.dialog_data.get('username')
    else:
        username = event_from_user.first_name
    phone = dialog_manager.dialog_data.get('phone')
    return {'username': username, 'phone': phone}


# Диалог регистрации пользователя
start_dialog = Dialog(
    Window(
        Const('Добро пожаловать!\nПеред тем как записаться, нужно пройти регистрацию'),
        Next(Const('Зарегистрироваться'), id='b_next'),
        getter=get_userdata,
        state=StartSG.start
    ),
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
            Back(Const('◀️ Назад'), id='b_back'),
            Button(Const('Продолжить ▶️'), id='b_next_username', on_click=go_next),
        ),
        getter=get_userdata,
        state=StartSG.get_name,
    ),
    Window(
        Format(
            'Отлично, {username}!\n Пожалуйста, отправьте в чат свой номер телефона для связи\n(на всякий случай)\n\nПримечание: Вы можете ввести свой номер в любом формате (8, +7, 7)'),
        TextInput(
            id='phone_input',
            type_factory=check_phone,
            on_success=correct_input,
            on_error=error_input,
        ),
        Back(Const('◀️ Назад'), id='b_back'),
        getter=get_userdata,
        state=StartSG.get_phone
    ),
    Window(
        Format('Пожалуйста, проверьте Ваши данные.\nИмя: {username}\nТелефон: {phone}\n\nВсе верно?'),
        Button(Const('Подтвердить регистрацию'), id='b_confirm', on_click=confirm_registration),
        Button(Const('Пройти регистрацию сначала'), id='b_cancel', on_click=cancel_registration),
        getter=get_userdata,
        state=StartSG.confirm
    ),
    getter=get_userdata,

)


# Хэндлер на команду "Старт" для незарегистрированных пользователей
@router.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)
