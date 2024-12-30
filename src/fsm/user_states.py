from aiogram.fsm.state import State, StatesGroup

'''
Состояния для всех диалогов (пользователи)
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


# Помощь
class HelpSG(StatesGroup):
    help_menu = State()  # окно с текстом "помощь"


# Помощь
class FeedbackSG(StatesGroup):
    feedback = State()  # окно обратной связи


# "Мои записи"
class UserAppointmentSG(StatesGroup):
    main = State()  # окно "мои записи" - отображает пользователю его записи (если есть)
    delete_appointment_datetime = State()  # окно выбора "слота" для отмены
    delete_appointment_confirm = State()  # окно подтверждения отмены
    delete_appointment_result = State()  # окно с результатом отмены
    no_one_appointment = State()  # окно если у пользователя нет ни одной записи


# Новая запись (пользователь)
class UserNewAppointmentSG(StatesGroup):
    calendary_first_month = State()  # окно календаря на текущий месяц
    calendary_second_month = State()  # окно календаря на следующий месяц
    choose_time = State()  # окно с доступным временем на выбранную дату
    confirm_datetime = State()  # окно с уведомлением об удачной записи на выбранный слот
    error_confirm = State()  # окно с ошибкой записи в базу (уже занято)
    user_max_appointment = State()  # окно с ошибкой (максимальное количество записей)
    # стейты для новой записи со стороны админа
    write_admin_comment = State()  # админ пишет комментарий к слоту
    admin_confirmed_new_appointment = State()  # подтверждение новой записи с комментарием
    confirm_admin_datetime = State()  # окно с уведомлением об удачной записи на выбранный слот
