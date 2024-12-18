from aiogram.fsm.state import State, StatesGroup

'''
Состояния для всех диалогов
'''


# Регистрация пользователя
class StartSG(StatesGroup):
    start = State()  # окно с приветствием и предложением пройти регистрацию
    get_name = State()  # окно ввода имени
    get_phone = State()  # окно ввода контактного телефона
    confirm = State()  # окно подтверждения, при положительном ответе - перекидываем в главное меню


# Главное меню
class MainMenuSG(StatesGroup):
    main_menu = State()  # окно с главным меню бота


# "Мои записи"
class UserAppointmentSG(StatesGroup):
    main = State()  # окно "мои записи" - отображает пользователю его записи (если есть)
    delete_appointment_datetime = State()  # окно выбора "слота" для отмены
    delete_appointment_confirm = State()  # окно подтверждения отмены
    delete_appointment_result = State()  # окно с результатом отмены
    no_one_appointment = State() # окно если у пользователя нет ни одной записи


# Новая запись (пользователь)
class UserNewAppointmentSG(StatesGroup):
    calendary_first_month = State()  # окно календаря на текущий месяц
    calendary_second_month = State()  # окно календаря на следующий месяц
    choose_time = State()  # окно с доступным временем на выбранную дату
    confirm_datetime = State()  # окно с уведомлением об удачной записи на выбранный слот
    error_confirm = State()  # окно с ошибкой записи
    user_max_appointment = State()  # окно с ошибкой записи
