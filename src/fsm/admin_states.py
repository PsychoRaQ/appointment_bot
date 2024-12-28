from aiogram.fsm.state import State, StatesGroup

'''
Состояния для всех диалогов (админка)
'''


# Главное меню
class AdminMenuSG(StatesGroup):
    admin_menu = State()  # окно с главным меню бота (админка)


# Изменение расписания
class AdminEditCalendary(StatesGroup):
    first_month = State()
    second_month = State()
    choose_time = State()
    user_on_date = State()


# Просмотр всех записей
class AllAppointments(StatesGroup):
    first_month = State()
    second_month = State()
    appointments_list = State()
