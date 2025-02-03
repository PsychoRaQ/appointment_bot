# аиограм
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button
# состояния
from app.fsm.admin_states import AdminMenuSG
from app.fsm.user_states import StartSG, MainMenuSG
# паблишер для создания демо-подписки нового админа
from app.services.nats_service.publishers.publishers import new_subscribe
# функции для работы с базой данных
from app.utils.database_func import add_new_user, get_pcode_with_name, edit_admin_pcode
# сервисные функции
from app.utils.service_func import refactor_phone_number


# Хэндлер для кнопки "Подтвердить регистрацию" в меню подтверждения данных
async def confirm_registration(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    # получаем нужные данные
    user_id = callback.message.chat.id
    phone = dialog_manager.dialog_data.get('phone')
    session = dialog_manager.middleware_data.get('session')
    admin_id = dialog_manager.dialog_data.get('admin_id')
    grand_admin_id = dialog_manager.middleware_data.get('admin_ids')
    username = dialog_manager.dialog_data.get('username')
    if username is None:
        username = callback.message.chat.first_name

    # проверяем id пригласившего администратора
    # если пригласивший был старшим админом - регистрируем как администратора
    # если нет - регистрируем как пользователя и привязываем к пригласившему админу
    if admin_id in grand_admin_id:
        role = 'admin'
        next_state = AdminMenuSG.admin_menu
        await edit_admin_pcode(user_id, str(user_id), session)

        # блок для создания пробной версии подписки
        js = dialog_manager.middleware_data.get('js')
        subject = dialog_manager.middleware_data.get('subscribe_subject')
        kv = dialog_manager.middleware_data.get('subscribe_storage')
        days = 30  # количество дней пробной подписки
        await kv.put(str(user_id), bytes(str(days), encoding='utf-8'))
        await new_subscribe(js=js, subject=subject, delay=1, user_id=user_id, days=days)
    else:
        role = 'user'
        next_state = MainMenuSG.main_menu

    await add_new_user(session, user_id, username, phone, admin_id, role)

    bot = dialog_manager.middleware_data.get('bot')

    if role == 'admin':
        await bot.send_message(user_id, 'Вы успешно зарегистрированы!\n '
                                        'Если админка не открылась автоматически, пожалуйста, откройте её вручную в меню бота.')
    await dialog_manager.start(state=next_state, mode=StartMode.RESET_STACK, show_mode=ShowMode.AUTO)


# проверка наличия прромокода в базе данных
async def check_pcode(message: Message,
                      widget: ManagedTextInput,
                      dialog_manager: DialogManager,
                      text: str):
    session = dialog_manager.middleware_data.get('session')
    pcode_from_db = await get_pcode_with_name(text.upper(), session)
    if pcode_from_db:
        admin_id = pcode_from_db.admin_id
        pcode = pcode_from_db.pcode
        dialog_manager.dialog_data.update({'admin_id': admin_id, 'pcode': pcode})
        await dialog_manager.switch_to(state=StartSG.start_with_pcode)
    else:
        await dialog_manager.switch_to(state=StartSG.wrong_pcode)


# Обработчик-фильтр для проверки корректности имени пользователя (только символы, не более 10)
def check_username(data: str) -> str:
    if data.isalpha() and len(data) < 10:
        return data
    raise ValueError


# Обработчик-фильтр для проверки корректности телефона пользователя (формат + длина)
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
    if text.isdigit():
        phone = await refactor_phone_number(text)
        await dialog_manager.update({'phone': phone})
    else:
        await dialog_manager.update({'username': text})
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
