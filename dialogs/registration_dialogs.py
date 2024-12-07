from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, User, CallbackQuery
from aiogram_dialog import DialogManager, StartMode, Dialog, Window
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const, Format

from filters.filters import UserIsRegister
from keyboards.other_kb import create_main_menu_kb
from lexicon.lexicon import LEXICON
from services.service_func import refactor_phone_number

router = Router()
router.message.filter(~UserIsRegister())


class StartSG(StatesGroup):
    start = State()
    get_name = State()
    get_phone = State()
    confirm = State()


async def go_next(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if button.widget_id == 'b_next_username':
        await dialog_manager.next()


async def go_back(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


async def cancel_registration(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(StartSG.start)


async def confirm_registration(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()
    await callback.message.answer(text=LEXICON['/registration_is_done'], reply_markup=create_main_menu_kb())


def check_username(data: str) -> str:
    if data.isalpha():
        return data
    raise ValueError


def check_phone(data: str) -> str:
    if len(data) == 11:
        if data[0] == '+' and data[1] == '7' and data[1:].isdigit():
            return data
    else:
        if (data[0] == '8' or data[0] == '7') and len(data) == 10:
            return data
    raise ValueError


# Хэндлер, который сработает, если пользователь ввел корректный возраст
async def correct_input(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str ) -> None:
    if text.isalpha():
        await dialog_manager.update({'username': text})
    else:
        phone = refactor_phone_number(text)
        await dialog_manager.update({'phone': phone})
    print('good')
    await dialog_manager.next()


# Хэндлер, который сработает на ввод некорректного возраста
async def error_input(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError):
    await message.answer(
        text='Вы ввели некорректное значение.\n Пожалуйста, введите правильно.'
    )
    print('not good')


# Это геттер
async def get_userdata(event_from_user: User, **kwargs):
    user_id = event_from_user.id,
    username = event_from_user.first_name
    return {'user_id': user_id, 'username': username}


start_dialog = Dialog(
    Window(
        Const('Добро пожаловать!\nПеред тем как записаться, нужно пройти регистрацию'),
        Button(Const('Зарегистрироваться'), id='b_next', on_click=go_next),
        getter=get_userdata,
        state=StartSG.start
    ),
    Window(
        Const(
            'Давайте познакомимся?\nПожалуйста, отправьте в чат Ваше имя.\n\nЕсли хотите взять Ваше имя из телеграмма - просто нажмите "Продолжить"'),
        TextInput(
            id='name_input',
            type_factory=check_username,
            on_success=correct_input,
            on_error=error_input,
        ),
        Row(
            Button(Const('◀️ Назад'), id='b_back', on_click=go_back),
            Button(Const('Продолжить ▶️'), id='b_next_username', on_click=go_next),
        ),
        getter=get_userdata,
        state=StartSG.get_name
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
        Row(
            Button(Const('◀️ Назад'), id='b_back', on_click=go_back),
        ),
        getter=get_userdata,
        state=StartSG.get_phone
    ),
    Window(
        Format('Пожалуйста, проверьте Ваши данные:\b Имя: {}\nТелефон: {}\n\nВсе верно?'),
        Button(Const('Подтвердить регистрацию'), id='b_confirm', on_click=confirm_registration),
        Button(Const('Пройти регистрацию сначала'), id='b_cancel', on_click=cancel_registration),
        getter=get_userdata,
        state=StartSG.confirm
    ),
)


# Хэндлер на команду "Старт" для незарегистрированных пользователей
@router.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)
