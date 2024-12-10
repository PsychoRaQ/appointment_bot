from aiogram.fsm.state import State, StatesGroup
'''
Класс FSM
'''

class FSMRegistrationGroup(StatesGroup):
    fill_name = State()  # Состояние ожидания ввода имени
    fill_phone = State()  # Состояние ожидания ввода возраста
    fill_user_accept = State()  # Состояние ожидания ввода возраста





# Регистрация пользователя
class StartSG(StatesGroup):
    start = State()
    get_name = State()
    get_phone = State()
    confirm = State()

# Главное меню
class MainMenuSG(StatesGroup):
    main_menu = State()


# "Мои записи"
class UserAppointmentSG(StatesGroup):
    main = State()
    delete_appointment = State()

# Новая запись (пользователь)
class UserNewAppointmentSG(StatesGroup):
    calendary_first_month = State()
    calendary_second_month = State()
    choose_time = State()
    confirm_datetime = State()
    error_confirm = State()
