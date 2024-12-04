from aiogram.fsm.state import State, StatesGroup
'''
Класс FSM
'''

class FSMRegistrationGroup(StatesGroup):
    fill_name = State()  # Состояние ожидания ввода имени
    fill_phone = State()  # Состояние ожидания ввода возраста
    fill_user_accept = State()  # Состояние ожидания ввода возраста
