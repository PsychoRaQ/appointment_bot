from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from keyboards.other_kb import create_confirm_registration_keyboard, create_main_menu_kb
from lexicon.lexicon import LEXICON
from services import database_func, service_func, callback_data_factory
from filters.filters import PhoneNumberIsCorrect, UsernameIsCorrect, UserIsRegister

from fsm.FSM import FSMRegistrationGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

router = Router()
router.message.filter(~UserIsRegister())

'''
Обработка всех message'ей
для незарегистрированных пользователей
'''


# Хэндлер для команды Старт (незарегистрированный пользователь)
@router.message(CommandStart(), StateFilter(default_state))
async def proccess_start_command_unregister_user(message: Message, state: FSMContext):
    await message.delete()
    await message.answer(text=LEXICON['/start'], reply_markup=ReplyKeyboardRemove())
    await state.set_state(FSMRegistrationGroup.fill_name)


# Хэндлер для команды Старт (незарегистрированный пользователь)
@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def proccess_start_command_unregister_user(message: Message, state: FSMContext):
    await message.delete()
    await message.answer(text='Отмена регистрации.\n Введите имя.')
    await state.clear()


# Хэндлер при корректном вводе имени, переводит в режим ввода телефона
@router.message(StateFilter(FSMRegistrationGroup.fill_name), UsernameIsCorrect())
async def proccess_add_phone_unregister_user(message: Message, state: FSMContext):
    name = service_func.username_is_correct(message.text)
    await state.update_data(name=name)
    await message.delete()
    text = f'Приятно познакомиться, {name}!\n' + LEXICON['/phone']
    await message.answer(text=text)
    await state.set_state(FSMRegistrationGroup.fill_phone)


# Хэндлер при некорректном вводе имени при регистрации
@router.message(StateFilter(FSMRegistrationGroup.fill_name))
async def process_warning_bad_name(message: Message):
    await message.delete()
    await message.answer(text=LEXICON['/bad_name'])


# Хэндлер при корректном вводе телефона, регистрация окончена
@router.message(StateFilter(FSMRegistrationGroup.fill_phone), PhoneNumberIsCorrect())
async def process_register_is_done(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    name = data.get('name')
    phone = service_func.refactor_phone_number(message.text)
    await state.update_data(phone=phone)
    text = f'{LEXICON['/confirm_userdata']}Ваше имя: {name}\nНомер телефона: {phone}'
    keyboard = create_confirm_registration_keyboard()
    await message.answer(text=text, reply_markup=keyboard)
    await state.set_state(FSMRegistrationGroup.fill_user_accept)


# Хэндлер при некорректном вводе телефона
@router.message(StateFilter(FSMRegistrationGroup.fill_phone))
async def process_warning_bad_name(message: Message):
    await message.delete()
    await message.answer(text=LEXICON['/bad_phone'])


# Хэндлер при подтверждении регистрации:
@router.callback_query(StateFilter(FSMRegistrationGroup.fill_user_accept),
                       callback_data_factory.CallbackFactoryForUserMenu.filter(F.status == 'RegConfirm'))
async def proccess_confirm_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    phone = data.get('phone')
    database_func.new_user_to_db(callback.message.chat.id, name, phone)
    await state.clear()
    await callback.message.edit_text(text=LEXICON['/registration_is_done'], reply_markup=create_main_menu_kb())


# Хэндлер при отмене регистрации:
@router.callback_query(StateFilter(FSMRegistrationGroup.fill_user_accept),
                       callback_data_factory.CallbackFactoryForUserMenu.filter(F.status == 'NoReg'))
async def proccess_confirm_registration_is_bad(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text=LEXICON['/no_reg'], reply_markup=None)

# # Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# # кроме состояния по умолчанию, и отключать машину состояний
# @router.message(Command(commands='cancel'), ~StateFilter(default_state))
# async def process_cancel_command_state(message: Message, state: FSMContext):
#     await message.answer(
#         text='Вы вышли из машины состояний\n\n'
#              'Чтобы снова перейти к заполнению анкеты - '
#              'отправьте команду /fillform'
#     )
#     # Сбрасываем состояние и очищаем данные, полученные внутри состояний
#     await state.clear()


#
# # Хэндлер обработки кнопки отправки телефона (регистрация пользователя в боте + заносим его в БД)
# @router.message(MessageContact())
# async def process_registration_user(message: Message):
#     database_func.new_user_to_db(message.from_user.id, message.from_user.first_name, message.contact.phone_number)
#     await message.delete()
#     await message.answer(text=LEXICON['/phone_is_add'],
#                          reply_markup=ReplyKeyboardRemove())
#
# # Хэндлер для всех остальных сообщений от незарегистрированного пользователя
# @router.message()
# async def other_unregister_message(message: Message):
#     await message.delete()
#     await message.answer(text=LEXICON['/unregister_message'])
